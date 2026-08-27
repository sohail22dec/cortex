# Cortex — AI Agent Project Guide

This file is a concise reference for AI coding agents working on **Cortex**, a multi-agent Retrieval-Augmented Generation (RAG) application. It covers the project architecture, technology stack, code organization, build/test commands, development conventions, and security considerations.

---

## Project Overview

Cortex is a full-stack AI assistant that routes user questions across three execution paths:

1. **Document RAG** — answers from uploaded PDF, DOCX, TXT, and Markdown files.
2. **Real-time Web Search** — fetches live information from the web.
3. **Direct LLM Knowledge** — answers general knowledge, coding, and math questions without retrieval.

The backend is implemented in Python with **FastAPI** and **LangGraph**, and the frontend is a **Next.js 16 / React 19** chat UI. The system emphasizes:

- **Corrective RAG (CRAG)** — retrieval evaluation, query rewriting, and web fallback.
- **Multi-layer guardrails** — prompt injection defense, PII redaction, ingestion validation, output scrubbing, and citation verification.
- **Groundedness checking** — an independent LLM judge detects hallucinations and triggers strict retries.
- **Cloud-native embeddings** — Google Gemini `text-embedding-004` truncated to 768 dimensions via MRL, stored in Supabase `pgvector`.

---

## Repository Layout

```
Cortex/
├── backend/                 # FastAPI + LangGraph Python service
│   ├── api/                 # FastAPI routers (chat, documents)
│   ├── crag/                # Corrective RAG graph, nodes, edges, state
│   ├── guardrails/          # Rate limiting, prompt guard, PII redaction, ingestion guard, output guard
│   ├── rag/                 # Document parsing, embeddings, Supabase vector store
│   ├── services/            # LLM business logic (router, generator, search, groundedness judge, evaluator)
│   ├── evals/               # Evaluation framework (dataset, evaluator, runner, report)
│   ├── tests/               # Backend unit and integration tests
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment-driven configuration
│   ├── pyproject.toml       # Python project metadata and dependencies
│   ├── requirements.txt     # Plain-text dependency mirror
│   └── langgraph.json       # LangGraph CLI graph registration
├── frontend/                # Next.js 16 (App Router) chat UI
│   ├── app/                 # App Router pages and components
│   ├── package.json         # NPM dependencies and scripts
│   ├── pnpm-lock.yaml       # pnpm lockfile
│   ├── pnpm-workspace.yaml  # pnpm workspace config
│   ├── next.config.ts       # Next.js config
│   ├── tsconfig.json        # TypeScript config
│   ├── eslint.config.mjs    # ESLint config (Next.js core-web-vitals + typescript)
│   └── postcss.config.mjs   # PostCSS config for Tailwind v4
└── AGENTS.md                # This file
```

---

## Technology Stack

### Backend

| Layer | Technology |
|---|---|
| Runtime | Python 3.12+ |
| Web Framework | FastAPI + Uvicorn |
| Agent Orchestration | LangGraph + LangChain |
| LLMs | Groq (`ChatGroq`) — reasoning and fast models |
| Embeddings | Google Gemini `embedding-001` (768-dim via MRL) |
| Vector Store | Supabase `pgvector` (via `match_document_chunks` RPC) |
| Web Search | Tavily API |
| Document Parsing | PyMuPDF, python-docx, docx2txt, LangChain text splitters |
| Evaluation | Custom LLM-as-a-judge metrics + RAGAS (optional) |
| Package Manager | `uv` (lockfile: `backend/uv.lock`) |

### Frontend

| Layer | Technology |
|---|---|
| Framework | Next.js 16.2.6 (App Router) |
| UI Library | React 19.2.4 |
| Styling | Tailwind CSS v4 (`@tailwindcss/postcss`) |
| Icons | Inline SVGs |
| Package Manager | `pnpm` |
| Linting | ESLint 9 with `eslint-config-next` |

---

## Code Organization

### Backend Modules

- **`api/chat.py`** — `/api/chat` endpoint. Applies guardrails, runs the CRAG workflow, and scrubs/verifies the output.
- **`api/documents.py`** — `/api/documents/upload`, `/api/documents`, and `/api/documents/{filename}` endpoints. Validates file magic, parses documents, and indexes chunks.
- **`crag/`** — The CRAG workflow:
  - `state.py` — `CRAGState` typed dictionary.
  - `nodes.py` — LangGraph node functions (router, retrieve, evaluate, web search, generate, groundedness judge, direct web search).
  - `edges.py` — Conditional routing with strict loop bounds.
  - `graph.py` — Compiles the `StateGraph` and exposes `run_crag_async()` / `run_crag()`.
- **`guardrails/`** — Security and reliability controls:
  - `prompt_guard.py` — Prompt injection/jailbreak detection (heuristics + optional local Hugging Face model).
  - `pii_redactor.py` — Regex-based PII/secrets redaction with optional Microsoft Presidio NER.
  - `ingestion_guard.py` — File magic-byte validation, text sanitization, indirect prompt injection scanning.
  - `output_guard.py` — Output scrubbing for secrets/system delimiters and citation verification.
  - `rate_limiter.py` — In-memory sliding-window rate limiter.
- **`rag/`** — Document processing and retrieval:
  - `document_processor.py` — Parses files, sanitizes text, redacts PII, chunks, and indexes.
  - `embeddings.py` — Gemini embedding clients for documents and queries.
  - `vector_store.py` — Supabase `document_chunks` table operations.
- **`services/`** — Pure domain services used by CRAG nodes:
  - `router_service.py` — Route classifier with structured outputs.
  - `evaluator_service.py` — Retrieval evaluator with bundled query rewriting.
  - `search_service.py` — Tavily search and query rewriting.
  - `generator_service.py` — RAG, web, and hybrid answer generation with context budgets.
  - `groundedness_service.py` — Independent groundedness judge.
  - `llm_service.py` — Direct LLM fallback.
- **`evals/`** — Evaluation framework:
  - `dataset.py` — `EvalSample` dataclass and curated benchmark dataset.
  - `evaluator.py` — Faithfulness, relevance, guardrail safety, and route accuracy metrics.
  - `runner.py` — CLI and programmatic benchmark runner.
  - `report.py` — Markdown and CSV report generation.

### Frontend Structure

- **`app/page.tsx`** — Main chat page. Manages sessions, messages, document state, and backend communication.
- **`app/layout.tsx`** — Root layout with metadata and font preconnects.
- **`app/globals.css`** — Tailwind v4 theme, custom color tokens, animations, and utility classes.
- **`app/components/`** — React components:
  - `ChatInput.tsx` — Auto-resizing textarea with send/attach controls.
  - `ChatMessage.tsx` — Renders assistant messages with source badges and citations.
  - `Sidebar.tsx` — Chat history, new chat, and global knowledge base UI.
  - `DocumentUpload.tsx` / `DocumentList.tsx` — Upload and delete documents.
  - `SourceBadge.tsx` — Displays answer source (RAG, LLM, web, hybrid).

---

## Configuration

Backend configuration is environment-driven via `backend/.env`. Copy `backend/.env.example` to `backend/.env` and fill in the values.

Required keys:

```bash
GROQ_API_KEY=...                    # Groq API key
TAVILY_API_KEY=...                  # Tavily web search API key
SUPABASE_URL=...                    # Supabase project URL
SUPABASE_KEY=...                    # Supabase service role key
GEMINI_API_KEY=...                  # Google Gemini API key
```

Optional behavior toggles (all in `backend/config.py`):

```bash
GROQ_REASONING_MODEL=qwen/qwen3.6-27b      # Main synthesis model
GROQ_FAST_MODEL=openai/gpt-oss-20b           # Router/evaluator/judge model
ENABLE_RATE_LIMITING=true
ENABLE_PROMPT_GUARD=true
ENABLE_PII_REDACTION=true
ENABLE_INGESTION_GUARD=true
ENABLE_LANGSMITH=false
LANGCHAIN_API_KEY=...                        # Only needed if LangSmith tracing enabled
LANGCHAIN_PROJECT=cortex
```

Frontend environment variable (in `frontend/.env.local`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Build and Run Commands

### Backend

The backend uses `uv` for dependency management and a local virtual environment at `backend/.venv`.

```bash
# Run the FastAPI dev server (reload on http://localhost:8000)
cd backend
uv run python main.py

# Or directly with the venv
backend/.venv/bin/python main.py

# Install/sync dependencies (if needed)
cd backend
uv sync
```

### Frontend

```bash
# Install dependencies
cd frontend
pnpm install

# Start the dev server (http://localhost:3000)
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start

# Lint
pnpm lint
```

### LangGraph CLI

The CRAG graph is registered in `backend/langgraph.json`:

```bash
cd backend
langgraph dev
```

### Docker & Docker Compose

Run the full stack containerized:

```bash
# Build and run backend & frontend containers
docker compose up --build -d

# View service logs
docker compose logs -f

# Shut down containers
docker compose down
```


---

## Testing

### Backend Tests

Backend tests use `pytest` with the `asyncio_mode = auto` setting configured in `pyproject.toml`. Some tests also use the standard `unittest` module.

```bash
cd backend
uv run pytest tests/ -q

# Or with the venv directly
backend/.venv/bin/python -m pytest tests/ -q
```

Test files:

- `tests/test_guardrails.py` — Rate limiting, prompt guard, PII redaction, ingestion guard.
- `tests/test_api_guardrails.py` — FastAPI `TestClient` tests for health, chat blocking, and upload validation.
- `tests/test_context_budget.py` — Context budget capping and web-result cleaning.
- `tests/test_crag_reliability.py` — CRAG routing, loop bounds, and node timeout fallbacks.
- `tests/test_eval_framework.py` — Evaluation dataset serialization and guardrail scoring.

### Evaluation Benchmark

Run the end-to-end evaluation suite from the backend root:

```bash
cd backend
uv run python -m evals.runner

# Custom dataset, category filter, or sample limit
uv run python -m evals.runner --dataset path/to/dataset.json --category fact_retrieval --samples 5
```

Reports are written to `backend/evals/reports/` as Markdown and CSV.

### Frontend Tests

There are currently no automated frontend tests in the repository. Manual verification is done by running `pnpm dev` and exercising the chat/document flows.

---

## Code Style and Conventions

### Python

- Use `from __future__ import annotations` at the top of files.
- Prefer `async`/`await` for I/O-bound work; wrap blocking calls with `asyncio.to_thread`.
- Use Pydantic `BaseModel` for structured LLM outputs.
- Keep business logic in `services/` and orchestration in `crag/`; routers in `api/` should be thin.
- All timeout values are centralized in `config.py` and applied per-node via `asyncio.wait_for`.
- Use module-level singletons for LLM clients and vector store clients (lazy initialization where possible).
- Guardrails are organized as classes with static/global helper functions.

### TypeScript / Frontend

- The project uses Next.js App Router with client components (`"use client"`) for interactive UI.
- Tailwind v4 theme tokens are defined in `app/globals.css` using `@theme`.
- Inline SVGs are used instead of icon libraries.
- `localStorage` is used for persistent session and user-id state on the client.

### As of this writing, the frontend has known lint issues

Running `pnpm lint` in `frontend/` currently reports several ESLint errors/warnings in `app/page.tsx`, including:

- `react-hooks/set-state-in-effect` — avoid calling `setState` directly inside `useEffect`.
- `react-hooks/exhaustive-deps` — missing memoization for derived values used as effect dependencies.
- `prefer-const` — `let activeIdx` is never reassigned.

These warnings/errors should be addressed when modifying `app/page.tsx`.

---

## CRAG Workflow Summary

1. **Router** classifies the user question into `rag`, `web_search`, `direct_answer`, or `unsafe`.
2. **Retrieve** fetches the top-k document chunks from Supabase.
3. **Retrieval Evaluator** classifies chunks as `CORRECT`, `INCORRECT`, or `AMBIGUOUS`, and rewrites queries.
4. If `INCORRECT`, the pipeline retries retrieval once, then falls back to **web search**.
5. If `AMBIGUOUS`, it proceeds to a **hybrid** answer using both documents and web results.
6. **Generate** produces an answer with strict context budgets.
7. **Groundedness Judge** verifies the answer is supported by the retrieved context.
8. If ungrounded, the pipeline retries once with a stricter prompt, then falls back to a safe refusal.

Loop bounds are hard-coded in `crag/edges.py` to prevent infinite cycles.

---

## Security Considerations

- **API keys and secrets** live only in `backend/.env` and `frontend/.env.local`. These files are gitignored. Never commit them.
- **Prompt injection** is blocked by regex heuristics and an optional local Hugging Face classifier.
- **PII redaction** masks emails, phones, SSNs, IP addresses, credit cards, and common API keys before indexing and before sending queries to downstream services.
- **File upload validation** checks magic bytes, rejects executable payloads, and validates file-extension/header consistency.
- **Indirect prompt injection** in uploaded documents is scanned and quarantined at chunk level.
- **Output guardrails** scrub leaked secrets/system delimiters and verify citations against real sources.
- **Rate limiting** is applied per client IP + session ID on chat and upload endpoints using a sliding-window limiter.
- **CORS** in `main.py` is restricted to `localhost:3000` and the production Vercel deployment URL.

---

## Deployment

- **Frontend**: Designed for Vercel. The production URL is already configured in backend CORS (`https://cortex-lime-zeta.vercel.app`).
- **Backend**: Can be deployed as a container or via a Python process manager. Exposes Uvicorn on port `8000` by default. Ensure all required environment variables are set in the target environment.
- **Supabase**: Requires a `document_chunks` table with a `pgvector` column and the `match_document_chunks` RPC function.
- **LangGraph CLI**: The graph is registered in `langgraph.json` for LangGraph Platform deployments.

---

## Useful Files to Know

- `backend/main.py` — FastAPI app and middleware.
- `backend/config.py` — Central configuration.
- `backend/crag/graph.py` — CRAG workflow compiler and public runner.
- `backend/crag/edges.py` — Workflow routing and loop bounds.
- `backend/guardrails/__init__.py` — Public guardrail API surface.
- `backend/services/__init__.py` — Public service API surface.
- `frontend/app/page.tsx` — Main application page.
- `frontend/app/globals.css` — Design tokens and theme.
- `frontend/package.json` — Scripts and dependencies.

---

## Getting Started (Minimal)

1. Install backend dependencies:
   ```bash
   cd backend
   uv sync
   ```
2. Create `backend/.env` from `backend/.env.example` and fill in API keys.
3. Start the backend:
   ```bash
   uv run python main.py
   ```
4. In a new terminal, install and run the frontend:
   ```bash
   cd frontend
   pnpm install
   pnpm dev
   ```
5. Open `http://localhost:3000`.
