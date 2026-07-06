# Agent Loops

Signal uses GitHub issues, labels, pull requests, CI, and workflow artifacts as
the durable state machine for Codex build loops. The current loop contract lives
in `.agents/loops/_loop-contract.md`; machine-readable defaults live in
`.agents/loops/manifest.yml`.

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

Low-risk issue-form submissions are normalized into loop labels, then start
only after a maintainer applies `agent:ready` or manually dispatches the loop
workflow. High-risk work remains in `agent:needs-human` until a human explicitly
applies `review:human` and `agent:ready`, or manually dispatches the loop
workflow.

Manual start:

```bash
gh workflow run codex-issue-loop.yml \
  --repo cameronervin/signal \
  -f issue_number=123 \
  -f loop=feature-build
```

Automatic start requires:

1. A complete agent-loop issue form.
2. Exactly one `loop:*` label after normalization.
3. Priority, type, surface, and risk labels after normalization.
4. Maintainer-applied `agent:ready`.
5. No active `agent:working`, `agent:reviewing`, or `agent:merge-ready` state.

## Labels That Matter

- `loop:feature-build`: normal product slice.
- `loop:bugfix`: focused defect fix.
- `loop:eval-calibration`: scoring, prompt, fixture, or eval tuning.
- `loop:frontend-fidelity`: visual and interaction polish.
- `agent:needs-human`: intake or risk gate needs human action.
- `agent:ready`: launchable work.
- `agent:working`: implementation is running.
- `agent:reviewing`: PR is open and under review.
- `agent:needs-fix`: review comments or CI need another pass.
- `agent:fix-pass-1`, `agent:fix-pass-2`: consumed fix-pass budget.
- `agent:merge-ready`: checks and review are satisfied.
- `agent:blocked`: workflow needs human input or external state.
- `review:codex-clear`: Codex review is clear; CI may still be catching up.

## Review And Fix Passes

PRs created by the issue loop get `review:codex` and `agent:reviewing`.
`codex-pr-review.yml` runs automatically for labeled loop PRs and can still be
run manually:

```bash
gh workflow run codex-pr-review.yml \
  --repo cameronervin/signal \
  -f pr_number=123
```

The review agent ends with `REVIEW_STATUS: needs-fix`, `clear`, or `human`.
`needs-fix` adds `agent:needs-fix`; `clear` adds `review:codex-clear`;
`human` adds a human review gate. If review clears before CI finishes, the
review workflow reconciles the PR to `agent:merge-ready` after backend and
frontend checks pass.

The babysitter can run from:

- A failed `CI` workflow for an open loop PR.
- A PR labeled `agent:needs-fix`.
- A trusted collaborator comment containing `@codex fix`.
- Manual workflow dispatch.

Fix passes are capped at two per PR. After `agent:fix-pass-2`, another fix
request marks the PR `agent:blocked`.

## Loop Artifacts

Each Codex workflow uploads `.codex-run/` as a GitHub Actions artifact. The
important file is `.codex-run/loop-result.json`, which records issue/PR ids,
loop type, status, model, timestamps, changed files, verification, docs state,
risk labels, blockers, and fix-pass count. The issue loop also updates the PR
body from this artifact.

## Merge Rules

`main` is protected. A low-risk agent PR may automerge only when all of these
are true:

- The PR is open, not draft, same-repository, and on a `codex/*` branch.
- Labels include `agent:merge-ready`, `review:codex-clear`, and `ci:passing`.
- Labels do not include `agent:needs-fix`, `agent:needs-human`,
  `agent:blocked`, or `review:human`.
- No high-risk labels are present.
- Required checks `backend`, `frontend`, and `review` are successful.
- Required conversations are resolved and branch protection allows the merge.

Keep high-risk work human-reviewed:

- `risk:scoring-change`
- `risk:outreach-gate`
- `risk:data-handling`
- `risk:external-api`

`Codex PR automerge` is the only workflow allowed to merge code. Implementation
and fix-pass agents must never merge their own work.

## Safe Operating Cadence

Start with one or two ready issues at a time. The manifest caps concurrent issue
loops at two. A scoping agent may create many issues, but they should remain in
`agent:needs-human` until normalized and deliberately launchable.
