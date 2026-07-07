# Signal Local Infrastructure

This folder contains local infrastructure dependencies that are easiest to keep
in Docker Compose while running the app processes directly with `uv` and `pnpm`.

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

Edit `deploy/envs/.env.litellm.local` with a real upstream API key before using
LLM drafting. The tracked example routes the `signal-chat` alias to
`openai/gpt-5.4-mini`. Keep private env files out of git.

The env templates use grouped Signal sections for application, public data,
database, workers, scoring, LLM, and frontend settings. Backend settings use
the exact key names from `backend/.env`; `DATABASE_URL` intentionally does not
use a `SIGNAL_` prefix.

## Start Dependencies

```bash
docker compose \
  --env-file deploy/envs/.env.local \
  --env-file deploy/envs/.env.litellm.local \
  -f deploy/compose/base.yml \
  -f deploy/compose/local.yml \
  up -d postgres valkey neo4j litellm
```

This starts:

- Postgres on `localhost:5433`
- Valkey on `localhost:6379`
- Neo4j Browser on `localhost:7474`
- Neo4j Bolt on `localhost:7687`
- LiteLLM on `localhost:4000`

Use the `signal` Compose project name from `deploy/envs/.env.local`; do not
start a parallel project with an alternate project name.

LiteLLM uses its database-backed image for the local proxy. On a fresh Postgres
volume, the first boot can take several minutes while proxy migrations run.

Start the optional DB UI when needed:

```bash
docker compose \
  --env-file deploy/envs/.env.local \
  --env-file deploy/envs/.env.litellm.local \
  -f deploy/compose/base.yml \
  -f deploy/compose/local.yml \
  up -d cloudbeaver
```

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

The backend uses `bolt://localhost:7687` when running on the host. If a backend
container is added later, use `bolt://neo4j:7687` for container-to-container
Neo4j access.

If port `5050` is already in use, set `DB_UI_PORT` in
`deploy/envs/.env.local` before starting the service. To change the local
CloudBeaver admin password, set `DB_UI_ADMIN_PASSWORD`.

Stop the stack with:

```bash
docker compose \
  --env-file deploy/envs/.env.local \
  --env-file deploy/envs/.env.litellm.local \
  -f deploy/compose/base.yml \
  -f deploy/compose/local.yml \
  down
```

Reset local dependency data with:

```bash
docker compose \
  --env-file deploy/envs/.env.local \
  --env-file deploy/envs/.env.litellm.local \
  -f deploy/compose/base.yml \
  -f deploy/compose/local.yml \
  down -v
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

## Seed Sample Leads

With Postgres running, seed reproducible A/B/C, gate-failed, missing-trigger,
and warning-only records through the backend service path for local evaluation:

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run python scripts/seed_demo_leads.py
```
