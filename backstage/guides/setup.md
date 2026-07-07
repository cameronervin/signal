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

Optional Postgres-backed backend:

```bash
cd backend
SIGNAL_REPOSITORY_BACKEND=postgres \
SIGNAL_DATABASE_URL=postgresql+asyncpg://signal:signal@localhost:5433/signal \
SIGNAL_CREATE_DB_SCHEMA_ON_STARTUP=true \
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Optional Celery worker for agent execution:

```bash
cd backend
uv run celery -A app.workers.app:celery_app worker --loglevel=INFO
```

## Frontend

```bash
cd frontend
pnpm install
pnpm typecheck
pnpm dev
```

## Environment

Copy `backend/.env.example` to `backend/.env` only when you need local backend
overrides. Do not commit `.env` files.

Default mode uses fixtures:

```bash
SIGNAL_USE_FIXTURES=true
```

Live public API adapters:

```bash
SIGNAL_USE_FIXTURES=false
SIGNAL_PUBLIC_DATA_USER_AGENT="Signal API local demo"
SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS=3600
SIGNAL_CENSUS_API_KEY=optional
SIGNAL_FRED_API_KEY=optional
SIGNAL_NEWS_API_KEY=optional
SIGNAL_NOMINATIM_EMAIL=optional-contact@example.com
```

LiteLLM settings:

```bash
SIGNAL_LITELLM_API_BASE=http://localhost:4000
SIGNAL_LITELLM_API_KEY=optional-local-key
SIGNAL_LLM_MODEL=signal-chat
```

## Demo Dependencies

Signal's demo dependency stack lives under `deploy/`, following the smaller
version of the playbook structure:

```text
deploy/compose/   Docker Compose files
deploy/envs/      Local env templates
deploy/litellm/   LiteLLM proxy config
```

Start Postgres, Valkey, and LiteLLM:

```bash
cp deploy/envs/.env.local.example deploy/envs/.env.local
cp deploy/envs/.env.litellm.local.example deploy/envs/.env.litellm.local
cp backend/.env.example backend/.env
make compose-up
```

LiteLLM uses its database-backed image for the local proxy. On a fresh Postgres
volume, the first boot can take several minutes while proxy migrations run.

Run the application processes directly while Compose provides dependencies:

```bash
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
uv run celery -A app.workers.app:celery_app worker --loglevel=INFO

cd ../frontend
pnpm dev
```
