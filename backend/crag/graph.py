"""
CRAG Graph — Compiles the StateGraph workflow for Corrective RAG.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from langgraph.graph import StateGraph, END

from crag.state import CRAGState
from crag import nodes, edges
from rag import vector_store as vs

logger = logging.getLogger(__name__)


def _build_crag_graph() -> Any:
    graph = StateGraph(CRAGState)

    # 1. Add CRAG Core Nodes
    graph.add_node("router", nodes.router_node)
    graph.add_node("retrieve_node", nodes.retrieve_node)
    graph.add_node("retrieval_eval_node", nodes.retrieval_eval_node)
    graph.add_node("web_search_node", nodes.web_search_node)
    graph.add_node("generate_node", nodes.generate_node)
    graph.add_node("groundedness_check_node", nodes.groundedness_check_node)
    graph.add_node("direct_web_search_node", nodes.direct_web_search_node)

    # 2. Set Entry Point
    graph.set_entry_point("router")

    # 3. Router Conditional Edges
    graph.add_conditional_edges(
        "router",
        edges.decide_route,
        {
            "retrieve_node": "retrieve_node",
            "direct_web_search_node": "direct_web_search_node",
            "END": END,
        },
    )


    # 4. CRAG Core Pipeline Edges
    graph.add_edge("retrieve_node", "retrieval_eval_node")
    graph.add_conditional_edges(
        "retrieval_eval_node",
        edges.decide_after_retrieval_eval,
        {
            "generate_node": "generate_node",
            "retrieve_node": "retrieve_node",
            "web_search_node": "web_search_node",
        },
    )

    # Web search fallback & hybrid path -> generate
    graph.add_edge("web_search_node", "generate_node")

    # Generation -> Independent Groundedness Fact-Check Judge
    graph.add_edge("generate_node", "groundedness_check_node")
    graph.add_conditional_edges(
        "groundedness_check_node",
        edges.decide_after_groundedness,
        {
            "generate_node": "generate_node",
            "END": END,
        },
    )

    # Direct Web Search Route Termination
    graph.add_edge("direct_web_search_node", END)

    return graph.compile()



_crag_graph = _build_crag_graph()



# ── Public API ────────────────────────────────────────────────────────────────

async def run_crag_async(session_id: str, question: str) -> Dict[str, Any]:
    """Asynchronously execute the CRAG workflow without blocking the event loop."""
    try:
        has_docs = await asyncio.to_thread(vs.has_documents, session_id)
        doc_names = (
            await asyncio.to_thread(vs.list_document_names, session_id)
            if has_docs
            else []
        )
    except Exception as e:
        logger.warning("Could not fetch vector store details: %s. Assuming no docs.", e)
        has_docs = False
        doc_names = []

    initial_state: CRAGState = {
        "question": question,
        "session_id": session_id,
        "has_documents": has_docs,
        "document_names": doc_names,
        "route": "",
        "chunks": [],
        "refined_chunks": [],
        "evaluation_result": "",
        "evaluation_reason": "",
        "db_retry_count": 0,
        "transformed_query": "",
        "web_results": [],
        "answer": "",
        "source": "",
        "citations": [],
        "is_grounded": True,
        "groundedness_reason": "",
        "groundedness_retry_count": 0,
    }

    run_config = {
        "recursion_limit": 10,
        "tags": ["cortex", "crag-workflow"],
        "metadata": {"session_id": session_id, "question": question[:50]},
    }
    final_state = await _crag_graph.ainvoke(initial_state, config=run_config)

    return {
        "answer": final_state.get("answer", ""),
        "source": final_state.get("source", "llm"),
        "citations": final_state.get("citations", []),
        "route": final_state.get("route", "llm"),
        "evaluation_result": final_state.get("evaluation_result", ""),
        "is_grounded": final_state.get("is_grounded", True),
    }


def run_crag(session_id: str, question: str) -> Dict[str, Any]:
    """Synchronous entrypoint."""
    return asyncio.run(run_crag_async(session_id, question))
