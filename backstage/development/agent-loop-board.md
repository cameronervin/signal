# Agent Loop Board

Signal uses GitHub as the durable state machine for agentic coding loops.
Codex threads should run finite loops, create or update pull requests, and then
stop. Labels, milestones, reviews, and CI decide what happens next.

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
| Intake | Work exists but has not been shaped for an agent | `agent:needs-human` |
| Ready | A bounded loop can start | `agent:ready` |
| Working | An implementation agent is active | `agent:working` |
| Review | A PR is open and under Codex or human review | `agent:reviewing`, `review:codex`, `review:human` |
| Needs Fix | Review comments or CI failures need another pass | `agent:needs-fix`, `ci:failed` |
| Blocked | Work cannot proceed without credentials, permissions, or product input | `agent:blocked` |
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
- Surface: `surface:backend`, `surface:frontend`, `surface:agent-pipeline`,
  `surface:scoring`, `surface:integrations`, `surface:docs`.
- Risk: `risk:scoring-change`, `risk:outreach-gate`,
  `risk:data-handling`, `risk:external-api`.
- Review and CI: `review:codex`, `review:human`, `ci:failed`,
  `ci:passing`.

## Operating Rules

1. Every agent-owned issue needs exactly one loop label.
2. Every implementation PR links back to an issue.
3. Risk labels require explicit PR checklist attention.
4. `risk:scoring-change`, `risk:outreach-gate`, `risk:data-handling`, and
   `risk:external-api` should receive human review before merge.
5. The babysitter can request fix passes, but merge decisions stay behind
   branch protection and human review until the automation is proven.

## Automation Setup

The workflow scaffolds in `.github/workflows/` use `openai/codex-action@v1`.
Before running them, add `OPENAI_API_KEY` as a repository Actions secret.

- `Codex issue loop` runs manually or when an issue with a loop label is
  assigned or labeled `agent:ready`.
- `Codex PR review` is manual-only while the scaffold stabilizes.
- `Codex PR babysitter` runs manually or when a trusted reviewer comments
  `@codex fix`.
- `Project label sync` maps issue and PR labels to the GitHub Project fields.
- `CI` runs backend tests/lint and frontend tests/lint/typecheck on pull
  requests and pushes to `main`.
- `backstage/development/loops.md` is the concise operator guide for launching
  and reviewing loops.

The issue and fix-pass workflows keep networked GitHub operations outside the
Codex sandbox. Codex edits files in the checkout; GitHub Actions commits,
pushes, opens pull requests, and updates labels.

All Codex GitHub Action jobs pin `model: gpt-5.5`. Issue implementation prompts
begin with `/goal` so assigned agents keep a persistent definition of done for
the issue loop.

For this user-owned Project v2, `Project label sync` needs a repository secret
named `PROJECT_TOKEN` with the `project` scope. The workflow skips with a notice
until that secret exists. The workflow uses project owner `@me` so the token can
resolve the current user's Project. If GitHub reports missing scopes, regenerate
the token with the reported scopes as well. Track that credential setup in
issue `#7`.

`Codex issue loop` needs `OPENAI_API_KEY` as a repository Actions secret. It
skips with a notice until that secret exists. Track that credential setup in
issue `#1`.

Keep automatic merging disabled until the review and fix-pass loop has proven
reliable on several low-risk PRs.

## Merge Gates

`main` is protected. Required status checks, required pull request reviews,
required conversation resolution, admin enforcement, and force-push/deletion
blocks are enabled.
