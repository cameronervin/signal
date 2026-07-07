# Doc Gardening

Find and fix Signal documentation drift.

## Scope

Primary docs:
- `AGENTS.md`
- `README.md`
- `backstage/prd/README.md`
- `backstage/architecture/overview.md`
- `backstage/prd/01-user-stories/_master-user-stories.md`
- `backstage/prd/02-technical-docs/01-signal/`
- `backstage/prd/03-implementation/`
- `backstage/design/README.md`
- `backstage/guides/setup.md`
- `backstage/development/tech-debt-tracker.md`

## Checks

- API docs match FastAPI routes and Pydantic DTOs.
- Data model docs match stored lead, enrichment, score, draft, and run fields.
- Agent docs match bounded LangGraph state, nodes, graph, and executor behavior.
- Scoring docs match gates, thresholds, weights, and why-line behavior.
- Integration docs match public-data adapters, cache, fixtures, and fallback behavior.
- Security docs match logging and data minimization behavior.
- Design docs match frontend tokens, primitives, and implemented surfaces.
- Phase docs mark only verified work as done.

## Output

```markdown
# Documentation Health Report

## Findings
- `path`: issue and recommended fix.

## Safe Fixes
- ...

## Needs Product/Tech Decision
- ...

## Verification
- Commands or manual checks used.
```

## Rules

- Do not update docs to describe planned behavior as implemented.
- Do not add third-party company/client brand names.
- Do not include secrets, real leads, full emails, draft bodies, prompts, or raw provider payloads.
- Update docs after behavior changes, especially API, data model, scoring, integration, setup, and security docs.

## Reference

Use `references/doc-coverage-checklist.md` as a supplemental checklist.
