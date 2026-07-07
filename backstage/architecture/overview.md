# Architecture Overview

Signal is a small monorepo with three collaboration surfaces:

- `backend/` owns APIs, enrichment orchestration, scoring, and agent runs.
- `frontend/` owns the SDR workspace.
- `backstage/` owns product, architecture, and rollout documentation.

## Request Lifecycle

```text
POST /api/v1/leads
  -> LeadService.create_and_enrich
  -> SignalPipelineExecutor
     -> deterministic_enrichment
     -> agent_scoring_and_drafting
     -> knowledge_graph_builder
  -> SignalRepository
     -> InMemorySignalRepository by default
     -> PostgresSignalRepository when SIGNAL_REPOSITORY_BACKEND=postgres
  -> LeadResponse + AgentRunResponse
```

## Boundaries

- Routes parse and return DTOs.
- Services orchestrate use cases.
- Repositories persist product records.
- Agent executors run bounded LangGraph graphs.
- Agent nodes transform typed state.
- Infrastructure normalizes public API payloads into source facts.
- Infrastructure owns swappable DB, LLM, and public data provider setup.

## V1 Persistence

The default scaffold still uses `InMemorySignalRepository` to keep setup fast.
Set `SIGNAL_REPOSITORY_BACKEND=postgres` to use `PostgresSignalRepository`,
which stores stable Pydantic response DTO snapshots in Postgres through
SQLAlchemy async sessions while indexing queue and run fields. This preserves
API response models while the relational model matures.

## V1 Agent Runtime

Agent code follows the Playbook package shape directionally:

```text
backend/app/agents/
  graph_provider.py  cached compiled graph provider
  runtime_context.py per-run LangGraph context
  builders/    chains -> nodes -> graph compilation
  chains/      outreach_drafting.py deterministic draft chain
  guardrails/  qualification.py hard-gate checks before draft output
  states/      typed LangGraph state
  nodes/       lead_intelligence.py node factories for graph steps
  graphs/      lead_intelligence.py uncompiled graph topology assembly
  executors/   inline and worker-facing graph execution
  prompts/     prompt-facing instructions
  tools/       deterministic public-data tool wrappers
  utils/       pure scoring/text helpers
```

The current HTTP lead-create path runs inline so it can preserve the existing
`201 LeadResponse` contract. `app.workers.tasks.execute_signal_agent_run` is the
Celery worker entrypoint for moving agent execution behind a queued contract in
the next slice.

Graph compilation follows the Playbook pattern: `chains_builder` creates the
workflow chain set, `nodes_builder` creates node closures from chains/tools,
`graphs_builder` composes and compiles the topology, and `SignalGraphProvider`
keeps a dependency-keyed process-local compiled graph cache.

Signal intentionally keeps one workflow-level executor for v1, while the modules
inside `chains/`, `nodes/`, `graphs/`, and `guardrails/` are named for their
actual responsibility. That avoids a stack of same-named `signal_pipeline.py`
files as the product adds review, approval, and worker-backed execution slices.

## Public Data Boundary

`backend/app/infrastructure/public_data/` owns live public API clients for
geocoding, ACS market data, DataUSA household context, FRED economic series,
News API triggers, Wikipedia search, and DNS/MX validation. The provider caches
responses by lead payload and falls back to deterministic fixtures when
`SIGNAL_USE_FIXTURES=true` or a provider fails.

## LLM Boundary

`backend/app/infrastructure/llm/` exposes a LiteLLM provider boundary. The
deterministic draft path remains the default runtime behavior for demo
reliability, and LiteLLM can be wired into drafting once the human-review flow
is ready for non-deterministic model output.
