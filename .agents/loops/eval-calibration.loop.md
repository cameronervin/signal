# Eval Calibration Loop

Use this for scoring, prompt, enrichment, and fixture tuning.

## Context Pack

Read:

- `backstage/prd/02-technical-docs/01-signal/scoring.md`
- `backstage/prd/02-technical-docs/01-signal/eval-framework.md`
- `backend/app/agents/scoring.py`
- `backend/app/agents/fixtures.py`

## Loop

1. Define the calibration question.
2. Add or update a fixture case.
3. Run the graph or service test.
4. Inspect gates, score components, tier, why-line, flags, and draft citations.
5. Adjust config or prompt, not hidden code paths.
6. Record assumptions in the scoring spec.

## Convergence

Stop when the expected tier and explanation are stable across the fixture set.
