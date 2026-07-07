# Garbage Cleanup

Find dead code, stale scaffolding, repeated logic, and architectural drift in Signal.

## Scan Commands

```bash
git status --short
git diff --stat
cd backend && uv run ruff check . --select F401,F841
pnpm --dir frontend lint
rg -n "TODO|FIXME|HACK|temporary|stub|mock|placeholder" backend frontend backstage
```

## Cleanup Targets

- Unused imports, variables, functions, fixtures, routes, and components.
- Repeated scoring/gate logic that should be centralized.
- Hardcoded tier thresholds, score weights, or design colors.
- Public-data adapter duplication or missing fixture fallback.
- Routes that bypass services or repositories.
- Components that bypass existing UI primitives.
- Stale docs that claim planned behavior is implemented.

## Do Not Remove Without A Plan

- Public API endpoints.
- Pydantic fields used by frontend fixtures or docs.
- Demo seed cases.
- Gate-failed/no-draft paths.
- Human review controls.
- Public-data fallbacks and caches.

## Output

```markdown
# Cleanup Report

## Safe To Remove Now
| Type | Location | Reason | Verification |

## Defer With Plan
| Location | Reason | Suggested plan |

## Architectural Drift
| Location | Issue | Fix |

## Verification
- ...
```

## References

- `references/cleanup-checklist.md`
- `references/code-smell-patterns.md`
