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
| LLM API | Draft generation and agent reasoning | Required agent capability with safe fallback behavior |

## Adapter Rules

- Public API clients live under `backend/app/integrations/`.
- Adapters return typed normalized results and sanitized errors.
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
- Request key or normalized lookup key.
- Normalized response.
- Retrieved timestamp.
- Expiration or refresh policy.

Fixture fallback must cover:

- A-tier lead with strong fit and urgency.
- B-tier lead with good fit but weaker urgency.
- C-tier lead below threshold.
- Hard-gate-failed lead with no draft.
- Missing-trigger lead.
- Warning-only lead that can still produce a draft.

## Trigger Design

V1 uses `POST /api/v1/leads` as the lead-insertion trigger. In production, a CRM,
form, sheet, or workflow automation can point at the same endpoint without
changing the enrichment engine.

A scheduled batch is acceptable as a future alternative, but the v1 spec centers
on the insertion trigger because it best supports speed-to-lead.

## Demo Reliability

For the demo:

- Seed leads before recording or presentation.
- Cache API responses for demo leads.
- Use fixtures when providers are down, missing keys, or rate-limited.
- Keep LLM draft fallback available.
- Never block the queue because one provider failed.
