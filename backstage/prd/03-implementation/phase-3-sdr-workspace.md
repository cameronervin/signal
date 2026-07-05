# Phase 3 - SDR Workspace

## Goal

Build the API-backed SDR workspace for ranked lead prioritization, lead review,
copy/export, run status, and demo presentation.

## Agent Threads

| Status | Agent Loop | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Planned | feature-build | Wire frontend API client and shared types to fresh backend contracts | US-1.1, US-2.1, US-3.1, US-5.2; `api-specification.md`, `data-model.md` | Queue, detail, and run views consume API responses; loading/error/empty/degraded states render; fixtures remain available for demo fallback; TypeScript types match DTOs | `frontend/src/lib/api/`, `frontend/src/types/`, `frontend/src/lib/fixtures/`, `frontend/src/app/` | `cd frontend && pnpm test`; `cd frontend && pnpm lint`; `cd frontend && pnpm typecheck` | Update setup/design docs if data-loading behavior changes | Backend API contracts | Backlog: frontend/api-alignment |
| Planned | frontend-fidelity | Build ranked SDR queue with filters, search, score/tier display, and urgency cues | US-3.1, US-3.2, US-6.1; `scoring.md`, `backstage/design/README.md` | Queue sorts by tier/score; search and tier/status filters work; each row shows why-line, flags, and draft availability; A-tier urgency is visible without hiding C-tier safety states | `frontend/src/app/leads/page.tsx`, `frontend/src/components/`, `frontend/src/lib/store/` | `cd frontend && pnpm test`; `cd frontend && pnpm lint`; `cd frontend && pnpm typecheck`; desktop/narrow manual QA | Update `backstage/design/README.md` if UI patterns change | Frontend API alignment | Backlog: frontend/ranked-queue |
| Planned | frontend-fidelity | Build lead detail with evidence, score components, talking points, related context, and reviewable draft | US-2.1, US-2.2, US-3.1, US-4.1, US-5.1; `data-model.md`, `security.md`, `backstage/design/README.md` | Detail shows enrichment facts/source chips, score components, flags, related leads, talking points, and cited draft; gate-failed leads show no draft body; text fits desktop and narrow layouts | `frontend/src/app/leads/[id]/page.tsx`, `frontend/src/components/`, `frontend/src/types/` | `cd frontend && pnpm test`; `cd frontend && pnpm lint`; `cd frontend && pnpm typecheck`; desktop/narrow manual QA | Update `backstage/design/README.md`, `security.md` if safety behavior changes | Frontend API alignment; LLM draft contract | Backlog: frontend/lead-detail |
| Planned | feature-build | Implement review/copy/export state without live send | US-4.1, US-4.2; `api-specification.md`, `security.md`, `rollout.md` | Copy/export action records reviewed state; no email is sent; gate-failed/no-draft leads return clear conflict; frontend controls are explicit and inaccessible for gate-failed leads | `backend/app/api/v1/`, `backend/app/services/`, `frontend/src/app/leads/[id]/page.tsx`, `frontend/src/components/` | `cd backend && uv run pytest -v`; `cd frontend && pnpm test`; `cd frontend && pnpm typecheck` | Update `api-specification.md`, `backstage/api/endpoints.md`, `security.md` | Lead detail; backend contracts | Backlog: workflow/review-copy-export |
| Planned | frontend-fidelity | Build agent run list/detail and demo dashboard states | US-1.2, US-5.2, US-6.1; `rollout.md`, `eval-framework.md` | Run list/detail show stages and degraded provider state; dashboard supports seeded demo narrative; no production analytics claims are implied; greyed future automation is labeled beyond v1 | `frontend/src/app/agents/`, `frontend/src/app/dashboard/`, `frontend/src/components/` | `cd frontend && pnpm test`; `cd frontend && pnpm lint`; `cd frontend && pnpm typecheck`; desktop/narrow manual QA | Update `backstage/design/README.md`, `rollout.md` if demo narrative changes | Frontend API alignment; run status API | Backlog: frontend/runs-dashboard |

## Exit Criteria

- SDR can move from ranked queue to lead detail to reviewed copy/export.
- Gate-failed states are first-class and draft-free.
- Agent run status explains ready, running, degraded, and blocked states.
- Dashboard/demo surfaces support the video narrative without production claims.
