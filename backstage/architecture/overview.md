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

## Digital Worker Lifecycle

```text
POST /api/v1/digital-workforce/assignments
  -> DigitalWorkerService.assign_lead
  -> validate completed lead snapshot, gates passed, draft present
  -> digital_worker_assignments + digital_worker_goal_states
  -> signal.digital_worker.execute queued run
  -> 202 DigitalWorkerAssignmentResponse

Celery worker
  -> loads assignment, lead snapshot, goals, messages, follow-ups
  -> DigitalWorkerExecutor via SignalGraphProvider.digital_worker_graph()
  -> Runtime[DigitalWorkerRuntimeContext] injects repos/settings/lifecycle
  -> digital_worker_context -> digital_worker_action
  -> digital_worker_decision chain plans sandbox tool calls
  -> sandbox email, goal update, phase update, follow-up tools execute
  -> digital_worker_runs/messages/follow_ups persisted state

Celery Beat
  -> signal.digital_worker.scan_due_follow_ups
  -> claim due pending follow-ups
  -> queue one bounded worker run per claimed assignment
```

## Boundaries

- Routes parse and return DTOs, with FastAPI dependency wiring centralized in
  `backend/app/api/v1/dependencies.py`.
- Services orchestrate use cases.
- Repositories persist product records.
- Agent executors run bounded LangGraph graphs.
- Agent nodes transform typed state.
- Digital Worker services run bounded communication wake-ups with explicit
  sandbox tools and durable Postgres state.
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

Digital Workforce uses normalized Postgres tables for long-lived assignment
state: assignments, runs, lifecycle goals, sandbox email messages, and
follow-ups. These tables do not replace lead snapshots or scoring output; they
reference completed leads after gates have passed and a draft exists.

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
  chains/      outreach drafting and digital worker decision chains
  guardrails/  qualification.py hard-gate checks before draft output
  states/      typed LangGraph state
  nodes/       lead intelligence and digital worker node factories
  graphs/      uncompiled graph topology assembly
  executors/   inline and worker-facing graph execution
  prompts/     prompt-facing instructions
  tools/       public-data tools and sandbox digital worker tools
  context/     prompt/runtime serializers and lifecycle specs
  utils/       pure scoring/text helpers
```

The HTTP lead-create path queues a Celery task and returns `202 AgentRunResponse`
with queued status. `app.workers.tasks.execute_signal_agent_run` is the Celery
worker entrypoint that loads queued run input from Postgres, runs the graph, and
persists completed analysis results. Celery's result backend is operational
metadata only; Signal APIs read run and lead state from Postgres.

Graph compilation follows the Playbook pattern for each workflow. The lead
pipeline uses `create_signal_pipeline_chain_set`,
`create_signal_pipeline_node_set`, `compose_signal_pipeline_dependencies`, and
`compile_signal_pipeline_graph`. The SDR Digital Worker mirrors that shape with
`create_digital_worker_chain_set`, `create_digital_worker_node_set`,
`compose_digital_worker_dependencies`, and `compile_digital_worker_graph`.
`SignalGraphProvider` keeps dependency-keyed process-local compiled graph
caches for both lead intelligence and the Digital Worker.

Signal intentionally keeps one workflow-level executor for v1, while the modules
inside `chains/`, `nodes/`, `graphs/`, and `guardrails/` are named for their
actual responsibility. That avoids a stack of same-named `signal_pipeline.py`
files as the product adds review, approval, and worker-backed execution slices.

## Public Data Boundary

`backend/app/infrastructure/public_data/` owns live public API clients for
geocoding, ACS market and household-growth data, FRED economic series, News API
triggers, Wikipedia search, and DNS/MX validation. DataUSA household context is
deferred until a stable current API contract is verified. The provider caches
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
