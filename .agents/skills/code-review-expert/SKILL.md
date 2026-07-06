# Code Review Expert

Review changes with findings first.

## Priority

- P0: security issue, secret leak, data loss, automatic send without approval.
- P1: linked issue not satisfied, existing contract broken, core architecture
  boundary violated, incorrect scoring/gating, broken trigger, or draft
  generated/exposed for failed gate.
- P2: maintainability, SOLID/DRY, missing tests, documentation, or integration
  reliability issue that materially affects the changed scope or makes the work
  unsafe to build on.
- P3: style, naming, minor readability, small accessibility issue.

## Checklist

- Routes are thin.
- Services own orchestration.
- DTOs and service boundaries are typed, explicit, and stable.
- Code has clear ownership, low coupling, cohesive functions/classes, and no
  duplicated domain rules.
- Scores and tiers are not client-trusted.
- Logs avoid secrets, full emails, drafts, prompts, and raw API payloads.
- Tests prove the requested behavior and important edge cases introduced by the
  PR.
- Docs changed when contracts, architecture, or behavior changed.

## Output

Lead with findings ordered by severity. If no findings, say that clearly and
note residual test or manual verification gaps.
