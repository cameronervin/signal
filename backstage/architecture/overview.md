# Architecture Overview

Signal is a small monorepo with three collaboration surfaces:

- `backend/` owns APIs, enrichment orchestration, scoring, and agent runs.
- `frontend/` owns the SDR workspace.
- `backstage/` owns product, architecture, and rollout documentation.

## Request Lifecycle

```text
POST /api/v1/leads
  -> LeadIntakeService.create_and_enqueue
  -> signal_agent_runs queued row + status event
  -> Celery execute_signal_agent_run task
  -> 202 AgentRunResponse

Celery worker
  -> loads queued run and lead input from Postgres
  -> marks run running
  -> SignalPipelineExecutor
     -> deterministic_enrichment
     -> knowledge_graph_ingest
     -> graph_context_retrieval
     -> deterministic_scoring
     -> agent_research_and_drafting
     -> knowledge_graph_builder
  -> SignalSnapshotRepository completed-analysis lead/run snapshots
```

## Boundaries

- Routes parse and return DTOs, with FastAPI dependency wiring centralized in
  `backend/app/api/v1/dependencies.py`.
- Services orchestrate use cases.
- Repositories persist product records.
- Agent executors run bounded LangGraph graphs.
- Agent nodes transform typed state.
- Infrastructure normalizes public API payloads into source facts.
- Infrastructure owns swappable DB, LLM, and public data provider setup.
- Infrastructure owns optional Neo4j driver setup and graph repository
  implementations.

## V1 Persistence

Signal uses `SignalSnapshotRepository`, which stores stable Pydantic response
DTO snapshots in Postgres through SQLAlchemy async sessions while indexing queue
and run fields such as tier, score, market, gate status, run status, and run
trigger. Primary identifiers are UUID4 values stored in native Postgres UUID
columns. Agent run lifecycle changes are recorded in
`signal_agent_run_status_events`. Alembic owns schema creation and migrations.
This preserves API response models while the relational model matures.

Neo4j is an optional relationship store for lead graph context. It is enabled
with `SIGNAL_KNOWLEDGE_GRAPH_ENABLED` and stores current lead, contact, company,
property, market, source fact, trigger, and related-lead relationships. Postgres
remains the canonical source of truth for lead and run snapshots.

## V1 Agent Runtime

Agent code follows the Playbook package shape directionally:

```text
backend/app/agents/
  graph_provider.py  cached compiled graph provider
  runtime_context.py per-run LangGraph context
  builders/    chains -> nodes -> graph compilation
  chains/      outreach_drafting.py LiteLLM-backed draft chain
  guardrails/  qualification.py hard-gate checks before draft output
  states/      typed LangGraph state
  nodes/       lead_intelligence.py node factories for graph steps
  graphs/      lead_intelligence.py uncompiled graph topology assembly
  executors/   inline and worker-facing graph execution
  prompts/     prompt-facing instructions
  tools/       deterministic wrapper + model-callable public-data tools
  utils/       pure scoring/text helpers
```

The HTTP lead-create path queues a Celery task and returns `202 AgentRunResponse`
with queued status. `app.workers.tasks.execute_signal_agent_run` is the Celery
worker entrypoint that loads queued run input from Postgres, runs the graph, and
persists completed analysis results. Celery's result backend is operational
metadata only; Signal APIs read run and lead state from Postgres.

Graph compilation follows the Playbook pattern: `chains_builder` creates the
workflow chain set with active research tools, `nodes_builder` creates node
closures from chains/tools, `graphs_builder` composes and compiles the topology,
and `SignalGraphProvider` keeps a dependency-keyed process-local compiled graph
cache.

Signal intentionally keeps one workflow-level executor for v1, while the modules
inside `chains/`, `nodes/`, `graphs/`, and `guardrails/` are named for their
actual responsibility. That avoids a stack of same-named `signal_pipeline.py`
files as the product adds review, approval, and worker-backed execution slices.

## Public Data Boundary

`backend/app/infrastructure/public_data/` owns live public API clients for
geocoding, ACS market data, DataUSA household context, FRED economic series,
News API triggers, Wikipedia search, and DNS/MX validation. The provider caches
responses by lead payload and surfaces provider failures as warnings or omitted
facts.

The FastAPI lifespan owns app-duration infrastructure: settings, DB
sessionmaker, a shared HTTPX async client, public-data provider, LiteLLM
provider, optional knowledge graph service, and compiled Signal graph provider
are warmed once and attached to `app.state`. Startup is intentionally warm-only;
it does not connect to the database, call public APIs, verify LiteLLM, verify
Neo4j connectivity, or create schemas. Celery workers own the same kind of
process-local resources through worker lifecycle signals so queued graph
execution can reuse compiled graphs and shared HTTP pooling.

## Knowledge Graph Boundary

`backend/app/services/knowledge_graph_service.py` owns deterministic entity
normalization, current-lead graph projection, and related-lead relationship
rules. `backend/app/infrastructure/knowledge_graph/` owns the disabled fallback
repository, Neo4j async driver setup, and Cypher. Disabled or unavailable Neo4j
returns a current-lead graph projection with explicit graph warnings.

## LLM Boundary

`backend/app/infrastructure/llm/` exposes a LiteLLM provider boundary. Drafting
uses the configured LiteLLM proxy alias and failed or empty model responses
produce explicit no-draft failure states before human review. Gate-passed drafts
may use a bounded LiteLLM tool-call loop over public-data research tools.
