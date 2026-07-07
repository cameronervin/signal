# Signal Demo Compose

This folder contains the local demo dependencies that are easiest to keep in
Docker Compose while running the app processes directly with `uv` and `pnpm`.

It mirrors the playbook deploy layout at a smaller scale:

```text
deploy/
  compose/   Compose base and local overrides
  envs/      Local env templates for dependency containers
  litellm/   LiteLLM proxy config
```

## First Run

```bash
cp deploy/envs/.env.local.example deploy/envs/.env.local
cp deploy/envs/.env.litellm.local.example deploy/envs/.env.litellm.local
cp backend/.env.example backend/.env
```

Edit `deploy/envs/.env.litellm.local` with a real upstream model and API key
before using live LLM drafting. Keep private env files out of git.

The env templates use grouped Signal sections for application, public data,
database, workers, scoring, LLM, and frontend settings. Keep the `SIGNAL_`
prefix for backend settings; the backend config loader depends on it.

## Start Dependencies

```bash
make compose-up
```

This starts:

- Postgres on `localhost:5433`
- Valkey on `localhost:6379`
- LiteLLM on `localhost:4000`

LiteLLM uses its database-backed image for the local proxy. On a fresh Postgres
volume, the first boot can take several minutes while proxy migrations run.

Stop the stack with:

```bash
make compose-down
```

Reset local dependency data with:

```bash
make compose-reset
```

## Run App Processes On Host

Backend:

```bash
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Celery worker:

```bash
cd backend
uv run celery -A app.workers.app:celery_app worker --loglevel=info
```

Frontend:

```bash
cd frontend
pnpm install
pnpm dev
```

## Seed Demo Leads

With Postgres running, seed deterministic A/B/C, gate-failed, missing-trigger,
and warning-only records through the backend service path:

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run python scripts/seed_demo_leads.py
```
