# Agent Loop Board

Signal uses GitHub as the durable state machine for agentic coding loops.
Issues queue work, labels carry state, pull requests carry review/fix context,
CI verifies changes, and workflow artifacts preserve loop evidence.

GitHub Project: `Signal Agent Loop Development`

- URL: `https://github.com/users/cameronervin/projects/2`
- Owner: `cameronervin`
- Number: `2`

The project has an `Agent Status` field with kanban states. GitHub's public API
does not currently expose project view creation, so the visual board view must
be created in the GitHub UI and grouped by `Agent Status`.

## Board Columns

| Column | Meaning | Primary labels |
| --- | --- | --- |
| Intake | Work exists but has not been shaped or approved for an agent | `agent:needs-human` |
| Ready | A bounded loop can start | `agent:ready` |
| Working | An implementation or fix agent is active | `agent:working` |
| Review | A PR is open and under Codex or human review | `agent:reviewing`, `review:codex`, `review:codex-clear`, `review:human` |
| Needs Fix | Review comments or CI failures need another pass | `agent:needs-fix`, `ci:failed` |
| Blocked | Work cannot proceed without credentials, permissions, budget, or product input | `agent:blocked` |
| Merge Ready | Required checks and review gates are satisfied | `agent:merge-ready`, `ci:passing` |
| Done | The work is merged or intentionally closed | Closed issue or merged PR |

## Required Label Groups

- Type: `type:feature`, `type:bug`, `type:chore`, `type:docs`,
  `type:test`, `type:security`, `type:refactor`.
- Priority: `priority:p0`, `priority:p1`, `priority:p2`, `priority:p3`.
- Loop: `loop:feature-build`, `loop:bugfix`, `loop:eval-calibration`,
  `loop:frontend-fidelity`.
- Agent state: `agent:ready`, `agent:working`, `agent:reviewing`,
  `agent:needs-fix`, `agent:needs-human`, `agent:blocked`,
  `agent:merge-ready`.
- Fix budget: `agent:fix-pass-1`, `agent:fix-pass-2`.
- Surface: `surface:backend`, `surface:frontend`, `surface:agent-pipeline`,
  `surface:scoring`, `surface:integrations`, `surface:docs`.
- Risk: `risk:scoring-change`, `risk:outreach-gate`,
  `risk:data-handling`, `risk:external-api`.
- Review and CI: `review:codex`, `review:codex-clear`, `review:human`,
  `ci:failed`, `ci:passing`.

## Operating Rules

1. Every agent-owned issue needs exactly one loop label.
2. Every implementation PR links back to an issue.
3. Risk labels require explicit PR checklist attention and human review.
4. Low-risk complete issue forms may be normalized automatically, but launch
   still requires maintainer-applied `agent:ready` or manual dispatch.
5. High-risk issue forms remain `agent:needs-human` until human-approved.
6. Fix passes stop after two attempts and then become `agent:blocked`.
7. Low-risk merge decisions may be made by Codex review plus branch protection.
   High-risk work stays human-reviewed.

## Automation Setup

The workflow scaffolds in `.github/workflows/` use `openai/codex-action@v1`.
Before running them, add these repository Actions secrets:

- `OPENAI_API_KEY` for Codex implementation, review, and fix passes.
- `AGENT_GITHUB_TOKEN` for agent branch pushes, PR creation, fix-pass pushes,
  and automerge. Use a bot or maintainer token with repository contents,
  issues, and pull request permissions so PR workflows trigger from
  agent-created branches. Do not grant workflow-file permission for the
  autonomous path; issue and fix-publish jobs reject control-plane changes under
  `.github/workflows/`, `.github/scripts/`, and `.github/codex/prompts/`.

- `Codex issue loop` validates issue intake, starts maintainer-ready issues,
  creates a branch, opens a PR, writes loop evidence, and moves the issue to
  review.
- `Codex PR review` runs automatically for PRs labeled `review:codex`,
  reconciles clear reviews after CI success, and can be manually dispatched.
- `Codex PR automerge` merges only low-risk agent PRs after the `backend`,
  `frontend`, and Codex `review` status checks pass.
- `Codex PR babysitter` runs on failed `CI`, `agent:needs-fix`, trusted
  `@codex fix` comments, or manual dispatch, with a two-pass budget.
- `Project label sync` maps issue and PR labels to the GitHub Project fields.
- `CI` runs backend tests/lint and frontend tests/lint/typecheck on pull
  requests and pushes to `main`.

The issue and fix-pass workflows keep networked GitHub operations outside the
Codex sandbox. Codex edits files in the checkout; GitHub Actions commits,
pushes, opens pull requests, updates labels, and uploads artifacts.

All Codex GitHub Action jobs pin `model: gpt-5.5`. Issue implementation prompts
begin with `/goal` so assigned agents keep a persistent definition of done for
the issue loop.

For this user-owned Project v2, `Project label sync` needs a repository secret
named `PROJECT_TOKEN` with the `project` scope. The workflow skips with a notice
until that secret exists. The workflow uses project owner `@me` so the token can
resolve the current user's Project. If GitHub reports missing scopes, regenerate
the token with the reported scopes as well.

`Codex issue loop`, `Codex PR review`, and `Codex PR babysitter` need
`OPENAI_API_KEY` as a repository Actions secret. They skip with a notice until
that secret exists.

`Codex issue loop`, `Codex PR babysitter`, and `Codex PR automerge` need
`AGENT_GITHUB_TOKEN` for tokened publish and merge steps. The default
`GITHUB_TOKEN` is not enough for the fully autonomous path because GitHub
suppresses follow-up workflows from PRs and pushes created by that token.
Autonomous issue and fix-publish jobs refuse control-plane file changes before
using this token; those changes need a trusted maintainer path.

## Dry Run

Use a low-risk docs or test issue to validate the autonomous path:

2026-07-06 dry-run note: issue #32 exercises the guarded autonomous loop path
with a docs-only change. The run must preserve high-risk human gates, avoid
product behavior changes, and leave loop evidence in `.codex-run/loop-result.json`.

1. Open a complete agent-loop issue with no risk flags.
2. Confirm intake normalization applies loop, priority, type, and surface
   labels while leaving the issue in human intake.
3. Apply `agent:ready` or manually dispatch the issue loop.
4. Confirm `Codex issue loop` creates a branch and PR.
5. Confirm `Codex PR review` posts a review.
6. Force or simulate a CI failure only on a disposable PR, then confirm the
   babysitter consumes at most two fix passes.
7. Confirm low-risk merge waits for Codex review plus branch protection, and
   high-risk work still requires human review.

## Merge Gates

`main` is protected. Low-risk agent PRs require the `backend`, `frontend`, and
Codex `review` status checks, required conversation resolution, admin
enforcement, and force-push/deletion blocks. Required human pull request
reviews are not enabled for the low-risk agent path. High-risk labels still
require human review before merge.
