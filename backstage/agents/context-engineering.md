# Context Engineering

Signal prompts and agent context should separate deterministic facts from model
judgment.

## Context Packs

For scoring and drafting, pass:

- Lead input.
- Gate result.
- Normalized enrichment facts.
- Source facts.
- Score components.
- Related-lead context.

Do not pass raw provider payloads or long prompt history.

## Prompt Rules

- Use supplied facts only.
- Cite every personalization fact.
- Do not create drafts for failed gates.
- Keep the draft reviewable and human-controlled.
- Prefer concise operational copy over broad marketing claims.

## Iteration Controls

The v1 graph is bounded. If future repeated tool steps are added:

- Define max iterations.
- Detect repeated tool calls.
- Return a safe incomplete state with flags.
- Persist traceable activity log entries.
