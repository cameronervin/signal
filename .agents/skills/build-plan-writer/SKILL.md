# Build Plan Writer

Use only when explicitly requested or when a task needs a durable plan for later
agents.

## Output

Write plans under `backstage/build-plans/` or `.agents/plans/` with:

- Current state.
- Target state.
- Phases.
- Suggested files.
- Acceptance criteria.
- Tests.
- Non-goals.

Keep planned work separate from implemented behavior.
