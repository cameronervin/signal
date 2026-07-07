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

Seed deterministic sample data into the configured Postgres database:

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
overrides. Do not commit `.env` files. `backend/.env` is the backend source of
truth for supported key names; `DATABASE_URL` intentionally has no `SIGNAL_`
prefix.

Public API adapters:

```bash
SIGNAL_PUBLIC_DATA_USER_AGENT="Signal"
SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS=3600
SIGNAL_CENSUS_API_KEY=optional
SIGNAL_FRED_API_KEY=optional
SIGNAL_NEWS_API_KEY=optional
SIGNAL_NOMINATIM_EMAIL=optional-contact@example.com
```

Agent research tools:

```bash
SIGNAL_AGENT_RESEARCH_TOOLS_ENABLED=true
SIGNAL_AGENT_RESEARCH_MAX_TOOL_ROUNDS=3
```

LiteLLM settings:

```bash
SIGNAL_LITELLM_API_BASE=http://localhost:4000
SIGNAL_LITELLM_API_KEY=optional-local-key
SIGNAL_LLM_MODEL=signal-chat
```

The LiteLLM proxy maps `signal-chat` to the upstream model configured in
`deploy/envs/.env.litellm.local`; the tracked example uses
`openai/gpt-5.4-mini`.

Scoring override:

```bash
SIGNAL_SCORING_CONFIG_PATH=/path/to/scoring.json
```

## Local Infrastructure

Signal's local dependency stack lives under `deploy/`, following the smaller
version of the playbook structure:

```text
deploy/compose/   Docker Compose files
deploy/envs/      Local env templates
deploy/litellm/   LiteLLM proxy config
```

Start Postgres, the DB UI, Valkey, and LiteLLM:

```bash
cp deploy/envs/.env.local.example deploy/envs/.env.local
cp deploy/envs/.env.litellm.local.example deploy/envs/.env.litellm.local
cp backend/.env.example backend/.env
make compose-up
```

This exposes local infrastructure on:

| Component | Local host port |
| --- | --- |
| Postgres | `5433` |
| CloudBeaver DB UI | `5050` |
| Valkey | `6379` |
| LiteLLM | `4000` |

Open the DB UI at `http://localhost:5050` and log in with:

```text
Username: signal
Password: signal-local-db-ui
```

Create a PostgreSQL connection through Signal's host-facing Postgres port:

```text
Host: host.docker.internal
Port: 5433
Database: signal
Username: postgres
Password: postgres
```

Compose services still use `postgres:5432` internally because `5432` is the
Postgres container port. The local developer-facing port is `localhost:5433`.

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
