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

State lives in `backend/app/agents/state.py` and includes:

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

## Node 1 - Deterministic Enrichment

Responsibilities:

- Resolve market/location context.
- Attach public source facts.
- Evaluate hard gates.
- Emit flags and activity log entries.

Current scaffold uses fixture-backed enrichment. Live adapters should be added
behind `backend/app/integrations/`.

## Node 2 - Agent Scoring And Drafting

Responsibilities:

- Score lead against the configured rubric.
- Assign tier and why-line.
- Generate talking points.
- Generate cited outreach draft only if gates pass.

Future LLM integration belongs here, but the scaffold keeps a deterministic
draft so tests and demos are reliable.

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
