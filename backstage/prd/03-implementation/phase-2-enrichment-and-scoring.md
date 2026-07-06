# Phase 2 - Enrichment And Scoring

## Goal

Implement public API enrichment, LLM scoring/drafting, gates, scoring rubric,
related context, and fixture/cache fallbacks.

## Agent Threads

| Status | Agent Loop | Goal | Story/Spec Refs | Acceptance Criteria | Likely Touch Points | Validation | Docs | Dependencies | Issue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Planned | feature-build | Add public API adapter boundary, cache contract, and fixture fallback framework | US-2.1, US-2.2, US-6.1; `integration-spec.md`, `security.md` | Adapters return typed normalized results; cache/fixture fallback behavior is shared; provider errors are sanitized; no raw provider payloads or secrets are logged; tests cover timeout/missing-key fallback | `backend/app/integrations/`, `backend/app/core/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `integration-spec.md`, `security.md`, `tech-debt-tracker.md` | Backend contracts; backend core infrastructure | [#12](https://github.com/cameronervin/signal/issues/12) |
| Planned | feature-build | Implement geocoding, demographics, economics, local-context, company, news, and DNS/MX enrichment adapters | US-2.1, US-2.2, US-3.1; `integration-spec.md`, `data-model.md`, `agentic-framework.md` | Required public sources normalize into source facts; hard gates evaluate address, company, and domain quality; missing optional data becomes warnings; fixture-backed tests cover success and degraded paths | `backend/app/integrations/`, `backend/app/agents/nodes.py`, `backend/app/agents/fixtures.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `integration-spec.md`, `agentic-framework.md`, `data-model.md` | Adapter fallback boundary; backend core infrastructure | [#13](https://github.com/cameronervin/signal/issues/13) |
| Planned | feature-build | Implement LLM scoring/drafting agent with safe fallback behavior | US-3.1, US-3.2, US-4.1, US-4.2; `agentic-framework.md`, `scoring.md`, `security.md` | LLM node uses the provider abstraction, produces score rationale, talking points, cited draft for gate-passed leads; gate-failed leads receive no draft; LLM outage uses deterministic score and marked fallback template; prompts/drafts are not logged | `backend/app/agents/`, `backend/app/services/`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `agentic-framework.md`, `security.md`, `eval-framework.md` | Public API enrichment suite; LiteLLM provider abstraction (#30) | [#15](https://github.com/cameronervin/signal/issues/15) |
| Planned | eval-calibration | Implement documented 60/40 scoring rubric, multipliers, tiers, and calibration fixtures | US-3.1, US-3.2, US-5.1; `scoring.md`, `eval-framework.md` | Gates force C-tier; A/B/C thresholds match spec; component scores sum correctly; recent trigger and related-context bonuses are bounded; fixtures assert expected why-lines and tiers | `backend/app/agents/scoring.py`, `backend/app/agents/fixtures.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `scoring.md`, `eval-framework.md` | Enrichment facts available | [#14](https://github.com/cameronervin/signal/issues/14) |
| Planned | feature-build | Build lightweight related-context graph and run status surface | US-5.1, US-5.2; `agentic-framework.md`, `data-model.md`, `api-specification.md` | Related context links by company, parent/portfolio hint, market, or repeat inbound; run detail exposes stages, task id, execution mode, queue, and degraded reasons; no graph database required; tests cover related bonus eligibility and worker status visibility | `backend/app/agents/`, `backend/app/repositories/`, `backend/app/api/v1/agents.py`, `backend/tests/` | `cd backend && uv run pytest -v`; `cd backend && uv run ruff check .` | Update `agentic-framework.md`, `data-model.md`, `api-specification.md` | Backend contracts; scoring rubric; lead read API; Celery worker execution path (#31) | [#16](https://github.com/cameronervin/signal/issues/16) |

## Exit Criteria

- At least two live public API adapters work, and all required adapter categories
  have fixture/cache fallback behavior.
- Gates, 60/40 scoring, multipliers, and tiers are test-protected.
- LLM drafting is available through the provider abstraction with safe fallback
  behavior.
- Related context and run states are visible through backend contracts.
