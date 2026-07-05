# Phase 2 - Live Public API Adapters

## Goal

Replace fixture-only enrichment with cache-backed public API adapters while
keeping demo reliability and gate safety.

## Agent Threads

| Status | Agent Loop | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Planned | feature-build | Add cache-backed geocoding adapter and address-resolution gate | US-1.1, US-2.2; `integration-spec.md`, `data-model.md`, `agentic-framework.md`, `security.md` | Address input resolves to normalized coordinates/source facts when available; unresolved or non-US addresses produce hard gate failures; provider errors produce warnings or fixture fallback; no raw provider payloads are logged | `backend/app/integrations/`, `backend/app/agents/nodes.py`, `backend/app/agents/fixtures.py`, `backend/app/schemas/lead.py`, `backend/tests/` | `cd backend && uv run pytest tests/test_lead_pipeline.py -v`; `cd backend && uv run ruff check .` | Update `integration-spec.md`, `data-model.md`, `agentic-framework.md`, `tech-debt-tracker.md` | Phase 1 backend scaffold | Backlog: adapter/geocoding |
| Planned | feature-build | Add cache-backed market demographics and economics adapters | US-2.1; `integration-spec.md`, `data-model.md`, `scoring.md`, `eval-framework.md` | Renter share, rent, household growth, and labor signals normalize into `SourceFact` records; missing fields degrade without blocking draftable leads unless a hard gate fails; fixture-backed tests cover success and outage paths; scoring inputs remain config-driven | `backend/app/integrations/`, `backend/app/agents/nodes.py`, `backend/app/agents/scoring.py`, `backend/app/agents/fixtures.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `integration-spec.md`, `scoring.md`, `eval-framework.md`, `tech-debt-tracker.md` | Geocoding adapter | Backlog: adapter/market-data |
| Planned | feature-build | Add company trigger/background adapter with cited fallback facts | US-3.1; `integration-spec.md`, `agentic-framework.md`, `data-model.md`, `security.md` | Company trigger lookup returns cited source facts or a no-trigger warning; draft personalization only uses available source facts; provider failures use cached/fixture fallback; tests cover missing trigger and cited draft behavior | `backend/app/integrations/`, `backend/app/agents/nodes.py`, `backend/app/agents/prompts.py`, `backend/app/agents/fixtures.py`, `backend/tests/` | `cd backend && uv run pytest tests/test_lead_pipeline.py -v`; `cd backend && uv run ruff check .` | Update `integration-spec.md`, `agentic-framework.md`, `eval-framework.md` | Phase 1 backend scaffold | Backlog: adapter/company-trigger |
| Planned | feature-build | Add corporate email domain and MX validation gate | US-2.2, US-3.2; `integration-spec.md`, `scoring.md`, `security.md` | Personal domains remain hard gate failures; corporate domains validate through domain/MX checks when available; DNS failures degrade to warnings when appropriate; gate-failed leads never receive drafts | `backend/app/integrations/`, `backend/app/agents/nodes.py`, `backend/app/agents/scoring.py`, `backend/app/agents/fixtures.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `integration-spec.md`, `scoring.md`, `security.md`, `tech-debt-tracker.md` | Phase 1 backend scaffold | Backlog: adapter/email-gate |

## Exit Criteria

- Live public API behavior is isolated behind typed adapters.
- Every adapter has fixture-backed tests and a degraded-service path.
- Draftable leads keep working when one provider is unavailable.
- Hard gate failures remain inspectable and suppress drafts.
