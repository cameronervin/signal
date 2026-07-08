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

Clients should use graph node `id`, graph edge `id`, and top-level related lead
`lead_id` values as stable UI identity. Display labels are rep-readable text and
may repeat across distinct graph nodes or related leads.

Drafts are omitted for hard-gate-failed leads. Draft sources are `SourceFact`
records that support personalization claims for human review.

## List Leads

`GET /leads`

Returns completed-analysis leads sorted by tier then score. Queued, running,
paused, and failed runs without completed lead snapshots do not appear in this
endpoint. Draftable leads become visible while awaiting review; gate-failed
analysis results become visible with completed run status and no draft.

## List Lead Queue

`GET /leads/queue`

Returns SDR queue rows for the inbound leads page. Completed-analysis rows are
returned first, sorted by tier and score. Queued and running submissions without
a completed lead snapshot are appended newest first as loading rows.

Response: `200 LeadQueueItemResponse[]`

```json
[
  {
    "id": "11111111-1111-4111-8111-111111111111",
    "run_id": "21111111-1111-4111-8111-111111111111",
    "state": "ready",
    "input": {
      "contact_name": "Sample Contact",
      "email": "contact@operator.example",
      "company": "Multifamily Operator",
      "role": "VP Leasing",
      "property_address": "100 Main St",
      "city": "Austin",
      "state": "TX",
      "country": "US"
    },
    "lead": "{LeadResponse}",
    "run": null
  },
  {
    "id": "11111111-2222-4222-8222-111111111111",
    "run_id": "21111111-2222-4222-8222-111111111111",
    "state": "loading",
    "input": {
      "contact_name": "Queued Contact",
      "email": "queued@operator.example",
      "company": "Multifamily Operator",
      "role": "Director Leasing",
      "property_address": "200 Main St",
      "city": "Austin",
      "state": "TX",
      "country": "US"
    },
    "lead": null,
    "run": "{AgentRunResponse}"
  }
]
```

Clients must treat `state: "loading"` rows as non-clickable because
`GET /leads/{lead_id}` still returns 404 until a completed lead snapshot exists.
Paused and failed runs without lead snapshots remain visible from
`GET /agent-runs`, not from the lead queue.

## Get Lead

`GET /leads/{lead_id}`

Returns one completed-analysis lead or 404. Queued, running, paused, and failed
runs return 404 from this endpoint until a visible lead snapshot exists.

## Delete Lead

`DELETE /leads/{lead_id}`

Deletes lead-intelligence records for one inbound lead. This removes the
completed lead snapshot, matching agent runs, and status events. Queued or
running persisted rows are deleted, but already-dispatched Celery tasks are not
revoked; workers that wake after deletion return a missing-run result.

Active or paused Digital Workforce assignments block deletion and return 409.
Missing lead intelligence returns 404.

Response: `200 LeadDeleteResponse`

```json
{
  "deleted_leads": 1,
  "deleted_agent_runs": 1,
  "deleted_status_events": 3,
  "skipped_assigned_leads": 0
}
```

## Delete All Leads

`DELETE /leads`

Deletes all lead-intelligence records except leads with active or paused Digital
Workforce assignments. Digital Workforce assignment, message, follow-up, and run
state is not deleted.

Response: `200 LeadDeleteResponse`

```json
{
  "deleted_leads": 5,
  "deleted_agent_runs": 5,
  "deleted_status_events": 15,
  "skipped_assigned_leads": 1
}
```

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

## Digital Workforce Assignments

Digital Workforce is separate from `/agent-runs`. Agent runs remain the
lead-intelligence history; Digital Workforce assignments are long-lived SDR
digital worker cases for sandbox communication follow-up.

### Create Digital Worker Assignment

`POST /digital-workforce/assignments`

Request:

```json
{
  "lead_id": "11111111-1111-4111-8111-111111111111"
}
```

Behavior:

- Requires an existing completed lead snapshot.
- Rejects gate-failed leads and leads without drafts.
- Rejects duplicate active or paused assignments for the same lead.
- Creates assignment, goal, run, and activity state.
- Queues `signal.digital_worker.execute` with the queued run id.
- The worker sends only to the sandbox email outbox.

Response: `202 DigitalWorkerAssignmentResponse`

### List Digital Worker Assignments

`GET /digital-workforce/assignments`

Returns persisted worker assignments with current phase, goal state, sandbox
messages, follow-ups, runs, and activity log.

### Get Digital Worker Assignment

`GET /digital-workforce/assignments/{assignment_id}`

Returns one assignment or 404.

### Inbound Email Trigger

`POST /digital-workforce/assignments/{assignment_id}/inbound-email`

Request:

```json
{
  "external_message_id": "optional-sandbox-id",
  "received_at": "2026-07-08T16:00:00Z",
  "subject": "Re: leasing follow-up",
  "body": "Can we schedule a call next week?"
}
```

Behavior:

- Stores the inbound sandbox email body in Postgres for worker context.
- Queues the worker with trigger `inbound_email`.
- Paused, completed, and failed assignments return 409.

Response: `202 DigitalWorkerAssignmentResponse`

### Pause Digital Worker Assignment

`POST /digital-workforce/assignments/{assignment_id}/pause`

Marks an active assignment paused. Paused assignments do not take communication
actions from inbound triggers or heartbeat scans.

### Resume Digital Worker Assignment

`POST /digital-workforce/assignments/{assignment_id}/resume`

Marks a paused assignment active and queues a `manual_resume` worker run.

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
