from __future__ import annotations

import logging
from functools import lru_cache

from supabase import create_client, Client

import config
from rag import embeddings as emb

logger = logging.getLogger(__name__)

TABLE = "document_chunks"


# ── Singleton Supabase client ─────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_client() -> Client:
    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in your .env file."
        )
    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)


# ── Document operations ───────────────────────────────────────────────────────

def add_documents(session_id: str, chunks: list[dict]) -> None:
    client = _get_client()

    texts = [c["text"] for c in chunks]
    sources = [c["source"] for c in chunks]

    # Step 1: Generate embeddings in the cloud (zero local RAM/CPU usage)
    vectors = emb.embed_texts(texts)

    # Step 2: Build rows for bulk insert
    rows = [
        {
            "session_id": session_id,
            "content": text,
            "source": source,
            "embedding": vector,
        }
        for text, source, vector in zip(texts, sources, vectors)
    ]

    client.table(TABLE).insert(rows).execute()

def similarity_search(session_id: str, query: str, k: int = config.TOP_K_RESULTS) -> list[dict]:
    client = _get_client()
    query_vector = emb.embed_query(query)

    try:
        match_count = int(k)
    except (TypeError, ValueError):
        match_count = 5

    response = client.rpc(
        "match_document_chunks",
        {
            "query_embedding": query_vector,
            "match_threshold": config.SIMILARITY_THRESHOLD,
            "match_count": match_count,
            "filter_session_id": session_id,
        },
    ).execute()

    return [
        {
            "text": row["content"],
            "source": row["source"],
        }
        for row in (response.data or [])
    ]


def has_documents(session_id: str) -> bool:
    client = _get_client()
    response = (
        client.table(TABLE)
        .select("id", count="exact")
        .eq("session_id", session_id)
        .limit(1)
        .execute()
    )
    return (response.count or 0) > 0


def list_document_names(session_id: str) -> list[str]:
    client = _get_client()
    response = (
        client.table(TABLE)
        .select("source")
        .eq("session_id", session_id)
        .execute()
    )
    names = {row["source"] for row in (response.data or []) if row.get("source")}
    return sorted(names)


def list_documents_info(session_id: str) -> list[dict]:
    client = _get_client()
    response = (
        client.table(TABLE)
        .select("source")
        .eq("session_id", session_id)
        .execute()
    )
    counts: dict[str, int] = {}
    for row in (response.data or []):
        src = row.get("source")
        if src:
            counts[src] = counts.get(src, 0) + 1
    return [{"filename": name, "chunks": count} for name, count in sorted(counts.items())]


def delete_document(session_id: str, filename: str) -> None:
    client = _get_client()
    client.table(TABLE).delete().eq("session_id", session_id).eq("source", filename).execute()

