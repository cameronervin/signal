# Signal Backend

FastAPI backend for triggered inbound lead enrichment.

## Run

```bash
uv sync --group dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Local Postgres dependency from Compose runs on `localhost:5433`:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Seed deterministic demo leads into Postgres:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run python scripts/seed_demo_leads.py
```

Celery worker entrypoint for agent execution:

```bash
uv run celery -A app.workers.app.celery_app worker --loglevel=INFO
```

## Test

```bash
uv run pytest -v
uv run ruff check .
```

## Shape

```text
app/api/v1             thin route handlers
app/services           product orchestration
app/repositories       Postgres persistence boundary
app/models             SQLAlchemy records for Postgres-backed DTO snapshots
app/agents/builders    chain/node/graph composition and compilation
app/agents/chains      outreach drafting workflow units
app/agents/guardrails  lead qualification gates for draft and scoring safety
app/agents/states      LangGraph state schemas
app/agents/nodes       lead intelligence graph node factories
app/agents/graphs      lead intelligence topology builders
app/agents/executors   inline/worker-facing graph execution
app/agents/tools       deterministic tool wrappers
app/agents/utils       pure scoring/talking-point/text helpers
app/infrastructure/db  SQLAlchemy async engine/session setup
app/infrastructure/llm LiteLLM provider boundary
app/infrastructure/public_data live public API adapters and fixture fallback
app/workers            Celery app and agent task entrypoints
app/schemas            Pydantic contracts
```

## Public Data

Default development uses fixture enrichment:

```bash
SIGNAL_USE_FIXTURES=true
```

Live adapters:

```bash
SIGNAL_USE_FIXTURES=false
SIGNAL_PUBLIC_DATA_USER_AGENT="Signal API local demo"
SIGNAL_CENSUS_API_KEY=optional
SIGNAL_FRED_API_KEY=optional
SIGNAL_NEWS_API_KEY=optional
SIGNAL_NOMINATIM_EMAIL=optional-contact@example.com
```

Scoring defaults are built in. To test a local scoring override, set:

```bash
SIGNAL_SCORING_CONFIG_PATH=/path/to/scoring.json
```
