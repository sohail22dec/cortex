"""
CRAG State — State schema for Corrective Retrieval-Augmented Generation.
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal
from typing_extensions import TypedDict


class CRAGState(TypedDict):
    question: str
    session_id: str
    has_documents: bool
    document_names: List[str]
    route: str                          # "rag" | "llm" | "web_search"
    
    # Retrieval & Evaluation
    chunks: List[Dict[str, Any]]        # Raw chunks from Supabase vector store
    refined_chunks: List[Dict[str, Any]]# Relevant, de-noised chunks
    evaluation_result: str              # "CORRECT" | "INCORRECT" | "AMBIGUOUS"
    evaluation_reason: str
    db_retry_count: int                 # 0 = initial, 1 = re-retrieved from DB
    
    # Query Transformation & Web Augmentation
    transformed_query: str              # Search-optimized keyword query
    web_results: List[Dict[str, Any]]   # Results from Tavily web search
    
    # Output & Groundedness
    answer: str
    source: str                         # "rag" | "web_search" | "hybrid" | "llm"
    citations: List[str]
    is_grounded: bool                   # Independent Judge result
    groundedness_reason: str
    groundedness_retry_count: int       # Guard against infinite hallucination retry loops
