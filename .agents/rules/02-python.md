# Python Rules

Signal uses Python 3.12, FastAPI, Pydantic v2, SQLAlchemy async, LangGraph, Celery, and uv.

## Layers

```text
backend/app/api/v1/        Thin routers
backend/app/services/      Product orchestration
backend/app/repositories/  Persistence boundary
backend/app/agents/        LangGraph state, nodes, graphs, executors
backend/app/infrastructure/Public data, DB, LLM boundaries
backend/app/schemas/       Pydantic request/response DTOs
```

## Do

- Type public functions and methods.
- Prefer async SQLAlchemy `select()` and explicit session boundaries.
- Return DTOs or domain values from services, not ORM objects.
- Use dependency injection where the app already does.
- Keep provider payloads normalized to `SourceFact`-style records before business logic consumes them.
- Keep deterministic fallback paths for demos.

## Avoid

- Blocking I/O in async routes or services.
- Logging raw request bodies, full emails, drafts, prompts, provider payloads, or secrets.
- Hardcoded score/tier logic outside scoring config or helpers.
- Raising HTTP exceptions from deep service/repository layers unless the local pattern already does.

## Verification

```bash
cd backend && uv run pytest -v
cd backend && uv run ruff check .
```
