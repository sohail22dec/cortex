"""
RAG Agent — retrieves relevant document chunks, evaluates relevance/groundedness/utility (Self-RAG/CRAG),
and generates grounded answers with citations.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import config
from rag import vector_store as vs

logger = logging.getLogger(__name__)

# LLM for generation
_llm = ChatGroq(
    model=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.3,
)

# LLM for evaluation (zero temperature for deterministic JSON responses)
_eval_llm = ChatGroq(
    model=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
)

SYSTEM_PROMPT = """You are Cortex, a document-aware AI assistant.
You are given relevant excerpts from the user's uploaded documents.
Answer the question accurately based ONLY on the provided context.
If the context doesn't contain enough information to answer, state clearly what is found and what is missing.
Always reference which document(s) you used in your answer.
Format your answer clearly using markdown where helpful."""

STRICT_SYSTEM_PROMPT = """You are Cortex, a document-aware AI assistant with STRICT groundedness rules.
Answer the question using ONLY facts directly stated in the provided document context.
Do NOT make assumptions, extrapolate, or bring in outside knowledge.
If a claim cannot be verified from the text, omit it entirely.
Format your answer clearly using markdown."""


def _clean_json(raw: str) -> str:
    """Strip markdown code block tags if present."""
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()
    return raw


def build_context(chunks: List[dict]) -> str:
    """Format a list of document chunks into a single readable context block."""
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        text = chunk.get("text", "")
        parts.append(f"[Excerpt {i} from '{source}']:\n{text}")
    return "\n\n---\n\n".join(parts)


def grade_chunks(question: str, chunks: List[dict]) -> Tuple[List[dict], bool]:
    """
    [IsRel Evaluator] Grade each retrieved chunk for relevance to the question.
    Returns (filtered_chunks, has_relevant).
    """
    if not chunks:
        return [], False

    filtered_chunks = []
    system_msg = SystemMessage(
        content=(
            "You are a document relevance grader. Evaluate if the document snippet "
            "contains information relevant to answering the user's question.\n"
            "Respond ONLY with a JSON object: {\"relevant\": true} or {\"relevant\": false}"
        )
    )

    for chunk in chunks:
        text = chunk.get("text", "")
        human_msg = HumanMessage(
            content=f"User Question: {question}\n\nDocument Snippet:\n{text}"
        )
        try:
            res = _eval_llm.invoke([system_msg, human_msg])
            raw = _clean_json(res.content)
            parsed = json.loads(raw)
            if parsed.get("relevant", False):
                filtered_chunks.append(chunk)
        except Exception as e:
            logger.warning("Error grading chunk relevance: %s. Keeping chunk by default.", e)
            filtered_chunks.append(chunk)

    has_relevant = len(filtered_chunks) > 0
    logger.info(
        "IsRel Evaluator | Total chunks: %d | Relevant chunks: %d",
        len(chunks), len(filtered_chunks),
    )
    return filtered_chunks, has_relevant


def generate_answer(question: str, chunks: List[dict], strict: bool = False) -> str:
    """Generate an answer using provided chunks."""
    context = build_context(chunks)
    prompt = STRICT_SYSTEM_PROMPT if strict else SYSTEM_PROMPT

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Context from documents:\n\n{context}\n\nQuestion: {question}"),
    ]
    res = _llm.invoke(messages)
    return res.content.strip()


def grade_groundedness(question: str, context: str, answer: str) -> bool:
    """
    [IsSup Evaluator] Verify if all claims in the generated answer are grounded in context.
    Returns True if grounded, False if hallucinated.
    """
    system_msg = SystemMessage(
        content=(
            "You are a hallucination grader. Evaluate whether the AI answer is strictly "
            "supported by the provided document context.\n"
            "Respond ONLY with a JSON object: {\"grounded\": true} or {\"grounded\": false}"
        )
    )
    human_msg = HumanMessage(
        content=f"Document Context:\n{context}\n\nQuestion: {question}\n\nAI Answer:\n{answer}"
    )

    try:
        res = _eval_llm.invoke([system_msg, human_msg])
        raw = _clean_json(res.content)
        parsed = json.loads(raw)
        is_grounded = parsed.get("grounded", True)
    except Exception as e:
        logger.warning("Error grading groundedness: %s. Defaulting to True.", e)
        is_grounded = True

    logger.info("IsSup Evaluator | Grounded: %s", is_grounded)
    return is_grounded


def grade_utility(question: str, answer: str) -> bool:
    """
    [IsUse Evaluator] Evaluate if the answer completely and directly resolves the question.
    Returns True if useful/complete, False if incomplete.
    """
    system_msg = SystemMessage(
        content=(
            "You are an answer utility evaluator. Determine if the AI answer completely and "
            "directly answers the user's question.\n"
            "Respond ONLY with a JSON object: {\"useful\": true} or {\"useful\": false}"
        )
    )
    human_msg = HumanMessage(
        content=f"Question: {question}\n\nAI Answer:\n{answer}"
    )

    try:
        res = _eval_llm.invoke([system_msg, human_msg])
        raw = _clean_json(res.content)
        parsed = json.loads(raw)
        is_useful = parsed.get("useful", True)
    except Exception as e:
        logger.warning("Error grading utility: %s. Defaulting to True.", e)
        is_useful = True

    logger.info("IsUse Evaluator | Useful: %s", is_useful)
    return is_useful


def run(session_id: str, question: str) -> Dict[str, Any]:
    """Retrieve relevant chunks and run simple RAG (legacy endpoint fallback)."""
    logger.info("RAG Agent | session=%s | question: %s", session_id, question[:80])

    chunks = vs.similarity_search(session_id, question, k=config.TOP_K_RESULTS)
    if not chunks:
        return {
            "answer": (
                "I couldn't find relevant information in your uploaded documents for this question."
            ),
            "source": "rag",
            "citations": [],
        }

    filtered_chunks, has_relevant = grade_chunks(question, chunks)
    target_chunks = filtered_chunks if has_relevant else chunks
    answer = generate_answer(question, target_chunks)
    sources = list({c.get("source", "Unknown") for c in target_chunks})

    return {
        "answer": answer,
        "source": "rag",
        "citations": sources,
    }

