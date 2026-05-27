"""
Qdrant vector store wrapper using fastembed (lightweight ONNX embeddings).
Each user session gets its own isolated collection.

Note: We let Qdrant/fastembed manage collection creation automatically
via client.add(), which picks the correct vector dimensions.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import List

from qdrant_client import QdrantClient, models

import config

logger = logging.getLogger(__name__)


# ── Singleton Qdrant client ───────────────────────────────────────────────────

@lru_cache(maxsize=1)
def get_client() -> QdrantClient:
    """Return the shared Qdrant client pointing to Qdrant Cloud."""
    if not config.QDRANT_URL or not config.QDRANT_API_KEY:
        raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in your configuration.")
    
    logger.info("Connecting to Qdrant Cloud at: %s", config.QDRANT_URL)
    return QdrantClient(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
    )




# ── Collection helpers ────────────────────────────────────────────────────────

def _col(session_id: str) -> str:
    """Safe Qdrant collection name from session_id."""
    return f"session_{session_id.replace('-', '_')}"


def collection_exists(session_id: str) -> bool:
    client = get_client()
    return _col(session_id) in [c.name for c in client.get_collections().collections]


def delete_collection(session_id: str) -> None:
    get_client().delete_collection(_col(session_id))
    logger.info("Deleted collection: %s", _col(session_id))


# ── Document operations ───────────────────────────────────────────────────────

def add_documents(session_id: str, chunks: List[dict]) -> None:
    """
    Embed and store chunks using fastembed.
    chunks: list of {"text": str, "source": str}
    
    client.add() auto-creates the collection with correct vector dimensions
    and uses fastembed for embedding — no manual collection creation needed.
    """
    client = get_client()
    name = _col(session_id)

    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]

    client.add(
        collection_name=name,
        documents=texts,
        metadata=[{"source": s} for s in sources],
    )
    logger.info("Added %d chunks to %s", len(chunks), name)


def similarity_search(
    session_id: str, query: str, k: int = config.TOP_K_RESULTS
) -> List[dict]:
    """
    Return top-k relevant chunks for a query.
    Returns list of {"text": str, "source": str}
    """
    if not collection_exists(session_id):
        return []

    client = get_client()
    results = client.query(
        collection_name=_col(session_id),
        query_text=query,
        limit=k,
    )

    return [
        {
            "text": r.document,
            "source": (r.metadata or {}).get("source", "Unknown"),
        }
        for r in results
    ]


def has_documents(session_id: str) -> bool:
    if not collection_exists(session_id):
        return False
    return get_client().count(collection_name=_col(session_id)).count > 0


def list_document_names(session_id: str) -> List[str]:
    if not collection_exists(session_id):
        return []
    points, _ = get_client().scroll(
        collection_name=_col(session_id),
        with_payload=True,
        limit=10_000,
    )
    seen: set[str] = set()
    for p in points:
        src = (p.payload or {}).get("source", "")
        if src:
            seen.add(src)
    return sorted(seen)


def delete_document(session_id: str, filename: str) -> None:
    if not collection_exists(session_id):
        return
    get_client().delete(
        collection_name=_col(session_id),
        points_selector=models.Filter(
            must=[
                models.FieldCondition(
                    key="source",
                    match=models.MatchValue(value=filename),
                )
            ]
        ),
    )
    logger.info("Deleted '%s' from %s", filename, _col(session_id))
