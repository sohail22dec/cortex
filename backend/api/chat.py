from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

import config
from crag import run_crag_async
from guardrails import (
    check_prompt_async,
    process_output,
    rate_limit,
    redact_pii_async,
)
from rag import storage_service, vector_store as vs
from services.conversation_service import (
    delete_conversation,
    get_conversation_context,
    save_message,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=128)
    user_id: str | None = Field(None, max_length=128)


class DeleteSessionResponse(BaseModel):
    status: str
    message: str


class ChunkInfo(BaseModel):
    source: str
    text: str
    similarity: float | None = None


class WebResultInfo(BaseModel):
    title: str
    url: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    source: str
    citations: list[str]
    route: str
    suggest_web_search: bool = False
    chunks: list[ChunkInfo] = []
    web_results: list[WebResultInfo] = []
    evaluation_result: str | None = None
    evaluation_reason: str | None = None
    is_grounded: bool | None = None
    groundedness_reason: str | None = None
    transformed_query: str | None = None


@router.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[
        Depends(
            rate_limit(
                config.RATE_LIMIT_CHAT_REQUESTS,
                config.RATE_LIMIT_CHAT_WINDOW,
            )
        )
    ],
)
async def chat(request: ChatRequest):
    try:
        # ── Layer 1 Guardrail: Prompt Injection & Jailbreak Defense ───────────
        guard_res = await check_prompt_async(request.message)
        if not guard_res.is_safe:
            logger.warning(
                "Blocked unsafe prompt for session %s: %s (%s)",
                request.session_id,
                guard_res.violation_type,
                guard_res.reason,
            )
            return ChatResponse(
                answer=(
                    "I cannot fulfill this request as it appears to contain unauthorized instructions "
                    "or system overrides. Please refine your query."
                ),
                source="guardrail",
                citations=[],
                route="guardrail_blocked",
                suggest_web_search=False,
            )

        # ── Layer 1 Guardrail: PII & Sensitive Data Redaction ─────────────────
        pii_res = await redact_pii_async(request.message)
        processed_query = pii_res.sanitized_text

        # ── Conversation Memory ─────────────────────────────────────────────
        # Fetch prior context. If over the token budget, older messages are
        # summarized and only the last MAX_RECENT_MESSAGES are kept verbatim.
        prior_context = await get_conversation_context(request.session_id)
        if prior_context:
            augmented_question = f"{prior_context}\n\nCurrent question: {processed_query}"
        else:
            augmented_question = processed_query

        # ── CRAG Workflow Execution ───────────────────────────────────────────
        result = await run_crag_async(
            session_id=request.session_id,
            question=augmented_question,
            user_id=request.user_id,
        )

        # ── Layer 3 Guardrail: Output Scrubbing & Citation Verification ───────
        clean_answer, clean_citations = process_output(
            answer=result.get("answer", ""),
            citations=result.get("citations", []),
            valid_doc_sources=result.get("valid_doc_sources", set()),
            valid_web_urls=result.get("valid_web_urls", set()),
        )

        # Persist this turn so future questions have context.
        # We save the redacted query (not raw) to avoid storing PII in Supabase.
        save_message(request.session_id, "user", processed_query)
        save_message(request.session_id, "assistant", clean_answer)

        raw_chunks = result.get("chunks", [])
        clean_chunks = [
            ChunkInfo(
                source=c.get("source", "Unknown"),
                text=c.get("text", ""),
                similarity=c.get("similarity"),
            )
            for c in raw_chunks
            if c.get("text")
        ]

        raw_web = result.get("web_results", [])
        clean_web = [
            WebResultInfo(
                title=w.get("title", "Web Source"),
                url=w.get("url", ""),
                content=w.get("content", ""),
            )
            for w in raw_web
            if w.get("url") or w.get("content")
        ]

        return ChatResponse(
            answer=clean_answer,
            source=result.get("source", "llm"),
            citations=clean_citations,
            route=result.get("route", "llm"),
            suggest_web_search=result.get("source") == "web_search",
            chunks=clean_chunks,
            web_results=clean_web,
            evaluation_result=result.get("evaluation_result") or None,
            evaluation_reason=result.get("evaluation_reason") or None,
            is_grounded=result.get("is_grounded"),
            groundedness_reason=result.get("groundedness_reason") or None,
            transformed_query=result.get("transformed_query") or None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat error for session %s", request.session_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", response_model=DeleteSessionResponse)
async def delete_session(session_id: str):
    """Delete all conversation history, document chunks, and storage files associated with a session."""
    try:
        await asyncio.to_thread(delete_conversation, session_id)
        await asyncio.to_thread(vs.delete_session_documents, session_id)
        await asyncio.to_thread(storage_service.delete_session_files, session_id)
        return DeleteSessionResponse(
            status="success",
            message=f"Session '{session_id}' deleted successfully",
        )
    except Exception as e:
        logger.exception("Failed to delete session %s", session_id)
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {e}")

