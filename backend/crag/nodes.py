"""
CRAG Nodes — Node execution functions for Corrective RAG.
"""
from __future__ import annotations

import asyncio
import logging
from typing import cast

import config
from crag.state import CRAGState
from rag import vector_store as vs
from services import (
    classify_async,
    evaluate_retrieval_async,
    rewrite_query_for_vector_db_async,
    rewrite_query_for_web_async,
    search_web_async,
    generate_rag_answer_async,
    generate_web_answer_async,
    generate_hybrid_answer_async,
    evaluate_groundedness_async,
    run_llm_async,
)

logger = logging.getLogger(__name__)


# ── 1. Router Node ────────────────────────────────────────────────────────────

async def router_node(state: CRAGState) -> CRAGState:
    question = state["question"]
    has_documents = state["has_documents"]
    doc_names = state.get("document_names", [])

    classification = await classify_async(question, has_documents, doc_names)
    return {**state, "route": classification["route"]}


# ── 2. Vector DB Retrieval Node (1st & 2nd Pass) ──────────────────────────────

async def retrieve_node(state: CRAGState) -> CRAGState:
    session_id = state["session_id"]
    # Use transformed query if available (e.g. on 2nd retrieval), otherwise original question
    query = state.get("transformed_query") or state["question"]

    chunks = await asyncio.to_thread(
        vs.similarity_search, session_id, query, k=config.TOP_K_RESULTS
    )
    return {**state, "chunks": chunks}


# ── 3. Retrieval Evaluator Node ───────────────────────────────────────────────

async def retrieval_eval_node(state: CRAGState) -> CRAGState:
    question = state["question"]
    chunks = state.get("chunks", [])

    eval_result, refined_chunks, reason = await evaluate_retrieval_async(question, chunks)
    return {
        **state,
        "evaluation_result": eval_result,
        "refined_chunks": refined_chunks,
        "evaluation_reason": reason,
    }


# ── 4. Knowledge Refinement Node (For CORRECT Path) ───────────────────────────

async def refine_docs_node(state: CRAGState) -> CRAGState:
    """De-noises the retrieved context by keeping only verified relevant chunks."""
    refined = state.get("refined_chunks", [])
    return {**state, "chunks": refined}


# ── 5. Query Rewriting Nodes ──────────────────────────────────────────────────

async def rewrite_query_for_db_node(state: CRAGState) -> CRAGState:
    """Rewrites query for a 2nd database retrieval attempt."""
    question = state["question"]
    doc_names = state.get("document_names", [])
    retry_count = state.get("db_retry_count", 0)

    rewritten = await rewrite_query_for_vector_db_async(question, doc_names)
    return {
        **state,
        "transformed_query": rewritten,
        "db_retry_count": retry_count + 1,
    }


async def rewrite_query_for_web_node(state: CRAGState) -> CRAGState:
    """Rewrites query for web search fallback."""
    question = state["question"]
    rewritten = await rewrite_query_for_web_async(question)
    return {**state, "transformed_query": rewritten}


async def rewrite_query_for_hybrid_node(state: CRAGState) -> CRAGState:
    """Rewrites query for hybrid web search augmentation."""
    question = state["question"]
    rewritten = await rewrite_query_for_web_async(question)
    return {**state, "transformed_query": rewritten}


# ── 6. Web Search Node ────────────────────────────────────────────────────────

async def web_search_node(state: CRAGState) -> CRAGState:
    query = state.get("transformed_query") or state["question"]
    results = await search_web_async(query, max_results=5)
    return {**state, "web_results": results}


# ── 7. Generation Node ────────────────────────────────────────────────────────

async def generate_node(state: CRAGState) -> CRAGState:
    question = state["question"]
    eval_result = state.get("evaluation_result", "CORRECT")
    chunks = state.get("chunks", [])
    web_results = state.get("web_results", [])
    retry_count = state.get("groundedness_retry_count", 0)
    strict_mode = retry_count > 0

    if eval_result == "CORRECT":
        result = await generate_rag_answer_async(question, chunks, strict=strict_mode)
    elif eval_result == "INCORRECT":
        result = await generate_web_answer_async(question, web_results)
    else:  # AMBIGUOUS
        result = await generate_hybrid_answer_async(question, chunks, web_results)

    return {
        **state,
        "answer": result["answer"],
        "source": result["source"],
        "citations": result["citations"],
        "groundedness_retry_count": retry_count + 1 if strict_mode else retry_count,
    }


# ── 8. Groundedness Judge Node (Independent Critic) ───────────────────────────

async def groundedness_check_node(state: CRAGState) -> CRAGState:
    """Evaluates whether the generated answer is strictly grounded in the context."""
    source = state.get("source", "rag")

    # If pure web search, skip doc groundedness check
    if source == "web_search":
        return {**state, "is_grounded": True, "groundedness_reason": "Web search response."}

    question = state["question"]
    answer = state.get("answer", "")
    chunks = state.get("chunks", [])

    context = "\n\n".join(c.get("text", "") for c in chunks)
    is_grounded, reason = await evaluate_groundedness_async(question, context, answer)

    return {
        **state,
        "is_grounded": is_grounded,
        "groundedness_reason": reason,
    }


# ── 9. Direct Routes (LLM & Direct Web Search) ────────────────────────────────

async def direct_llm_node(state: CRAGState) -> CRAGState:
    result = await run_llm_async(state["question"])
    return cast(
        CRAGState,
        {
            **state,
            "answer": result["answer"],
            "source": result["source"],
            "citations": result["citations"],
            "is_grounded": True,
        },
    )


async def direct_web_search_node(state: CRAGState) -> CRAGState:
    query = await rewrite_query_for_web_async(state["question"])
    results = await search_web_async(query, max_results=5)
    gen_result = await generate_web_answer_async(state["question"], results)

    return cast(
        CRAGState,
        {
            **state,
            "transformed_query": query,
            "web_results": results,
            "answer": gen_result["answer"],
            "source": gen_result["source"],
            "citations": gen_result["citations"],
            "is_grounded": True,
        },
    )
