"""
LLM Service — Direct conversational AI response service.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import config

logger = logging.getLogger(__name__)


# Initialize Groq 20b (primary) and Gemini Flash-Lite (fallback) models
_groq_direct_llm = ChatGroq(
    model=config.GROQ_FAST_MODEL,  # openai/gpt-oss-20b
    api_key=config.GROQ_API_KEY,
    temperature=0.7,
)

try:
    _gemini_direct_llm = ChatGoogleGenerativeAI(
        model=config.GEMINI_FAST_MODEL,  # gemini-3.5-flash-lite
        google_api_key=config.GEMINI_API_KEY,
        temperature=0.7,
        max_retries=0,
    )
except Exception as e:
    logger.warning("Could not initialize Gemini direct LLM: %s", e)
    _gemini_direct_llm = None

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

    answer = ""
    try:
        response = await _groq_direct_llm.ainvoke(messages)
        answer = _clean_response(str(response.content))
    except Exception as e:
        logger.warning("Groq 20b direct LLM failed: %s. Falling back to Gemini.", e)

    if not answer and _gemini_direct_llm:
        try:
            response = await _gemini_direct_llm.ainvoke(messages)
            answer = _clean_response(str(response.content))
        except Exception as e:
            logger.error("Gemini direct LLM fallback failed: %s", e)

    if not answer:
        answer = "I am Cortex, an AI assistant. How can I help you today?"

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
