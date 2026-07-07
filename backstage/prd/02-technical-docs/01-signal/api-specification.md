# API Specification

Base path: `/api/v1`

## Health

`GET /health`

Response:

```json
{
  "status": "ok",
  "service": "signal-api"
}
```

## Create Lead

`POST /leads`

Request:

```json
{
  "contact_name": "Sample Contact",
  "email": "contact@operator.example",
  "company": "Multifamily Operator",
  "role": "VP Leasing",
  "property_address": "100 Main St",
  "city": "Austin",
  "state": "TX",
  "country": "US"
}
```

Behavior:

- Validates input.
- Creates lead and run ids.
- Invokes the LangGraph pipeline.
- Persists the enriched lead and run in the v1 repository.
- Returns the full lead response.

Response: `201 LeadResponse`

## List Leads

`GET /leads`

Returns leads sorted by tier then score.

## Get Lead

`GET /leads/{lead_id}`

Returns one lead or 404.

## List Agent Runs

`GET /agent-runs`

Returns current and historical v1 runs.

## Get Agent Run

`GET /agent-runs/{run_id}`

Returns one run or 404.

## Approve Agent Run

`POST /agent-runs/{run_id}/approve`

Marks an `awaiting_review` run as reviewed and completed. Approval never sends
outreach. Invalid transitions return 409.

Response: `200 AgentRunResponse`

## Pause Agent Run

`POST /agent-runs/{run_id}/pause`

Marks a `queued`, `running`, or `awaiting_review` run as paused. Invalid
transitions return 409.

Response: `200 AgentRunResponse`

## Analytics Summary

`GET /analytics/summary`

Returns dashboard KPIs derived from current lead and run records:

```json
{
  "total_leads": 6,
  "tier_distribution": {"A": 2, "B": 2, "C": 2},
  "awaiting_review_count": 5,
  "gate_failed_count": 1,
  "average_score": 67.5,
  "top_markets": [{"market": "Austin, TX", "lead_count": 2}]
}
```

## Sample Seed Script

Seed sample data through the backend script, not a public API endpoint:

```bash
cd backend
uv run alembic upgrade head
uv run python scripts/seed_demo_leads.py
```

The script writes deterministic A/B/C, gate-failed, missing-trigger, and
warning-only records through the normal service and repository path.

## Deferred Endpoints

- Send/outreach endpoints remain out of scope for v1.
