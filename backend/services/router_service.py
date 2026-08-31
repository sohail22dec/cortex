"""
Router Service — Intelligent, document-aware LLM classifier.
Uses Google Gemini Flash-Lite (with Groq fallback) with Pydantic structured outputs for high-speed routing and safety checks.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


class RouteDecision(BaseModel):
    route: Literal["rag", "web_search", "direct_answer", "unsafe"] = Field(
        description=(
            "The selected execution route: "
            "'rag' for questions about uploaded documents or policy manuals; "
            "'web_search' for live/current events, weather, stock prices, or recent news; "
            "'direct_answer' for greetings, identity/persona questions, general concepts, explanations, coding, or math; "
            "'unsafe' for requests asking for malware, cyberattacks, exploit payloads, dangerous weapons, harassment, or self-harm."
        )
    )
    reason: str = Field(
        default="",
        description="Brief explanation of why this route was selected",
    )


def _get_router_llm():
    """Initializes router LLM with Gemini Flash-Lite, falling back to Groq if needed."""
    try:
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_FAST_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.0,
        )
    except Exception as e:
        logger.warning("Could not initialize Gemini router LLM: %s. Falling back to Groq.", e)
        return ChatGroq(
            model=config.GROQ_FAST_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.0,
        )


_router_llm = _get_router_llm()
_structured_router_llm = _router_llm.with_structured_output(RouteDecision)

ROUTER_SYSTEM_PROMPT = """You are Cortex, a helpful, intelligent, document-aware AI assistant.
Your job is to classify the user's intent into exactly one of the following 4 routes:

1. "unsafe" — The request asks for malware/ransomware generation, vulnerability exploit scripts, DDoS payloads, cyberattack instructions, dangerous chemical/explosive weapons, severe hate speech, or self-harm.

2. "rag" — The question is about content in the user's uploaded documents or corporate policies.
   CLASSIFY AS "rag" IF ANY OF THESE ARE TRUE:
   - The question relates to topics, subjects, titles, or domains of the active uploaded files: {document_names}
   - The user uses references like "this document", "the file", "the report", "what does it say", "summarize this", "the policy", "Novacore".
   - has_documents is True and the user asks for specific factual information stored in corporate/uploaded files.

3. "web_search" — The question requires current, recent, or live real-time information.
   Examples: latest news today, current stock market trends, weather forecasts, recent international events, or begins with "Search the web for".

4. "direct_answer" — Greetings ("hi", "who are you"), general concepts, explanations, coding questions, math problems, or creative writing that do NOT require uploaded documents or live web data.
   Examples: "What is machine learning?", "Write a Python function for Fibonacci", "Explain relativity", "Calculate derivative".

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
    """Asynchronously classify user question with per-node timeout."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "direct_answer": "", "reason": "UI button override"}

    messages = _build_messages(question, has_documents, document_names)

    try:
        decision: RouteDecision = await asyncio.wait_for(
            _structured_router_llm.ainvoke(messages),
            timeout=config.TIMEOUT_ROUTER,
        )
        route = decision.route
        reason = decision.reason
    except asyncio.TimeoutError:
        logger.warning("Router LLM timed out after %.1fs. Using safe fallback.", config.TIMEOUT_ROUTER)
        route = "rag" if has_documents else "direct_answer"
        reason = "timeout_fallback"
    except Exception as e:
        logger.warning("Structured routing error: %s. Using safe fallback.", e)
        route = "rag" if has_documents else "direct_answer"
        reason = "fallback"

    if route == "rag" and not has_documents:
        route = "direct_answer"
        reason = "No documents uploaded, defaulting to direct answer"

    direct_answer = ""
    if route == "unsafe":
        direct_answer = "I cannot provide assistance with malware, cyberattacks, exploit payloads, dangerous weapons, harassment, or self-harm."

    return {"route": route, "direct_answer": direct_answer, "reason": reason}


def classify(question: str, has_documents: bool, document_names: list) -> Dict[str, Any]:
    """Synchronous wrapper for classify_async."""
    return asyncio.run(classify_async(question, has_documents, document_names))
