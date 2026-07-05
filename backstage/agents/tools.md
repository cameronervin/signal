# Agent Tools

Current scaffold has no live LLM tools. It uses deterministic fixture functions
and score calculators.

## Planned Tools

| Tool | Purpose | Output |
| --- | --- | --- |
| `geocode_address` | Resolve property address | Coordinates, place confidence, source fact |
| `fetch_market_demographics` | Fetch renter and household stats | Source facts |
| `fetch_market_economics` | Fetch rent/labor signals | Source facts |
| `lookup_company_trigger` | Find recent company event | Source fact or no-trigger flag |
| `validate_email_domain` | Check corporate domain and MX | Gate signal |

All tools must return typed results and sanitized errors.
