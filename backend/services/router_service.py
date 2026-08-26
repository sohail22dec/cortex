"""
Router Service — Intelligent, document-aware LLM classifier and direct general-knowledge responder.
Uses openai/gpt-oss-20b with Pydantic structured outputs for high-speed routing, safety checks, and zero-latency general answering.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


class RouteDecision(BaseModel):
    route: Literal["rag", "web_search", "direct_answer", "unsafe"] = Field(
        description=(
            "The selected execution route: "
            "'rag' for questions about uploaded documents; "
            "'web_search' for live/current events, stock prices, or recent 2026 data; "
            "'direct_answer' for greetings, identity/persona questions, general concepts, explanations, coding, or math; "
            "'unsafe' for requests asking for malware, cyberattacks, exploit payloads, dangerous weapons, harassment, or self-harm."
        )
    )
    direct_answer: str = Field(
        default="",
        description=(
            "If route is 'direct_answer' or 'unsafe', provide the complete, helpful (or polite refusal) markdown response directly here. "
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
Your job is to classify the user's intent and, if it's general knowledge, greetings, safety refusals, or explanations, answer it directly:

1. "unsafe" — The request asks for malware/ransomware generation, vulnerability exploit scripts, DDoS payloads, cyberattack instructions, dangerous chemical/explosive weapons, severe hate speech, or self-harm.
   (Write a concise, polite refusal directly in 'direct_answer', e.g., "I cannot provide assistance with malware or cyberattack development.")

2. "rag" — The question is about content in the user's uploaded documents.
   CLASSIFY AS "rag" IF ANY OF THESE ARE TRUE:
   - The question relates to topics, subjects, titles, or domains of the active uploaded files: {document_names}
   - The user uses references like "this document", "the file", "the report", "what does it say", "summarize this", "the policy".
   - has_documents is True and the user asks for specific information stored in their files.
   (Leave 'direct_answer' empty).

3. "web_search" — The question requires current, recent, or live real-time information.
   Examples: latest news today, stock prices, sports scores, recent 2026 events, weather, or starts with "Search the web for".
   (Leave 'direct_answer' empty).

4. "direct_answer" — Greetings ("hi", "who are you"), general concepts, explanations, coding, math, or creative writing that do NOT require uploaded documents or live web data.
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
    """Asynchronously classify user question and provide direct answers with per-node timeout."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "direct_answer": "", "reason": "UI button override"}

    messages = _build_messages(question, has_documents, document_names)

    try:
        decision: RouteDecision = await asyncio.wait_for(
            _structured_router_llm.ainvoke(messages),
            timeout=config.TIMEOUT_ROUTER,
        )
        route = decision.route
        direct_answer = decision.direct_answer.strip()
        reason = decision.reason
    except asyncio.TimeoutError:
        logger.warning("Router LLM timed out after %.1fs. Using safe fallback.", config.TIMEOUT_ROUTER)
        route = "rag" if has_documents else "direct_answer"
        direct_answer = ""
        reason = "timeout_fallback"
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
    return asyncio.run(classify_async(question, has_documents, document_names))
