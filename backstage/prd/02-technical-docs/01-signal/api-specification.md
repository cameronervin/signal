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

The FastAPI app factory wires the v1 router under `/api/v1`, keeps OpenAPI
available at `/openapi.json`, and applies explicit CORS origins from
`SIGNAL_FRONTEND_ORIGIN` plus comma-separated `SIGNAL_EXTRA_CORS_ORIGINS`.
Wildcard CORS is not part of the supported configuration.

Core backend settings use fixture-first demo defaults:

| Setting | Default | Notes |
| --- | --- | --- |
| `SIGNAL_USE_FIXTURES` | `true` | Keeps local/demo paths independent of live provider uptime. |
| `SIGNAL_API_BASE_URL` | `http://127.0.0.1:8000` | Backend origin for local clients and docs. |
| `SIGNAL_FRONTEND_ORIGIN` | `http://localhost:3000` | Primary browser origin allowed by CORS. |
| `SIGNAL_EXTRA_CORS_ORIGINS` | `http://127.0.0.1:3000` | Additional explicit browser origins. |
| `SIGNAL_SCORING_CONFIG_PATH` | `app/agents/scoring.py` | Current scoring source path until external config lands. |
| `SIGNAL_MAX_AGENT_RETRIES` | `2` | Bounded agent retry count. |
| `SIGNAL_PROVIDER_RETRY_COUNT` | `2` | Bounded live-provider retry count. |
| `SIGNAL_PROVIDER_TIMEOUT_SECONDS` | `8` | Live-provider timeout budget. |
| `SIGNAL_REQUEST_TIMEOUT_SECONDS` | `15` | General backend request timeout budget. |

Optional provider/LLM settings are `SIGNAL_NEWS_API_KEY`,
`SIGNAL_FRED_API_KEY`, `SIGNAL_OPENAI_API_KEY`,
`SIGNAL_LITELLM_GATEWAY_URL`, `SIGNAL_LITELLM_GATEWAY_KEY`, and
`SIGNAL_LLM_MODEL`. Credential values are secret inputs; app code may use only
presence checks for health or capability branching.

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
  pipeline through the configured execution mode:
  - `inline`/`eager`: executes immediately for deterministic local/demo/test
    paths.
  - `worker`: enqueues a Celery task with identifier-only payload and exposes
    progress through agent-run APIs.
- Persists normalized lead, enrichment, score, draft, related context, task id,
  execution mode, and run state in the v1 repository boundary as they become
  available.
- Returns the lead response with the current run summary. In worker mode, the
  initial response may show queued/running state before enrichment and scoring
  are complete; clients should poll the lead or run endpoints.

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

## Draft Copy State

`POST /leads/{lead_id}/draft/copy`

Behavior:

- Records that the reviewed draft was copied into the SDR's existing sales
  tools.
- Does not send email.
- Sets draft `review_status` to `copied`.
- Returns updated lead review state.

Response: `LeadResponse`

Gate-failed leads or leads with no draft return `409`.

## Draft Export State

`POST /leads/{lead_id}/draft/export`

Behavior:

- Records that the reviewed draft was exported into an existing sales workflow.
- Does not send email.
- Sets draft `review_status` to `exported`.
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
human review, execution mode, task id, queue name, and degraded-provider steps.

## Planned Beyond V1

- Read-only CRM or PMS context import.
- Production auth and RBAC.
- Durable storage.
- Approval workflow with audit logs.
- Live send or cadence behavior after compliance review.
