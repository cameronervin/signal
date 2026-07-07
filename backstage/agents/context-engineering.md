# Context Engineering

Signal prompts and agent context should separate deterministic facts from model
judgment.

## Context Packs

For scoring and drafting, pass:

- Lead input with masked email local-part.
- Gate result.
- Normalized enrichment facts.
- Source facts.
- Score components.
- Deterministic talking points.

Do not pass raw provider payloads or long prompt history.

## Prompt Rules

- Use supplied facts only.
- Cite every personalization fact.
- Do not create drafts for failed gates.
- Keep the draft reviewable and human-controlled.
- Prefer concise operational copy over broad marketing claims.
- Use research tools only for supplemental draft evidence; do not use them to
  revise deterministic score, tier, gates, or talking points.

## Iteration Controls

The v1 graph is bounded, and the LiteLLM tool loop is capped by
`SIGNAL_AGENT_RESEARCH_MAX_TOOL_ROUNDS`.

- Define max iterations.
- Detect repeated tool calls.
- Return a safe incomplete state with flags.
- Persist traceable activity log entries.
