# Testing Rules

## Backend

Signal backend tests use pytest.

```text
backend/tests/
```

Do:
- Use async tests for async services/repositories.
- Mock or fixture external public APIs.
- Cover gate-failed no-draft behavior.
- Cover scoring/tier/why-line changes with deterministic expectations.
- Cover invalid run state transitions with clear errors.

Commands:

```bash
cd backend && uv run pytest -v
cd backend && uv run ruff check .
```

## Frontend

Signal frontend tests use Jest and Testing Library.

Do:
- Test behavior through accessible roles, labels, and visible text.
- Use `@testing-library/user-event` for interactions.
- Mock the API client or use typed fixtures.
- Cover loading, error, empty, gate-failed, and awaiting-review states when the behavior changes.

Commands:

```bash
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend typecheck
```

## Test Data

- Keep demo fixtures neutral and free of third-party company names.
- Do not include real emails, real leads, secrets, or raw provider payloads.
