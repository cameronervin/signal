---
name: build-plan-writer
description: Manual invocation only. Use only when explicitly requested to create or update an implementation plan or build plan.
---

# Build Plan Writer

Create Signal implementation plans that a later coding agent can execute without rediscovering the product.

## Grounding

Read before drafting:
- `backstage/prd/README.md`
- `backstage/architecture/overview.md`
- `backstage/prd/01-user-stories/_master-user-stories.md`
- Relevant specs under `backstage/prd/02-technical-docs/01-signal/`
- Existing phase files under `backstage/prd/03-implementation/`
- `backstage/design/README.md` for frontend plans
- Current implementation paths that prove what already exists

## Plan Rules

- Separate discovered facts from product decisions.
- Ask only when a decision cannot be found in docs or code and guessing would materially change the plan.
- Keep implementation slices small, testable, and demo-safe.
- Explicitly call out score, gate, draft, public-data, review-gate, storage, and logging impacts.
- Do not introduce new persistent storage, paid dependencies, auth, background-worker changes, or live send behavior without approval.
- Do not add third-party company/client brand names to docs, fixtures, prompts, comments, or tests.

## Output

Prefer this structure:

```markdown
# <Plan Title>

## Summary
- ...

## Key Changes
- ...

## Public Interfaces
- ...

## Test Plan
- ...

## Assumptions
- ...
```

For phased work, use the existing implementation table style in `backstage/prd/03-implementation/`.

## Reference

Use `references/build-plan-template.md` for larger plans when helpful.
