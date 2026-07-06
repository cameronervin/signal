# Phase 1 - Foundations

## Goal

Create a development-ready scaffold for Signal with real contracts, docs, and
manual work-item guidance.

## Work Items

| Status | Work Type | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Done | Implementation | Create workspace scaffold and repo guidance | US-5.1; `backstage/prd/README.md` | Root README, package workspace, env example, gitignore, and Makefile exist; AGENTS.md captures Signal-specific constraints | `README.md`, `package.json`, `pnpm-workspace.yaml`, `AGENTS.md`, `Makefile` | Manual file review; `rg --files backstage` | `AGENTS.md`, `backstage/guides/setup.md` | None | Backlog: foundations/workspace |
| Done | Implementation | Create FastAPI lead and run pipeline scaffold | US-1.1, US-2.1, US-2.2, US-3.1, US-3.2, US-4.1; `api-specification.md`, `data-model.md`, `agentic-framework.md`, `scoring.md`, `security.md` | Health, lead, and agent-run routes exist; lead creation runs the graph; score/tier/why-line are server-generated; hard gate failures suppress drafts; tests cover health and lead pipeline | `backend/app/api/v1/`, `backend/app/services/lead_service.py`, `backend/app/agents/`, `backend/app/repositories/`, `backend/app/schemas/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | API, data model, agent, scoring, and security specs | Workspace scaffold | Backlog: foundations/backend |
| Done | Frontend | Create Next.js SDR workspace scaffold | US-2.1, US-2.2, US-3.1, US-3.2, US-4.1; `backstage/design/README.md` | Dashboard, leads, lead detail, agents, and run detail routes exist; shared shell and score/tier primitives exist; static fixtures support A/B/C and gate-failed states; primary views follow design-system direction | `frontend/src/app/`, `frontend/src/components/`, `frontend/src/lib/fixtures/`, `frontend/src/types/` | `cd frontend && pnpm test`; `cd frontend && pnpm lint`; `cd frontend && pnpm typecheck` | `backstage/design/README.md` | Workspace scaffold | Backlog: foundations/frontend |
| Done | Implementation | Create backstage product and architecture documentation baseline | US-1.1, US-1.2, US-2.1, US-2.2, US-3.1, US-3.2, US-4.1, US-5.1; all PRD specs | PRD, user stories, technical specs, architecture overview, design docs, setup guide, and development trackers exist; known gaps are captured as tech debt; docs index links key artifacts | `backstage/prd/`, `backstage/architecture/`, `backstage/design/`, `backstage/guides/`, `backstage/development/` | Manual doc review; `rg --files backstage/prd backstage/architecture backstage/design backstage/guides backstage/development` | PRD and backstage docs | Workspace scaffold | Backlog: foundations/docs |

## Next Phase Entry Criteria

- Backend tests pass after dependencies are installed.
- Frontend installs and typechecks.
- No banned client brand references are present in the repo.
