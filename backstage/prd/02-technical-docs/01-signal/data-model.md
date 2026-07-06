# Data Model

Signal v1 uses typed API contracts and a demo-safe repository boundary. The
model is designed so a future durable database can be introduced without
changing response shapes.

## Lead Input

| Field | Type | Notes |
| --- | --- | --- |
| `contact_name` | string | Required inbound contact name |
| `email` | email | Required; used for corporate-domain and MX gates |
| `company` | string | Required company or operator name from inbound form |
| `property_address` | string | Required address or street-level property hint |
| `city` | string | Required market input |
| `state` | string | Required US state input |
| `country` | string | Required; v1 supports US leads only |
| `source` | string nullable | Optional lead-source label for future routing/scoring |
| `submitted_at` | datetime nullable | Optional inbound timestamp; server may default it |

Client input is untrusted for score, tier, gate status, source facts, draft
eligibility, and run state.

## Enrichment

`Enrichment` contains normalized facts from public APIs, cache, or fixtures.
Agents and UI consume normalized fields, not raw provider payloads.
The deterministic enrichment node receives one normalized adapter result and
stores only display-safe field values plus `SourceFact` citations.

| Field | Type | Source |
| --- | --- | --- |
| `market` | string | Input plus geocoding |
| `coordinates` | tuple nullable | Geocoding |
| `geo_confidence` | enum nullable | Geocoding confidence bucket |
| `census_geo_id` | string nullable | Census-compatible geography id |
| `renter_share` | float nullable | Census/DataUSA |
| `median_rent` | integer nullable | Census/FRED |
| `rent_growth_yoy` | float nullable | Census/FRED |
| `household_growth` | float nullable | Census/DataUSA |
| `unemployment_rate` | float nullable | FRED/DataUSA |
| `walkability_score` | integer nullable | Walkability/local-context API or fixture |
| `company_units` | integer nullable | Company context heuristic |
| `asset_type_fit` | enum nullable | Multifamily, student, SFR, commercial, unclear |
| `recent_trigger` | string nullable | News/events or company context |
| `domain_status` | enum nullable | Corporate, personal, invalid, unknown |
| `sources` | `SourceFact[]` | Citable facts for scoring and drafts |

## Source Fact

Every fact used for scoring, talking points, or draft personalization must map
to a `SourceFact`.

| Field | Type | Notes |
| --- | --- | --- |
| `source` | string | Provider or fixture category |
| `label` | string | Human-readable fact label |
| `value` | string | Display-safe fact value |
| `url` | string nullable | Public citation when available |
| `retrieved_at` | datetime nullable | Fetch/cache timestamp |
| `confidence` | enum nullable | High, medium, low, fallback |

Do not persist raw provider payloads in v1 responses.

## Gates

`GateResult` contains:

- `status`: `passed` or `failed`
- `failures`: hard failures
- `warnings`: non-blocking concerns

Hard gate failures:

- Email is personal, invalid, or has no usable corporate-domain evidence.
- Company cannot resolve to a plausible property-management, owner/operator, or
  platform-relevant entity.
- Property is non-US, cannot geocode, or cannot be mapped to a usable market.

Hard gate failures force C-tier and suppress drafts.
Warnings include optional adapter no-data states, such as unavailable local
context or trigger context, and do not suppress drafts when hard gates pass.

## Score

`ScoreBreakdown` contains:

- `total`: 0-100
- `tier`: A/B/C
- `company_fit`: 0-60
- `market_opportunity`: 0-40
- `multipliers`: bounded score additions or multiplier notes
- `why_line`: rep-readable explanation
- `components`: named component points with rationale and optional source refs

Score and tier are trusted server outputs.

## Draft

`DraftEmail` contains:

- `subject`
- `body`
- `talking_points`
- `sources`
- `generation_mode`: `llm`, `fallback_template`, or `none`
- `review_status`: `needs_review`, `copied`, or `exported`

Drafts are absent for gate-failed leads. V1 supports copy/export only; it does
not send outreach.

## Related Context

`RelatedLead` contains:

- `lead_id`
- `label`
- `reason`
- `relationship_type`: company, parent, market, submarket, repeat_inbound
- `score_impact`: optional bounded bonus note

The v1 graph is lightweight. A graph database is out of scope.

## Agent Run

`AgentRunResponse` tracks:

- `run_id`
- `lead_id`
- `status`
- `trigger`
- `execution_mode`: `inline`, `eager`, or `worker`
- `task_id`: nullable worker task id
- `worker_queue`: nullable queue name
- `current_stage`
- `steps`
- `activity_log`
- `degraded_reasons`

The activity log may show provider categories and stages, but must not include
raw emails, prompt text, draft bodies, secrets, tokens, or raw provider payloads.
Celery broker payloads should carry only identifiers and minimal metadata needed
to re-load this state through the repository boundary.
Adapter degraded reasons use provider categories and fallback/no-data states
only, for example fixture fallback or optional category unavailable, without
raw payload details.
