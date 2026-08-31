"""
Generator Service — Synthesizes answers based on Document context, Web context, or Hybrid context
with strict token budget capping and clean snippet formatting.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

import config

logger = logging.getLogger(__name__)


def _get_generator_llm():
    """Initializes generator LLM with Gemini 2.5 Flash, falling back to Groq if needed."""
    try:
        return ChatGoogleGenerativeAI(
            model=config.GEMINI_REASONING_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.2,
        )
    except Exception as e:
        logger.warning("Could not initialize Gemini generator LLM: %s. Falling back to Groq.", e)
        return ChatGroq(
            model=config.GROQ_REASONING_MODEL,
            api_key=config.GROQ_API_KEY,
            temperature=0.2,
        )


_generator_llm = _get_generator_llm()

DIRECT_SYSTEM_PROMPT = """You are Cortex, an intelligent, helpful, and concise AI assistant.
Answer the user's question directly, accurately, and politely in markdown.
Provide clean explanations, code blocks, or mathematical derivations where appropriate."""

RAG_SYSTEM_PROMPT = """You are Cortex, a document-aware AI assistant.
Answer the user's question accurately using ONLY the provided document context.
If the context does not contain enough information, clearly explain what was found and what is missing.
Format your answer clearly using markdown.
CRITICAL CONSTRAINT: Do NOT write "Source:", "Sources:", or document filenames anywhere in your response text. Citations and document badges are rendered automatically by the UI."""

STRICT_RAG_SYSTEM_PROMPT = """You are Cortex, a document-aware AI assistant with STRICT groundedness rules.
Answer the question using ONLY facts directly stated in the provided document context.
Do NOT extrapolate, guess, or add outside knowledge.
CRITICAL CONSTRAINT: Do NOT write "Source:", "Sources:", or document filenames anywhere in your response text."""

WEB_SYSTEM_PROMPT = """You are Cortex, a real-time web-aware AI assistant.
Answer the question accurately using the provided web search results.
Mention key facts clearly.
CRITICAL CONSTRAINT: Do NOT write "Source:", "Sources:", or URLs as a manual footer at the end of your answer."""

HYBRID_SYSTEM_PROMPT = """You are Cortex, an intelligent hybrid AI assistant.
You have access to excerpts from the user's uploaded documents AND supplementary real-time web search results.
Synthesize a comprehensive, accurate answer combining both sources.
Clearly distinguish what comes from uploaded documents vs what comes from the web.
CRITICAL CONSTRAINT: Do NOT write "Source:" or "Sources:" footers at the end of your answer."""


def _clean_response(content: Any) -> str:
    if isinstance(content, list):
        text = "".join(c.get("text", "") if isinstance(c, dict) else str(c) for c in content)
    else:
        text = str(content)
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return cleaned if cleaned else text.strip()


def build_doc_context(
    chunks: List[Dict[str, Any]],
    max_chars: int = getattr(config, "MAX_DOC_CONTEXT_CHARS", 10000),
) -> str:
    """
    Builds a clean, formatted document context string capped to max_chars to avoid
    'Lost in the Middle' attention degradation and reduce LLM token latency.
    """
    if not chunks:
        return ""

    parts = []
    current_len = 0

    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        text = str(chunk.get("text", "")).strip()
        if not text:
            continue

        formatted = f"[Document Chunk {i} from '{source}']:\n{text}"
        chunk_len = len(formatted)

        if current_len + chunk_len > max_chars:
            remaining_budget = max_chars - current_len
            if remaining_budget > 150:
                # Include trimmed snippet up to remaining budget
                truncated_text = text[: remaining_budget - 70].rsplit(" ", 1)[0]
                parts.append(
                    f"[Document Chunk {i} from '{source}']:\n{truncated_text} ... [truncated to fit context budget]"
                )
            break

        parts.append(formatted)
        current_len += chunk_len + 8  # separator padding

    return "\n\n---\n\n".join(parts)


def build_web_context(
    web_results: List[Dict[str, Any]],
    max_chars: int = getattr(config, "MAX_WEB_CONTEXT_CHARS", 5000),
    max_snippet_chars: int = getattr(config, "MAX_WEB_SNIPPET_CHARS", 800),
) -> str:
    """
    Extracts only relevant clean fields from web search results (title, url, content)
    and enforces strict length and snippet caps, discarding raw HTML payloads.
    """
    if not web_results:
        return ""

    parts = []
    current_len = 0

    for i, r in enumerate(web_results, 1):
        title = str(r.get("title", "No title")).strip()
        url = str(r.get("url", "")).strip()
        content = str(r.get("content", "")).strip()
        if not content:
            continue

        # Cap individual snippet length
        if len(content) > max_snippet_chars:
            content = content[:max_snippet_chars].rsplit(" ", 1)[0] + "..."

        formatted = f"[Web Source {i}: {title}]\nURL: {url}\nSummary: {content}"
        snippet_len = len(formatted)

        if current_len + snippet_len > max_chars:
            break

        parts.append(formatted)
        current_len += snippet_len + 8

    return "\n\n---\n\n".join(parts)


async def generate_rag_answer_async(
    question: str,
    chunks: List[Dict[str, Any]],
    strict: bool = False,
) -> Dict[str, Any]:
    """Generates an answer from document chunks with budget-capped context."""
    context = build_doc_context(chunks, max_chars=config.MAX_DOC_CONTEXT_CHARS)
    prompt = STRICT_RAG_SYSTEM_PROMPT if strict else RAG_SYSTEM_PROMPT

    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=f"Document Context:\n\n{context}\n\nQuestion: {question}"),
    ]
    res = await _generator_llm.ainvoke(messages)
    answer = _clean_response(str(res.content))
    sources = sorted(list({c.get("source", "Unknown") for c in chunks if c.get("source")}))

    return {
        "answer": answer,
        "source": "rag",
        "citations": sources,
    }


async def generate_web_answer_async(
    question: str,
    web_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generates an answer from clean web search results with budget-capped context."""
    if not web_results:
        return {
            "answer": "I searched the web but could not find relevant results for your query.",
            "source": "web_search",
            "citations": [],
        }

    context = build_web_context(web_results, max_chars=config.MAX_WEB_CONTEXT_CHARS)
    urls = [r.get("url", "") for r in web_results if r.get("url")]

    messages = [
        SystemMessage(content=WEB_SYSTEM_PROMPT),
        HumanMessage(content=f"Web Search Results:\n\n{context}\n\nQuestion: {question}"),
    ]
    res = await _generator_llm.ainvoke(messages)
    answer = _clean_response(str(res.content))

    return {
        "answer": answer,
        "source": "web_search",
        "citations": urls[:3],
    }


async def generate_hybrid_answer_async(
    question: str,
    chunks: List[Dict[str, Any]],
    web_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Generates an answer combining document chunks and supplementary web search results with balanced budgets."""
    doc_context = build_doc_context(chunks, max_chars=config.MAX_HYBRID_DOC_CHARS)
    web_context = build_web_context(web_results, max_chars=config.MAX_HYBRID_WEB_CHARS)

    combined_context = f"=== UPLOADED DOCUMENTS ===\n{doc_context}\n\n=== WEB SEARCH RESULTS ===\n{web_context}"

    doc_sources = [c.get("source", "Unknown") for c in chunks if c.get("source")]
    web_urls = [r.get("url", "") for r in web_results if r.get("url")]
    citations = list(set(doc_sources + web_urls[:2]))

    messages = [
        SystemMessage(content=HYBRID_SYSTEM_PROMPT),
        HumanMessage(content=f"Provided Sources:\n\n{combined_context}\n\nQuestion: {question}"),
    ]
    res = await _generator_llm.ainvoke(messages)
    answer = _clean_response(str(res.content))

    return {
        "answer": answer,
        "source": "hybrid",
        "citations": citations,
    }


async def generate_direct_answer_async(question: str) -> Dict[str, Any]:
    """Generates a direct, clean answer for general concepts, coding, math, or greetings."""
    messages = [
        SystemMessage(content=DIRECT_SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]
    try:
        res = await _generator_llm.ainvoke(messages)
        answer = _clean_response(res.content)
    except Exception as e:
        logger.warning("Direct answer synthesis error: %s. Using simple fallback.", e)
        answer = "I am Cortex, an AI assistant. How can I help you today?"

    return {
        "answer": answer,
        "source": "llm",
        "citations": [],
    }

