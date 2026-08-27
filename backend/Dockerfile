# syntax=docker/dockerfile:1
# ── Stage 1: Build virtual environment with uv ──────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies for C-extensions (e.g. PyMuPDF, fitz)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution and virtual environment creation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install project dependencies into /app/.venv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
RUN uv sync --frozen --no-install-project --no-dev

# ── Stage 2: Minimal Runtime Image ──────────────────────────────────────────
FROM python:3.12-slim AS runner

WORKDIR /app

# Install minimal runtime libraries needed by PDF / document parsers
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libmupdf-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r cortex && useradd -r -g cortex -m -d /home/cortexuser cortexuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY --chown=cortexuser:cortex . /app

# Switch to non-root user
USER cortexuser

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1

# Start Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
