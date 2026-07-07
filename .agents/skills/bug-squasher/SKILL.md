# Bug Squasher

Systematic Signal debugging workflow. Use this for unclear bugs, intermittent failures, regressions, and fixes that should be proven before patching.

## Workflow

### 1. Preflight

Gather current context without exposing sensitive data:

```bash
git status --short
git diff --stat
rg "error|Error|ERROR|warning|Warning" backend/app backend/tests frontend/src -C 2
```

Read the relevant docs:
- `backstage/prd/README.md`
- `backstage/architecture/overview.md`
- Relevant spec under `backstage/prd/02-technical-docs/01-signal/`
- `backstage/design/README.md` for UI bugs

Collect from the user only if needed:
- Exact error message or unexpected behavior.
- Steps to reproduce.
- Expected behavior.
- Environment: backend, frontend, worker, seeded demo, or live-adapter mode.

### 2. Hypotheses

List 3-7 likely causes before editing. Rank by likelihood and ease of verification.

Common Signal categories:
- API/DTO mismatch between backend Pydantic schemas and frontend types.
- Missing fixture/cache fallback.
- Gate, scoring, or no-draft behavior drift.
- Async repository/session issue.
- LangGraph state update or run-status transition issue.
- Frontend client/server component boundary issue.
- Styling/layout regression against the Signal design tokens.

Use `references/hypothesis-template.md` if helpful.

### 3. Targeted Evidence

Prefer tests, focused repro commands, existing logs, and code inspection. Add temporary instrumentation only when necessary, and sanitize it.

Never log full emails, draft bodies, prompts, request bodies, provider payloads, tokens, or API keys.

### 4. Minimal Fix

Patch the root cause with the smallest clear change. Preserve:
- Server-owned score, tier, gate, draft, and run fields.
- Gate-failed no-draft behavior.
- Human review before outreach.
- Demo fixture/cache fallback.
- Neutral product copy and fixtures.

### 5. Verification

Run the smallest relevant checks first, then broaden when risk warrants:

```bash
cd backend && uv run pytest -v
cd backend && uv run ruff check .
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend typecheck
```

### 6. Report

Summarize:
- Root cause.
- Files changed.
- Tests or checks run.
- Docs updated or not needed.
- Remaining risk.

## References

- `references/hypothesis-template.md`
- `references/instrumentation-patterns.md`
- `references/root-cause-checklist.md`
