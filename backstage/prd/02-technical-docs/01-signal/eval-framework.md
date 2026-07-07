# Eval Framework

Signal evals start as deterministic fixture tests and can grow into a broader
calibration suite.

## Current Evals

Backend tests cover:

- Health endpoint.
- Gate-passed lead gets score, tier, why-line, related context, and draft.
- Gate-failed lead gets C-tier and no draft.
- Demo seed records produce deterministic A, B, C, gate-failed,
  missing-trigger, and warning-only outcomes.
- Agent run approve/pause transitions preserve the human review gate.
- Analytics summary derives dashboard KPIs from persisted lead/run snapshots.
- Scoring defaults preserve current tier behavior and can load from a config
  path.

## Required Fixture Set

Maintain seed records for:

- A-tier large-portfolio senior contact.
- B-tier good fit without urgency.
- C-tier gate failure.
- Edge case with missing news trigger.
- Edge case with warning but no hard failure.

## Future Evals

- Public API fallback check: outage returns cached/fixture values.
- Broader calibration checks after pilot outcome data exists.

## Manual Demo Checks

- Queue sorts A before B before C.
- Lead detail shows market signals and sources.
- Gate-failed detail explains why the lead should not be worked.
- Agent run shows deterministic enrichment, scoring/drafting, graph, and review.
