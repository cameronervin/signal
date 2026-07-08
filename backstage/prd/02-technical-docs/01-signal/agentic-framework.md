# Agentic Framework

Signal uses a bounded LangGraph pipeline. The graph is meant to be inspectable,
testable, and production-ready.

## Graph Topology

```text
START
  -> deterministic_enrichment
  -> knowledge_graph_ingest
  -> graph_context_retrieval
  -> deterministic_scoring
  -> agent_research_and_drafting
  -> knowledge_graph_builder
  -> END
```

## Runtime

Lead intake queues `signal.agent_runs.execute` through Celery. The HTTP API
persists the submitted input and a queued run in Postgres, then returns `202`
with the queued `AgentRunResponse`. The worker loads that run, marks it running,
executes the bounded graph, and persists the finished run plus a lead snapshot
only when analysis reaches an SDR-visible state.

## State

Graph state lives in `backend/app/agents/states/signal_state.py` and includes:

- `lead_id`
- `run_id`
- `lead`
- `gates`
- `enrichment`
- `score`
- `talking_points`
- `flags`
- `draft`
- `related_leads`
- `graph_context`
- `knowledge_graph`
- `activity_log`

Nodes return partial state updates.

## Package Shape

Signal follows the Playbook agent structure directionally:

- `agents/builders/` composes chains, nodes, and compiled graphs.
- `agents/chains/outreach_drafting.py` contains the LiteLLM-backed draft chain.
- `agents/guardrails/qualification.py` contains deterministic hard-gate checks.
- `agents/states/` contains typed graph state.
- `agents/nodes/lead_intelligence.py` contains node factories and node keys.
- `agents/graphs/lead_intelligence.py` wires uncompiled node topology.
- `agents/executors/` runs the compiled graph inline or from a worker.
- `agents/prompts/` holds prompt-facing instructions.
- `agents/tools/` contains deterministic enrichment wrappers plus model-callable
  public-data research tools.
- `agents/utils/` contains pure scoring and text helpers.

## Node 1 - Deterministic Enrichment

Responsibilities:

- Resolve market/location context.
- Attach public source facts.
- Evaluate hard gates.
- Emit flags and activity log entries.

Runtime enrichment uses live public-data adapters behind
`backend/app/infrastructure/public_data/`. Tests and sample seeding inject
mocked or fixed data explicitly.

The compiled graph is provided by `SignalGraphProvider`, which caches compiled
graphs by settings/checkpointer identity. `SignalPipelineExecutor` injects a
`SignalRuntimeContext` containing settings, the public data provider, and the
knowledge graph service into each `ainvoke` call, so adapters are selected per
run without recompiling the graph.

## Node 2 - Knowledge Graph Ingest

Responsibilities:

- Build deterministic graph entity ids from lead input and enrichment facts.
- Write the current lead graph to Neo4j when graph storage is enabled.
- Return explicit graph warnings when Neo4j is disabled or unavailable.

## Node 3 - Graph Context Retrieval

Responsibilities:

- Retrieve prior related-lead candidates from the graph repository.
- Apply deterministic relationship rules for same-company, same-market,
  shared-trigger, and shared-source context.
- Keep graph context bounded and explainable before scoring and drafting.

## Node 4 - Deterministic Scoring

Responsibilities:

- Score lead against the configured rubric.
- Assign tier and why-line.
- Generate talking points.
- Use scoring defaults from the backend scoring config, or load an override
  from `SIGNAL_SCORING_CONFIG_PATH`.

## Node 5 - Agent Research And Drafting

Responsibilities:

- Skip hard-gate-failed leads without calling LiteLLM or tools.
- Pass a deterministic, sanitized context pack to the model.
- Allow bounded supplemental research through public-data tools.
- Generate cited outreach draft through LiteLLM only if gates pass.
- Append supplemental source facts to draft citations when used.

The LiteLLM provider boundary lives under `backend/app/infrastructure/llm/`.
Model-backed drafting preserves the human review gate. Empty or failed model
responses produce an explicit no-draft failure state.

## Node 6 - Knowledge Graph Builder

Responsibilities:

- Project current lead, contact, company, property, market, source fact,
  trigger, and related lead context into `LeadResponse.knowledge_graph`.
- Surface graph-backed related leads through the legacy `related_leads` field.
- Mark the run as awaiting human review when gates pass.

Neo4j is optional and scoped to graph context. Postgres remains the source of
truth for lead and run snapshots.

## Loop Guardrails

- Bounded graph and bounded tool loop, no open-ended autonomous loop.
- Typed state.
- Hard gate short-circuit for drafts.
- Human review required before outreach.
- Approve/pause transitions update run status only and never send outreach.
- Postgres run state is authoritative; Celery results are operational metadata.
- Lead queue APIs hide queued, running, paused, and failed runs until analysis
  produces an awaiting-review or completed lead result.
- Explicit warnings for unavailable public-data providers.
- Activity log for operational traceability.
