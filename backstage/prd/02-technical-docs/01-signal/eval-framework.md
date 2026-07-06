# Eval Framework

Signal evals start as deterministic fixture tests and can grow into a broader
calibration suite.

## Current Evals

Backend tests cover:

- Health endpoint.
- Gate-passed lead gets score, tier, why-line, related context, and draft.
- Gate-failed lead gets C-tier and no draft.

## Required Fixture Set

Maintain fixtures for:

- A-tier large-portfolio senior contact.
- B-tier good fit without urgency.
- C-tier gate failure.
- Edge case with missing news trigger.
- Edge case with warning but no hard failure.

## Future Evals

- Score distribution check across seeded leads.
- Draft citation check: every personalization claim maps to a source fact.
- Gate-fail safety check: no draft body or send action is exposed.
- Public API fallback check: outage returns cached/fixture values.
- Human review check: agent runs cannot advance to send without approval.

## Manual Demo Checks

- Queue sorts A before B before C.
- Lead detail shows market signals and sources.
- Gate-failed detail explains why the lead should not be worked.
- Agent run shows deterministic enrichment, scoring/drafting, graph, and review.
