# Agentic Framework

Signal uses a bounded LangGraph pipeline. The graph is meant to be inspectable,
testable, and demo-safe.

## Graph Topology

```text
START
  -> deterministic_enrichment
  -> agent_scoring_and_drafting
  -> knowledge_graph_builder
  -> END
```

## State

State lives in `backend/app/agents/states/signal_state.py` and includes:

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
- `activity_log`

Nodes return partial state updates.

## Package Shape

Signal follows the Playbook agent structure directionally:

- `agents/builders/` composes chains, nodes, and compiled graphs.
- `agents/chains/outreach_drafting.py` contains the deterministic draft chain.
- `agents/guardrails/qualification.py` contains deterministic hard-gate checks.
- `agents/states/` contains typed graph state.
- `agents/nodes/lead_intelligence.py` contains node factories and node keys.
- `agents/graphs/lead_intelligence.py` wires uncompiled node topology.
- `agents/executors/` runs the compiled graph inline or from a worker.
- `agents/prompts/` holds prompt-facing instructions.
- `agents/tools/` contains deterministic tool wrappers.
- `agents/utils/` contains pure scoring and text helpers.

## Node 1 - Deterministic Enrichment

Responsibilities:

- Resolve market/location context.
- Attach public source facts.
- Evaluate hard gates.
- Emit flags and activity log entries.

Current scaffold uses fixture-backed enrichment. Live adapters should be added
behind `backend/app/infrastructure/public_data/`.

The compiled graph is provided by `SignalGraphProvider`, which caches compiled
graphs by settings/checkpointer identity. `SignalPipelineExecutor` injects a
`SignalRuntimeContext` containing settings and the public data provider into
each `ainvoke` call, so adapters are selected per run without recompiling the
graph.

## Node 2 - Agent Scoring And Drafting

Responsibilities:

- Score lead against the configured rubric.
- Assign tier and why-line.
- Generate talking points.
- Generate cited outreach draft only if gates pass.

Future LLM integration belongs here, but the scaffold keeps a deterministic
draft so tests and demos are reliable.

The LiteLLM provider boundary lives under `backend/app/infrastructure/llm/`.
Model-backed drafting should retain deterministic fallback behavior and the
human review gate.

## Node 3 - Knowledge Graph Builder

Responsibilities:

- Link contact, company, property, and market context.
- Surface related leads.
- Mark the run as awaiting human review when gates pass.

V1 uses lightweight related records. A graph database is out of scope.

## Loop Guardrails

- Bounded graph, no open-ended autonomous loop.
- Typed state.
- Hard gate short-circuit for drafts.
- Human review required before outreach.
- Fixture fallback for public data.
- Activity log for demo traceability.
