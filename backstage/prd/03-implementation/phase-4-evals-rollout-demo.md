# Phase 4 - Evals, Rollout, Demo

## Goal

Protect score quality, draft safety, provider fallback, and the take-home rollout
narrative with tests, docs, and demo evidence.

## Agent Threads

| Status | Agent Loop | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Planned | eval-calibration | Add citation, draft-safety, provider-fallback, and no-send regression tests | US-2.1, US-2.2, US-4.1, US-4.2, US-6.1; `eval-framework.md`, `security.md` | Every personalization claim maps to a source fact; gate-failed leads expose no draft; provider and LLM outage cases are stable; copy/export never sends outreach; tests fail on unsupported personalization | `backend/tests/`, `frontend/src/**/*.test.tsx`, `backend/app/agents/fixtures.py` | `cd backend && uv run pytest -v`; `cd frontend && pnpm test`; `cd backend && uv run ruff check .`; `cd frontend && pnpm typecheck` | Update `eval-framework.md`, `security.md` | LLM agent; review/copy/export | Backlog: eval/safety-suite |
| Planned | eval-calibration | Add calibration reporting for score distribution and rep feedback | US-3.1, US-3.2, US-6.1; `scoring.md`, `eval-framework.md`, `rollout.md` | Seeded and pilot leads can be summarized by tier, score drivers, and feedback label; reweighting assumptions are documented; no hidden scoring paths bypass config | `backend/app/agents/scoring.py`, `backend/tests/`, `backstage/prd/02-technical-docs/01-signal/` | `cd backend && uv run pytest -v`; manual doc review | Update `scoring.md`, `eval-framework.md`, `rollout.md` | Scoring rubric; seeded leads | Backlog: eval/calibration-reporting |
| Planned | feature-build | Complete rollout guide, demo script, and video-ready evidence | US-6.1; `rollout.md`, `eval-framework.md` | Rollout doc covers testing, stakeholders, timelines, success and kill criteria; demo script maps to assignment requirements; open owner notes are visible; tech debt captures remaining production gaps | `backstage/prd/02-technical-docs/01-signal/rollout.md`, `backstage/guides/`, `backstage/development/tech-debt-tracker.md` | Manual doc review for owner notes, TODOs, and planned markers | Update `rollout.md`, `tech-debt-tracker.md`, setup/demo guide if added | Evals; demo UI states | Backlog: rollout/video-readiness |

## Exit Criteria

- Regression tests protect gates, tiers, citations, LLM fallback, provider
  fallback, and no-send behavior.
- Rollout docs can be used directly in the 5-15 minute video.
- Remaining production gaps are visible and intentionally out of scope.
