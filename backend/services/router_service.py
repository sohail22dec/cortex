"""
Router Service — Intelligent, document-aware LLM classifier.
Uses Groq with Pydantic structured outputs for high-speed routing and safety checks.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
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
            "'rag' for questions about uploaded documents or policy manuals; "
            "'web_search' for live/current events, weather, stock prices, or recent news; "
            "'direct_answer' for greetings, identity/persona questions, general concepts, explanations, coding, or math; "
            "'unsafe' for requests asking for malware, cyberattacks, exploit payloads, dangerous weapons, harassment, or self-harm."
        )
    )


# Initialize Groq structured router model
_groq_router = ChatGroq(
    model=config.GROQ_REASONING_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
).with_structured_output(RouteDecision)


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
        rag_section = f"""- "rag": Inquiries seeking internal facts, proprietary guidelines, procedures, or domain specifics contained within the user's uploaded documents:
{doc_context}
  Choose "rag" when the question seeks information specific to these documents or asks to analyze, extract, or summarize uploaded material."""
    else:
        # Dynamic Token Pruning: omit RAG rule if no documents exist
        rag_section = """- "rag": (DISABLED: No documents are currently uploaded by the user)."""

    return f"""You are the intent classification engine for Cortex, an intelligent AI assistant.
Today's date is: {current_date}.

Analyze the user's active query and classify their primary intent into the single most appropriate execution route:

- "unsafe": Requests involving weapon creation, cyberattacks, exploit payloads, malware generation, severe harassment, or self-harm.

{rag_section}

- "web_search": Inquiries requiring real-time, live, or time-sensitive external information (such as today's breaking news, recent events, live financial markets, current weather, or begins with "Search the web for").

- "direct_answer": General knowledge, conceptual explanations, coding assistance, mathematical calculations, logic problems, creative writing, or casual greetings that do not require external documents or real-time data.

Decision Guidelines:
- If a query is a general concept (e.g. "Explain binary search", "What is machine learning?") that has no dependency on uploaded files, prefer "direct_answer".
- If a query pertains to the specific topics, policies, or content of the uploaded files, route to "rag".
- Prioritize user safety above all other routes."""



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
        reason = getattr(decision, "reason", "")
    except Exception as e:
        logger.warning("Router classification failed: %s. Using default.", e)

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

