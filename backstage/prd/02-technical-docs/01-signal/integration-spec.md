# Integration Spec

Signal uses public APIs through adapter boundaries. The scaffold currently uses
fixtures so the demo is reliable without keys.

## Public Data Sources

| Source | Purpose | V1 Role |
| --- | --- | --- |
| Nominatim/OpenStreetMap | Address to coordinates and place context | Planned live adapter |
| U.S. Census ACS | Renter share, rent, vacancy, household growth | Planned live adapter |
| DataUSA | Market economics fallback | Planned live adapter |
| FRED | Labor and rent trend context | Planned live adapter |
| News API | Company trigger events | Optional key-backed adapter |
| Wikipedia API | Company background and scale hints | Planned live adapter |
| DNS/MX lookup | Corporate email gate | Planned live adapter |

## Adapter Rules

- Public API clients live under `backend/app/integrations/`.
- Agents consume normalized facts, not raw provider payloads.
- Every fact used in a draft must become a `SourceFact`.
- Live adapters must have fixture-backed tests.
- Failures return warnings or fallback facts, not unhandled exceptions.

## Demo Reliability

For the video/demo:

- Use seeded fixture leads with A, B, and C outcomes.
- Cache live API responses when live adapters are introduced.
- Keep LLM drafting optional with deterministic fallback.
- Never block the queue on a single API outage.
