# Agentic Pipeline Rules

Signal's agentic runtime is a bounded LangGraph workflow, not an open-ended
chat loop.

## Required Pipeline

1. Deterministic enrichment.
2. Agent scoring and drafting.
3. Knowledge graph builder.
4. Human review gate.

## Loop Guardrails

- Each node has explicit inputs, outputs, and stop criteria.
- Tool calls are typed and allowlisted.
- Retry counts are bounded.
- Missing data returns flags, not hidden assumptions.
- Drafts cite the source facts used for personalization.
- Hard gate failure short-circuits drafting.

## State Rules

- State lives in `backend/app/agents/state.py`.
- Nodes return partial state updates.
- Graph topology lives in `backend/app/agents/graph.py`.
- Prompts live in `backend/app/agents/prompts.py`.
- Scoring thresholds live in config or data files, not in prompts.

## Human Review

Any send-like action must stay behind a review/approve state. Do not add
automatic send behavior without explicit user approval and a new ADR.
