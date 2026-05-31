"""
Embeddings — generates text embeddings using Google Gemini's
`text-embedding-004` model (cloud-based, 768 dimensions, free tier).

No local model is downloaded. No RAM/CPU spike occurs on your machine.
All computation happens on Google's servers and results are returned
as plain Python float lists.
"""
from __future__ import annotations

import logging
from typing import List

from google import genai
from google.genai import types

import config

logger = logging.getLogger(__name__)

# Singleton Gemini client — initialised once on first import
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not config.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. "
                "Get a free key at https://aistudio.google.com/ and add it to your .env file."
            )
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
        logger.info("Gemini embedding client initialised (model: %s)", config.GEMINI_EMBEDDING_MODEL)
    return _client


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of text chunks (for indexing documents).
    Returns a list of 768-dimensional float vectors.
    """
    client = _get_client()
    
    # The Gemini API has a strict limit of 100 items per batch request.
    # We batch the texts into chunks of 100 to avoid 400 INVALID_ARGUMENT errors.
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        response = client.models.embed_content(
            model=config.GEMINI_EMBEDDING_MODEL,
            contents=batch_texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            ),
        )
        batch_embeddings = [e.values for e in response.embeddings]
        all_embeddings.extend(batch_embeddings)

    logger.info("Embedded %d text chunks via Gemini", len(all_embeddings))
    return all_embeddings


def embed_query(query: str) -> List[float]:
    """
    Generate an embedding for a single search query.
    Uses RETRIEVAL_QUERY task type which is optimised for semantic search.
    Returns a single 768-dimensional float vector.
    """
    client = _get_client()

    response = client.models.embed_content(
        model=config.GEMINI_EMBEDDING_MODEL,
        contents=[query],
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768
        ),
    )

    embedding = response.embeddings[0].values
    logger.info("Embedded search query via Gemini")
    return embedding
