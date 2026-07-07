# Scoring

Signal uses gates, weighted fit/opportunity, and bounded bonuses. The default
weights live in the backend scoring config object and can be overridden with
`SIGNAL_SCORING_CONFIG_PATH` without changing API contracts.

## Stage 1 - Hard Gates

Failing any hard gate forces C-tier and suppresses drafts:

- Personal email domain.
- Email domain has no MX records when live domain validation is available.
- Non-US property for v1.
- Address or market cannot resolve.
- Company cannot resolve to a plausible operating entity.

Warnings do not suppress drafts but appear as flags.

## Stage 2 - Weighted Score

Total score target: 0-100.

### Company Fit - 60 Points

| Signal | Points | Notes |
| --- | ---: | --- |
| Portfolio scale | 25 | Larger portfolios have stronger operational pain |
| Contact seniority | 15 | VP/C-suite/director rank higher |
| Asset-type fit | 10 | Multifamily-oriented inputs score highest |
| Company momentum | 10 | Trigger events or scale evidence |

### Market Opportunity - 40 Points

| Signal | Points | Notes |
| --- | ---: | --- |
| Renter share | 12 | Higher renter density means more leasing demand |
| Rent level/trend | 10 | Growth suggests urgency |
| Household growth | 8 | Demand expansion |
| Labor tightness | 5 | Staffing pain proxy |
| Walkability/density | 5 | Tour and leasing volume proxy |

## Stage 3 - Bonuses

- Recent trigger event: +10.
- Repeat inbound or related graph signal: planned +10.

Bonuses are bounded by a max score of 100.

## Tiers

| Tier | Score |
| --- | --- |
| A | 75-100 |
| B | 50-74 |
| C | 0-49 or gate failed |

## Calibration Assumption

All weights are hypotheses for the take-home MVP. A production rollout should
compare score bands against meeting conversion after roughly 90 days, then
reweight the rubric in config.
