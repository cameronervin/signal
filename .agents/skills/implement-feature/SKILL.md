# Implement Feature

Implement a Signal feature with a bounded build loop.

## Workflow

1. Read `AGENTS.md` and relevant docs.
2. State acceptance criteria.
3. Write failing tests first for non-trivial behavior.
4. Implement through existing layers.
5. Verify targeted and broad checks.
6. Update docs.

## Signal Checks

- Does the change affect who-first, what-to-say, or urgency?
- Are gate failures handled explicitly?
- Is scoring explainable and config-driven?
- Are public API failures cached or fixture-safe?
- Is human review preserved?
