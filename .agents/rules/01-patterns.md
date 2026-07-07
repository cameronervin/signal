# Signal Patterns

## Backend Boundaries

```text
FastAPI route -> service -> repository -> model/database
                     |
                     -> agent executor/public data provider
```

## Do

- Keep routes thin: parse DTOs, call a service, return DTOs.
- Put business decisions in services, scoring config/helpers, or LangGraph nodes.
- Keep persistence behind repositories.
- Use Pydantic schemas for request and response contracts.
- Keep public API adapters behind `backend/app/infrastructure/public_data/` with cache or fixture fallback.
- Keep graph state explicit and bounded.

## Avoid

- Business logic in routes.
- Raw dict contracts across module boundaries.
- Client-controlled score, tier, gate, or draft fields.
- New abstractions without repeated complexity.
- Hidden assumptions when public data is missing; return flags instead.

## Decision Rule

- DB access: repository.
- Use-case orchestration: service.
- Agent workflow step: LangGraph node with typed state.
- External public source: adapter/provider with normalized source facts.
- UI behavior: feature component using existing primitives and typed fixtures/API client.
