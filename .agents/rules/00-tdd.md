# TDD Workflow

## When To Apply TDD

Use TDD for non-trivial Signal behavior:
- Backend services, repositories, API contracts, and async persistence.
- Scoring weights, tier thresholds, gates, and why-line behavior.
- LangGraph nodes, agent state transitions, draft suppression, and review gates.
- Frontend interactions with business rules, such as filtering, copy feedback, no-draft states, and approve/pause controls.

Skip strict TDD for docs-only changes, simple config edits, and mechanical refactors.

## Cycle

```text
RED -> write a failing test
GREEN -> implement the smallest passing change
REFACTOR -> clean up while tests stay green
```

## Commands

```bash
cd backend && uv run pytest -v
cd backend && uv run ruff check .
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend typecheck
```

## Guardrails

- Confirm the test fails for the intended reason before implementing.
- Keep fixtures deterministic and safe for demos.
- Do not alter score weights or tier thresholds without explicit approval.
- Docs follow behavior changes, not planned intent.
