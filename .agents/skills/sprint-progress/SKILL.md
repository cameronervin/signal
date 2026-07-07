# Sprint Progress

Generate a Markdown progress report from Signal user stories and implementation phase files.

## Inputs

Defaults:

```yaml
implementation_path: backstage/prd/03-implementation/
user_stories_path: backstage/prd/01-user-stories/_master-user-stories.md
output_path: backstage/development/sprint-reports/YYYY-MM-DD/sprint-progress.md
```

## Workflow

1. Read `_implementation-plan.md` and all `phase-*.md` files under `backstage/prd/03-implementation/`.
2. Read `backstage/prd/01-user-stories/_master-user-stories.md`.
3. Extract status, goal, story/spec refs, validation, and docs columns.
4. Optionally verify claimed completed work with targeted `rg` searches and relevant tests.
5. Write a Markdown report only. Do not generate images or call external AI APIs.

## Status Mapping

| Source marker | Report status |
| --- | --- |
| `Done` or checked row | Completed |
| `Planned` or unchecked row with active phase context | Planned |
| Partial marker or explicit note | In progress |
| Missing implementation evidence for completed claim | Needs verification |

## Output Format

```markdown
# Signal Sprint Progress - YYYY-MM-DD

## Summary
- Completed:
- In progress:
- Planned:
- Needs verification:

## By Phase
| Phase | Status | Goal | Story/Spec Refs | Validation |

## Verification Notes
- ...

## Follow-ups
- ...
```

## Scripts

The retained helper `scripts/parse_status.py` can parse implementation files for table reports. Keep it local and deterministic.

## Rules

- Do not include secrets, full emails, draft bodies, prompts, or raw provider payloads.
- Do not mark work complete unless code or docs prove it.
- Do not add paid API dependencies.
