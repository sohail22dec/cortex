import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
QDRANT_PATH = os.getenv("QDRANT_PATH", "./qdrant_data")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Chunking config
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval config
TOP_K_RESULTS = 5
