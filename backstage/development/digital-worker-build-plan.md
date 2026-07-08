# SDR Digital Worker Backend Build Plan

## Summary

This plan adds a new backend domain for the SDR Digital Worker behind the
Digital Workforce product surface. The worker is assigned by an SDR to a
qualified inbound lead after the existing lead-intelligence pipeline has
produced a gate-passed lead snapshot and review-ready draft. Once assigned, the
worker can send the existing draft to a sandbox email outbox, wake on inbound
email triggers, schedule follow-ups, and expose durable progress for SDR
check-ins.

The existing `/api/v1/agent-runs` API remains the historical lead-intelligence
run surface. The new worker is long-lived and communication-oriented, so it gets
separate assignment, run, message, goal, and follow-up state under
`/api/v1/digital-workforce`.

## Current State

- Signal stores completed lead snapshots and lead-intelligence run snapshots in
  Postgres through `SignalSnapshotRepository`.
- The lead-intelligence graph stops at human review and never sends outreach.
- The frontend already has a Digital Workforce preview, but the backend has no
  persistent worker assignment, sandbox send, inbound-message trigger, or
  heartbeat follow-up mechanism.
- Celery already executes queued lead-intelligence runs, and Redis-backed Celery
  is part of the local stack.

## Target Architecture

```text
POST /api/v1/digital-workforce/assignments
  -> DigitalWorkerService.assign_lead
  -> validate completed lead snapshot, gates passed, draft present
  -> digital_worker_assignments + goal rows
  -> queue signal.digital_worker.execute
  -> worker sends existing draft to sandbox email outbox
  -> schedules first follow-up

POST /api/v1/digital-workforce/assignments/{assignment_id}/inbound-email
  -> store inbound message body in Postgres
  -> queue signal.digital_worker.execute with trigger inbound_email
  -> worker updates lifecycle goals and schedules or closes next step

Celery Beat
  -> signal.digital_worker.scan_due_follow_ups
  -> claim due pending follow-ups
  -> queue signal.digital_worker.execute for each assignment
```

Postgres is the authoritative worker memory for v1. The worker graph/executor
loads case state on every invocation, reads a repo-versioned lifecycle JSON
spec, executes a bounded tool set, persists state, then exits. This keeps the
system inspectable and avoids hidden in-memory continuity.

## Key Changes

- Add a repo-versioned lifecycle spec at
  `backend/app/agents/context/lifecycle_specs/qualify_to_meeting.v1.json`.
  Initial phases are `initial_outreach`, `reply_qualification`,
  `objection_or_follow_up`, `meeting_handoff`, and `closed_outcome`.
- Add `backend/app/schemas/digital_worker.py` with typed Pydantic request and
  response contracts for assignments, runs, messages, goals, and follow-ups.
- Add SQLAlchemy records and an Alembic migration for:
  `digital_worker_assignments`, `digital_worker_runs`,
  `digital_worker_goal_states`, `digital_worker_messages`, and
  `digital_worker_follow_ups`.
- Add `DigitalWorkerRepository` and `DigitalWorkerService` boundaries. Routes
  remain thin and only translate service errors into HTTP status codes.
- Add a bounded digital worker LangGraph workflow inside the existing agent
  layers instead of a standalone `agents/digital_worker/` package:
  `agents/chains/digital_worker.py`, `agents/states/digital_worker_state.py`,
  `agents/nodes/digital_worker.py`, `agents/graphs/digital_worker.py`,
  `agents/executors/digital_worker.py`, `agents/prompts/digital_worker.py`,
  `agents/tools/digital_worker.py`, and
  `agents/context/digital_worker_lifecycle.py`.
- Compile the workflow through `SignalGraphProvider.digital_worker_graph()`.
  Nodes receive `Runtime[DigitalWorkerRuntimeContext]`; the executor passes
  repositories, settings, and the lifecycle spec through invoke-time
  `context=...`.
- Mirror the existing signal builder flow with Digital Worker-specific builder
  objects: `create_digital_worker_chain_set`,
  `create_digital_worker_node_set`, `compose_digital_worker_dependencies`, and
  `compile_digital_worker_graph`. These stay separate from the signal intake
  builders while following the same chains -> nodes -> graph compilation shape.
- Explicit tools are `send_sandbox_email`, `record_inbound_email`,
  `schedule_follow_up`, `mark_goal_complete`, and `mark_phase_outcome`.
- Add Celery tasks:
  `signal.digital_worker.execute` and
  `signal.digital_worker.scan_due_follow_ups`. Configure Celery Beat to run the
  scanner every 5 minutes in UTC.

## Public Interfaces

- `POST /api/v1/digital-workforce/assignments`
  - Request: `{ "lead_id": "<uuid>" }`
  - Returns `202 DigitalWorkerAssignmentResponse`.
  - Requires a completed lead snapshot with `gates.status == "passed"` and a
    non-null draft.
  - Rejects gate-failed, no-draft, missing, and duplicate active assignments.
- `GET /api/v1/digital-workforce/assignments`
  - Returns persisted worker assignments for the Digital Workforce page.
- `GET /api/v1/digital-workforce/assignments/{assignment_id}`
  - Returns assignment detail, goals, runs, messages, follow-ups, and activity.
- `POST /api/v1/digital-workforce/assignments/{assignment_id}/inbound-email`
  - Stores a sandbox inbound email and queues the worker.
- `POST /api/v1/digital-workforce/assignments/{assignment_id}/pause`
  - Pauses the assignment and prevents worker communication actions.
- `POST /api/v1/digital-workforce/assignments/{assignment_id}/resume`
  - Reactivates the assignment and queues a worker run if work is due.

## Safety Rules

- No live email, SMS, CRM, or paid-provider dependency is added in this slice.
- Sandbox outbound email is persisted as an outbound message row only.
- Raw email bodies, draft bodies, prompts, tokens, API keys, and full emails are
  not logged.
- Client input cannot set score, tier, gate status, lifecycle goal completion,
  or assignment terminal state.
- Gate-failed leads and leads without drafts cannot be assigned.
- Existing scoring, lead gates, lead snapshots, and `/agent-runs` behavior stay
  unchanged.

## Test Plan

- Unit tests for lifecycle spec loading, initial goal creation, tool behavior,
  and service transition errors.
- Repository tests for assignment persistence, active duplicate lookup, message
  storage, run storage, and due follow-up claiming.
- API tests for assignment, detail, inbound email trigger, pause, resume, and
  rejection cases.
- Worker tests for initial sandbox send, inbound email wake-up, due follow-up
  scanner claiming, paused no-op behavior, and idempotent first-send behavior.
- Verification:
  - `cd backend && uv run pytest -v`
  - `cd backend && uv run ruff check .`

## Assumptions

- The SDR assignment action is the human handoff that authorizes sandbox email
  sending for v1.
- Full sandbox message bodies are stored for local demo continuity but are never
  logged.
- Follow-up timing is configurable later; v1 uses lifecycle defaults from the
  JSON spec.
- Production live-send, auth/RBAC, unsubscribe/compliance controls, SMS, and
  production audit policy are deferred.
