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

Default mode uses fixtures:

```bash
SIGNAL_USE_FIXTURES=true
```

Live public API adapters can read optional keys from the environment when they
are implemented.
