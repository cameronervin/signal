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

## Merge Gates

Low-risk agent pull requests may merge automatically when Codex review is clear,
required CI and review checks pass, conversations are resolved, and the PR has
only agent-owned labels allowed by the manifest. The automerge workflow is the
only component allowed to merge code; implementation and fix-pass agents must
not merge.

Tokened publish and merge steps must use `AGENT_GITHUB_TOKEN`, not the default
Actions `GITHUB_TOKEN`, so GitHub runs follow-up CI and review workflows for
agent-created branches and PRs.

Autonomous issue and fix-publish steps must refuse agent-generated changes to
`.github/workflows/`, `.github/scripts/`, or `.github/codex/prompts/` before
using `AGENT_GITHUB_TOKEN`. Control-plane changes require a trusted maintainer
path.

High-risk labels require human review before merge and before autonomous launch
unless manually dispatched by a repository maintainer:

- `risk:scoring-change`
- `risk:outreach-gate`
- `risk:data-handling`
- `risk:external-api`

Product outreach behavior remains human-gated regardless of code automerge.
