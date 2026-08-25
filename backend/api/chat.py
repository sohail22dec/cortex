from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from crag import run_crag_async

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
        result = await run_crag_async(
            session_id=request.session_id,
            question=request.message,
        )
        return ChatResponse(
            answer=result.get("answer", ""),
            source=result.get("source", "llm"),
            citations=result.get("citations", []),
            route=result.get("route", "llm"),
            suggest_web_search=result.get("source") == "web_search",
        )
    except Exception as e:
        logger.exception("Chat error for session %s", request.session_id)
        raise HTTPException(status_code=500, detail=str(e))



