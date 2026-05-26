"""
Web Search Agent — uses Tavily to fetch current/live information
and synthesises an answer with Groq.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

import config

logger = logging.getLogger(__name__)

_llm = ChatGroq(
    model=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.5,
)

SYSTEM_PROMPT = """You are Cortex, a real-time web-aware AI assistant.
You are given search results from the web. Use them to answer the question accurately.
Always mention the key facts from the search results.
If specific sources are available, reference them.
Format your answer clearly using markdown where helpful."""


def _format_results(results: List[Dict]) -> str:
    parts = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "")
        parts.append(f"[Result {i}: {title}]\nURL: {url}\n{content}")
    return "\n\n---\n\n".join(parts)


def run(question: str) -> Dict[str, Any]:
    """Search the web with Tavily and answer using Groq."""
    logger.info("Web Search Agent | question: %s", question[:80])

    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    try:
        response = client.search(
            query=question,
            search_depth="basic",
            max_results=5,
        )
        results = response.get("results", [])
    except Exception as e:
        logger.error("Tavily search failed: %s", e)
        return {
            "answer": (
                f"I tried to search the web but encountered an error: {e}. "
                "Please check your Tavily API key."
            ),
            "source": "web_search",
            "citations": [],
        }

    if not results:
        return {
            "answer": "The web search didn't return any relevant results for your query.",
            "source": "web_search",
            "citations": [],
        }

    context = _format_results(results)
    urls = [r.get("url", "") for r in results if r.get("url")]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Web search results:\n\n{context}\n\n"
                f"Question: {question}"
            )
        ),
    ]

    llm_response = _llm.invoke(messages)
    answer = llm_response.content

    return {
        "answer": answer,
        "source": "web_search",
        "citations": urls[:3],  # top 3 URLs as citations
    }
