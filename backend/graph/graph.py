from __future__ import annotations

import logging
from typing import Any, Dict, Literal

from langgraph.graph import StateGraph, END

from graph.state import AgentState
from graph import nodes
from rag import vector_store as vs

logger = logging.getLogger(__name__)


# ── Conditional Routing Functions ─────────────────────────────────────────────

def decide_route(state: AgentState) -> Literal["retrieve_node", "llm_node", "web_search_node"]:
    route = state.get("route", "llm")
    mapping = {
        "rag": "retrieve_node",
        "llm": "llm_node",
        "web_search": "web_search_node",
    }
    return mapping.get(route, "llm_node")


def decide_after_doc_grading(state: AgentState) -> Literal["generate_node", "suggest_web_search_node"]:
    if state.get("documents_relevant", False):
        return "generate_node"
    return "suggest_web_search_node"


def decide_after_groundedness(state: AgentState) -> Literal["grade_utility_node", "generate_node"]:
    if state.get("is_grounded", True):
        return "grade_utility_node"

    retry_count = state.get("retry_count", 0)
    if retry_count < 1:
        logger.warning("Groundedness Check Failed. Retrying generation with strict prompt...")
        return "generate_node"

    logger.warning("Groundedness retry limit reached. Proceeding to utility check.")
    return "grade_utility_node"


def decide_after_utility(state: AgentState) -> Literal["partial_answer_node", "END"]:
    if state.get("is_useful", True):
        return "END"
    return "partial_answer_node"


# ── Build & Compile the StateGraph ─────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(AgentState)

    # 1. Add Nodes
    graph.add_node("router", nodes.router_node)
    graph.add_node("retrieve_node", nodes.retrieve_node)
    graph.add_node("grade_documents_node", nodes.grade_documents_node)
    graph.add_node("suggest_web_search_node", nodes.suggest_web_search_node)
    graph.add_node("generate_node", nodes.generate_node)
    graph.add_node("grade_groundedness_node", nodes.grade_groundedness_node)
    graph.add_node("grade_utility_node", nodes.grade_utility_node)
    graph.add_node("partial_answer_node", nodes.partial_answer_node)
    graph.add_node("llm_node", nodes.llm_node)
    graph.add_node("web_search_node", nodes.web_search_node)

    # 2. Set Entry Point
    graph.set_entry_point("router")

    # 3. Add Conditional Routing Edges from Router
    graph.add_conditional_edges("router", decide_route)

    # 4. RAG Self-RAG Flow Edges
    graph.add_edge("retrieve_node", "grade_documents_node")
    graph.add_conditional_edges(
        "grade_documents_node",
        decide_after_doc_grading,
        {
            "generate_node": "generate_node",
            "suggest_web_search_node": "suggest_web_search_node",
        },
    )
    graph.add_edge("generate_node", "grade_groundedness_node")
    graph.add_conditional_edges(
        "grade_groundedness_node",
        decide_after_groundedness,
        {
            "grade_utility_node": "grade_utility_node",
            "generate_node": "generate_node",
        },
    )
    graph.add_conditional_edges(
        "grade_utility_node",
        decide_after_utility,
        {
            "END": END,
            "partial_answer_node": "partial_answer_node",
        },
    )

    # 5. Terminal Edges
    graph.add_edge("suggest_web_search_node", END)
    graph.add_edge("partial_answer_node", END)
    graph.add_edge("llm_node", END)
    graph.add_edge("web_search_node", END)

    return graph.compile()


_graph = _build_graph()


# ── Public API ────────────────────────────────────────────────────────────────

def run(session_id: str, question: str) -> Dict[str, Any]:
    try:
        has_docs = vs.has_documents(session_id)
        doc_names = vs.list_document_names(session_id) if has_docs else []
    except Exception as e:
        logger.warning("Could not fetch vector store details: %s. Assuming no docs.", e)
        has_docs = False
        doc_names = []

    initial_state: AgentState = {
        "question": question,
        "session_id": session_id,
        "has_documents": has_docs,
        "document_names": doc_names,
        "route": "",
        "chunks": [],
        "filtered_chunks": [],
        "documents_relevant": False,
        "answer": "",
        "source": "",
        "citations": [],
        "is_grounded": True,
        "is_useful": True,
        "suggest_web_search": False,
        "retry_count": 0,
    }

    run_config = {
        "tags": ["cortex", "intelligent-router"],
        "metadata": {"session_id": session_id, "question": question[:50]},
    }
    final_state = _graph.invoke(initial_state, config=run_config)

    return {
        "answer": final_state["answer"],
        "source": final_state["source"],
        "citations": final_state.get("citations", []),
        "route": final_state.get("route", "llm"),
        "suggest_web_search": final_state.get("suggest_web_search", False),
    }
