# Signal

Signal is an SDR-facing inbound lead intelligence tool. It accepts new lead
records, enriches them with public data, scores and explains the opportunity,
builds related-lead context, and prepares cited outreach drafts for human
review.

The first build is intentionally demo-safe:

- FastAPI backend with a trigger endpoint for inserted leads.
- LangGraph pipeline with deterministic enrichment, agent scoring and drafting,
  and lightweight graph context.
- Next.js App Router frontend for the SDR queue, lead detail, and agent runs.
- Config-driven scoring so assumptions can be tuned without rewriting code.
- Fixture-backed public API adapters so demos can run without live API risk.

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js App Router, TypeScript, Tailwind CSS v4, TanStack Query, Zustand |
| Backend | FastAPI, Pydantic v2, LangGraph, httpx, structlog |
| Data v1 | In-memory repository with typed fixtures, ready to swap for SQLAlchemy |
| Tests | pytest for backend, Vitest and React Testing Library for frontend |

## Repository Map

```text
backend/      FastAPI API, LangGraph pipeline, public API adapters, tests
frontend/     Next.js SDR workspace and typed fixture adapters
backstage/    Product specs, architecture, API docs, setup guides, decisions
AGENTS.md     Primary instructions for coding agents working in this repo
```

## Quick Start

```bash
# Backend
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd frontend
pnpm install
pnpm dev
```

Backend API docs: `http://127.0.0.1:8000/docs`

Frontend app: `http://localhost:3000`

## Development Flow

1. Read `AGENTS.md`.
2. Read the relevant files in `backstage/prd/` and `backstage/architecture/`.
3. Implement in small, tested slices.
4. Update docs after behavior changes.
5. Run the relevant backend and frontend verification commands.

The repo should not contain third-party brand references. Keep product copy and
documentation centered on Signal.
