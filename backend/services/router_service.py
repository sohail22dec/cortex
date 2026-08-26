"""
Router Service — Intelligent, document-aware LLM classifier and direct general-knowledge responder.
Uses openai/gpt-oss-20b with Pydantic structured outputs for high-speed routing and zero-latency general answering.
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
    route: Literal["rag", "web_search", "direct_answer"] = Field(
        description=(
            "The selected execution route: "
            "'rag' for questions about uploaded documents; "
            "'web_search' for live/current events, stock prices, or recent 2026 data; "
            "'direct_answer' for greetings, identity/persona questions, general concepts, explanations, coding, or math."
        )
    )
    direct_answer: str = Field(
        default="",
        description=(
            "If route is 'direct_answer', provide the complete, helpful, well-formatted markdown response directly here. "
            "Otherwise, leave empty."
        ),
    )
    reason: str = Field(
        default="",
        description="Brief explanation of why this route was selected",
    )


# Shared fast LLM client for routing and direct general answering (gpt-oss-20b)
_router_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.3,
)

_structured_router_llm = _router_llm.with_structured_output(RouteDecision)

ROUTER_SYSTEM_PROMPT = """You are Cortex, a helpful, intelligent, document-aware AI assistant.
Your job is to classify the user's intent and, if it's general knowledge, greetings, or explanations, answer it directly:

1. "rag" — The question is about content in the user's uploaded documents.
   CLASSIFY AS "rag" IF ANY OF THESE ARE TRUE:
   - The question relates to topics, subjects, titles, or domains of the active uploaded files: {document_names}
   - The user uses references like "this document", "the file", "the report", "what does it say", "summarize this", "the policy".
   - has_documents is True and the user asks for specific information stored in their files.
   (Leave 'direct_answer' empty).

2. "web_search" — The question requires current, recent, or live real-time information.
   Examples: latest news today, stock prices, sports scores, recent 2026 events, weather, or starts with "Search the web for".
   (Leave 'direct_answer' empty).

3. "direct_answer" — Greetings ("hi", "who are you"), general concepts, explanations, coding, math, or creative writing that do NOT require uploaded documents or live web data.
   Examples: "What is machine learning?", "Write a Python function for Fibonacci", "Explain relativity".
   (Write the complete, helpful markdown answer directly in 'direct_answer').

Active state: has_documents={has_documents}, document_names={document_names}"""


def _build_messages(question: str, has_documents: bool, document_names: list) -> list:
    prompt = (
        ROUTER_SYSTEM_PROMPT
        .replace("{has_documents}", str(has_documents))
        .replace("{document_names}", json.dumps(document_names))
    )
    return [
        SystemMessage(content=prompt),
        HumanMessage(content=f"User Query: {question}"),
    ]


async def classify_async(question: str, has_documents: bool, document_names: list) -> Dict[str, Any]:
    """Asynchronously classify user question and provide direct answers for general queries."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "direct_answer": "", "reason": "UI button override"}

    messages = _build_messages(question, has_documents, document_names)

    try:
        decision: RouteDecision = await _structured_router_llm.ainvoke(messages)
        route = decision.route
        direct_answer = decision.direct_answer.strip()
        reason = decision.reason
    except Exception as e:
        logger.warning("Structured routing error: %s. Using safe fallback.", e)
        route = "rag" if has_documents else "direct_answer"
        direct_answer = ""
        reason = "fallback"

    if route == "rag" and not has_documents:
        route = "direct_answer"
        reason = "No documents uploaded, defaulting to direct answer"

    return {"route": route, "direct_answer": direct_answer, "reason": reason}


def classify(question: str, has_documents: bool, document_names: list) -> Dict[str, Any]:
    """Synchronous wrapper for classify_async."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "direct_answer": "", "reason": "UI button override"}

    messages = _build_messages(question, has_documents, document_names)

    try:
        decision: RouteDecision = _structured_router_llm.invoke(messages)
        route = decision.route
        direct_answer = decision.direct_answer.strip()
        reason = decision.reason
    except Exception as e:
        logger.warning("Structured routing error: %s. Using safe fallback.", e)
        route = "rag" if has_documents else "direct_answer"
        direct_answer = ""
        reason = "fallback"

    if route == "rag" and not has_documents:
        route = "direct_answer"
        reason = "No documents uploaded, defaulting to direct answer"

    return {"route": route, "direct_answer": direct_answer, "reason": reason}
