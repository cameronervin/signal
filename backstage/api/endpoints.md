# API Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Service health |
| POST | `/api/v1/leads` | Trigger enrichment for a new lead |
| GET | `/api/v1/leads` | List enriched leads |
| GET | `/api/v1/leads/{lead_id}` | Get lead detail |
| GET | `/api/v1/agent-runs` | List agent runs |
| GET | `/api/v1/agent-runs/{run_id}` | Get run detail |

See `backstage/prd/02-technical-docs/01-signal/api-specification.md` for
request and response shapes.
