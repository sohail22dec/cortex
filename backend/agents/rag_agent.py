"""
RAG Agent — retrieves relevant document chunks from the user's Qdrant collection
and uses Groq to synthesise an answer with citations.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

import config
from rag import vector_store as vs

logger = logging.getLogger(__name__)

_llm = ChatGroq(
    model=config.GROQ_MODEL,
    api_key=config.GROQ_API_KEY,
    temperature=0.3,
)

SYSTEM_PROMPT = """You are Cortex, a document-aware AI assistant.
You are given relevant excerpts from the user's uploaded documents.
Answer the question accurately based ONLY on the provided context.
If the context doesn't contain enough information to answer, say so clearly.
Always reference which document(s) you used in your answer.
Format your answer clearly using markdown where helpful."""


def _build_context(chunks: List[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        text = chunk.get("text", "")
        parts.append(f"[Excerpt {i} from '{source}']:\n{text}")
    return "\n\n---\n\n".join(parts)


def run(session_id: str, question: str) -> Dict[str, Any]:
    """Retrieve relevant chunks and generate an answer with Groq."""
    logger.info("RAG Agent | session=%s | question: %s", session_id, question[:80])

    chunks = vs.similarity_search(session_id, question, k=config.TOP_K_RESULTS)

    if not chunks:
        return {
            "answer": (
                "I couldn't find relevant information in your uploaded documents for this question. "
                "Please make sure you've uploaded the right documents, or rephrase your question."
            ),
            "source": "rag",
            "citations": [],
        }

    context = _build_context(chunks)
    sources = list({c.get("source", "Unknown") for c in chunks})

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(
            content=f"Context from documents:\n\n{context}\n\nQuestion: {question}"
        ),
    ]

    response = _llm.invoke(messages)

    return {
        "answer": response.content,
        "source": "rag",
        "citations": sources,
    }
