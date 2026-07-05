# Eval Framework

Signal evals start as deterministic fixture and contract tests. They should
prove that the demo stays reliable and that score, draft, citation, and safety
behavior do not regress.

## Required Evals

Backend tests should cover:

- Health endpoint.
- Lead insertion triggers a run and returns enriched/scored output.
- A-tier lead receives high score, why-line, talking points, related context,
  and cited draft.
- B-tier lead receives medium score with clear weaker-urgency explanation.
- C-tier non-gate lead receives low score with no false urgency.
- Hard-gate-failed lead receives C-tier, flags, and no draft.
- Provider outage returns cache, fixture, warning, or no-data state.
- LLM outage returns safe fallback behavior for gate-passed leads.
- Draft personalization claims map to source facts.
- Copy/export action cannot send outreach.

Frontend tests should cover:

- Queue sorts A before B before C.
- Filters/search do not hide gate-failed states incorrectly.
- Lead detail shows source facts, talking points, and score components.
- Gate-failed leads show no draft body and no copy/export action.
- Draft review/copy/export controls are explicit and accessible.
- Agent run detail shows stage and degraded-provider state.

## Required Fixture Set

Maintain fixtures for:

- A-tier large-portfolio senior contact with strong market and recent trigger.
- B-tier good fit without strong urgency.
- C-tier low-fit lead without a hard gate.
- Hard-gate-failed lead.
- Missing news/trigger edge case.
- Warning-only lead where draft remains allowed.
- LLM-unavailable fallback case.

## Manual Demo Checks

- Insert or seed a lead and show the pipeline run.
- Queue sorts by tier and score.
- Lead detail shows enriched facts, source citations, why-line, and cited draft.
- Gate-failed detail explains why the lead should not be worked and shows no
  draft.
- Copy/export updates review state without sending outreach.
- Run detail shows deterministic enrichment, LLM scoring/drafting, related
  context, and review gate.

## Calibration Checks

During shadow and pilot:

- Track speed-to-first-action for A-tier leads.
- Compare score bands with SDR manager judgment.
- Log rep feedback when a score feels wrong.
- Track draft edit distance as an adoption/quality proxy.
- Reweight only after enough labeled examples exist.
