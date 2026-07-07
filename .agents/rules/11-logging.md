# Logging Rules

Signal uses structured logging through `structlog`.

## Do

- Log service boundaries and important state transitions.
- Include sanitized context such as lead id, run id, operation, status, and duration.
- Use appropriate levels: DEBUG for local detail, INFO for normal events, WARNING for recoverable issues, ERROR for failures.
- Log provider failures in a way that proves fallback behavior without storing raw payloads.

## Do Not

- Use `print()` in application code.
- Log full emails, request bodies, draft bodies, prompts, model inputs, tokens, API keys, secrets, or raw provider payloads.
- Log inside hot loops without a clear need.
- Use string interpolation for structured values when logger key/value fields are available.

## Pattern

```python
import structlog

logger = structlog.get_logger(__name__)

logger.info("agent_run_started", lead_id=lead_id, run_id=run_id)
logger.warning("public_data_fallback_used", provider=provider_name, lead_id=lead_id)
```
