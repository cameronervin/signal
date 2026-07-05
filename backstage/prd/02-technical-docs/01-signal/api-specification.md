# API Specification

Base path: `/api/v1`

These contracts describe the fresh target spec. Existing implementation may need
follow-up slices to match the full contract.

## Health

`GET /health`

Response:

```json
{
  "status": "ok",
  "service": "signal-api"
}
```

## Create Lead And Trigger Pipeline

`POST /leads`

Request:

```json
{
  "contact_name": "Demo Contact",
  "email": "contact@operator.example",
  "company": "Regional Housing Operator",
  "property_address": "100 Main St",
  "city": "Austin",
  "state": "TX",
  "country": "US",
  "source": "demo_request"
}
```

Behavior:

- Validates input.
- Creates a lead id and agent run id.
- Triggers the LangGraph enrichment, LLM scoring/drafting, and graph context
  pipeline.
- Persists normalized lead, enrichment, score, draft, related context, and run
  state in the v1 repository boundary.
- Returns the full lead response.

Response: `201 LeadResponse`

Validation errors return `422` with field-specific details. Unhandled provider
or LLM outages should not turn a valid lead into a 5xx response when cached,
fixture, warning, or fallback output can be returned safely.

## List Leads

`GET /leads`

Query params:

| Param | Type | Notes |
| --- | --- | --- |
| `tier` | A/B/C optional | Filter by tier |
| `status` | string optional | Filter by gate or review status |
| `q` | string optional | Search contact, company, market, or why-line |

Returns leads sorted by tier priority, score descending, and submitted time.

## Get Lead

`GET /leads/{lead_id}`

Returns one lead detail record or `404`.

Lead detail includes:

- Original input.
- Enrichment facts and source facts.
- Gates and flags.
- Score breakdown and why-line.
- Talking points.
- Draft when gate-passed.
- Related-lead context.
- Current run summary.

## Seed Demo Leads

`POST /leads/seed`

Behavior:

- Resets or inserts deterministic fixture leads for A, B, C, warning-only, and
  hard-gate-failed examples.
- Does not require live public API or LLM uptime.
- Returns created or reset lead ids and run ids.

Response: `SeedLeadsResponse`

This endpoint is intended for demo and local development only.

## Draft Review State

`POST /leads/{lead_id}/draft/copy`

Behavior:

- Records that the reviewed draft was copied or exported.
- Does not send email.
- Returns updated lead review state.

Response: `LeadResponse`

Gate-failed leads or leads with no draft return `409`.

## List Agent Runs

`GET /agent-runs`

Returns current and historical v1 runs.

## Get Agent Run

`GET /agent-runs/{run_id}`

Returns one run or `404`.

Run detail includes deterministic enrichment, LLM scoring/drafting, graph build,
human review, and degraded-provider steps.

## Planned Beyond V1

- Read-only CRM or PMS context import.
- Production auth and RBAC.
- Durable storage.
- Approval workflow with audit logs.
- Live send or cadence behavior after compliance review.
