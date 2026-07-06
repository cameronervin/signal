# Tech Debt Tracker

| Date | ID | Item | Impact | Plan |
| --- | --- | --- | --- | --- |
| 2026-07-05 | TD-001 | In-memory repository | Data resets on restart | Replace with SQLAlchemy/PostgreSQL after demo scaffold is stable |
| 2026-07-05 | TD-002 | Fixture enrichment | Public API behavior not live yet | Add cache-backed adapters in Phase 2 |
| 2026-07-05 | TD-003 | Static frontend fixtures | UI not wired to API yet | Add TanStack Query hooks and API adapters in Phase 3 |
| 2026-07-05 | TD-004 | Guarded autonomous loop dry run still needs workflow confirmation | Intake normalization, automatic review, CI-triggered fix passes, and loop artifacts are wired but need a low-risk end-to-end GitHub Actions run | Run the docs-only dry run in `backstage/development/agent-loop-board.md` before trusting broader automation |
| 2026-07-06 | TD-005 | Externalized scoring config file not yet present | Settings expose a scoring config path, but the current scaffold still reads scoring constants from code | Move scoring weights and thresholds into a versioned config file before calibration work |
| 2026-07-06 | TD-006 | Frontend visual QA blocked in sandbox | Local Next dev/build paths cannot bind worker ports in the restricted runner, so desktop/narrow screenshot QA could not run here | Run manual desktop and narrow viewport QA in an unrestricted local or CI browser environment before merge |
| 2026-07-06 | TD-007 | Agent style docs are read-only in loop sandbox | `.agents/style/ui-patterns.md` could not be updated with the new Button/StateNotice guidance from issue #28 | Mirror the implemented frontend primitive guidance into `.agents/style/ui-patterns.md` from a maintainer-writable path |
| 2026-07-06 | TD-008 | Public-data live coverage is partial | Geocoding and DNS/MX domain quality have live-capable paths, but demographic, economic, local-context, company-context, and trigger-context categories are fixture-normalized without cache-backed live adapters | Add cache-backed live adapters and fixture fallback tests for the remaining categories before pilot use |
