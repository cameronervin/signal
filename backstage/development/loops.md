# Agent Loops

Signal uses GitHub issues as the queue for Codex build loops. A loop starts
from one bounded issue, creates a branch, opens a PR, gets reviewed, accepts
fix passes, and stops at the merge gate.

## Start A Loop

Manual start:

```bash
gh workflow run codex-issue-loop.yml \
  --repo cameronervin/signal \
  -f issue_number=123 \
  -f loop=feature-build
```

Automatic start:

1. Create or scope an issue with clear acceptance criteria.
2. Add exactly one `loop:*` label.
3. Add priority, type, surface, risk, and review labels.
4. Add `agent:ready` last, or assign the issue after it already has
   `agent:ready`.

Issues do not start agents just because they exist. The builder runs only on
manual dispatch, or when an `assigned`/`labeled` event finds both `agent:ready`
and a loop label.

## Labels That Matter

- `loop:feature-build`: normal product slice.
- `loop:bugfix`: focused defect fix.
- `loop:eval-calibration`: scoring, prompt, fixture, or eval tuning.
- `loop:frontend-fidelity`: visual and interaction polish.
- `agent:ready`: launchable work.
- `agent:working`: implementation is running.
- `agent:reviewing`: PR is open for review.
- `agent:needs-fix`: comments or CI need another pass.
- `agent:merge-ready`: checks and review are satisfied.
- `agent:blocked`: workflow needs human input or external state.

Use `agent:needs-human` for intake items that are not ready to run.

## Review And Fix Passes

PRs created by the issue loop get `review:codex`. The review workflow comments
with findings or "No findings."

To ask the babysitter for a fix pass, comment on the PR:

```text
@codex fix
```

The babysitter checks out the PR branch, applies a focused fix, commits, and
pushes back to the same PR. The review workflow then runs again on the updated
branch.

## Merge Rules

`main` is protected. A PR must pass `backend` and `frontend`, have an approving
review, resolve conversations, and satisfy branch freshness before merge.

Keep high-risk work human-reviewed:

- `risk:scoring-change`
- `risk:outreach-gate`
- `risk:data-handling`
- `risk:external-api`

## Safe Operating Cadence

Start with one to three ready issues at a time. A scoping agent may create many
issues, but they should stay in `agent:needs-human` until you deliberately add
`agent:ready`.
