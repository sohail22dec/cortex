"""
Embeddings — generates text embeddings using Google Gemini's
`text-embedding-004` model via LangChain.
"""
from __future__ import annotations

import logging

from langchain_google_genai import GoogleGenAIEmbeddings

import config

logger = logging.getLogger(__name__)

# Singleton Gemini clients for different task types
_document_client: GoogleGenAIEmbeddings | None = None
_query_client: GoogleGenAIEmbeddings | None = None


def _get_document_client() -> GoogleGenAIEmbeddings:
    global _document_client
    if _document_client is None:
        _document_client = GoogleGenAIEmbeddings(
            model=config.GEMINI_EMBEDDING_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            task_type="RETRIEVAL_DOCUMENT"
        )
        logger.info("LangChain Gemini document embeddings client initialised (model: %s)", config.GEMINI_EMBEDDING_MODEL)
    return _document_client


def _get_query_client() -> GoogleGenAIEmbeddings:
    global _query_client
    if _query_client is None:
        _query_client = GoogleGenAIEmbeddings(
            model=config.GEMINI_EMBEDDING_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            task_type="RETRIEVAL_QUERY"
        )
        logger.info("LangChain Gemini query embeddings client initialised (model: %s)", config.GEMINI_EMBEDDING_MODEL)
    return _query_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text chunks (for indexing documents).
    Returns a list of 768-dimensional float vectors.
    """
    client = _get_document_client()
    embeddings = client.embed_documents(texts)
    logger.info("Embedded %d text chunks via LangChain", len(embeddings))
    return embeddings


def embed_query(query: str) -> list[float]:
    """
    Generate an embedding for a single search query.
    Returns a single 768-dimensional float vector.
    """
    client = _get_query_client()
    embedding = client.embed_query(query)
    logger.info("Embedded search query via LangChain")
    return embedding
