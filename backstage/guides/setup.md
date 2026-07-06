# Setup Guide

## Prerequisites

- Python 3.12.
- uv.
- Node.js 20 or newer.
- pnpm 10 or newer.

## Backend

```bash
cd backend
uv sync --group dev
uv run pytest -v
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```bash
cd frontend
pnpm install
pnpm typecheck
pnpm dev
```

## Environment

Copy `.env.example` to `.env` only for local use. Do not commit `.env`.

Default mode uses fixtures and explicit local origins:

```bash
SIGNAL_USE_FIXTURES=true
SIGNAL_API_BASE_URL=http://127.0.0.1:8000
SIGNAL_FRONTEND_ORIGIN=http://localhost:3000
SIGNAL_EXTRA_CORS_ORIGINS=http://127.0.0.1:3000
```

Live public API adapters can read optional keys from the environment when they
are implemented. Keep these blank unless you are testing a live adapter:

```bash
SIGNAL_NEWS_API_KEY=
SIGNAL_FRED_API_KEY=
SIGNAL_OPENAI_API_KEY=
SIGNAL_LITELLM_GATEWAY_URL=
SIGNAL_LITELLM_GATEWAY_KEY=
SIGNAL_LLM_MODEL=
```

Backend retry and timeout defaults are intentionally bounded for demo safety:

```bash
SIGNAL_MAX_AGENT_RETRIES=2
SIGNAL_PROVIDER_RETRY_COUNT=2
SIGNAL_PROVIDER_TIMEOUT_SECONDS=8
SIGNAL_REQUEST_TIMEOUT_SECONDS=15
```
