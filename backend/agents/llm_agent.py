"""
LLM Agent — answers general knowledge questions directly from Groq,
without any retrieval or web search.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import config

logger = logging.getLogger(__name__)

_llm = ChatGroq(
    model=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.7,
)

SYSTEM_PROMPT = """You are Cortex, a helpful and knowledgeable AI assistant.
You answer questions clearly and concisely based on your training knowledge.
If you're unsure, say so honestly rather than guessing.
Format your answers in a readable way using markdown where helpful."""


def run(question: str) -> Dict[str, Any]:
    """Answer a general knowledge question directly with the LLM."""
    logger.info("LLM Agent | question: %s", question[:80])

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    response = _llm.invoke(messages)
    answer = response.content

    return {
        "answer": answer,
        "source": "llm",
        "citations": [],
    }
