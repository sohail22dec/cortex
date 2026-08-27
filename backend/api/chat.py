from __future__ import annotations

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
from services.conversation_service import get_conversation_context, save_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=128)


class ChatResponse(BaseModel):
    answer: str
    source: str
    citations: list[str]
    route: str
    suggest_web_search: bool = False


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

        return ChatResponse(
            answer=clean_answer,
            source=result.get("source", "llm"),
            citations=clean_citations,
            route=result.get("route", "llm"),
            suggest_web_search=result.get("source") == "web_search",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Chat error for session %s", request.session_id)
        raise HTTPException(status_code=500, detail=str(e))
