"""
Router Service — Intelligent, document-aware LLM classifier.
Uses Google Gemini Flash-Lite (with Groq fallback) with Pydantic structured outputs for high-speed routing and safety checks.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)


class RouteDecision(BaseModel):
    reason: str = Field(
        default="",
        description=(
            "Brief 1-sentence step-by-step reasoning evaluating user intent against document topics, "
            "temporal freshness requirements, and safety rules."
        ),
    )
    route: Literal["rag", "web_search", "direct_answer", "unsafe"] = Field(
        description=(
            "The selected execution route: "
            "'rag' for questions about uploaded documents or policy manuals; "
            "'web_search' for live/current events, weather, stock prices, or recent news; "
            "'direct_answer' for greetings, identity/persona questions, general concepts, explanations, coding, or math; "
            "'unsafe' for requests asking for malware, cyberattacks, exploit payloads, dangerous weapons, harassment, or self-harm."
        )
    )


# Initialize Groq 120b (primary) and Gemini Flash-Lite (fallback) structured router models
_groq_router = ChatGroq(
    model=config.GEMINI_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
).with_structured_output(RouteDecision)

try:
    _gemini_router = ChatGoogleGenerativeAI(
        model=config.GEMINI_FAST_MODEL,  # gemini-3.5-flash-lite
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.0,
        max_retries=0,
    ).with_structured_output(RouteDecision)
except Exception as e:
    logger.warning("Could not initialize Gemini router: %s", e)
    _gemini_router = None


def _format_documents(documents: list) -> str:
    """Format documents with their extracted topics for the system prompt."""
    if not documents:
        return "None"
    lines = []
    for doc in documents:
        if isinstance(doc, dict):
            name = doc.get("filename") or doc.get("name") or "Unknown"
            topics = doc.get("topics", "").strip()
            if topics:
                lines.append(f'   - "{name}" (Topics: {topics})')
            else:
                lines.append(f'   - "{name}"')
        else:
            lines.append(f'   - "{doc}"')
    return "\n".join(lines)


def _build_system_prompt(has_documents: bool, documents: list) -> str:
    current_date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    if has_documents and documents:
        doc_context = _format_documents(documents)
        rag_rule = f"""2. "rag" — The question is about content in the user's uploaded documents.
   Active Uploaded Documents:
{doc_context}
   CLASSIFY AS "rag" IF ANY OF THESE ARE TRUE:
   - The question relates to topics, subjects, or domains of the active uploaded files above.
   - The user uses references like "this document", "the file", "the report", "what does it say", "summarize this".
   - The user asks for specific internal facts stored in these files."""
    else:
        # Dynamic Token Pruning: omit RAG rule if no documents exist
        rag_rule = """2. "rag" — (DISABLED: No documents are currently uploaded by the user)."""

    return f"""You are Cortex, a helpful, intelligent, document-aware AI assistant.
Today's date is: {current_date}.

Your job is to classify the user's intent into exactly one of the following 4 routes:

1. "unsafe" — The request asks for malware/ransomware generation, vulnerability exploit scripts, DDoS payloads, cyberattack instructions, dangerous chemical/explosive weapons, severe hate speech, or self-harm.

{rag_rule}

3. "web_search" — The question requires current, recent, or live real-time information (e.g. today's news, stock market updates, recent sports/events, weather, or begins with "Search the web for").

4. "direct_answer" — Greetings ("hi", "who are you"), general concepts, explanations, coding questions, math problems, or creative writing that do NOT require uploaded documents or live web data.
   Examples: "What is machine learning?", "Write a Python function for Fibonacci", "Explain relativity", "Calculate derivative"."""


def _build_messages(question: str, has_documents: bool, documents: list) -> list:
    prompt = _build_system_prompt(has_documents, documents)
    return [
        SystemMessage(content=prompt),
        HumanMessage(content=f"User Query: {question}"),
    ]


async def classify_async(
    question: str,
    has_documents: bool,
    document_names: list | None = None,
    documents: list | None = None,
) -> Dict[str, Any]:
    """Asynchronously classify user question with Groq primary and Gemini Flash-Lite fallback."""
    if question.lower().startswith("search the web for "):
        return {"route": "web_search", "direct_answer": "", "reason": "UI button override"}

    docs = documents if documents is not None else (document_names or [])
    messages = _build_messages(question, has_documents, docs)
    route, reason = "", ""

    # 1. Attempt Primary
    try:
        decision: RouteDecision = await asyncio.wait_for(
            _groq_router.ainvoke(messages),
            timeout=config.TIMEOUT_ROUTER,
        )
        route = decision.route
        reason = decision.reason
    except Exception as e:
        logger.warning("Primary router failed: %s. Falling back to Gemini.", e)

    # 2. Fallback to Gemini Flash-Lite if Primary failed
    if not route and _gemini_router:
        try:
            decision: RouteDecision = await asyncio.wait_for(
                _gemini_router.ainvoke(messages),
                timeout=config.TIMEOUT_ROUTER,
            )
            route = decision.route
            reason = decision.reason
        except Exception as e:
            logger.warning("Gemini router fallback error: %s. Using default.", e)

    if not route:
        route = "rag" if has_documents else "direct_answer"
        reason = "fallback"

    if route == "rag" and not has_documents:
        route = "direct_answer"
        reason = "No documents uploaded, defaulting to direct answer"

    direct_answer = ""
    if route == "unsafe":
        direct_answer = "I cannot provide assistance with malware, cyberattacks, exploit payloads, dangerous weapons, harassment, or self-harm."

    return {"route": route, "direct_answer": direct_answer, "reason": reason}


def classify(
    question: str,
    has_documents: bool,
    document_names: list | None = None,
    documents: list | None = None,
) -> Dict[str, Any]:
    """Synchronous wrapper for classify_async."""
    return asyncio.run(classify_async(question, has_documents, document_names, documents))

