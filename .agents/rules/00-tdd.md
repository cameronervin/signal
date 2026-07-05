# TDD Workflow

Use TDD for non-trivial behavior:

- New service logic.
- New API behavior.
- LangGraph node changes.
- Scoring and gating changes.
- Frontend interactions with business rules.

Skip TDD only for static docs, config, simple layout placeholders, and
mechanical dependency updates.

## Cycle

1. RED - write a focused failing test.
2. GREEN - implement the smallest change that passes.
3. REFACTOR - improve names, boundaries, and duplication while tests stay green.

## Signal-Specific Checks

- Hard-gate-failed leads never expose a draft.
- Score, tier, and why-line are computed server-side.
- Public API failures fall back to cache or fixtures.
- Human review is required before any send-like action.
