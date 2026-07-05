# Bugfix Loop

## Context Pack

Read:

- `AGENTS.md`
- The failing test, error output, or reproduction path.
- Related service, graph node, or component.

## Loop

1. Generate 3-5 hypotheses.
2. Pick the cheapest diagnostic.
3. Add a failing test or targeted assertion.
4. Implement the smallest fix.
5. Verify the original failure and nearby regression paths.
6. Remove temporary instrumentation.
7. Update `backstage/development/bug-log.md`.

## Convergence

Stop when the failure is reproduced, fixed, and protected by a test or explicit
manual verification note.
