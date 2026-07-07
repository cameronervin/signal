# Local And Deployment Rules

Signal's local dependency stack lives under `deploy/` and is intentionally small.

## Structure

```text
deploy/compose/   Compose base and local overrides
deploy/envs/      Local env templates
deploy/litellm/   Local LiteLLM proxy config
```

## Local Commands

```bash
make compose-up
make compose-logs
make compose-down
make compose-reset
make dev-backend
make dev-frontend
```

## Environment Rules

- Commit only examples or placeholders.
- Do not commit real `.env` files, API keys, tokens, or provider credentials.
- Backend defaults come from `backend/.env.example` and `backstage/guides/setup.md`.
- Keep CORS origins explicit.
- Keep demo mode reliable with fixtures and cache-backed provider fallbacks.

## Ask First

- New persistent storage.
- Production auth or permissions.
- Background worker changes beyond the existing Celery scaffold.
- New paid API dependency.
- Live send behavior.
