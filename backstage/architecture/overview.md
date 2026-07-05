# Architecture Overview

Signal is a small monorepo with three collaboration surfaces:

- `backend/` owns APIs, enrichment orchestration, scoring, and agent runs.
- `frontend/` owns the SDR workspace.
- `backstage/` owns product, architecture, and rollout documentation.

## Request Lifecycle

```text
POST /api/v1/leads
  -> LeadService.create_and_enrich
  -> LangGraph run
     -> deterministic_enrichment
     -> agent_scoring_and_drafting
     -> knowledge_graph_builder
  -> InMemorySignalRepository
  -> LeadResponse + AgentRunResponse
```

## Boundaries

- Routes parse and return DTOs.
- Services orchestrate use cases.
- Repositories persist product records.
- Agent nodes transform typed state.
- Integrations normalize public API payloads into source facts.

## V1 Persistence

The scaffold uses `InMemorySignalRepository` to keep setup fast. A later phase
can introduce PostgreSQL and SQLAlchemy without changing API response models.

## V1 Agent Runtime

The graph is compiled per run in `backend/app/agents/graph.py`. That is fine for
the scaffold. If graph construction becomes expensive, cache the compiled graph
behind a service dependency.
