# Code Review Expert

Review changes with findings first.

## Priority

- P0: security issue, secret leak, data loss, automatic send without approval.
- P1: incorrect scoring/gating, broken trigger, draft generated for failed gate.
- P2: maintainability, missing tests, brittle fixture or API fallback.
- P3: style, naming, small accessibility issue.

## Checklist

- Routes are thin.
- Services own orchestration.
- Scores and tiers are not client-trusted.
- Logs avoid secrets, full emails, drafts, prompts, and raw API payloads.
- Tests cover gate pass and gate fail.
- Docs changed when contracts changed.

## Output

Lead with findings ordered by severity. If no findings, say that clearly and
note residual test or manual verification gaps.
