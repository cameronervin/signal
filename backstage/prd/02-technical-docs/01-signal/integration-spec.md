# Integration Spec

Signal uses public APIs through adapter boundaries. The target v1 should support
live calls where configured, cache-backed responses for repeatability, and
fixture fallbacks for demo reliability.

## Public Data Sources

| Source | Purpose | V1 Role |
| --- | --- | --- |
| Nominatim/OpenStreetMap | Address to coordinates and place context | Required geocoding adapter |
| U.S. Census ACS | Renter share, median rent, vacancy, household growth | Required demographic adapter |
| DataUSA | Market economics and demographic fallback | Required fallback/secondary adapter |
| FRED | Labor and rent trend context | Required economic adapter |
| NewsAPI | Company trigger events | Required when key is configured; fixture/cache fallback required |
| Wikipedia API | Company background and scale hints | Required company-context adapter |
| WalkScore or local-context equivalent | Walkability/density proxy | Required adapter or fixture-backed proxy |
| DNS/MX lookup | Corporate email quality gate | Required domain-quality adapter |
| LLM gateway/API | Draft generation and agent reasoning | Required agent capability through LiteLLM gateway mode with safe fallback behavior |

## LLM Gateway

Signal v1 includes a provider abstraction for agent LLM calls.

| Mode | Purpose | Required Config |
| --- | --- | --- |
| `litellm` | Normal gateway mode through a LiteLLM OpenAI-compatible proxy | `LLM_PROVIDER_MODE`, `LLM_CHAT_MODEL`, `LITELLM_BASE_URL`, `LITELLM_API_KEY`, common timeout/token settings |
| `direct` | Local/test or explicit break-glass provider access | `LLM_PROVIDER_MODE`, `LLM_DIRECT_PROVIDER`, selected provider API key, common timeout/token settings |

Gateway model aliases should be Signal-neutral, such as `signal-chat` and
`signal-fast`. Provider-specific model ids and credentials belong in
environment variables, gateway config, or secret storage, not in code, prompts,
fixtures, tests, or committed docs.

The scope should follow the user's `cameronervin/playbook` GitHub repo
direction for gateway/provider factories, direct break-glass mode, and
OpenAI-compatible gateway clients while keeping Signal domain language neutral.

## Adapter Rules

- Public API clients live under `backend/app/integrations/`.
- Adapters share the public-data boundary in
  `backend/app/integrations/public_data.py`: `NormalizedPublicDataResult`,
  `ProviderWarning`, `PublicDataCacheRecord`, `PublicDataFixtureStore`, and the
  base adapter lookup flow.
- Adapters return typed normalized results and sanitized warnings/errors.
- Agents consume normalized facts, not raw provider payloads.
- Every fact used in scoring, talking points, or drafts must become a
  `SourceFact`.
- Live adapters must have fixture-backed tests.
- Provider timeouts, missing keys, rate limits, and schema changes return
  warnings, cached values, fixture values, or no-data states, not unhandled
  exceptions.
- Do not log raw provider payloads, API keys, tokens, prompts, full emails, or
  draft bodies.

## Cache And Fixture Behavior

Cache records should include:

- Provider category.
- Provider/source identifier, so primary and fallback adapters in the same
  category do not share records accidentally.
- Request key or normalized lookup key.
- Normalized response.
- Retrieved timestamp.
- Expiration or refresh policy.

The implemented in-memory cache stores those fields on `PublicDataCacheRecord`
with a TTL, refresh policy, and normalized lookup key. It is a demo-safe cache
boundary; durable storage remains out of scope for v1 until a later persistence
phase.

Fixture fallback must cover:

- A-tier lead with strong fit and urgency.
- B-tier lead with good fit but weaker urgency.
- C-tier lead below threshold.
- Hard-gate-failed lead with no draft.
- Missing-trigger lead.
- Warning-only lead that can still produce a draft.

The shared fixture path can be selected explicitly, or when a required key is
missing, a provider times out, a response schema changes, a rate limit is hit, or
another provider request fails. Returned warnings use sanitized reason codes and
generic messages rather than raw provider payloads or request details.

## Trigger Design

V1 uses `POST /api/v1/leads` as the lead-insertion trigger. In production, a CRM,
form, sheet, or workflow automation can point at the same endpoint without
changing the enrichment engine.

The trigger can run inline/eager for demo reliability or enqueue a Celery worker
task for agent execution. A scheduled batch is acceptable as a future
alternative, but the v1 spec centers on the insertion trigger because it best
supports speed-to-lead.

## Worker Infrastructure

Signal v1 includes a Celery worker for agent run execution only.

Required configuration:

- `SIGNAL_AGENT_EXECUTION_MODE`: `inline`, `eager`, or `worker`.
- `CELERY_BROKER_URL`: Valkey/Redis broker URL.
- `CELERY_RESULT_BACKEND`: Valkey/Redis result backend URL.
- `CELERY_AGENT_QUEUE`: named agent execution queue.
- `CELERY_TASK_MAX_RETRIES`, `CELERY_TASK_RETRY_COUNTDOWN`,
  `CELERY_TASK_SOFT_TIME_LIMIT`, `CELERY_TASK_HARD_TIME_LIMIT`, and
  `CELERY_WORKER_LOG_LEVEL`.

Worker requirements:

- Use JSON serialization and named task routes.
- Track started/result states so run APIs can show progress.
- Use late ACKs, worker-lost rejection, publish retry, prefetch fairness, and
  bounded visibility/timeouts.
- Send only identifiers and minimal metadata through the broker.
- Preserve an eager/local path for tests and demos when the broker is not
  running.

## Demo Reliability

For the demo:

- Seed leads before recording or presentation.
- Cache API responses for demo leads.
- Use fixtures when providers are down, missing keys, or rate-limited.
- Keep LLM draft fallback available.
- Keep worker eager/fixture fallback available for local demos.
- Never block the queue because one provider failed.
