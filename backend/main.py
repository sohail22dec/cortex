import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.chat import router as chat_router
from api.documents import router as documents_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cortex API",
    description="Multi-Agent RAG Application — powered by Groq, Qdrant & Tavily",
    version="1.0.0",
)

# ── CORS (Next.js frontend) ───────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(documents_router)


# ── Health & root ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Cortex Multi-Agent RAG API",
        "version": "1.0.0",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
