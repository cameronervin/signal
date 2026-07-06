# Signal Backend

FastAPI backend for triggered inbound lead enrichment.

## Run

```bash
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Configuration

Settings are loaded from `SIGNAL_` environment variables, with fixture-first
defaults for local and demo reliability. Key knobs:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SIGNAL_USE_FIXTURES` | `true` | Keeps enrichment and drafting on deterministic fallback paths. |
| `SIGNAL_API_BASE_URL` | `http://127.0.0.1:8000` | API origin advertised to local clients and docs. |
| `SIGNAL_FRONTEND_ORIGIN` | `http://localhost:3000` | Primary allowed frontend origin for CORS. |
| `SIGNAL_EXTRA_CORS_ORIGINS` | `http://127.0.0.1:3000` | Comma-separated additional explicit CORS origins. |
| `SIGNAL_SCORING_CONFIG_PATH` | `app/agents/scoring.py` | Scoring configuration source path for the current scaffold. |
| `SIGNAL_MAX_AGENT_RETRIES` | `2` | Bounded agent retry count. |
| `SIGNAL_PROVIDER_RETRY_COUNT` | `2` | Bounded public-provider retry count. |
| `SIGNAL_PROVIDER_TIMEOUT_SECONDS` | `8` | Provider call timeout budget. |
| `SIGNAL_REQUEST_TIMEOUT_SECONDS` | `15` | General backend request timeout budget. |

Optional provider and LLM credentials are read from `SIGNAL_NEWS_API_KEY`,
`SIGNAL_FRED_API_KEY`, `SIGNAL_OPENAI_API_KEY`, `SIGNAL_LITELLM_GATEWAY_URL`,
`SIGNAL_LITELLM_GATEWAY_KEY`, and `SIGNAL_LLM_MODEL`. Do not commit real values.

Structured logging redacts sensitive keys and masks email addresses before JSON
logs are emitted. Do not log raw request bodies, provider payloads, prompts,
drafts, API keys, tokens, or full email addresses.

## Test

```bash
uv run pytest -v
uv run ruff check .
```

## Shape

```text
app/api/v1       thin route handlers
app/services     product orchestration
app/repositories in-memory persistence boundary for v1
app/agents       LangGraph state, nodes, scoring, fixtures
app/integrations public API adapter boundaries
app/schemas      Pydantic contracts
```
