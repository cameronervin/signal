# Signal PRD

Signal is an inbound lead intelligence MVP for SDR teams. It accepts sparse lead
records, enriches them with public data, scores and explains fit, and prepares
reviewable outreach drafts with cited personalization.

## MVP Goal

Help a sales rep answer three questions:

1. Who should I work first?
2. What should I say?
3. How urgently should I act?

Anything that does not support those questions is out of scope for v1.

## In Scope

- API-triggered lead intake.
- Deterministic enrichment with public data adapters.
- LangGraph pipeline: enrichment, scoring/drafting, graph context.
- Config-driven gates and score components.
- SDR queue sorted by tier and score.
- Lead detail with enrichment, flags, related context, and draft.
- Agent run status surface with human review gate.
- Fixture/cache fallback for demo reliability.

## Out of Scope For V1

- Live CRM integration.
- Automatic email sending.
- Paid data providers.
- Full graph database.
- Production auth and permissions.
- Large analytics dashboard beyond demo KPIs.

## Docs

| File | Purpose |
| --- | --- |
| `01-user-stories/_master-user-stories.md` | MVP user stories |
| `02-technical-docs/01-signal/data-model.md` | Lead, enrichment, score, run models |
| `02-technical-docs/01-signal/api-specification.md` | FastAPI contracts |
| `02-technical-docs/01-signal/agentic-framework.md` | LangGraph pipeline |
| `02-technical-docs/01-signal/scoring.md` | Gates, weights, tiers, assumptions |
| `02-technical-docs/01-signal/integration-spec.md` | Public APIs and fallbacks |
| `02-technical-docs/01-signal/eval-framework.md` | Demo and scoring eval strategy |
| `02-technical-docs/01-signal/security.md` | Data handling and safety constraints |
| `02-technical-docs/01-signal/rollout.md` | Demo, shadow, pilot, and rollout plan |
| `03-implementation/_implementation-plan.md` | Phase roadmap |
| `03-implementation/phase-1-foundations.md` | Completed scaffold and doc foundation |
| `03-implementation/phase-2-live-public-api-adapters.md` | Cache-backed public data adapters |
| `03-implementation/phase-3-sdr-workflow-polish.md` | SDR workspace and review workflow polish |
| `03-implementation/phase-4-rollout-evaluation.md` | Demo readiness, evals, and rollout evidence |
