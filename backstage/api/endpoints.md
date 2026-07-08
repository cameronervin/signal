# API Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Service health |
| POST | `/api/v1/leads` | Queue enrichment for a new lead and return `202 AgentRunResponse` |
| GET | `/api/v1/leads` | List completed-analysis leads |
| GET | `/api/v1/leads/{lead_id}` | Get completed-analysis lead detail |
| GET | `/api/v1/agent-runs` | List agent runs across queued/running/final states |
| GET | `/api/v1/agent-runs/{run_id}` | Get run detail |
| POST | `/api/v1/agent-runs/{run_id}/approve` | Mark a review-gated run approved without sending outreach |
| POST | `/api/v1/agent-runs/{run_id}/pause` | Pause a queued, running, or review-gated run |
| POST | `/api/v1/digital-workforce/assignments` | Assign SDR Digital Worker to a gate-passed drafted lead |
| GET | `/api/v1/digital-workforce/assignments` | List Digital Worker assignments |
| GET | `/api/v1/digital-workforce/assignments/{assignment_id}` | Get Digital Worker assignment progress |
| POST | `/api/v1/digital-workforce/assignments/{assignment_id}/inbound-email` | Store sandbox inbound email and wake the worker |
| POST | `/api/v1/digital-workforce/assignments/{assignment_id}/pause` | Pause Digital Worker assignment |
| POST | `/api/v1/digital-workforce/assignments/{assignment_id}/resume` | Resume Digital Worker assignment and queue worker |
| GET | `/api/v1/analytics/summary` | Dashboard KPI summary |

See `backstage/prd/02-technical-docs/01-signal/api-specification.md` for
request and response shapes.
