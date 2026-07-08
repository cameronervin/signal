# Phase 4 - Rollout And Evaluation

## Goal

Support operational readiness with stable seeded data, regression evals,
rollout notes, and visible production gaps.

## Work Items

| Status | Work Type | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Done | Evaluation | Build seeded sample-data suite for stable A/B/C and gate-failed outcomes | US-1.2, US-2.1, US-2.2, US-5.1; `eval-framework.md`, `scoring.md`, `rollout.md` | Sample-data suite includes A, B, C, gate-failed, missing-trigger, and warning-only cases; expected tiers and why-lines are asserted; seeded results are reproducible; drift requires explicit scoring doc update | `backend/scripts/demo_seed.py`, `backend/app/agents/utils/scoring.py`, `backend/tests/`, `backstage/prd/02-technical-docs/01-signal/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | `eval-framework.md`, `scoring.md`, `tech-debt-tracker.md` | Seed script; adapter behavior stable enough for sample expectations | Backlog: eval/seed-suite |
| Done | Evaluation | Add draft citation and human-review safety evals | US-3.1, US-3.2; `eval-framework.md`, `agentic-framework.md`, `security.md` | Every deterministic draft source maps to a personalization claim; hard gate failures expose no draft; run cannot move beyond review without approval; tests cover cited and no-draft paths | `backend/app/agents/chains/outreach_drafting.py`, `backend/app/agents/nodes/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | `eval-framework.md`, `security.md`, `agentic-framework.md` | Review-gate transitions; fixture suite | Backlog: eval/draft-safety |
| Done | Implementation | Complete rollout guide, sample-data script, and production gap checklist | US-5.1; `rollout.md`, `security.md`, `eval-framework.md` | Rollout doc covers local evaluation, shadow, pilot, success metrics, kill criteria, stakeholders, and production hardening boundaries; sample-data script references implemented screens and seeded data | `backstage/prd/02-technical-docs/01-signal/rollout.md`, `backstage/guides/`, `backstage/development/tech-debt-tracker.md` | Manual doc review; stale-status scan over implementation and rollout docs passes | `rollout.md`, setup and guide docs | Dashboard KPIs; sample-data suite | Backlog: rollout/docs |
| Done | Implementation | Add observability notes for local evaluation and pilot operations | US-4.1, US-5.1; `security.md`, `rollout.md`, `agentic-framework.md` | Activity log and run status fields are documented for support review; logs avoid sensitive raw data; implementation owners can identify failed adapter, gate, model, review, and worker states; production observability gaps are explicit hardening decisions | `backend/app/core/logging.py`, `backend/app/observability/`, `backend/app/agents/nodes/`, `backstage/guides/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .`; manual doc review | `rollout.md`, `security.md`, `agentic-framework.md`, `tech-debt-tracker.md` | Agent controls and eval suite | Backlog: rollout/observability |

## Exit Criteria

- Sample-data outcomes are stable enough for repeatable local evaluation.
- Regression tests protect gates, tiers, draft citations, and review safety.
- Rollout docs identify the next production decisions without treating them as
  completed v1 behavior.
- The implementation plan is complete for the assignment/demo build.
