# Tech Debt Tracker

| Date | ID | Item | Impact | Plan |
| --- | --- | --- | --- | --- |
| 2026-07-05 | TD-001 | In-memory repository | Data resets on restart | Replace with SQLAlchemy/PostgreSQL after demo scaffold is stable |
| 2026-07-05 | TD-002 | Fixture enrichment | Public API behavior not live yet | Add cache-backed adapters in Phase 2 |
| 2026-07-05 | TD-003 | Static frontend fixtures | UI not wired to API yet | Add TanStack Query hooks and API adapters in Phase 3 |
| 2026-07-05 | TD-004 | First Codex issue loop dry run still needs workflow confirmation | Branch preparation and `agent:working` happen before Codex; commit, PR creation, and `agent:reviewing` happen after Codex exits | Review issue `#2`, the generated PR, and the `Codex issue loop` run before enabling broader automation |
