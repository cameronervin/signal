# Agent Loop Contract

Signal loops are GitHub-backed state machines. Issues describe work, labels hold
launch and risk state, pull requests hold review state, CI verifies work, and
workflow artifacts preserve loop evidence.

## Required Fields

Every agent-owned issue must provide:

- A single loop type.
- A single priority.
- At least one surface.
- One user-visible outcome.
- Three to five acceptance checks.
- A budget statement.
- A stop condition.
- Expected artifacts or evidence.

## State Owner

GitHub is the durable state owner. Agents may read issue bodies, labels, pull
request diffs, review comments, and CI state, but they must not rely on their
own conversation memory as the only source of progress.

## Budget And Stop Rules

- Implementation loops stop at the issue definition of done or workflow timeout.
- Review loops stop after one review pass.
- Fix loops stop after two fix passes for a pull request.
- Repeated failure after the fix-pass budget becomes `agent:blocked`.
- High-risk work may run only after explicit human review labeling.

## Required Evidence

Each loop writes a `.codex-run/loop-result.json` artifact with:

- Issue and pull request identifiers.
- Loop type and model.
- Status and timestamps.
- Changed files.
- Verification summary.
- Documentation state.
- Risk labels.
- Blockers.
- Fix-pass count.

## Human Gates

No Signal loop may merge code. Branch protection, required checks, resolved
conversations, and human review remain the merge gate. High-risk labels require
human review before merge and before autonomous launch unless manually
dispatched by a repository maintainer.
