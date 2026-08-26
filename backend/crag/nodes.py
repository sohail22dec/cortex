"""
CRAG Nodes — Node execution functions for Corrective RAG with per-node execution timeouts.
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
    evaluate_groundedness_async,
    evaluate_retrieval_async,
    generate_hybrid_answer_async,
    generate_rag_answer_async,
    generate_web_answer_async,
    rewrite_query_for_web_async,
    search_web_async,
)

logger = logging.getLogger(__name__)


# ── 1. Router Node ────────────────────────────────────────────────────────────

async def router_node(state: CRAGState) -> CRAGState:
    question = state["question"]
    has_documents = state["has_documents"]
    doc_names = state.get("document_names", [])

    classification = await classify_async(question, has_documents, doc_names)
    route = classification["route"]
    direct_answer = classification.get("direct_answer", "")

    is_unsafe = route == "unsafe"
    is_direct = route == "direct_answer"

    return {
        **state,
        "route": route,
        "answer": direct_answer if (is_direct or is_unsafe) else state.get("answer", ""),
        "source": "guardrail" if is_unsafe else ("llm" if is_direct else state.get("source", "")),
        "is_grounded": True if (is_direct or is_unsafe) else state.get("is_grounded", True),
    }


# ── 2. Vector DB Retrieval Node (1st & 2nd Pass) ──────────────────────────────

async def retrieve_node(state: CRAGState) -> CRAGState:
    session_id = state["session_id"]
    query = state.get("transformed_query") or state["question"]

    try:
        chunks = await asyncio.wait_for(
            asyncio.to_thread(
                vs.similarity_search, session_id, query, k=config.TOP_K_RESULTS
            ),
            timeout=config.TIMEOUT_RETRIEVAL,
        )
    except asyncio.TimeoutError:
        logger.warning("Vector DB retrieval timed out after %.1fs. Falling back to empty chunks.", config.TIMEOUT_RETRIEVAL)
        chunks = []
    except Exception as e:
        logger.warning("Vector DB retrieval error: %s. Falling back to empty chunks.", e)
        chunks = []

    return {**state, "chunks": chunks}


# ── 3. Retrieval Evaluator Node (Bundled Eval, Refinement & Query Optimizer) ─

async def retrieval_eval_node(state: CRAGState) -> CRAGState:
    question = state["question"]
    chunks = state.get("chunks", [])
    doc_names = state.get("document_names", [])
    db_retry_count = state.get("db_retry_count", 0)

    # If no chunks were retrieved, immediately flag INCORRECT
    if not chunks:
        return {
            **state,
            "chunks": [],
            "refined_chunks": [],
            "evaluation_result": "INCORRECT",
            "evaluation_reason": "No document chunks retrieved",
            "db_retry_count": db_retry_count + 1,
            "transformed_query": question,
            "web_rewritten_query": question,
        }

    try:
        eval_result, refined_chunks, reason, db_query, web_query = await asyncio.wait_for(
            evaluate_retrieval_async(question, chunks, doc_names),
            timeout=config.TIMEOUT_RETRIEVAL_EVAL,
        )
    except asyncio.TimeoutError:
        logger.warning(
            "Retrieval evaluator timed out after %.1fs. Defaulting to CORRECT to proceed with generation.",
            config.TIMEOUT_RETRIEVAL_EVAL,
        )
        eval_result = "CORRECT"
        refined_chunks = chunks
        reason = "evaluator_timeout_fallback"
        db_query = question
        web_query = question
    except Exception as e:
        logger.warning("Retrieval evaluator error: %s. Proceeding with raw chunks.", e)
        eval_result = "CORRECT"
        refined_chunks = chunks
        reason = "evaluator_error_fallback"
        db_query = question
        web_query = question

    # Branch assignment with strict retry counting
    if eval_result == "CORRECT":
        active_chunks = refined_chunks
        transformed_query = state.get("transformed_query") or question
        next_retry_count = db_retry_count
    elif eval_result == "INCORRECT" and db_retry_count < 1:
        active_chunks = chunks
        transformed_query = db_query
        next_retry_count = db_retry_count + 1
    else:  # INCORRECT (Retry >= 1) or AMBIGUOUS
        active_chunks = refined_chunks if eval_result == "AMBIGUOUS" else []
        transformed_query = web_query
        next_retry_count = db_retry_count + 1

    return {
        **state,
        "chunks": active_chunks,
        "refined_chunks": refined_chunks,
        "evaluation_result": eval_result,
        "evaluation_reason": reason,
        "db_retry_count": next_retry_count,
        "transformed_query": transformed_query,
        "db_rewritten_query": db_query,
        "web_rewritten_query": web_query,
    }


# ── 6. Web Search Node ────────────────────────────────────────────────────────

async def web_search_node(state: CRAGState) -> CRAGState:
    query = state.get("transformed_query") or state["question"]
    try:
        results = await asyncio.wait_for(
            search_web_async(query, max_results=5),
            timeout=config.TIMEOUT_WEB_SEARCH,
        )
    except asyncio.TimeoutError:
        logger.warning("Tavily web search timed out after %.1fs. Continuing with empty web results.", config.TIMEOUT_WEB_SEARCH)
        results = []
    except Exception as e:
        logger.warning("Web search error: %s. Continuing with empty web results.", e)
        results = []

    return {**state, "web_results": results}


# ── 7. Generation Node ────────────────────────────────────────────────────────

async def generate_node(state: CRAGState) -> CRAGState:
    question = state["question"]
    eval_result = state.get("evaluation_result", "CORRECT")
    chunks = state.get("chunks", [])
    web_results = state.get("web_results", [])
    retry_count = state.get("groundedness_retry_count", 0)
    strict_mode = retry_count > 0

    try:
        if eval_result == "CORRECT":
            coro = generate_rag_answer_async(question, chunks, strict=strict_mode)
        elif eval_result == "INCORRECT":
            coro = generate_web_answer_async(question, web_results)
        else:  # AMBIGUOUS
            coro = generate_hybrid_answer_async(question, chunks, web_results)

        result = await asyncio.wait_for(coro, timeout=config.TIMEOUT_GENERATION)
    except asyncio.TimeoutError:
        logger.warning("Generation node timed out after %.1fs.", config.TIMEOUT_GENERATION)
        result = {
            "answer": "I apologize, but answering your request took longer than expected. Please try again or simplify your question.",
            "source": "llm",
            "citations": [],
        }
    except Exception as e:
        logger.exception("Generation error: %s", e)
        result = {
            "answer": "An error occurred while generating the answer. Please try again.",
            "source": "llm",
            "citations": [],
        }

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

    # If pure web search or guardrail, skip doc groundedness check
    if source in ("web_search", "guardrail", "llm"):
        return {**state, "is_grounded": True, "groundedness_reason": "Skipped for non-rag source."}

    question = state["question"]
    answer = state.get("answer", "")
    chunks = state.get("chunks", [])

    context = "\n\n".join(c.get("text", "") for c in chunks)

    try:
        is_grounded, reason = await asyncio.wait_for(
            evaluate_groundedness_async(question, context, answer),
            timeout=config.TIMEOUT_GROUNDEDNESS,
        )
    except asyncio.TimeoutError:
        logger.warning(
            "Groundedness judge timed out after %.1fs. Defaulting to is_grounded=True.",
            config.TIMEOUT_GROUNDEDNESS,
        )
        is_grounded, reason = True, "judge_timeout_fallback"
    except Exception as e:
        logger.warning("Groundedness judge error: %s. Defaulting to is_grounded=True.", e)
        is_grounded, reason = True, "judge_error_fallback"

    return {
        **state,
        "is_grounded": is_grounded,
        "groundedness_reason": reason,
    }


# ── 9. Direct Routes (Direct Web Search) ──────────────────────────────────────

async def direct_web_search_node(state: CRAGState) -> CRAGState:
    try:
        query = await asyncio.wait_for(
            rewrite_query_for_web_async(state["question"]),
            timeout=config.TIMEOUT_ROUTER,
        )
        results = await asyncio.wait_for(
            search_web_async(query, max_results=5),
            timeout=config.TIMEOUT_WEB_SEARCH,
        )
        gen_result = await asyncio.wait_for(
            generate_web_answer_async(state["question"], results),
            timeout=config.TIMEOUT_GENERATION,
        )
    except Exception as e:
        logger.warning("Direct web search error: %s", e)
        query = state["question"]
        results = []
        gen_result = {
            "answer": "Unable to fetch live web search results at this moment. Please try again.",
            "source": "web_search",
            "citations": [],
        }

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
