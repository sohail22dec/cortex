import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GROQ_REASONING_MODEL = os.getenv("GROQ_REASONING_MODEL", os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"))
GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "qwen/qwen3.6-27b")

# Supabase (vector store + future auth & sessions)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Google Gemini (cloud embeddings — no local model, no RAM spikes)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
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


