from __future__ import annotations

import logging
from typing import cast

import config
from graph.state import AgentState
from rag import vector_store as vs
from agents import router_agent, rag_agent, llm_agent, web_search_agent

logger = logging.getLogger(__name__)


# ── Intelligent Router Node ───────────────────────────────────────────────────

def router_node(state: AgentState) -> AgentState:
    question = state["question"]
    has_documents = state["has_documents"]
    doc_names = state.get("document_names", [])

    classification = router_agent.classify(question, has_documents, doc_names)
    return {**state, "route": classification["route"]}


# ── RAG Pipeline Nodes (Self-RAG / CRAG) ──────────────────────────────────────

def retrieve_node(state: AgentState) -> AgentState:
    session_id = state["session_id"]
    question = state["question"]

    chunks = vs.similarity_search(session_id, question, k=config.TOP_K_RESULTS)
    return {**state, "chunks": chunks}


def grade_documents_node(state: AgentState) -> AgentState:
    question = state["question"]
    chunks = state.get("chunks", [])

    filtered_chunks, has_relevant = rag_agent.grade_chunks(question, chunks)
    return {
        **state,
        "filtered_chunks": filtered_chunks,
        "documents_relevant": has_relevant,
    }


def suggest_web_search_node(state: AgentState) -> AgentState:
    answer = (
        "I couldn't find relevant information in your uploaded documents for this question.\n\n"
        "Would you like me to search the web for you?"
    )
    return {
        **state,
        "answer": answer,
        "source": "rag",
        "citations": [],
        "suggest_web_search": True,
    }


def generate_node(state: AgentState) -> AgentState:
    question = state["question"]
    filtered_chunks = state.get("filtered_chunks", [])
    retry_count = state.get("retry_count", 0)

    strict_mode = retry_count > 0

    answer = rag_agent.generate_answer(question, filtered_chunks, strict=strict_mode)
    sources = list({c.get("source", "Unknown") for c in filtered_chunks})

    return {
        **state,
        "answer": answer,
        "source": "rag",
        "citations": sources,
        "retry_count": retry_count + 1,
    }


def grade_groundedness_node(state: AgentState) -> AgentState:
    """[IsSup Node] Check if answer contains hallucinations."""
    question = state["question"]
    filtered_chunks = state.get("filtered_chunks", [])
    context = rag_agent.build_context(filtered_chunks)
    answer = state.get("answer", "")

    is_grounded = rag_agent.grade_groundedness(question, context, answer)
    return {**state, "is_grounded": is_grounded}


def grade_utility_node(state: AgentState) -> AgentState:
    """[IsUse Node] Evaluate if the answer completely resolves the user query."""
    question = state["question"]
    answer = state.get("answer", "")

    is_useful = rag_agent.grade_utility(question, answer)
    return {**state, "is_useful": is_useful}


def partial_answer_node(state: AgentState) -> AgentState:
    current_answer = state.get("answer", "")
    note = (
        "\n\n---\n*Note: The uploaded documents only partially answer your question. "
        "Would you like me to search the web for complete details?*"
    )
    return {
        **state,
        "answer": current_answer + note,
        "suggest_web_search": True,
    }


# ── Direct LLM & Web Search Nodes ─────────────────────────────────────────────

def llm_node(state: AgentState) -> AgentState:
    result = llm_agent.run(state["question"])
    return cast(AgentState, {**state, **result, "suggest_web_search": False})


def web_search_node(state: AgentState) -> AgentState:
    result = web_search_agent.run(state["question"])
    return cast(AgentState, {**state, **result, "suggest_web_search": False})
