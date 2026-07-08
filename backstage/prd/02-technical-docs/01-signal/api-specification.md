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
- Creates UUID4 lead and run ids.
- Persists a queued agent run and submitted lead input.
- Queues `signal.agent_runs.execute` in Celery with `task_id` equal to the run
  UUID.
- Returns the queued run response immediately.

Response: `202 AgentRunResponse`

```json
{
  "run_id": "21111111-1111-4111-8111-111111111111",
  "lead_id": "11111111-1111-4111-8111-111111111111",
  "status": "queued",
  "trigger": "api_insert",
  "current_stage": "queued",
  "steps": [],
  "activity_log": ["api_insert: lead received", "agent_run: queued"]
}
```

The Celery worker loads the queued run from Postgres, runs the LangGraph
pipeline, and persists the resulting lead snapshot only after analysis
completes.

## Lead Response Shape

Completed lead responses include the assignment outputs reps need for inbound
lead work: deterministic scoring, public-data enrichment, sales insights,
review-ready draft outreach, citable source facts, and `knowledge_graph`.

`LeadResponse` keeps the stable `talking_points` API field name, but that array
represents sales insights for prioritization and draft personalization.

`LeadResponse.knowledge_graph` includes:

```json
{
  "nodes": [
    {
      "id": "lead:lead_123",
      "kind": "lead",
      "label": "Sample Contact",
      "subtitle": "Current inbound lead",
      "source_fact_ids": []
    }
  ],
  "edges": [
    {
      "id": "lead:lead_123:HAS_CONTACT:contact_123",
      "source": "lead:lead_123",
      "target": "contact_123",
      "relationship": "HAS_CONTACT",
      "reason": "Lead input includes this contact.",
      "confidence": 1.0,
      "source_fact_ids": []
    }
  ],
  "sources": [],
  "related_leads": [],
  "warnings": []
}
```

The legacy `related_leads` field remains in the response and is populated from
graph related-lead context when available.

Drafts are omitted for hard-gate-failed leads. Draft sources are `SourceFact`
records that support personalization claims for human review.

## List Leads

`GET /leads`

Returns completed-analysis leads sorted by tier then score. Queued, running,
paused, and failed runs do not appear in the lead queue. Draftable leads become
visible while awaiting review; gate-failed analysis results become visible with
completed run status and no draft.

## Get Lead

`GET /leads/{lead_id}`

Returns one completed-analysis lead or 404. Queued, running, paused, and failed
runs return 404 from this endpoint until a visible lead snapshot exists.

## List Agent Runs

`GET /agent-runs`

Returns current and historical v1 runs across queued, running, paused, failed,
awaiting-review, and completed statuses.

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
