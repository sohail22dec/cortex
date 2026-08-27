"""
Conversation Service — Stores session history, summarizes old messages, and keeps
the most recent N messages verbatim so the LLM never loses short-term context.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

import config
from rag import vector_store as vs

logger = logging.getLogger(__name__)

# Fast/cheap model for summarization so we don't burn reasoning-model quota
_summarizer_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.3,
)


@dataclass
class ChatMessage:
    role: str
    content: str


def _get_client():
    """Reuse the singleton Supabase client from the vector store module."""
    return vs._get_client()


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 characters per token for English text."""
    return max(1, len(text) // 4)


def _format_messages(messages: List[ChatMessage]) -> str:
    """Formats a list of messages into a single conversation string."""
    lines: List[str] = []
    for msg in messages:
        label = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{label}: {msg.content}")
    return "\n".join(lines)


def save_message(session_id: str, role: str, content: str) -> None:
    """Persist a user or assistant message to Supabase."""
    try:
        client = _get_client()
        client.table("conversations").insert(
            {
                "session_id": session_id,
                "role": role,
                "content": content,
            }
        ).execute()
    except Exception as e:
        logger.warning("Failed to save conversation message for %s: %s", session_id, e)


def get_messages(session_id: str) -> List[ChatMessage]:
    """Fetch all messages for a session, ordered by time."""
    try:
        client = _get_client()
        response = (
            client.table("conversations")
            .select("role,content,created_at")
            .eq("session_id", session_id)
            .order("created_at")
            .execute()
        )
        return [
            ChatMessage(role=row["role"], content=row["content"])
            for row in (response.data or [])
        ]
    except Exception as e:
        logger.warning("Failed to fetch conversation for %s: %s", session_id, e)
        return []


async def _summarize_messages(messages: List[ChatMessage]) -> str:
    """Ask a fast LLM to compress older messages into a concise summary."""
    text = _format_messages(messages)
    system_prompt = (
        "You are a conversation summarizer. Condense the following chat history into 2-3 concise sentences. "
        "Preserve key facts, user preferences, and any unresolved questions. Do not add commentary."
    )
    user_prompt = f"Conversation to summarize:\n\n{text}\n\nSummary:"

    try:
        res = await _summarizer_llm.ainvoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )
        return str(res.content).strip()
    except Exception as e:
        logger.warning("Conversation summarization failed: %s", e)
        return "[Earlier conversation summary unavailable.]"


async def get_conversation_context(session_id: str) -> str:
    """
    Returns prior conversation context for the LLM.

    - If total estimated tokens are under the budget, return all messages.
    - If over budget, summarize all but the last N messages and keep those verbatim.
    """
    messages = get_messages(session_id)
    if not messages:
        return ""

    total_tokens = sum(_estimate_tokens(m.content) for m in messages)

    # Under budget: include full history
    if total_tokens <= config.MAX_CONVERSATION_TOKENS:
        return _format_messages(messages)

    # Over budget: summarize older messages, keep last N verbatim
    recent = messages[-config.MAX_RECENT_MESSAGES :]
    older = messages[: -config.MAX_RECENT_MESSAGES]

    if older:
        summary = await _summarize_messages(older)
        return (
            f"Summary of earlier conversation:\n{summary}\n\n"
            f"Recent messages:\n{_format_messages(recent)}"
        )

    return _format_messages(recent)
