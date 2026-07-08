# Data Model

Signal v1 uses Pydantic contracts at the API boundary. Postgres stores DTO
snapshots through SQLAlchemy async models without changing API responses, and
Alembic owns schema creation and migrations.

## Lead Input

| Field | Type | Notes |
| --- | --- | --- |
| `contact_name` | string | Required |
| `email` | email | Used for domain gate and contact |
| `company` | string | Required |
| `role` | string nullable | Seniority signal |
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
| `provider_warnings` | string[] | Unavailable or failed upstream providers |

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

Drafts are absent for gate-failed leads.

## Knowledge Graph

`LeadKnowledgeGraph` contains:

- `nodes`: bounded graph nodes for the current lead, contact, company,
  property, market, source facts, triggers, and related leads.
- `edges`: graph relationships with `reason`, `confidence`, and supporting
  source fact ids.
- `sources`: citable graph source facts derived from normalized enrichment
  facts.
- `related_leads`: structured related-lead records used to preserve the legacy
  `related_leads` response field.
- `warnings`: explicit graph storage or retrieval warnings.

Neo4j stores relationship-native graph context when
`SIGNAL_KNOWLEDGE_GRAPH_ENABLED=true`. Postgres remains the canonical store for
lead and run DTO snapshots. Disabled or unavailable graph storage returns a
current-lead projection plus graph warnings.

## Agent Run

`AgentRunResponse` tracks:

- `run_id`: UUID4
- `lead_id`: UUID4
- `status`
- `trigger`
- `current_stage`
- `steps`
- `activity_log`

The v1 status surface is enough for polling. Streaming can be added later.
Postgres is the source of truth for queued, running, paused, failed,
awaiting-review, and completed statuses.

## Agent Run Status Event

`AgentRunStatusEvent` records lifecycle changes:

- `id`: UUID4
- `run_id`: UUID4
- `status`
- `current_stage`
- `message`
- `payload`
- timestamp

## Persistence Records

Signal writes:

- `signal_leads`: UUID lead id, UUID run id, tier, score total, market, gate
  status, timestamps, and the serialized `LeadResponse` payload. Records are
  only written after analysis completes.
- `signal_agent_runs`: UUID run id, UUID lead id, Celery task id, status,
  trigger, current stage, submitted lead input, lifecycle timestamps, and the
  serialized `AgentRunResponse` payload.
- `signal_agent_run_status_events`: UUID event id, UUID run id, status, stage,
  optional message/payload, and timestamp.
- Neo4j, when enabled, stores graph relationships for lead context. It does not
  replace Postgres snapshots as the source of truth.

The JSON snapshot approach is intentional for this slice. It keeps the backend
aligned with the current Pydantic contracts while leaving room to normalize
lead, enrichment, score, and run records later.
