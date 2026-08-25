"""
Router Service — Intelligent, document-aware LLM classifier for user question routing.
Uses Pydantic structured outputs for deterministic, guaranteed schema validation.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Literal

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


class RouteDecision(BaseModel):
    route: Literal["rag", "llm", "web_search"] = Field(
        description="The selected execution route: 'rag' for uploaded docs, 'web_search' for live/current info, 'llm' for general reasoning"
    )
    reason: str = Field(
        default="",
        description="Brief explanation of why this route was selected",
    )


# Shared fast LLM client for routing decision
_router_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
)

_structured_router_llm = _router_llm.with_structured_output(RouteDecision)

ROUTER_SYSTEM_PROMPT = """You are an intelligent routing assistant for Cortex.
Your job is to classify a user question into EXACTLY ONE of three categories:

1. "rag" — The question is about content in the user's uploaded documents.
   CLASSIFY AS "rag" IF ANY OF THESE ARE TRUE:
   - The question relates to the topics, subjects, titles, or domains of the active uploaded files: {document_names}
   - The user uses implicit references like "this document", "the file", "the report", "this company", "what does it say", "summarize this", "tell me about this", "the policy", "the data", "the candidate".
   - has_documents is True and the user asks for information likely stored in their uploaded files.

2. "web_search" — The question requires current, recent, or live information that would NOT be in static documents or LLM training data.
   Examples: latest news today, stock prices, sports scores, recent events, 2026 data, weather, or explicitly starts with "Search the web for".

3. "llm" — General knowledge, concepts, explanations, coding, math, or creative writing that can be answered directly without documents or web search.
   Examples: "What is machine learning?", "Write a Python binary search function", "Explain quantum computing".

Consider: has_documents={has_documents}, document_names={document_names}"""


def _build_messages(question: str, has_documents: bool, document_names: list) -> list:
    prompt = (
        ROUTER_SYSTEM_PROMPT
        .replace("{has_documents}", str(has_documents))
        .replace("{document_names}", json.dumps(document_names))
    )
    return [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Classify this user question: {question}"),
    ]


async def classify_async(question: str, has_documents: bool, document_names: list) -> Dict[str, Any]:
    """Asynchronously classify the user question into rag, web_search, or llm route."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "reason": "UI button override"}

    messages = _build_messages(question, has_documents, document_names)

    try:
        decision: RouteDecision = await _structured_router_llm.ainvoke(messages)
        route = decision.route
        reason = decision.reason
    except Exception as e:
        logger.warning("Structured routing error: %s. Using safe fallback.", e)
        route = "rag" if has_documents else "llm"
        reason = "fallback"

    if route == "rag" and not has_documents:
        route = "llm"
        reason = "No documents uploaded, defaulting to LLM"

    return {"route": route, "reason": reason}


def classify(question: str, has_documents: bool, document_names: list) -> Dict[str, Any]:
    """Synchronous wrapper for classify_async."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "reason": "UI button override"}

    messages = _build_messages(question, has_documents, document_names)

    try:
        decision: RouteDecision = _structured_router_llm.invoke(messages)
        route = decision.route
        reason = decision.reason
    except Exception as e:
        logger.warning("Structured routing error: %s. Using safe fallback.", e)
        route = "rag" if has_documents else "llm"
        reason = "fallback"

    if route == "rag" and not has_documents:
        route = "llm"
        reason = "No documents uploaded, defaulting to LLM"

    return {"route": route, "reason": reason}
