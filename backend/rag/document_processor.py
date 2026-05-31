"""
Document processor — parses PDF, DOCX, and TXT files,
splits them into chunks, and indexes them into Supabase via Gemini embeddings.
"""
from __future__ import annotations

import logging
import os
import tempfile
from typing import List

import config
from rag import vector_store as vs

logger = logging.getLogger(__name__)


# ── Text splitter (manual, no LangChain dep needed here) ─────────────────────

def _split_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Simple recursive character splitter."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        # Try to break at a paragraph, then sentence, then space
        if end < len(text):
            for sep in ["\n\n", "\n", ". ", " "]:
                idx = text.rfind(sep, start, end)
                if idx > start:
                    end = idx + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        next_start = end - overlap
        # Prevent infinite loops if a separator was found very close to the start
        if next_start <= start:
            start = end
        else:
            start = next_start
            
    return chunks


# ── Parsers ───────────────────────────────────────────────────────────────────

def _parse_pdf(path: str) -> str:
    import fitz  # pymupdf
    doc = fitz.open(path)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n\n".join(pages)


def _parse_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _parse_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _extract_text(path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return _parse_pdf(path)
    elif ext in (".docx", ".doc"):
        return _parse_docx(path)
    else:
        return _parse_txt(path)


# ── Public API ────────────────────────────────────────────────────────────────

def process_and_index(session_id: str, file_bytes: bytes, filename: str) -> int:
    """
    Parse, chunk, and index a document for a session.
    Returns the number of chunks indexed.
    """
    suffix = os.path.splitext(filename)[1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        text = _extract_text(tmp_path, filename)
    finally:
        os.unlink(tmp_path)

    if not text.strip():
        raise ValueError("No text could be extracted from the file.")

    raw_chunks = _split_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)

    # Build dict chunks for the vector store
    chunks = [{"text": c, "source": filename} for c in raw_chunks]

    logger.info("Session %s | '%s' → %d chunks", session_id, filename, len(chunks))

    vs.add_documents(session_id, chunks)
    return len(chunks)
