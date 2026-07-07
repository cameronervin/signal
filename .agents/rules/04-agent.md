# Agent Rules

Signal uses a bounded LangGraph pipeline for lead intelligence.

## Topology

```text
START
  -> deterministic_enrichment
  -> agent_scoring_and_drafting
  -> knowledge_graph_builder
  -> END
```

## Do

- Keep state typed in `backend/app/agents/states/`.
- Keep graph topology in `graphs/`, node factories in `nodes/`, and execution in `executors/`.
- Use `SignalRuntimeContext` and provider boundaries instead of global runtime decisions.
- Return flags for missing or unverifiable data.
- Generate drafts only when hard gates pass.
- Cite personalization facts through normalized source records.
- Stop outbound workflow at human review; approval marks review complete and does not send live outreach in v1.

## Avoid

- Open-ended autonomous loops.
- Raw model/provider responses in state.
- Hidden score assumptions.
- Draft text for gate-failed leads.
- Live send behavior without explicit approval and updated specs.

## Docs

Read `backstage/prd/02-technical-docs/01-signal/agentic-framework.md`, `scoring.md`, `integration-spec.md`, and `security.md` before changing agent behavior.
