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
uv run alembic upgrade head
uv run pytest -v
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend with the local Compose Postgres port:

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Seed deterministic demo data into the configured Postgres database:

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run python scripts/seed_demo_leads.py
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
overrides. Do not commit `.env` files. The env examples use grouped section
headers for application, public data, database, workers, scoring, LLM, and
frontend settings.

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

Scoring override:

```bash
SIGNAL_SCORING_CONFIG_PATH=/path/to/scoring.json
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
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
uv run celery -A app.workers.app:celery_app worker --loglevel=INFO

cd ../frontend
pnpm dev
```
