# Agent Tools

Signal uses a Playbook-shaped tool registry for optional agent research during
outreach drafting. Deterministic enrichment still runs first as a graph node;
tools are only model-callable after gates pass.

## Build Flow

```text
registry -> active tools -> workflow/chain assignment -> prompt snippets -> draft chain
```

- `tool_registry.py` declares each `ToolSpec`.
- `tool_assignment.py` resolves enabled tools and assigns them to
  `signal_pipeline -> outreach_draft`.
- `tool_prompts.py` holds model-facing guidance for active tools.
- `public_data.py` creates `StructuredTool` wrappers over the existing public
  data adapters.

## Built-In Research Tools

| Tool | Source | Purpose |
| --- | --- | --- |
| `geocode_property_address` | Nominatim/OpenStreetMap | Verify property place context. |
| `fetch_census_market_demographics` | Census ACS | Fetch renter share, median rent, and household count. |
| `fetch_fred_market_economics` | FRED | Fetch rent-growth and unemployment context; key-gated. |
| `lookup_news_company_trigger` | News API | Find one recent company trigger; key-gated. |
| `lookup_wikipedia_company_background` | Wikipedia | Fetch concise company background. |
| `validate_email_domain_mx` | DNS/MX | Verify domain MX records without exposing a full email. |

Tools return normalized JSON with `status`, `summary`, `source_facts`, and an
optional sanitized `warning`. They never return raw provider payloads.

## Guardrails

- Tools do not change gates, score, tier, or deterministic talking points.
- Gate-failed leads skip model drafting and never call research tools.
- Tool failures are non-fatal and return sanitized unavailable results.
- Supplemental facts may be cited on `DraftEmail.sources`; no new public API
  response field is added.
