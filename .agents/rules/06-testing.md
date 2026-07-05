# Testing Rules

## Backend

```text
backend/tests/
  test_health.py
  test_lead_pipeline.py
```

Use pytest. Mock live public APIs. Fixture-backed graph tests should verify:

- Gate pass and gate fail paths.
- Score and tier cutoffs.
- Draft suppressed for failed gates.
- Pipeline outputs include why-line and citations.

## Frontend

Use Vitest and React Testing Library. Test behavior:

- Queue renders tier ordering.
- Copy draft button is hidden or disabled for gate-failed leads.
- Detail pages show flags and review state.

## Verification

```bash
cd backend && uv run pytest -v
cd frontend && pnpm test
```
