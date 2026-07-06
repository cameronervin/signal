# Signal Build Loops

These are modern agentic loops for building the repo. They are not long-lived
autonomous processes. They are repeatable execution patterns for coding agents:

1. Load the smallest useful context pack.
2. State the slice and convergence criteria.
3. Implement in a narrow pass.
4. Verify with tests, lint, and targeted inspection.
5. Update docs and risk trackers.
6. Stop when acceptance criteria are met or a real blocker is reached.

Use one loop per task. If a task spans backend, frontend, and docs, still keep
the loop bounded by one user-visible outcome.

The shared contract lives in `_loop-contract.md`. Machine-readable defaults for
workflow timeouts, fix-pass budgets, risk gates, and per-loop policy live in
`manifest.yml`.
