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

Enrichment is normalized public API context used to score inbound multifamily
leads, produce sales insights, and ground draft personalization.

| Field | Type | Source |
| --- | --- | --- |
| `market` | string | Resolved property market for scoring and outreach context |
| `coordinates` | tuple nullable | Geocoding context for property resolution |
| `renter_share` | float nullable | Leasing demand and prospect-volume signal |
| `median_rent` | integer nullable | Market context for rep review |
| `rent_growth_yoy` | float nullable | Urgency and market-pressure signal |
| `household_growth` | float nullable | Demand expansion context |
| `unemployment_rate` | float nullable | Operational capacity pressure proxy |
| `company_units` | integer nullable | Portfolio scale and follow-up complexity signal |
| `recent_trigger` | string nullable | Cited personalization or urgency signal |
| `sources` | `SourceFact[]` | Citable public facts for scoring, insights, and drafts |
| `provider_warnings` | string[] | Unavailable or failed upstream providers |

## Gates

`GateResult` contains:

- `status`: `passed` or `failed`
- `failures`: hard failures
- `warnings`: non-blocking concerns

Hard gate failures suppress draft generation.

## Score

Scores are deterministic lead-scoring outputs for SDR prioritization. They are
not set by client input or changed by the drafting model.

`ScoreBreakdown` contains:

- `total`: 0-100
- `tier`: A/B/C
- `company_fit`: 0-60
- `market_opportunity`: 0-40
- `bonuses`: bounded score additions
- `why_line`: rep-readable explanation of the top score drivers
- `components`: named component points

## Sales Insights

`LeadResponse.talking_points` contains sales insights derived from enrichment
and graph context. The API field name remains `talking_points` for compatibility,
but the product surface may label the section as Sales insights.

Insights translate public API facts into SDR-ready context, such as leasing
demand, response urgency, portfolio follow-up complexity, and related inbound
signals.

## Draft

`DraftEmail` contains:

- `subject`: review-ready draft subject line
- `body`: review-ready inbound outreach body for SDR editing
- `sources`: facts supporting cited personalization claims

Drafts are absent for gate-failed leads and are never sent automatically.

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

Graph node `id` values and related lead `lead_id` values are the stable identity
fields for clients. Rep-readable `label` values are display text only and are
not guaranteed to be unique.

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

## Lead Queue Item

`LeadQueueItemResponse` powers the inbound leads page:

- `id`: lead id for row identity.
- `run_id`: agent run id for the row.
- `state`: `ready` or `loading`.
- `input`: submitted `LeadCreate` contact and property fields.
- `lead`: completed `LeadResponse` when `state` is `ready`, otherwise null.
- `run`: current `AgentRunResponse` when `state` is `loading`, otherwise null.

Ready rows are ranked by tier and score. Loading rows represent queued or
running agent runs that do not yet have a lead snapshot, appear after ready rows
newest first, and are not clickable until analysis completes.

## Lead Delete Result

`LeadDeleteResponse` reports backend cleanup counts for lead-intelligence delete
APIs:

- `deleted_leads`: completed lead snapshots deleted.
- `deleted_agent_runs`: lead-intelligence agent runs deleted.
- `deleted_status_events`: agent run status events deleted.
- `skipped_assigned_leads`: active or paused Digital Workforce lead assignments
  skipped during bulk cleanup.

Delete APIs remove Signal lead snapshots, matching agent runs, and status
events only. They do not delete Digital Workforce assignment state, sandbox
messages, follow-ups, worker runs, Neo4j graph context, or Celery tasks already
dispatched.

## Agent Run Status Event

`AgentRunStatusEvent` records lifecycle changes:

- `id`: UUID4
- `run_id`: UUID4
- `status`
- `current_stage`
- `message`
- `payload`
- timestamp

## Digital Worker Assignment

`DigitalWorkerAssignmentResponse` tracks the long-lived SDR digital worker case:

- `assignment_id`: UUID4 worker case id.
- `lead_id`: completed lead snapshot assigned to the worker.
- `status`: `active`, `paused`, `completed`, or `failed`.
- `current_phase`: lifecycle phase from the repo-versioned spec.
- `lifecycle_version`: versioned JSON spec name.
- `latest_run_id`: most recent worker wake-up.
- `activity_log`: sanitized operational events.
- `goals`, `messages`, `follow_ups`, and `runs`: durable worker state for SDR
  progress monitoring.

Only gate-passed leads with an existing draft can be assigned. Assignment does
not alter score, tier, gates, or lead-intelligence run state.

## Digital Worker State Records

Digital Workforce writes:

- `digital_worker_assignments`: canonical case status, phase, lifecycle
  version, latest run id, lead id, and sanitized activity payload.
- `digital_worker_runs`: one bounded worker wake-up per assignment trigger.
- `digital_worker_goal_states`: phase/goal completion from the lifecycle spec.
- `digital_worker_messages`: full sandbox inbound/outbound email copies for
  local worker context.
- `digital_worker_follow_ups`: scheduled wake-ups scanned by Celery Beat.

Sandbox messages are stored for demo continuity but must not be logged. There
is no live email, SMS, CRM, or paid communication provider in this slice.

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
- Digital Workforce tables listed above for worker assignments, runs, goals,
  messages, and follow-ups.
- Neo4j, when enabled, stores graph relationships for lead context. It does not
  replace Postgres snapshots as the source of truth.

The JSON snapshot approach is intentional for this slice. It keeps the backend
aligned with the current Pydantic contracts while leaving room to normalize
lead, enrichment, score, and run records later.
