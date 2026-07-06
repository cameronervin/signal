# Agent Loops

Signal uses GitHub issues as the queue for Codex build loops. A loop starts
from one bounded issue, creates a branch, opens a PR, gets reviewed, accepts
fix passes, and stops at the merge gate.

## Agent Defaults

The GitHub Action Codex jobs pin `model: gpt-5.5`.

Issue implementation agents start their prompt with `/goal` so Codex keeps one
definition of done while it works the issue. If you run loops locally, set
`model = "gpt-5.5"` in `~/.codex/config.toml` and enable goals:

```toml
[features]
goals = true
```

## Start A Loop

Issue loop automation is manual-only while the build backlog is being created.
Creating, assigning, or labeling issues will not start agents right now.

Start a loop:

```bash
gh workflow run codex-issue-loop.yml \
  --repo cameronervin/signal \
  -f issue_number=123 \
  -f loop=feature-build
```

When automatic issue triggers are re-enabled:

1. Create or scope an issue with clear acceptance criteria.
2. Add exactly one `loop:*` label.
3. Add priority, type, surface, risk, and review labels.
4. Add `agent:ready` last, or assign the issue after it already has
   `agent:ready`.

Issues do not start agents just because they exist. With automation paused, the
builder runs only on manual dispatch. After issue triggers are re-enabled, an
`assigned`/`labeled` event must find both `agent:ready` and a loop label.

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

PRs created by the issue loop get `review:codex`.

During scaffold and early product build, Codex PR review is manual-only. Run it
when a PR has enough implementation surface to inspect:

```bash
gh workflow run codex-pr-review.yml \
  --repo cameronervin/signal \
  -f pr_number=123
```

Turn automatic PR review back on after several low-risk loop PRs are stable.

To ask the babysitter for a fix pass, comment on the PR:

```text
@codex fix
```

The babysitter checks out the PR branch, applies a focused fix, commits, and
pushes back to the same PR. Re-run the review workflow manually when you want
another Codex review pass.

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
