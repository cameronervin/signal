# Phase 1 - Spec And Baseline

## Goal

Establish the fresh Signal PRD, update local agent guidance, and identify the
first code-alignment slices required by the new spec.

## Agent Threads

| Status | Agent Loop | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Done | feature-build | Rewrite fresh Signal PRD and local agent guidance | US-1.1 through US-6.1; all PRD specs | PRD docs describe vendor-SDR inbound demo lead workflow; agent guidance uses neutral framing; repo-local spec-builder asks about v1/v2 before future replacement; forbidden source-company names do not appear in generated docs/guidance | `backstage/prd/`, `AGENTS.md`, `.agents/skills/spec-builder/SKILL.md` | `git diff --check`; `rg -n "<forbidden-source-name>" backstage/prd AGENTS.md .agents/skills/spec-builder/SKILL.md` | This PRD set | None | Backlog: docs/fresh-spec |
| Planned | feature-build | Align backend DTOs and repository state with fresh lead, enrichment, score, draft, related-context, and run models | US-1.1, US-2.1, US-2.2, US-3.1, US-4.1, US-5.1, US-5.2; `data-model.md`, `api-specification.md` | DTOs include fresh input fields and response sections; server owns trusted score/gate/draft eligibility; run state can store degraded reasons; existing tests updated for new contract | `backend/app/schemas/`, `backend/app/repositories/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `data-model.md` and API spec if contract changes | Fresh PRD | Backlog: backend/contracts |
| Planned | feature-build | Implement lead insertion trigger and demo seed endpoint | US-1.1, US-1.2, US-6.1; `api-specification.md`, `eval-framework.md`, `rollout.md` | `POST /api/v1/leads` triggers the pipeline; `POST /api/v1/leads/seed` creates stable A/B/C, warning-only, and gate-failed examples; invalid input returns field errors; seed path works without live APIs | `backend/app/api/v1/`, `backend/app/services/`, `backend/app/agents/fixtures.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `backstage/api/endpoints.md`, `api-specification.md`, `eval-framework.md` | Backend contracts | Backlog: backend/intake-seed |

## Exit Criteria

- Fresh product docs are the PRD source of truth.
- Local guidance tells future agents how to handle spec versioning questions.
- Initial backend contract and seed tasks are ready for implementation.
