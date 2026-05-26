"""
Documents API — upload, list, and delete documents for a session.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from rag import document_processor, vector_store as vs

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md", ".rst"}
MAX_FILE_SIZE_MB = 20


class UploadResponse(BaseModel):
    filename: str
    chunks: int
    message: str


class DocumentListResponse(BaseModel):
    session_id: str
    documents: list[str]


class DeleteResponse(BaseModel):
    message: str


@router.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: str = Form(...),
):
    """Upload and index a document for a session."""
    import os

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()

    # Size check
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB",
        )

    try:
        chunks = document_processor.process_and_index(
            session_id=session_id,
            file_bytes=content,
            filename=file.filename or "unknown",
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Failed to process document '%s'", file.filename)
        raise HTTPException(status_code=500, detail=f"Processing error: {e}")

    return UploadResponse(
        filename=file.filename or "unknown",
        chunks=chunks,
        message=f"Successfully indexed {chunks} chunks from '{file.filename}'",
    )


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(session_id: str):
    """List all documents indexed for a session."""
    docs = vs.list_document_names(session_id)
    return DocumentListResponse(session_id=session_id, documents=docs)


@router.delete("/documents/{filename}", response_model=DeleteResponse)
async def delete_document(filename: str, session_id: str):
    """Remove a document from the session's vector store."""
    if not vs.collection_exists(session_id):
        raise HTTPException(status_code=404, detail="No documents found for this session")

    vs.delete_document(session_id, filename)
    return DeleteResponse(message=f"Document '{filename}' removed from your session")
