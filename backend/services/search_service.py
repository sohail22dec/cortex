"""
Search Service — Query rewriting and Tavily web search integration with clean snippet extraction.
"""
from __future__ import annotations

import asyncio
import logging
import re
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from tavily import TavilyClient

import config

logger = logging.getLogger(__name__)

# Fast LLM for query transformation
_query_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.0,
)


class QueryTransform(BaseModel):
    transformed_query: str = Field(
        description="The rewritten, search-engine or vector-search optimized query."
    )
    reason: str = Field(
        default="",
        description="Brief explanation of how the query was transformed."
    )


_structured_query_llm = _query_llm.with_structured_output(QueryTransform)


def _clean_web_results(raw_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extracts only clean, relevant fields from Tavily search results, discarding raw scrapes."""
    clean_results = []
    seen_urls = set()

    for r in raw_results:
        url = str(r.get("url", "")).strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        title = str(r.get("title", "No Title")).strip()
        content = str(r.get("content", "")).strip()
        # Normalize whitespace (collapse multiple newlines/tabs/spaces)
        content = re.sub(r"\s+", " ", content)

        if not content:
            continue

        clean_results.append({
            "title": title,
            "url": url,
            "content": content,
            "score": float(r.get("score", 0.0)) if r.get("score") is not None else 0.0,
        })

    return clean_results


async def rewrite_query_for_vector_db_async(question: str, document_names: List[str]) -> str:
    """
    Rewrites a conversational or vague user query to improve similarity search
    against the uploaded document titles/domain.
    """
    messages = [
        SystemMessage(
            content=(
                "You are an expert Query Optimizer for vector similarity search.\n"
                "Your task is to rewrite the user's question into a clear, keyword-dense query "
                "that maximizes semantic matching against the user's documents.\n"
                f"Active uploaded documents: {document_names}\n"
                "Remove conversational filler, expand pronouns, and focus on core concepts."
            )
        ),
        HumanMessage(content=f"Original Question: {question}"),
    ]
    try:
        res: QueryTransform = await _structured_query_llm.ainvoke(messages)
        return res.transformed_query.strip()
    except Exception as e:
        logger.warning("Vector DB query rewriting failed: %s. Using original.", e)
        return question


async def rewrite_query_for_web_async(question: str) -> str:
    """
    Rewrites a user question into an effective, search-engine-optimized keyword query for Tavily.
    """
    messages = [
        SystemMessage(
            content=(
                "You are a web search query rewriter.\n"
                "Rewrite the user's question into a clean, concise, keyword-focused search engine query.\n"
                "Do NOT use quotes or operators unless essential. Strip conversational phrases like 'can you tell me'."
            )
        ),
        HumanMessage(content=f"Original Question: {question}"),
    ]
    try:
        res: QueryTransform = await _structured_query_llm.ainvoke(messages)
        return res.transformed_query.strip()
    except Exception as e:
        logger.warning("Web query rewriting failed: %s. Using original.", e)
        return question


async def search_web_async(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Asynchronously executes a web search using Tavily without blocking the event loop.
    Extracts and sanitizes only relevant clean text fields, discarding raw HTML payloads.
    """
    client = TavilyClient(api_key=config.TAVILY_API_KEY)

    try:
        response = await asyncio.to_thread(
            client.search,
            query=query,
            search_depth="basic",
            max_results=max_results,
        )
        raw_results = response.get("results", [])
        return _clean_web_results(raw_results)
    except Exception as e:
        logger.error("Tavily search error for query '%s': %s", query, e)
        return []
