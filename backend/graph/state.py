from __future__ import annotations

from typing_extensions import TypedDict


class AgentState(TypedDict):
    question: str
    session_id: str
    has_documents: bool
    document_names: list
    route: str                      # "rag" | "llm" | "web_search"
    chunks: list                    # Raw retrieved chunks from Supabase
    filtered_chunks: list           # Relevant chunks after IsRel evaluation
    documents_relevant: bool        # IsRel outcome
    answer: str
    source: str                     # "rag" | "llm" | "web_search"
    citations: list
    is_grounded: bool               # IsSup outcome
    is_useful: bool                 # IsUse outcome
    suggest_web_search: bool        # Interactive web search suggestion flag
    retry_count: int                # Guard against infinite hallucination loops
