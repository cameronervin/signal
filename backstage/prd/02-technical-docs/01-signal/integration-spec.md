# Integration Spec

Signal uses public APIs through infrastructure adapter boundaries. The default
mode still uses fixtures so the demo is reliable without keys; live mode calls
public APIs with cached fixture fallback.

## Public Data Sources

| Source | Purpose | V1 Role |
| --- | --- | --- |
| Nominatim/OpenStreetMap | Address to coordinates and place context | Live adapter |
| U.S. Census ACS | Renter share, rent, and household count | Live adapter |
| DataUSA | Household growth fallback | Live adapter |
| FRED | Labor and rent trend context | Optional key-backed adapter |
| News API | Company trigger events | Optional key-backed adapter |
| Wikipedia API | Company background hints | Live adapter |
| DNS/MX lookup | Corporate email gate signal | Live adapter |

## Adapter Rules

- Public API clients live under `backend/app/infrastructure/public_data/`.
- Agents consume normalized facts, not raw provider payloads.
- Every fact used in a draft must become a `SourceFact`.
- Live adapters must have fixture-backed tests.
- Failures return warnings or fallback facts, not unhandled exceptions.
- The public data provider is cached by settings and injected into LangGraph
  runtime context per run.

## Demo Reliability

For the video/demo:

- Use seeded fixture leads with A, B, and C outcomes.
- Cache live API responses with `SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS`.
- Keep LLM drafting optional with deterministic fallback.
- Never block the queue on a single API outage.

## Runtime Configuration

```bash
SIGNAL_USE_FIXTURES=false
SIGNAL_PUBLIC_DATA_USER_AGENT="Signal API local demo"
SIGNAL_PUBLIC_DATA_CACHE_TTL_SECONDS=3600
SIGNAL_CENSUS_API_KEY=optional
SIGNAL_FRED_API_KEY=optional
SIGNAL_NEWS_API_KEY=optional
SIGNAL_NOMINATIM_EMAIL=optional-contact@example.com
```
