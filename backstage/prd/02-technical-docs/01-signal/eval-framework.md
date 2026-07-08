# Eval Framework

Signal evals start as mocked contract tests, model-call tests, and reproducible
sample-data checks. They can grow into a broader calibration suite.

## Current Evals

Backend tests cover:

- Health endpoint.
- Gate-passed lead gets score, tier, why-line, related context, and draft.
- Gate-failed lead gets C-tier and no draft.
- Sample seed records produce deterministic A, B, C, gate-failed,
  missing-trigger, and warning-only outcomes.
- Public API clients are tested with mocked HTTP transports over request
  params, headers, status errors, and response parsing.
- Agent research tool registry and tool wrappers are tested for stable
  assignment, hidden injected dependencies, normalized source facts, and
  sanitized failures.
- Outreach prompt composition is tested for structured instructions, active
  tool snippets, inbound framing, grounded claims, and safe CTA guidance.
- LiteLLM calls are mocked in tests and cover success, empty response, failure,
  bounded tool calls, and no-call gate-failed paths.
- Agent run approve/pause transitions preserve the human review gate.
- Analytics summary derives dashboard KPIs from persisted lead/run snapshots.
- Scoring defaults preserve current tier behavior and can load from a config
  path.

## Required Sample Data Set

Maintain seed records for:

- A-tier large-portfolio senior contact.
- B-tier good fit without urgency.
- C-tier gate failure.
- Edge case with missing news trigger.
- Edge case with warning but no hard failure.

## Future Evals

- Broader calibration checks after pilot outcome data exists.

## Manual Operational Checks

- Queue sorts A before B before C.
- Lead detail shows market signals and sources.
- Gate-failed detail explains why the lead should not be worked.
- Agent run shows public-data enrichment, deterministic scoring, research and
  drafting, graph, and review.
