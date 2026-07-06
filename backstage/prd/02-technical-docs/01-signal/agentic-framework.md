# Agentic Framework

Signal uses a bounded LangGraph pipeline triggered when a lead is inserted
through the API. The graph enriches the lead, scores it, prepares reviewed
outreach, and builds lightweight related context for the SDR workspace.

## Graph Topology

```text
START
  -> deterministic_enrichment
  -> llm_scoring_and_drafting
  -> related_context_builder
  -> END
```

The graph is deliberately bounded. There is no open-ended autonomous loop in
v1.

## Execution Runtime

V1 supports two execution modes:

- `inline` or `eager`: deterministic local/demo/test execution that can run
  without a broker and return completed fixture outputs when configured.
- `worker`: API creates a lead and agent run, then dispatches the run to a
  Celery worker through a Valkey/Redis broker and exposes progress through the
  agent-run APIs.

The worker path should follow the user's `cameronervin/playbook` GitHub repo
patterns for backend Celery setup: named queues, JSON serialization, ID-only
dispatch payloads, late ACKs, worker-lost rejection, bounded time limits, result
tracking, lazy broker connection, and explicit startup commands. Do not copy
product copy, branded identifiers, or unrelated domain concepts from that repo
into Signal.

Celery payloads must contain only identifiers and minimal execution metadata,
such as `lead_id`, `run_id`, and `execution_mode`. The worker re-loads lead/run
state through the repository boundary and writes sanitized stage transitions.

## State

State includes:

- `lead_id`
- `run_id`
- `task_id`
- `execution_mode`
- `worker_queue`
- `lead`
- `sources`
- `gates`
- `enrichment`
- `score`
- `talking_points`
- `flags`
- `draft`
- `related_leads`
- `degraded_reasons`
- `activity_log`

Nodes return typed partial state updates.

Run status should support at least `queued`, `running`, `degraded`, `succeeded`,
and `failed` states. Activity logs may name stages and provider categories, but
must not include raw prompts, draft bodies, full emails, secrets, token payloads,
or raw provider responses.

## Node 1 - Deterministic Enrichment

Responsibilities:

- Resolve property address into market, coordinates, and geocoding confidence.
- Fetch or load demographic, economic, local-context, company, news/event, and
  domain-quality facts.
- Normalize all provider outputs into `SourceFact` records.
- Evaluate hard gates and warnings.
- Emit degraded-provider notes when live data falls back to cache or fixtures.

The node should use live public APIs when configured, cached data when
available, and fixtures for demo reliability.

## Node 2 - LLM Scoring And Drafting Agent

Responsibilities:

- Review deterministic enrichment and source facts.
- Fill gaps only through approved public-data tools.
- Score the lead against the documented 60/40 rubric.
- Generate a why-line, score-component rationale, talking points, and cited
  draft email for gate-passed leads.
- Suppress drafts for hard-gate-failed leads.

The LLM is required for the target v1 agent node, but the product must define
safe fallback behavior:

- Agent LLM calls go through a provider abstraction.
- Normal gateway mode routes through a LiteLLM OpenAI-compatible proxy using
  configured model aliases, base URL, and gateway key.
- Direct mode is reserved for local/test or explicit break-glass use.
- If LLM is unavailable but gates pass, return deterministic score output and a
  clearly marked fallback template draft.
- If source facts are insufficient for personalization, produce generic copy
  without unsupported claims.
- If gates fail, return no draft even when the LLM is available.

Prompt inputs and outputs are sensitive. Do not log prompts, raw draft bodies,
tokens, secrets, or full emails.

## Node 3 - Related Context Builder

Responsibilities:

- Link contact, company, property, market, and submarket context.
- Surface repeat inbound, same company, same parent/portfolio hint, or same
  market relationships.
- Apply the bounded related-inbound bonus only when scoring spec criteria are
  met.
- Mark the run as awaiting human review when a draft exists.

V1 uses lightweight related records in the repository. A graph database is out
of scope.

## Human Review Boundary

- Signal can prepare, display, copy, or export reviewed draft content.
- Signal v1 must not send email or start autonomous follow-up.
- Review/copy/export events should update product state without changing
  trusted score, gates, or source facts.

## Tool Guardrails

- Tools return structured DTOs and sanitized errors.
- Agents consume normalized facts, not raw provider payloads.
- Provider failures become degraded states, warnings, cached data, or fixtures.
- Every draft personalization claim maps to `SourceFact` or is omitted.
- Activity logs show stage progress and degraded provider categories only.
- Worker dispatch and task logs show ids, counts, stages, and sanitized error
  types only.
