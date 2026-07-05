# Python Rules

## Backend Shape

```text
backend/app/api/v1       FastAPI routers
backend/app/services     orchestration
backend/app/repositories persistence boundary
backend/app/agents       LangGraph pipeline
backend/app/integrations public API adapters
backend/app/schemas      Pydantic contracts
```

## Do

- Use Python 3.12 typing.
- Use async functions for IO.
- Use `httpx.AsyncClient` for live public API calls.
- Validate input with Pydantic.
- Return DTOs, not ORM or repository internals.
- Use dependency injection for services and settings.

## Do Not

- Block the event loop with `requests` or `time.sleep`.
- Return raw dicts from route handlers.
- Log full email addresses, prompt payloads, draft bodies, or API responses.
- Hardcode model names, API keys, or scoring thresholds in service code.
