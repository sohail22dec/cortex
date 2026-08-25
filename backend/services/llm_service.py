"""
LLM Service — Direct conversational AI response service.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import config

logger = logging.getLogger(__name__)

_llm = ChatGroq(
    model=config.GROQ_REASONING_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.7,
)

SYSTEM_PROMPT = """You are Cortex, a helpful and knowledgeable AI assistant.
You answer questions clearly and concisely based on your training knowledge.
If you're unsure, say so honestly rather than guessing.
Format your answers in a readable way using markdown where helpful."""


def _clean_response(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return cleaned if cleaned else text.strip()


async def run_llm_async(question: str) -> Dict[str, Any]:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    response = await _llm.ainvoke(messages)
    answer = _clean_response(str(response.content))

    return {
        "answer": answer,
        "source": "llm",
        "citations": [],
    }


def run_llm(question: str) -> Dict[str, Any]:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question),
    ]

    response = _llm.invoke(messages)
    answer = _clean_response(str(response.content))

    return {
        "answer": answer,
        "source": "llm",
        "citations": [],
    }
