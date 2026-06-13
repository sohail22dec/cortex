"""
Document processor — parses PDF, DOCX, and TXT files,
splits them into chunks, and indexes them into Supabase via Gemini embeddings.
"""
from __future__ import annotations

import logging
import os
import tempfile
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

import config
from rag import vector_store as vs

logger = logging.getLogger(__name__)


# ── Public API ────────────────────────────────────────────────────────────────

def process_and_index(session_id: str, file_bytes: bytes, filename: str) -> int:
    """
    Parse, chunk, and index a document for a session.
    Returns the number of chunks indexed.
    """
    suffix = os.path.splitext(filename)[1].lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        if suffix == ".pdf":
            loader = PyMuPDFLoader(tmp_path)
        elif suffix in (".docx", ".doc"):
            loader = Docx2txtLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8", autodetect_encoding=True)
            
        docs = loader.load()
    finally:
        os.unlink(tmp_path)

    if not docs:
        raise ValueError("No text could be extracted from the file.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    split_docs = splitter.split_documents(docs)

    # Build dict chunks for the vector store
    chunks = [{"text": doc.page_content, "source": filename} for doc in split_docs]

    logger.info("Session %s | '%s' → %d chunks", session_id, filename, len(chunks))

    vs.add_documents(session_id, chunks)
    return len(chunks)
