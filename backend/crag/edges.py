"""
CRAG Edges — Conditional routing and branching logic for Corrective RAG.
"""
from __future__ import annotations

import logging
from typing import Literal

from crag.state import CRAGState

logger = logging.getLogger(__name__)


def decide_route(state: CRAGState) -> Literal["retrieve_node", "direct_web_search_node", "END"]:
    """Routes initial user intent from the Router Node."""
    route = state.get("route", "direct_answer")
    if route == "rag":
        return "retrieve_node"
    if route == "web_search":
        return "direct_web_search_node"
    # "direct_answer" terminates immediately since answer was generated directly by Router
    return "END"



def decide_after_retrieval_eval(
    state: CRAGState
) -> Literal[
    "generate_node",
    "retrieve_node",
    "web_search_node",
]:
    """
    CRAG Direct Branching:
    - CORRECT: Chunks are relevant -> Proceed directly to generate_node.
    - INCORRECT (1st attempt): Loops back to retrieve_node with bundled db query.
    - INCORRECT (2nd attempt): Vector DB exhausted -> Proceeds directly to web_search_node.
    - AMBIGUOUS: Proceeds directly to web_search_node for hybrid augmentation.
    """
    evaluation = state.get("evaluation_result", "CORRECT")
    db_retry_count = state.get("db_retry_count", 0)

    if evaluation == "CORRECT":
        return "generate_node"

    if evaluation == "INCORRECT":
        # db_retry_count is 1 on the 1st failure (after increment), >1 on 2nd failure
        if db_retry_count <= 1:
            logger.info("CRAG Eval: Chunks INCORRECT on 1st retrieval. Looping directly back to retrieve_node for 2nd DB attempt...")
            return "retrieve_node"
        logger.info("CRAG Eval: Chunks STILL INCORRECT after 2nd DB retrieval. Falling back directly to web_search_node...")
        return "web_search_node"

    # AMBIGUOUS path
    logger.info("CRAG Eval: Retrieval is AMBIGUOUS. Falling back directly to web_search_node for hybrid augmentation...")
    return "web_search_node"



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
