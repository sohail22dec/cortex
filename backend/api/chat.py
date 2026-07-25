from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agents import orchestrator

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


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = orchestrator.run(
            session_id=request.session_id,
            question=request.message,
        )
        return ChatResponse(**result)
    except Exception as e:
        logger.exception("Chat error for session %s", request.session_id)
        raise HTTPException(status_code=500, detail=str(e))
