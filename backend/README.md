# Signal Backend

FastAPI backend for triggered inbound lead enrichment.

## Run

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Test

```bash
uv run pytest -v
uv run ruff check .
```

## Shape

```text
app/api/v1       thin route handlers
app/services     product orchestration
app/repositories in-memory persistence boundary for v1
app/agents       LangGraph state, nodes, scoring, fixtures
app/integrations public API adapter boundaries
app/schemas      Pydantic contracts
```
