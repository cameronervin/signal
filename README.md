# Signal

Signal is a completed GTM practical-assignment build for automating and
augmenting the inbound sales lead process with public/free data APIs. The
assignment starts from sparse lead inputs - name, email, company, role, and
property location - and asks for enriched, scored, outreach-ready leads plus a
rollout plan for a sales organization.

Signal's product answer is intentionally focused: help an SDR decide who to work
first, what to say, and how urgently to act. It accepts a new inbound lead
through an API trigger, enriches the record with public-data signals, scores and
explains fit, builds related-lead context, and prepares cited outreach for human
review.

## What It Does

- **Takes lead inputs:** contact, company, email, role, property address, city,
  state, and country.
- **Runs on a trigger:** `POST /api/v1/leads` queues the lead-intelligence
  pipeline, mirroring how a CRM webhook or lead-list trigger would hand off a
  new inbound record.
- **Enriches with public data:** geocoding, market demographics, economic
  context, company/background signals, and corporate email validation are
  normalized into inspectable source facts.
- **Scores and ranks leads:** config-driven gates, weighted score components,
  tiers, why-lines, flags, and top-market summaries make prioritization
  explainable.
- **Prepares outreach safely:** draft emails include cited personalization and
  stay behind human review; hard-gate-failed leads never expose a draft.
- **Shows the rep workflow:** the Next.js workspace includes dashboard KPIs,
  ranked queue, lead detail, source chips, editable drafts, knowledge graph
  context, gate-failed states, and Digital Worker sandbox handoff/progress.
- **Supports rollout review:** seeded A/B/C and edge-case records, mocked
  contract tests, evaluation docs, and rollout notes make the demo repeatable
  without relying on live provider behavior.

## How To Review It

Use the root docs as the assignment narrative and evidence trail:

- `backstage/prd/README.md` - MVP scope and product surfaces.
- `backstage/prd/03-implementation/_implementation-plan.md` - completed phase
  evidence.
- `backstage/prd/02-technical-docs/01-signal/rollout.md` - sales-org rollout,
  success metrics, and production-hardening boundaries.
- `backstage/guides/setup.md` - full local infrastructure and seed-data guide.

The shortest local walkthrough is: start the backend, worker, and frontend;
seed demo leads; open the dashboard; review the inbound queue; inspect a
gate-passed lead draft; inspect a gate-failed no-draft lead; then assign an
eligible lead to the Digital Worker sandbox flow.

## Quick Start

```bash
# Backend
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend
cd frontend
pnpm install
pnpm dev
```

Backend API docs: `http://127.0.0.1:8000/docs`

Frontend app: `http://localhost:3000`

## Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js App Router, TypeScript, Tailwind CSS v4, TanStack Query, Zustand |
| Backend | FastAPI, Pydantic v2, LangGraph, Celery, LiteLLM, httpx, structlog |
| Data v1 | Postgres/SQLAlchemy repository with DTO snapshot records |
| Tests | pytest for backend, Vitest and React Testing Library for frontend |

## Repository Map

```text
backend/      FastAPI API, LangGraph pipeline, public API adapters, tests
frontend/     Next.js SDR workspace and typed API adapters
backstage/    Product specs, architecture, API docs, setup guides, decisions
AGENTS.md     Primary instructions for coding agents working in this repo
```

## Development Flow

1. Read `AGENTS.md`.
2. Read the relevant files in `backstage/prd/` and `backstage/architecture/`.
3. Implement in small, tested slices.
4. Update docs after behavior changes.
5. Run the relevant backend and frontend verification commands.

The repo should not contain third-party brand references. Keep product copy and
documentation centered on Signal.
