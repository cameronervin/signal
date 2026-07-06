# Tech Debt Tracker

| Date | ID | Item | Impact | Plan |
| --- | --- | --- | --- | --- |
| 2026-07-05 | TD-001 | In-memory repository | Data resets on restart | Replace with SQLAlchemy/PostgreSQL after demo scaffold is stable |
| 2026-07-05 | TD-002 | Fixture enrichment | Public API behavior not live yet | Add cache-backed adapters in Phase 2 |
| 2026-07-05 | TD-003 | Static frontend fixtures | UI not wired to API yet | Add TanStack Query hooks and API adapters in Phase 3 |
| 2026-07-05 | TD-004 | Guarded autonomous loop dry run still needs workflow confirmation | Intake normalization, automatic review, CI-triggered fix passes, and loop artifacts are wired but need a low-risk end-to-end GitHub Actions run | Run the docs-only dry run in `backstage/development/agent-loop-board.md` before trusting broader automation |
