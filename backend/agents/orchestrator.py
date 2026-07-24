from __future__ import annotations

import json
import logging
from typing import Any, Dict, Literal, cast

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
    temperature=0.0,
)

# ── State schema ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    question: str
    session_id: str
    has_documents: bool
    route: str                      # "rag" | "llm" | "web_search"
    chunks: list                    # Raw retrieved chunks
    filtered_chunks: list           # Relevant chunks after IsRel
    documents_relevant: bool        # IsRel outcome
    answer: str
    source: str                     # "rag" | "llm" | "web_search"
    citations: list
    is_grounded: bool               # IsSup outcome
    is_useful: bool                 # IsUse outcome
    suggest_web_search: bool        # Flag sent to frontend
    retry_count: int                # Loop safety guard


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

    if route == "rag" and not has_documents:
        route = "llm"
        reason = "No documents uploaded, falling back to LLM"

    logger.info(
        "Router | session=%s | route=%s | reason=%s",
        state["session_id"], route, reason,
    )

    return {**state, "route": route}


# ── RAG Pipeline Nodes (Self-RAG / CRAG) ──────────────────────────────────────

def retrieve_node(state: AgentState) -> AgentState:
    """Fetch vector chunks from Supabase."""
    session_id = state["session_id"]
    question = state["question"]
    logger.info("Retrieve Node | session=%s | question=%s", session_id, question[:80])

    chunks = vs.similarity_search(session_id, question, k=config.TOP_K_RESULTS)
    return {**state, "chunks": chunks}


def grade_documents_node(state: AgentState) -> AgentState:
    """[IsRel Node] Filter out irrelevant chunks using rag_agent evaluator."""
    question = state["question"]
    chunks = state.get("chunks", [])

    filtered_chunks, has_relevant = rag_agent.grade_chunks(question, chunks)
    return {
        **state,
        "filtered_chunks": filtered_chunks,
        "documents_relevant": has_relevant,
    }


def decide_after_doc_grading(state: AgentState) -> Literal["generate_node", "suggest_web_search_node"]:
    """Branch based on document relevance (IsRel)."""
    if state.get("documents_relevant", False):
        return "generate_node"
    return "suggest_web_search_node"


def suggest_web_search_node(state: AgentState) -> AgentState:
    """Triggered when 0 document chunks are relevant. Offers web search prompt."""
    logger.info("Suggest Web Search Node | No relevant chunks found.")
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
    """Synthesize answer from filtered relevant chunks."""
    question = state["question"]
    filtered_chunks = state.get("filtered_chunks", [])
    retry_count = state.get("retry_count", 0)

    strict_mode = retry_count > 0
    logger.info("Generate Node | strict_mode=%s | retry_count=%d", strict_mode, retry_count)

    answer = rag_agent.generate_answer(question, filtered_chunks, strict=strict_mode)
    sources = list({c.get("source", "Unknown") for c in filtered_chunks})

    return {
        **state,
        "answer": answer,
        "source": "rag",
        "citations": sources,
    }


def grade_groundedness_node(state: AgentState) -> AgentState:
    """[IsSup Node] Check if answer contains hallucinations."""
    question = state["question"]
    filtered_chunks = state.get("filtered_chunks", [])
    context = rag_agent.build_context(filtered_chunks)
    answer = state.get("answer", "")

    is_grounded = rag_agent.grade_groundedness(question, context, answer)
    return {**state, "is_grounded": is_grounded}


def decide_after_groundedness(state: AgentState) -> Literal["grade_utility_node", "generate_node"]:
    """Branch based on groundedness evaluation."""
    if state.get("is_grounded", True):
        return "grade_utility_node"

    retry_count = state.get("retry_count", 0)
    if retry_count < 1:
        logger.warning("Groundedness Check Failed. Retrying generation with strict prompt...")
        return "generate_node"

    logger.warning("Groundedness retry limit reached. Proceeding to utility check.")
    return "grade_utility_node"


def grade_utility_node(state: AgentState) -> AgentState:
    """[IsUse Node] Evaluate if the answer completely resolves the user query."""
    question = state["question"]
    answer = state.get("answer", "")

    is_useful = rag_agent.grade_utility(question, answer)
    return {**state, "is_useful": is_useful}


def decide_after_utility(state: AgentState) -> Literal["partial_answer_node", "END"]:
    """Branch based on utility evaluation."""
    if state.get("is_useful", True):
        return "END"
    return "partial_answer_node"


def partial_answer_node(state: AgentState) -> AgentState:
    """Triggered when answer is incomplete. Appends note + suggests web search."""
    logger.info("Partial Answer Node | Answer judged incomplete.")
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


# ── Other Agent Nodes ─────────────────────────────────────────────────────────

def llm_node(state: AgentState) -> AgentState:
    """Direct LLM response for general knowledge questions."""
    result = llm_agent.run(state["question"])
    return cast(AgentState, {**state, **result, "suggest_web_search": False})


def web_search_node(state: AgentState) -> AgentState:
    """Web search response using Tavily."""
    result = web_search_agent.run(state["question"])
    return cast(AgentState, {**state, **result, "suggest_web_search": False})


# ── Entry Router & Fallbacks ───────────────────────────────────────────────────

def decide_entry_point(state: AgentState) -> Literal["retrieve_node", "router", "web_search_node"]:
    """
    Vector-First Adaptive Routing:
    - If user explicitly clicked "Search the web for ...", route directly to web_search_node.
    - If session has documents uploaded, check Vector Retrieval first to prevent false negatives.
    - Otherwise, use router node to classify into LLM or Web Search.
    """
    question = state["question"]
    has_documents = state["has_documents"]

    if question.lower().startswith("search the web for "):
        return "web_search_node"

    if has_documents:
        return "retrieve_node"

    return "router"


def fallback_router_node(state: AgentState) -> AgentState:
    """
    Triggered when 0 document chunks are relevant to the question.
    Classifies whether to fall back to Direct LLM or Web Search.
    """
    question = state["question"]
    prompt = ROUTER_SYSTEM_PROMPT.replace("{has_documents}", "False")

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Classify this question for fallback route: {question}"),
    ]

    try:
        response = _router_llm.invoke(messages)
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        route = parsed.get("route", "llm")
    except Exception:
        route = "llm"

    logger.info("Fallback Router | question=%s | chosen_route=%s", question[:50], route)
    return {**state, "route": route}


def decide_after_doc_grading(state: AgentState) -> Literal["generate_node", "fallback_router_node"]:
    """Branch based on document relevance (IsRel)."""
    if state.get("documents_relevant", False):
        return "generate_node"
    return "fallback_router_node"


def decide_after_fallback(state: AgentState) -> Literal["llm_node", "web_search_node"]:
    """Branch based on fallback router choice."""
    route = state.get("route", "llm")
    if route == "web_search":
        return "web_search_node"
    return "llm_node"


def decide_route(state: AgentState) -> Literal["retrieve_node", "llm_node", "web_search_node"]:
    route = state.get("route", "llm")
    mapping = {
        "rag": "retrieve_node",
        "llm": "llm_node",
        "web_search": "web_search_node",
    }
    return mapping.get(route, "llm_node")


# ── Build the Self-RAG Graph ──────────────────────────────────────────────────

def _build_graph() -> Any:
    graph = StateGraph(AgentState)

    # Add Nodes
    graph.add_node("router", router_node)
    graph.add_node("fallback_router_node", fallback_router_node)
    graph.add_node("retrieve_node", retrieve_node)
    graph.add_node("grade_documents_node", grade_documents_node)
    graph.add_node("suggest_web_search_node", suggest_web_search_node)
    graph.add_node("generate_node", generate_node)
    graph.add_node("grade_groundedness_node", grade_groundedness_node)
    graph.add_node("grade_utility_node", grade_utility_node)
    graph.add_node("partial_answer_node", partial_answer_node)
    graph.add_node("llm_node", llm_node)
    graph.add_node("web_search_node", web_search_node)

    # Vector-First Entry Point
    graph.set_conditional_entry_point(decide_entry_point)

    # Edges from Router
    graph.add_conditional_edges("router", decide_route)
    graph.add_conditional_edges("fallback_router_node", decide_after_fallback)

    # RAG Self-RAG Flow Edges
    graph.add_edge("retrieve_node", "grade_documents_node")
    graph.add_conditional_edges(
        "grade_documents_node",
        decide_after_doc_grading,
        {
            "generate_node": "generate_node",
            "fallback_router_node": "fallback_router_node",
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

    # Terminal Edges
    graph.add_edge("suggest_web_search_node", END)
    graph.add_edge("partial_answer_node", END)
    graph.add_edge("llm_node", END)
    graph.add_edge("web_search_node", END)

    return graph.compile()


_graph = _build_graph()


# ── Public API ────────────────────────────────────────────────────────────────

def run(session_id: str, question: str) -> Dict[str, Any]:
    """
    Route the question through the Adaptive Self-RAG state graph and return the result.
    Returns: { answer, source, citations, route, suggest_web_search }
    """
    try:
        has_docs = vs.has_documents(session_id)
    except Exception as e:
        logger.warning("Could not check vector store for documents: %s. Assuming has_documents=False", e)
        has_docs = False

    initial_state: AgentState = {
        "question": question,
        "session_id": session_id,
        "has_documents": has_docs,
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

    final_state = _graph.invoke(initial_state)

    return {
        "answer": final_state["answer"],
        "source": final_state["source"],
        "citations": final_state.get("citations", []),
        "route": final_state.get("route", "llm"),
        "suggest_web_search": final_state.get("suggest_web_search", False),
    }

