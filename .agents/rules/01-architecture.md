# Architecture Rules

## Layers

```text
Route -> Service -> Repository
               -> Agent graph
               -> Integration adapter
```

## Do

- Keep FastAPI routes thin.
- Put orchestration in services.
- Keep repositories focused on persistence.
- Keep public API calls behind integration adapters.
- Keep LangGraph nodes small and state-shaped.
- Use Pydantic models for every request and response boundary.

## Do Not

- Put scoring logic in routes or React components.
- Let frontend fixture values become trusted backend outcomes.
- Add a graph database for v1 unless the product scope changes.
- Create abstractions without at least two concrete call sites or a real test
  benefit.

## Decision Rule

If a change affects trigger semantics, scoring weights, contact data retention,
or outreach delivery, create an ADR under `backstage/architecture/decisions/`.
