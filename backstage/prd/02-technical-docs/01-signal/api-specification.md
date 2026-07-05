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
  "contact_name": "Demo Contact",
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

## Planned Endpoints

- `POST /leads/seed` for demo fixture reset.
- `POST /agent-runs/{run_id}/approve` for human review.
- `POST /agent-runs/{run_id}/pause` for run control.
- `GET /analytics/summary` for dashboard KPIs.
