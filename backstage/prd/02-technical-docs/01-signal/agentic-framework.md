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
- `talking_points` sales insights for rep prioritization and draft grounding
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
- `agents/chains/digital_worker.py` contains the SDR Digital Worker lifecycle
  decision chain and prompt/tool instruction composition.
- `agents/guardrails/qualification.py` contains deterministic hard-gate checks.
- `agents/states/` contains typed graph state for lead intelligence and the
  Digital Worker.
- `agents/nodes/lead_intelligence.py` and `agents/nodes/digital_worker.py`
  contain node factories and node keys.
- `agents/graphs/lead_intelligence.py` and `agents/graphs/digital_worker.py`
  wire uncompiled node topology.
- `agents/executors/` runs the compiled graph inline or from a worker.
- `agents/prompts/` holds prompt-facing instructions.
- `agents/tools/` contains deterministic enrichment wrappers, model-callable
  public-data research tools, and sandbox Digital Worker tools.
- `agents/utils/` contains pure scoring and text helpers.

The builder layer uses the same flow for both agent workflows:

- Signal intake: `create_signal_pipeline_chain_set` ->
  `create_signal_pipeline_node_set` -> `compose_signal_pipeline_dependencies`
  -> `compile_signal_pipeline_graph`.
- Digital Worker: `create_digital_worker_chain_set` ->
  `create_digital_worker_node_set` -> `compose_digital_worker_dependencies` ->
  `compile_digital_worker_graph`.

Each builder returns only its workflow's objects; lead-intelligence builders do
not construct Digital Worker chains or nodes, and Digital Worker builders do not
construct lead-intelligence chains or nodes.

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
- Generate sales insights in the stable `talking_points` state field.
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
- The completed lead API hides queued, running, paused, and failed runs until
  analysis produces an awaiting-review or completed lead result.
- The inbound lead queue API surfaces queued and running submissions as loading
  rows after ready leads, using only submitted input and run status until a lead
  snapshot is available.
- Explicit warnings for unavailable public-data providers.
- Activity log for operational traceability.

## SDR Digital Worker Runtime

Digital Workforce is a separate long-lived worker runtime from the bounded lead
intelligence graph above. It starts only after an SDR assigns the worker to an
eligible completed lead snapshot.

```text
POST /api/v1/digital-workforce/assignments
  -> validate completed lead snapshot, gates passed, draft present
  -> create digital_worker_assignments + goal rows
  -> queue signal.digital_worker.execute

signal.digital_worker.execute
  -> load assignment, lead snapshot, goals, messages, follow-ups
  -> read qualify_to_meeting.v1 lifecycle JSON
  -> invoke digital_worker_decision chain
  -> execute planned bounded sandbox tools
  -> persist messages, goals, follow-ups, phase, run status
  -> END
```

The worker uses Postgres as authoritative memory across runs. The repo-versioned
lifecycle spec defines phases, goals, and example actions. Each worker wake-up
handles one trigger: assignment created, inbound email, due follow-up, or manual
resume.

The worker uses the same graph-provider pattern as the lead-intelligence
pipeline. `SignalGraphProvider.digital_worker_graph()` compiles and caches the
graph, `DigitalWorkerExecutor` invokes it with `context=DigitalWorkerRuntimeContext(...)`,
and node functions read repositories/settings/lifecycle from
`Runtime[DigitalWorkerRuntimeContext]`.

The Digital Worker graph state lives in
`backend/app/agents/states/digital_worker_state.py` and includes:

- `run_id`
- `assignment_id`
- `trigger`
- `run`
- `assignment`
- `lead`
- `activity_log`

The topology lives in `backend/app/agents/graphs/digital_worker.py`:

```text
START
  -> digital_worker_context
  -> digital_worker_action
  -> END
```

`digital_worker_context` loads the run, assignment, and lead snapshot from
runtime-injected repositories. `digital_worker_action` invokes the
`digital_worker_decision` chain, then dispatches planned calls through
`agents/tools/digital_worker.py`.

### Digital Worker Tools

- `send_sandbox_email`: persists an outbound sandbox email message only.
- `record_inbound_email`: persists inbound sandbox email for worker context.
- `schedule_follow_up`: writes a due follow-up row.
- `mark_goal_complete`: updates phase/goal progress.
- `mark_phase_outcome`: updates current phase or terminal assignment status.

### Heartbeat

Celery Beat runs `signal.digital_worker.scan_due_follow_ups` on the configured
interval. The scanner claims pending due follow-ups and enqueues
`signal.digital_worker.execute` for each claimed assignment. Run and assignment
state remain in Postgres; Celery result backend state is operational metadata.
