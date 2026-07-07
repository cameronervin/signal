# Phase 2 - Live Public API Adapters

## Goal

Replace fixture-only enrichment with cache-backed public API adapters while
keeping demo reliability and gate safety.

## Work Items

| Status | Work Type | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Done | Implementation | Add cache-backed geocoding adapter and address-resolution gate | US-1.1, US-2.2; `integration-spec.md`, `data-model.md`, `agentic-framework.md`, `security.md` | Address input resolves to normalized coordinates/source facts when available; provider errors use fixture fallback; no raw provider payloads are logged | `backend/app/infrastructure/public_data/`, `backend/app/agents/nodes/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | `integration-spec.md`, `agentic-framework.md`, architecture overview | Phase 1 backend scaffold | Backlog: adapter/geocoding |
| Done | Implementation | Add cache-backed market demographics and economics adapters | US-2.1; `integration-spec.md`, `data-model.md`, `scoring.md`, `eval-framework.md` | Renter share, rent, household growth, and labor signals normalize into `SourceFact` records; missing fields degrade without blocking draftable leads; fixture-backed tests cover adapter success and provider merge paths; scoring inputs remain config-driven | `backend/app/infrastructure/public_data/`, `backend/app/agents/scoring.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | `integration-spec.md`, setup guide | Geocoding adapter | Backlog: adapter/market-data |
| Done | Implementation | Add company trigger/background adapter with cited fallback facts | US-3.1; `integration-spec.md`, `agentic-framework.md`, `data-model.md`, `security.md` | Company trigger and background lookup return cited source facts when available; provider failures use cached/fixture fallback; tests cover parsed trigger/background facts | `backend/app/infrastructure/public_data/`, `backend/app/agents/nodes/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | `integration-spec.md`, `agentic-framework.md` | Phase 1 backend scaffold | Backlog: adapter/company-trigger |
| Done | Implementation | Add corporate email domain and MX validation gate | US-2.2, US-3.2; `integration-spec.md`, `scoring.md`, `security.md` | Personal domains remain hard gate failures; corporate domains validate through domain/MX checks when available; gate-failed leads never receive drafts | `backend/app/infrastructure/public_data/`, `backend/app/agents/scoring.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | `integration-spec.md`, `scoring.md` | Phase 1 backend scaffold | Backlog: adapter/email-gate |

## Exit Criteria

- Live public API behavior is isolated behind typed adapters.
- Every adapter has fixture-backed tests and a degraded-service path.
- Draftable leads keep working when one provider is unavailable.
- Hard gate failures remain inspectable and suppress drafts.
