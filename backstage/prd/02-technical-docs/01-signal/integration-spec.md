# Integration Spec

Signal uses public APIs through infrastructure adapter boundaries. Runtime
enrichment uses live adapter code paths, caches normalized responses, and
surfaces unavailable providers as warnings instead of substituting fixture data.

## Public Data Sources

| Source | Purpose | V1 Role |
| --- | --- | --- |
| Nominatim/OpenStreetMap | Address to coordinates and place context | Live adapter |
| U.S. Census ACS | Renter share, rent, and household count | Live adapter |
| DataUSA | Household growth context | Live adapter |
| FRED | Labor and rent trend context | Optional key-backed adapter |
| News API | Company trigger events | Optional key-backed adapter |
| Wikipedia API | Company background hints | Live adapter |
| DNS/MX lookup | Corporate email gate signal | Live adapter |

## Adapter Rules

- Public API clients live under `backend/app/infrastructure/public_data/`.
- Agents consume normalized facts, not raw provider payloads.
- Every fact used in a draft must become a `SourceFact`.
- Live adapters must have mocked contract tests over request and response shape.
- Failures return warnings or omitted facts, not unhandled exceptions or
  production fixture substitutes.
- The public data provider is warmed by the API lifespan or worker process
  lifecycle and injected into LangGraph runtime context per run.
- Runtime public-data adapters reuse a shared scoped HTTPX async client for
  connection pooling; tests may still inject explicit mocked transports for
  contract isolation.
- The same provider methods back deterministic enrichment and optional
  model-callable research tools.

## Operational Reliability

For local evaluation and production-readiness:

- Use seeded sample leads with A, B, and C outcomes for repeatable local checks.
- Cache live API responses with `SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS`.
- Keep LLM drafting model-backed through LiteLLM; model failures produce an
  explicit no-draft failure state.
- Never hide a provider outage behind synthetic production facts.

## Runtime Configuration

```bash
SIGNAL_PUBLIC_DATA_USER_AGENT="Signal"
SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS=3600
SIGNAL_CENSUS_API_KEY=optional
SIGNAL_FRED_API_KEY=optional
SIGNAL_NEWS_API_KEY=optional
SIGNAL_NOMINATIM_EMAIL=optional-contact@example.com
SIGNAL_AGENT_RESEARCH_TOOLS_ENABLED=true
SIGNAL_AGENT_RESEARCH_MAX_TOOL_ROUNDS=3
SIGNAL_KNOWLEDGE_GRAPH_ENABLED=false
SIGNAL_NEO4J_URI=bolt://localhost:7687
SIGNAL_NEO4J_USER=neo4j
SIGNAL_NEO4J_PASSWORD=optional-local-password
SIGNAL_NEO4J_DATABASE=neo4j
```

Neo4j is optional. Disabled or unavailable graph storage returns a bounded
current-lead graph projection with explicit graph warnings instead of falling
back to fixture relationship data.
