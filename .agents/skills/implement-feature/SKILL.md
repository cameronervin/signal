# Implement Feature

Implement Signal features with small, tested, demo-safe changes.

## 1. Preflight

Run:

```bash
git status --short
git diff --stat
```

Read:
- `backstage/prd/README.md`
- `backstage/architecture/overview.md`
- Relevant specs under `backstage/prd/02-technical-docs/01-signal/`
- Relevant phase file under `backstage/prd/03-implementation/`
- `backstage/design/README.md` for frontend work

Identify affected layers:
- `backend/app/api/v1/`
- `backend/app/services/`
- `backend/app/repositories/`
- `backend/app/agents/`
- `backend/app/infrastructure/public_data/`
- `backend/app/schemas/`
- `frontend/src/app/`
- `frontend/src/components/`
- `frontend/src/lib/`
- `frontend/src/types/`

## 2. Test First When Non-Trivial

Use TDD for backend behavior, scoring/gate changes, agent nodes, public-data adapters, and frontend business-rule interactions.

Backend examples:

```bash
cd backend && uv run pytest -v -k "lead"
```

Frontend examples:

```bash
pnpm --dir frontend test -- --runInBand
```

## 3. Implement

- Keep FastAPI routes thin.
- Put orchestration in services.
- Keep persistence behind repositories.
- Use Pydantic DTOs at boundaries.
- Keep LangGraph state explicit and bounded.
- Preserve fixture/cache fallbacks for public APIs.
- Keep gate-failed leads draftless.
- Keep outbound actions human-reviewed.
- Use existing frontend primitives and tokens.

Ask before:
- New persistent storage.
- Auth or permissions.
- Background worker behavior beyond existing Celery scaffold.
- New paid API dependency.
- Scoring weights or tier thresholds.
- Live send behavior.

## 4. Docs

Update docs after behavior changes:
- API: `api-specification.md`
- Data model: `data-model.md`
- Agent behavior: `agentic-framework.md`
- Scoring: `scoring.md`
- Public APIs: `integration-spec.md`
- Security: `security.md`
- Design/setup/rollout when affected

## 5. Verification

Run relevant checks:

```bash
cd backend && uv run pytest -v
cd backend && uv run ruff check .
pnpm --dir frontend test
pnpm --dir frontend lint
pnpm --dir frontend typecheck
```

If dependencies are missing, state the failing command and the install command from `backstage/guides/setup.md`.

## 6. Summary

Report:
- Files changed.
- Tests added or updated.
- Verification commands and results.
- Docs updated or not needed.
- Open risks.

## References

- `references/feature-template.md`
- `references/tdd-checklist.md`
