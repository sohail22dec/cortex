"""
Evaluator Service — Corrective RAG (CRAG) Retrieval Evaluator.
Evaluates the quality of retrieved document chunks into CORRECT, INCORRECT, or AMBIGUOUS.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Literal, Tuple

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
    reason: str = Field(
        default="",
        description="Brief explanation of the retrieval evaluation decision.",
    )


# Fast LLM for evaluation
_eval_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
)

_structured_evaluator_llm = _eval_llm.with_structured_output(RetrievalEvaluation)


def _build_evaluation_messages(question: str, chunks: List[dict]) -> list:
    chunks_text = "\n\n".join(
        f"--- Chunk {i} (Source: {chunk.get('source', 'Unknown')}) ---\n{chunk.get('text', '')}"
        for i, chunk in enumerate(chunks, 1)
    )
    return [
        SystemMessage(
            content=(
                "You are an expert Retrieval Evaluator for a Corrective RAG (CRAG) pipeline.\n"
                "Carefully evaluate whether the provided document chunks contain relevant, sufficient facts "
                "to answer the user's question.\n\n"
                "Classification rules:\n"
                "- 'CORRECT': The document chunks contain clear, direct facts to answer the question completely.\n"
                "- 'INCORRECT': The document chunks are off-topic or lack any meaningful information to answer the question.\n"
                "- 'AMBIGUOUS': The document chunks contain partial information or hints, but are incomplete.\n\n"
                "Return the 1-based indices of any relevant chunks in 'relevant_chunk_indices'."
            )
        ),
        HumanMessage(
            content=f"User Question: {question}\n\nCandidate Document Chunks:\n{chunks_text}"
        ),
    ]


async def evaluate_retrieval_async(
    question: str,
    chunks: List[dict]
) -> Tuple[Literal["CORRECT", "INCORRECT", "AMBIGUOUS"], List[dict], str]:
    """
    Asynchronously evaluates retrieved chunks and refines them by removing noise.
    Returns (evaluation_result, refined_chunks, reason).
    """
    if not chunks:
        return "INCORRECT", [], "No chunks retrieved from vector store."

    messages = _build_evaluation_messages(question, chunks)

    try:
        result: RetrievalEvaluation = await _structured_evaluator_llm.ainvoke(messages)
        indices = set(result.relevant_chunk_indices)
        refined_chunks = [
            chunk for i, chunk in enumerate(chunks, 1) if i in indices
        ]
        evaluation = result.evaluation
        reason = result.reason
    except Exception as e:
        logger.warning("CRAG retrieval evaluation error: %s. Defaulting to CORRECT with all chunks.", e)
        evaluation = "CORRECT"
        refined_chunks = list(chunks)
        reason = "fallback"

    # Sanity check: if classified CORRECT but no chunks selected, fall back to AMBIGUOUS or all chunks
    if evaluation == "CORRECT" and not refined_chunks:
        refined_chunks = list(chunks)

    return evaluation, refined_chunks, reason
