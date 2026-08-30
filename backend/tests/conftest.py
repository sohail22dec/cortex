import os

# Set dummy fallback environment variables for pytest if not already provided
os.environ.setdefault("GROQ_API_KEY", "gsk_mockgroqkey1234567890abcdef1234567890abcdef")
os.environ.setdefault("TAVILY_API_KEY", "tvly-mocktavilykey1234567890")
os.environ.setdefault("SUPABASE_URL", "https://mockproject.supabase.co")
os.environ.setdefault("SUPABASE_KEY", "mock-supabase-service-key")
os.environ.setdefault("GEMINI_API_KEY", "mock-gemini-api-key")
os.environ.setdefault("ENABLE_RATE_LIMITING", "true")
os.environ.setdefault("ENABLE_PROMPT_GUARD", "true")
os.environ.setdefault("ENABLE_PII_REDACTION", "true")
os.environ.setdefault("ENABLE_INGESTION_GUARD", "true")
