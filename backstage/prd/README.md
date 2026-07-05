# Signal PRD

Signal is an internal SDR workspace for an AI leasing platform vendor. It helps
SDRs work inbound demo leads from multifamily operators by turning sparse lead
records into enriched, scored, explained, and outreach-ready opportunities.

This PRD replaces the earlier directional product notes in place. Treat these
docs as the source of truth for the next implementation pass. Existing backend
and frontend code may still need alignment work called out in the implementation
plan.

## Product Goal

Help an SDR make a faster first action on each inbound demo lead:

1. Who should I work first?
2. Why is this lead worth urgent attention?
3. What reviewed message should I copy or export into the existing sales tools?

Anything that does not support those questions is out of scope for v1.

## Primary Users

| User | Need |
| --- | --- |
| SDR | Prioritize inbound demo leads, understand score drivers, and copy a reviewed draft |
| SDR manager | Trust that scoring is explainable, calibrated, and safe for pilot use |
| Demo operator | Seed reliable A/B/C and gate-failed examples for the take-home walkthrough |
| GTM or RevOps owner | Review assumptions, rollout steps, and future integration boundaries |

## In Scope For V1

- API-triggered lead intake using contact name, email, company, property address,
  city, state, and country.
- Seeded fixture leads for repeatable demo runs.
- Public API enrichment across geocoding, demographics/economics, local context,
  news/events, company context, domain quality, and LLM drafting.
- LangGraph pipeline: deterministic enrichment, LLM scoring/drafting agent, and
  lightweight related-lead graph builder.
- Config-driven hard gates, 60/40 scoring rubric, multipliers, A/B/C tiers, and
  rep-readable why-lines.
- SDR queue sorted by tier and score.
- Lead detail with enrichment facts, score explanation, flags, related context,
  talking points, cited draft, and review/copy/export controls.
- Human review before any send-like behavior.
- Fixture/cache fallbacks so demo quality does not depend on live provider
  uptime.
- Rollout plan covering MVP testing, shadow mode, pilot, stakeholders, success
  metrics, and rework criteria.

## Out Of Scope For V1

- Live email sending or autonomous follow-up.
- Production authentication and role-based permissions.
- CRM/PMS writeback or live routing changes.
- Durable production storage beyond the demo repository boundary.
- Paid data dependencies as required demo paths.
- Full graph database.
- Fully automated scheduling, cadence, or follow-up workers.

## Non-Negotiables

- Keep Signal neutral. Do not include client, prospect, competitor, or source
  company names in repo docs, code, fixtures, tests, prompts, comments, or env
  files.
- Score, tier, gate status, and draft eligibility are trusted server outcomes.
- Hard-gate-failed leads are C-tier and never receive draft bodies.
- Every draft personalization claim must be backed by a cited source fact or
  clearly fall back to generic copy.
- Public API failures must degrade through cache, fixtures, warnings, or a clear
  no-data state instead of breaking the demo.
- Raw emails, raw drafts, prompts, provider payloads, API keys, and tokens must
  not be logged.

## Docs

| File | Purpose |
| --- | --- |
| `01-user-stories/_master-user-stories.md` | Fresh v1 user stories |
| `02-technical-docs/01-signal/data-model.md` | Lead, enrichment, score, draft, graph, and run models |
| `02-technical-docs/01-signal/api-specification.md` | FastAPI contracts and planned trigger endpoints |
| `02-technical-docs/01-signal/agentic-framework.md` | LangGraph pipeline and LLM agent behavior |
| `02-technical-docs/01-signal/scoring.md` | Gates, 60/40 rubric, multipliers, tiers, and calibration |
| `02-technical-docs/01-signal/integration-spec.md` | Public API choices, fallbacks, and source fact rules |
| `02-technical-docs/01-signal/eval-framework.md` | Demo, scoring, citation, and safety eval strategy |
| `02-technical-docs/01-signal/security.md` | Data handling and safety constraints |
| `02-technical-docs/01-signal/rollout.md` | MVP test, shadow, pilot, rollout, and video narrative |
| `03-implementation/_implementation-plan.md` | One-thread implementation roadmap |
| `03-implementation/phase-1-spec-and-baseline.md` | Fresh spec and baseline alignment |
| `03-implementation/phase-2-enrichment-and-scoring.md` | Public API enrichment and scoring implementation |
| `03-implementation/phase-3-sdr-workspace.md` | Queue, detail, review, copy/export, and run UX |
| `03-implementation/phase-4-evals-rollout-demo.md` | Evals, rollout evidence, and demo readiness |
