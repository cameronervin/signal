## Summary

- 

## Agent Loop

- Issue:
- Loop:
- Surfaces:
- Risk labels:

## Verification

- [ ] Backend tests: `cd backend && uv run pytest -v`
- [ ] Backend lint: `cd backend && uv run ruff check .`
- [ ] Frontend tests: `cd frontend && pnpm test`
- [ ] Frontend lint: `cd frontend && pnpm lint`
- [ ] Frontend typecheck: `cd frontend && pnpm typecheck`
- [ ] Targeted manual check:

## Signal Gates

- [ ] Routes stayed thin and orchestration stayed in services.
- [ ] Scores, tiers, and gate status are server-computed.
- [ ] Hard-gate-failed leads do not expose drafts.
- [ ] Human review remains required before outreach.
- [ ] Logs avoid secrets, full emails, prompts, drafts, and raw request bodies.
- [ ] Public API paths have cache or fixture fallback where needed.

## Review State

- [ ] Ready for Codex review.
- [ ] Ready for human review.
- [ ] Docs updated or not needed.
- [ ] Open risks are captured in `backstage/development/tech-debt-tracker.md`.
