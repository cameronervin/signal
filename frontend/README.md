# Signal Frontend

Next.js SDR workspace for the dashboard, ranked lead queue, lead detail review,
and agent-run monitoring surfaces.

## Data Mode

By default the frontend reads from the FastAPI backend through
`NEXT_PUBLIC_SIGNAL_API_BASE_URL`, falling back to `http://127.0.0.1:8000`.
Fixture data is available only when explicitly enabled:

```bash
NEXT_PUBLIC_SIGNAL_USE_FIXTURES=true pnpm dev
```

## Verification

```bash
pnpm test
pnpm lint
pnpm typecheck
pnpm build
```
