# ADR 0002 - Config-Driven Scoring Rubric

## Status

Accepted.

## Context

Signal scoring affects lead priority, draft eligibility, and SDR trust. The
rubric needs to be inspectable and recalibrated without hiding weights in
imperative code.

## Decision

Store the v1 scoring rubric in
`backend/app/agents/scoring-rubric.v1.json` and load it through
`SIGNAL_SCORING_CONFIG_PATH`. The Python scorer applies the configured tier
thresholds, gate-failed score, component caps, buckets, seniority and asset-type
tables, and bounded bonuses.

Related-context scoring is applied only when the scoring node receives
qualifying explicit fixture history. Hard-gate failures still force C-tier, zero
component totals, and draft suppression.

## Consequences

- Scoring assumptions are reviewable in a versioned data file.
- Future calibration can ship as a config diff plus tests.
- Weight and threshold changes still require ADR review.
