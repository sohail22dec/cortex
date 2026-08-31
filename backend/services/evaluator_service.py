"""
Evaluator Service — Corrective RAG (CRAG) Retrieval Evaluator.
Evaluates the quality of retrieved document chunks into CORRECT, INCORRECT, or AMBIGUOUS.
Also bundles intelligent query rewriting into the same single pass to eliminate redundant LLM calls on retries/fallbacks.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Tuple

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


class RetrievalEvaluation(BaseModel):
    evaluation: Literal["CORRECT", "INCORRECT", "AMBIGUOUS"] = Field(
        description=(
            "Retrieval classification: "
            "'CORRECT' if chunks contain sufficient and directly relevant facts to answer the question; "
            "'INCORRECT' if chunks are irrelevant or contain no useful facts; "
            "'AMBIGUOUS' if chunks are only partially relevant or miss important parts of the question."
        )
    )
    relevant_chunk_indices: List[int] = Field(
        default_factory=list,
        description="1-based indices of chunks that contain useful relevant facts. Return [] if none are relevant.",
    )
    rewritten_query_for_db: str = Field(
        default="",
        description=(
            "If INCORRECT, provide a clean, keyword-dense query optimized for a 2nd vector DB retrieval attempt. "
            "Remove conversational filler, expand pronouns, and focus on core entity/topic terms."
        ),
    )
    rewritten_query_for_web: str = Field(
        default="",
        description=(
            "If INCORRECT (after retry) or AMBIGUOUS, provide a clean search-engine keyword query for Tavily web search."
        ),
    )
    reason: str = Field(
        default="",
        description="Brief explanation of the retrieval evaluation decision.",
    )


def _get_evaluator_llm():
    """Initializes evaluator LLM with Gemini Flash-Lite, falling back to Groq if needed."""
    try:
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_FAST_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.0,
        )
    except Exception as e:
        logger.warning("Could not initialize Gemini evaluator LLM: %s. Falling back to Groq.", e)
        return ChatGroq(
            model=config.GROQ_FAST_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.0,
        )


_eval_llm = _get_evaluator_llm()
_structured_evaluator_llm = _eval_llm.with_structured_output(RetrievalEvaluation)


def _build_evaluation_messages(question: str, chunks: List[dict], document_names: List[str] = None) -> list:
    chunks_text = "\n\n".join(
        f"--- Chunk {i} (Source: {chunk.get('source', 'Unknown')}) ---\n{chunk.get('text', '')}"
        for i, chunk in enumerate(chunks, 1)
    )
    doc_info = f"Uploaded files in session: {document_names}\n" if document_names else ""
    return [
        SystemMessage(
            content=(
                "You are an expert Retrieval Evaluator & Query Optimizer for a Corrective RAG (CRAG) pipeline.\n"
                f"{doc_info}"
                "Carefully evaluate whether the provided document chunks contain relevant, sufficient facts "
                "to answer the user's question.\n\n"
                "Classification rules:\n"
                "- 'CORRECT': The document chunks contain clear, direct facts to answer the question completely.\n"
                "- 'INCORRECT': The document chunks are off-topic or lack any meaningful information to answer the question.\n"
                "- 'AMBIGUOUS': The document chunks contain partial information or hints, but are incomplete.\n\n"
                "Tasks:\n"
                "1. Return relevant chunk indices in 'relevant_chunk_indices'.\n"
                "2. If INCORRECT: provide 'rewritten_query_for_db' (optimized for vector search) and 'rewritten_query_for_web'.\n"
                "3. If AMBIGUOUS: provide 'rewritten_query_for_web' for supplementary search."
            )
        ),
        HumanMessage(
            content=f"User Question: {question}\n\nCandidate Document Chunks:\n{chunks_text}"
        ),
    ]


async def evaluate_retrieval_async(
    question: str,
    chunks: List[dict],
    document_names: List[str] = None,
) -> Tuple[Literal["CORRECT", "INCORRECT", "AMBIGUOUS"], List[dict], str, str, str]:
    """
    Asynchronously evaluates retrieved chunks and bundles query rewrites into a SINGLE call.
    Returns (evaluation_result, refined_chunks, reason, db_query, web_query).
    """
    if not chunks:
        # If no chunks at all, prepare clean fallback query
        fallback_query = question.strip()
        return "INCORRECT", [], "No chunks retrieved from vector store.", fallback_query, fallback_query

    messages = _build_evaluation_messages(question, chunks, document_names)

    try:
        result: RetrievalEvaluation = await _structured_evaluator_llm.ainvoke(messages)
        indices = set(result.relevant_chunk_indices)
        refined_chunks = [
            chunk for i, chunk in enumerate(chunks, 1) if i in indices
        ]
        evaluation = result.evaluation
        reason = result.reason
        db_query = result.rewritten_query_for_db.strip() or question
        web_query = result.rewritten_query_for_web.strip() or question
    except Exception as e:
        logger.warning("CRAG retrieval evaluation error: %s. Defaulting to CORRECT with all chunks.", e)
        evaluation = "CORRECT"
        refined_chunks = list(chunks)
        reason = "fallback"
        db_query = question
        web_query = question

    # Sanity check: if classified CORRECT but no chunks selected, fall back to AMBIGUOUS or all chunks
    if evaluation == "CORRECT" and not refined_chunks:
        refined_chunks = list(chunks)

    return evaluation, refined_chunks, reason, db_query, web_query

