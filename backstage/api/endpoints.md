# API Endpoints

| Status | Method | Path | Purpose |
| --- | --- | --- | --- |
| Live | GET | `/api/v1/health` | Service health |
| Live | POST | `/api/v1/leads` | Trigger enrichment for a new lead |
| Live | GET | `/api/v1/leads` | List enriched leads |
| Live | GET | `/api/v1/leads/{lead_id}` | Get lead detail |
| Live | POST | `/api/v1/leads/seed` | Reset deterministic demo leads |
| Planned | POST | `/api/v1/leads/{lead_id}/draft/copy` | Record reviewed draft copy action |
| Planned | POST | `/api/v1/leads/{lead_id}/draft/export` | Record reviewed draft export action |
| Live | GET | `/api/v1/agent-runs` | List agent runs |
| Live | GET | `/api/v1/agent-runs/{run_id}` | Get run detail |

See `backstage/prd/02-technical-docs/01-signal/api-specification.md` for
request and response shapes.
