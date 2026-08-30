import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") or "gsk_mock_fallback_key_for_ci_testing"
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY") or "tvly-mock-fallback-key-for-ci"
GROQ_REASONING_MODEL = os.getenv("GROQ_REASONING_MODEL", "qwen/qwen3.6-27b")
GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")


# Supabase (vector store + future auth & sessions)
SUPABASE_URL = os.getenv("SUPABASE_URL") or "https://mockproject.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or "mock-supabase-service-key"

# Google Gemini (cloud embeddings — no local model, no RAM spikes)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "mock-gemini-key-for-ci"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"  # 3072-dim, truncated to 768 via MRL

# Chunking config
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval config
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# LangSmith Tracing Config
_enable_tracing = os.getenv("ENABLE_LANGSMITH", "false").lower() in ("true", "1")
_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY", "")
_project = os.getenv("LANGCHAIN_PROJECT") or os.getenv("LANGSMITH_PROJECT", "cortex")

if _enable_tracing and _api_key:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = _api_key
    os.environ["LANGSMITH_API_KEY"] = _api_key
    os.environ["LANGCHAIN_PROJECT"] = _project
    os.environ["LANGSMITH_PROJECT"] = _project
else:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGSMITH_TRACING"] = "false"
# ── Layer 1: Frontline Guardrails Configuration ──────────────────────────────
# Rate Limiting & Throttling
ENABLE_RATE_LIMITING = os.getenv("ENABLE_RATE_LIMITING", "true").lower() in ("true", "1")
RATE_LIMIT_CHAT_REQUESTS = int(os.getenv("RATE_LIMIT_CHAT_REQUESTS", "20"))
RATE_LIMIT_CHAT_WINDOW = int(os.getenv("RATE_LIMIT_CHAT_WINDOW", "60"))
RATE_LIMIT_UPLOAD_REQUESTS = int(os.getenv("RATE_LIMIT_UPLOAD_REQUESTS", "5"))
RATE_LIMIT_UPLOAD_WINDOW = int(os.getenv("RATE_LIMIT_UPLOAD_WINDOW", "60"))

# Prompt Injection & Jailbreak Defense
ENABLE_PROMPT_GUARD = os.getenv("ENABLE_PROMPT_GUARD", "true").lower() in ("true", "1")
USE_LOCAL_PROMPT_GUARD_MODEL = os.getenv("USE_LOCAL_PROMPT_GUARD_MODEL", "false").lower() in ("true", "1")
PROMPT_GUARD_MODEL = os.getenv("PROMPT_GUARD_MODEL", "meta-llama/Prompt-Guard-86M")
PROMPT_GUARD_THRESHOLD = float(os.getenv("PROMPT_GUARD_THRESHOLD", "0.6"))

# PII & Sensitive Data Redaction
ENABLE_PII_REDACTION = os.getenv("ENABLE_PII_REDACTION", "true").lower() in ("true", "1")
ENABLE_PRESIDIO_NER = os.getenv("ENABLE_PRESIDIO_NER", "false").lower() in ("true", "1")

# Document Ingestion Security
ENABLE_INGESTION_GUARD = os.getenv("ENABLE_INGESTION_GUARD", "true").lower() in ("true", "1")

# ── Per-Node Execution Timeouts (Seconds) ────────────────────────────────────
TIMEOUT_ROUTER = float(os.getenv("TIMEOUT_ROUTER", "3.5"))
TIMEOUT_RETRIEVAL = float(os.getenv("TIMEOUT_RETRIEVAL", "3.0"))
TIMEOUT_RETRIEVAL_EVAL = float(os.getenv("TIMEOUT_RETRIEVAL_EVAL", "4.0"))
TIMEOUT_WEB_SEARCH = float(os.getenv("TIMEOUT_WEB_SEARCH", "4.0"))
TIMEOUT_GENERATION = float(os.getenv("TIMEOUT_GENERATION", "10.0"))
TIMEOUT_GROUNDEDNESS = float(os.getenv("TIMEOUT_GROUNDEDNESS", "3.5"))

# ── Context Token Budget & Length Ceilings (Characters) ──────────────────────
MAX_DOC_CONTEXT_CHARS = int(os.getenv("MAX_DOC_CONTEXT_CHARS", "10000"))      # ~2,500 tokens
MAX_WEB_CONTEXT_CHARS = int(os.getenv("MAX_WEB_CONTEXT_CHARS", "5000"))       # ~1,250 tokens
MAX_WEB_SNIPPET_CHARS = int(os.getenv("MAX_WEB_SNIPPET_CHARS", "800"))        # ~200 tokens per snippet
MAX_HYBRID_DOC_CHARS = int(os.getenv("MAX_HYBRID_DOC_CHARS", "7000"))         # ~1,750 tokens
MAX_HYBRID_WEB_CHARS = int(os.getenv("MAX_HYBRID_WEB_CHARS", "3500"))         # ~875 tokens

# ── Conversation Memory & Summarization ────────────────────────────────────────
MAX_CONVERSATION_TOKENS = int(os.getenv("MAX_CONVERSATION_TOKENS", "4000"))  # Token budget for prior context
MAX_RECENT_MESSAGES = int(os.getenv("MAX_RECENT_MESSAGES", "2"))             # Keep last N messages verbatim
