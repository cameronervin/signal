# Data Model

Signal v1 uses an in-memory repository with Pydantic contracts. The model is
shaped so it can move to SQLAlchemy/PostgreSQL without changing API responses.

## Lead Input

| Field | Type | Notes |
| --- | --- | --- |
| `contact_name` | string | Required |
| `email` | email | Used for domain gate and contact |
| `company` | string | Required |
| `role` | string nullable | Seniority signal |
| `source` | string nullable | Optional inbound source label, for example form or manual entry |
| `submitted_at` | datetime nullable | Optional client-observed submission timestamp |
| `property_address` | string | Geocoding input |
| `city` | string | Market signal |
| `state` | string | Market signal |
| `country` | string | US-only gate in v1 |

## Enrichment

| Field | Type | Source |
| --- | --- | --- |
| `market` | string | Input plus geocoding |
| `coordinates` | tuple nullable | Geocoding |
| `renter_share` | float nullable | Census/DataUSA |
| `median_rent` | integer nullable | Census/FRED |
| `rent_growth_yoy` | float nullable | Census/FRED |
| `household_growth` | float nullable | Census/DataUSA |
| `unemployment_rate` | float nullable | FRED/DataUSA |
| `company_units` | integer nullable | Company lookup heuristic |
| `recent_trigger` | string nullable | News/Wikipedia |
| `sources` | `SourceFact[]` | Citable facts |

## Gates

`GateResult` contains:

- `status`: `passed` or `failed`
- `failures`: hard failures
- `warnings`: non-blocking concerns

Hard gate failures suppress draft generation.

## Score

`ScoreBreakdown` contains:

- `total`: 0-100
- `tier`: A/B/C
- `company_fit`: 0-60
- `market_opportunity`: 0-40
- `bonuses`: bounded score additions
- `why_line`: rep-readable explanation
- `components`: named component points

## Draft

`DraftEmail` contains:

- `subject`
- `body`
- `sources`

`DraftState` contains:

- `eligible`: whether server-owned gates permit draft generation
- `status`: `awaiting_review` or `blocked`
- `reason`: failed hard gates when blocked

`ReviewState` contains:

- `status`: `awaiting_review` or `blocked`
- `human_review_required`: always true for v1 draftable outreach
- `reason`: failed hard gates when blocked

Drafts are absent for gate-failed leads. Draftable leads still require human
review before any send-like action.

## Related Context

`LeadResponse.related_context` contains related lead or account context assembled
by the graph. v1 uses in-memory fixture-style context; later phases can replace
that implementation without changing the response contract.

## Agent Run

`AgentRunResponse` tracks:

- `run_id`
- `lead_id`
- `status`
- `trigger`
- `current_stage`
- `stage_index`
- `steps`
- `activity_log`
- `degraded_reasons`

The v1 status surface is enough for polling. `activity_log` and
`degraded_reasons` must omit raw emails, prompts, draft bodies, secrets, tokens,
and provider payloads. Streaming can be added later.
