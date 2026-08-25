"""
CRAG Edges — Conditional routing and branching logic for Corrective RAG.
"""
from __future__ import annotations

import logging
from typing import Literal

from crag.state import CRAGState

logger = logging.getLogger(__name__)


def decide_route(state: CRAGState) -> Literal["retrieve_node", "direct_llm_node", "direct_web_search_node"]:
    """Routes initial user intent from the Router Node."""
    route = state.get("route", "llm")
    mapping = {
        "rag": "retrieve_node",
        "llm": "direct_llm_node",
        "web_search": "direct_web_search_node",
    }
    return mapping.get(route, "direct_llm_node")


def decide_after_retrieval_eval(
    state: CRAGState
) -> Literal[
    "refine_docs_node",
    "rewrite_query_for_db_node",
    "rewrite_query_for_web_node",
    "rewrite_query_for_hybrid_node",
]:
    """
    CRAG Core Branching:
    - CORRECT: Chunks are relevant -> Refine docs -> Generate.
    - INCORRECT (Retry 0): Rewrite query -> 2nd DB retrieval.
    - INCORRECT (Retry >= 1): Vector DB exhausted -> Fallback to Tavily Web Search.
    - AMBIGUOUS: Partially relevant -> Combine Refined Docs + Web Search.
    """
    evaluation = state.get("evaluation_result", "CORRECT")
    db_retry_count = state.get("db_retry_count", 0)

    if evaluation == "CORRECT":
        return "refine_docs_node"

    if evaluation == "INCORRECT":
        if db_retry_count < 1:
            logger.info("CRAG Eval: Chunks INCORRECT on 1st retrieval. Rewriting query for 2nd DB retrieval...")
            return "rewrite_query_for_db_node"
        logger.info("CRAG Eval: Chunks STILL INCORRECT after 2nd DB retrieval. Falling back to Web Search...")
        return "rewrite_query_for_web_node"

    # AMBIGUOUS path
    logger.info("CRAG Eval: Retrieval is AMBIGUOUS. Triggering Hybrid Web Search Augmentation...")
    return "rewrite_query_for_hybrid_node"


def decide_after_groundedness(
    state: CRAGState
) -> Literal["generate_node", "END"]:
    """
    Independent Groundedness Check:
    - If grounded: terminate to END.
    - If ungrounded (hallucination detected) and retry_count < 1: retry generation with strict prompt.
    - If retry limit reached: terminate to END.
    """
    is_grounded = state.get("is_grounded", True)
    retry_count = state.get("groundedness_retry_count", 0)

    if is_grounded:
        return "END"

    if retry_count < 1:
        logger.warning("Groundedness Judge detected hallucination. Retrying generation with strict prompt...")
        return "generate_node"

    logger.warning("Groundedness retry limit reached. Delivering answer.")
    return "END"
