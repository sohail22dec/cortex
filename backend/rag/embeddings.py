"""
Embeddings — generates text embeddings using Google Gemini's
`text-embedding-004` model via LangChain.
"""
from __future__ import annotations

from langchain_google_genai import GoogleGenerativeAIEmbeddings

import config

# Singleton Gemini clients for different task types
_document_client: GoogleGenerativeAIEmbeddings | None = None
_query_client: GoogleGenerativeAIEmbeddings | None = None


def _get_document_client() -> GoogleGenerativeAIEmbeddings:
    global _document_client
    if _document_client is None:
        _document_client = GoogleGenerativeAIEmbeddings(
            model=config.GEMINI_EMBEDDING_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            task_type="RETRIEVAL_DOCUMENT"
        )
    return _document_client


def _get_query_client() -> GoogleGenerativeAIEmbeddings:
    global _query_client
    if _query_client is None:
        _query_client = GoogleGenerativeAIEmbeddings(
            model=config.GEMINI_EMBEDDING_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            task_type="RETRIEVAL_QUERY"
        )
    return _query_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of text chunks (for indexing documents).
    Returns a list of 768-dimensional float vectors (MRL truncated).
    """
    client = _get_document_client()
    embeddings = client.embed_documents(texts)
    return [vec[:768] for vec in embeddings]


def embed_query(query: str) -> list[float]:
    """
    Generate an embedding for a single search query.
    Returns a single 768-dimensional float vector (MRL truncated).
    """
    client = _get_query_client()
    embedding = client.embed_query(query)
    return embedding[:768]
