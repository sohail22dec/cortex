"""
Orchestrator — LangGraph-based supervisor that decides which agent
should handle each user question.

Routing logic:
  1. If session has documents AND question is about them → RAG Agent
  2. If question needs current/recent/live info → Web Search Agent
  3. Otherwise → Direct LLM Agent
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Literal

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from typing_extensions import TypedDict

import config
from rag import vector_store as vs
from agents import rag_agent, llm_agent, web_search_agent

logger = logging.getLogger(__name__)

# ── Shared LLM (fast, for routing decisions) ──────────────────────────────────

_router_llm = ChatGroq(
    model=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0,  # deterministic routing
)

# ── State schema ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    question: str
    session_id: str
    has_documents: bool
    route: str           # "rag" | "llm" | "web_search"
    answer: str
    source: str
    citations: list


# ── Router node ───────────────────────────────────────────────────────────────

ROUTER_SYSTEM_PROMPT = """You are a routing assistant. Your job is to classify a user question into ONE of three categories:

1. "rag" — The question is specifically about content in the user's uploaded documents.
   Use this when the question references documents, files, or when it's clear the user wants information from their uploaded materials.

2. "web_search" — The question requires current, recent, or live information that would not be in an LLM's training data.
   Examples: latest news, today's prices, recent events, current statistics, real-time data.
   Do NOT use this for general knowledge questions that don't depend on recency.

3. "llm" — General knowledge, concepts, explanations, or creative tasks that an LLM can answer from training data.
   Examples: "What is machine learning?", "Explain quantum computing", "Write a poem".

Respond with ONLY a valid JSON object in this exact format:
{"route": "rag|llm|web_search", "reason": "brief explanation"}

Consider: has_documents={has_documents}"""


def router_node(state: AgentState) -> AgentState:
    """Classify the question and pick a route."""
    question = state["question"]
    has_documents = state["has_documents"]

    prompt = ROUTER_SYSTEM_PROMPT.replace("{has_documents}", str(has_documents))

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Classify this question: {question}"),
    ]

    response = _router_llm.invoke(messages)
    raw = response.content.strip()

    try:
        # Strip markdown code blocks if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        route = parsed.get("route", "llm")
        reason = parsed.get("reason", "")
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Router returned non-JSON: %s", raw)
        route = "llm"
        reason = "fallback"

    # Safety guard: can't use RAG if no documents
    if route == "rag" and not has_documents:
        route = "llm"
        reason = "No documents uploaded, falling back to LLM"

    logger.info(
        "Router | session=%s | route=%s | reason=%s",
        state["session_id"], route, reason,
    )

    return {**state, "route": route}


# ── Agent nodes ───────────────────────────────────────────────────────────────

def rag_node(state: AgentState) -> AgentState:
    result = rag_agent.run(state["session_id"], state["question"])
    return {**state, **result}


def llm_node(state: AgentState) -> AgentState:
    result = llm_agent.run(state["question"])
    return {**state, **result}


def web_search_node(state: AgentState) -> AgentState:
    result = web_search_agent.run(state["question"])
    return {**state, **result}


# ── Conditional edge ──────────────────────────────────────────────────────────

def decide_route(state: AgentState) -> Literal["rag_node", "llm_node", "web_search_node"]:
    route = state.get("route", "llm")
    mapping = {
        "rag": "rag_node",
        "llm": "llm_node",
        "web_search": "web_search_node",
    }
    return mapping.get(route, "llm_node")


# ── Build the graph ───────────────────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("rag_node", rag_node)
    graph.add_node("llm_node", llm_node)
    graph.add_node("web_search_node", web_search_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", decide_route)
    graph.add_edge("rag_node", END)
    graph.add_edge("llm_node", END)
    graph.add_edge("web_search_node", END)

    return graph.compile()


_graph = _build_graph()


# ── Public API ────────────────────────────────────────────────────────────────

def run(session_id: str, question: str) -> Dict[str, Any]:
    """
    Route the question to the best agent and return the result.
    Returns: { answer, source, citations, route }
    """
    has_docs = vs.has_documents(session_id)

    initial_state: AgentState = {
        "question": question,
        "session_id": session_id,
        "has_documents": has_docs,
        "route": "",
        "answer": "",
        "source": "",
        "citations": [],
    }

    final_state = _graph.invoke(initial_state)

    return {
        "answer": final_state["answer"],
        "source": final_state["source"],
        "citations": final_state.get("citations", []),
        "route": final_state.get("route", "llm"),
    }
