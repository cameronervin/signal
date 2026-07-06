# Scoring

Signal scoring uses gates, weighted fit/opportunity, and bounded multipliers.
The goal is not a mysterious "AI score"; the goal is a rep-readable priority
decision that can be calibrated after pilot feedback.

## Stage 1 - Hard Gates

Failing any hard gate forces C-tier and suppresses drafts:

- Email domain is personal, invalid, or lacks usable corporate-domain evidence.
- Company cannot resolve to a plausible property-management, owner/operator, or
  platform-relevant entity.
- Property is non-US, cannot geocode, or cannot be mapped to a usable market.

Warnings do not suppress drafts but appear as flags. Example warnings:

- Missing recent news trigger.
- Low geocoding confidence with usable market fallback.
- Missing walkability/local-context data.
- Company scale estimate is low-confidence.

## Stage 2 - Weighted Score

Total score target: 0-100.

Implemented configuration lives in `backend/app/agents/scoring.py` as explicit
rubric tables:

- `COMPANY_FIT_COMPONENTS` caps the company/contact fit components at 60
  points.
- `MARKET_OPPORTUNITY_COMPONENTS` caps the market/property opportunity
  components at 40 points.
- `BONUS_COMPONENTS`, `BONUS_POINTS`, and `TIER_THRESHOLDS` define bounded
  bonuses and A/B/C thresholds.

Each scored response returns component names, point values, rationales, and
source-reference labels when the component maps to an enrichment fact.

### Company And Contact Fit - 60 Points

| Signal | Points | Notes |
| --- | ---: | --- |
| Portfolio scale | 25 | Bucketed or log-scaled unit/portfolio estimate; dominant ICP signal |
| Contact seniority | 15 | C/VP/director titles score above manager or site-level titles |
| Asset-type fit | 10 | Multifamily, student, and SFR are strongest; commercial or unclear is lower |
| Company momentum | 10 | Company context, notable scale, expansion, or multi-property evidence |

### Market And Property Opportunity - 40 Points

| Signal | Points | Notes |
| --- | ---: | --- |
| Renter share | 12 | Higher renter density suggests more leasing demand |
| Rent level and trend | 10 | Higher rent and growth indicate stronger urgency |
| Population or household growth | 8 | Demand expansion and leasing volume proxy |
| Labor-market tightness | 5 | Staffing pressure proxy |
| Walkability or density | 5 | Tour volume or property desirability proxy |

Rationale: a strong market cannot rescue a bad-fit company, but a strong company
in an average market may still deserve attention.

## Stage 3 - Multipliers And Bonuses

- Recent trigger event: +10 points or equivalent bounded multiplier.
- Repeat inbound or related context signal: +10 points.
- Future CRM/form-source intent: planned only; not part of v1 unless imported
  as fixture/context data.

Bonuses are bounded by a max score of 100.

The scorer accepts related-context count as an explicit input and caps that
bonus at +10. The current fixture graph attaches related context after scoring,
so seeded calibration fixtures assert a `related_context_bonus` component at 0
until a later pipeline slice moves repeat-inbound context ahead of scoring.

## Tiers

| Tier | Score |
| --- | --- |
| A | 75-100 |
| B | 50-74 |
| C | 0-49 or gate failed |

## Why-Line Rules

Why-lines should:

- Name the strongest fit and opportunity drivers.
- Mention recent triggers or repeat inbound when they affect urgency.
- Name failed hard gates for C-tier gate failures.
- Avoid unsupported claims that do not map to source facts.

Example neutral patterns:

- `A-tier: large portfolio, senior leasing contact, high renter share, recent expansion signal.`
- `B-tier: good market fit and usable contact, but no recent trigger found.`
- `C-tier: gate failed because company and email domain could not be verified.`

## Calibration Assumption

All weights are documented hypotheses for the take-home MVP. After a pilot,
compare score bands against rep judgment, speed-to-lead, response rate, and
meeting conversion. Reweight the rubric in config after enough labeled examples
exist.

Current deterministic fixture calibration:

| Fixture handle | Tier | Company/contact | Market/property | Total |
| --- | --- | ---: | ---: | ---: |
| `a_tier` | A | 60 | 40 | 100 |
| `b_tier` | B | 42 | 27 | 69 |
| `c_tier` | C | 24 | 9 | 33 |
| `warning_only` | B | 32 | 40 | 72 |
| `missing_trigger` | B | 32 | 27 | 59 |
| `hard_gate_failed` | C | 0 | 0 | 0 |

Hard-gate failures return C-tier, zero scored component totals, a gate-failure
why-line, and no draft eligibility even when the underlying enrichment values
would otherwise score highly.
