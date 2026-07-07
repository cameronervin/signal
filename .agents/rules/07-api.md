# API Rules

Base path: `/api/v1`.

## Current Surfaces

- `GET /health`
- `POST /leads`
- `GET /leads`
- `GET /leads/{lead_id}`
- `GET /agent-runs`
- `GET /agent-runs/{run_id}`
- `POST /agent-runs/{run_id}/approve`
- `POST /agent-runs/{run_id}/pause`
- `GET /analytics/summary`

## Do

- Keep routes thin.
- Use Pydantic request and response models.
- Return server-generated score, tier, gates, draft state, and run state.
- Use proper validation and transition errors.
- Update `backstage/prd/02-technical-docs/01-signal/api-specification.md` after behavior changes.

## Avoid

- Raw dict response contracts.
- Client-controlled trusted fields.
- Send/outreach endpoints in v1.
- Exposing internal provider payloads or secrets.
