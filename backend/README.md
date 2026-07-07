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

Seed example leads into Postgres for local evaluation:

```bash
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run alembic upgrade head
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/signal \
uv run python scripts/seed_demo_leads.py
```

Celery worker entrypoint for agent execution:

```bash
uv run celery -A app.workers.app:celery_app worker --loglevel=INFO
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
app/services/knowledge_graph deterministic graph projection and relation rules
app/repositories       Postgres persistence boundary
app/models             SQLAlchemy records for Postgres-backed DTO snapshots
app/agents/builders    chain/node/graph composition and compilation
app/agents/chains      outreach drafting workflow units
app/agents/guardrails  lead qualification gates for draft and scoring safety
app/agents/states      LangGraph state schemas
app/agents/nodes       lead intelligence graph node factories
app/agents/graphs      lead intelligence topology builders
app/agents/executors   inline/worker-facing graph execution
app/agents/tools       public-data tool wrappers
app/agents/utils       pure scoring/talking-point/text helpers
app/infrastructure/db  SQLAlchemy async engine/session setup
app/infrastructure/knowledge_graph Neo4j and disabled graph repositories
app/infrastructure/llm LiteLLM provider boundary
app/infrastructure/public_data live public API adapters and cache boundary
app/workers            Celery app and agent task entrypoints
app/schemas            Pydantic contracts
```

## Public Data

Public data adapters use live provider code paths. Tests mock the HTTP
transport and seed tooling injects sample data explicitly.

```bash
SIGNAL_PUBLIC_DATA_USER_AGENT="Signal"
SIGNAL_CENSUS_API_KEY=optional
SIGNAL_FRED_API_KEY=optional
SIGNAL_NEWS_API_KEY=optional
SIGNAL_NOMINATIM_EMAIL=optional-contact@example.com
```

## LiteLLM

Backend drafting calls the LiteLLM proxy alias configured by
`SIGNAL_LLM_MODEL`. The default alias is `signal-chat`, with the proxy
configured from `deploy/envs/.env.litellm.local`.

```bash
SIGNAL_LLM_MODEL=signal-chat
SIGNAL_LITELLM_API_BASE=http://localhost:4000
SIGNAL_LITELLM_API_KEY=sk-local-litellm-master-key
```

Scoring defaults are built in. To test a local scoring override, set:

```bash
SIGNAL_SCORING_CONFIG_PATH=/path/to/scoring.json
```

## Knowledge Graph

Neo4j-backed graph storage is optional. Disabled mode still returns a
current-lead graph projection with explicit graph warnings.

```bash
SIGNAL_KNOWLEDGE_GRAPH_ENABLED=false
SIGNAL_NEO4J_URI=bolt://localhost:7687
SIGNAL_NEO4J_USER=neo4j
SIGNAL_NEO4J_PASSWORD=signal-local-neo4j
SIGNAL_NEO4J_DATABASE=neo4j
```
