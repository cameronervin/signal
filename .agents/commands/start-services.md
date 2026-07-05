# Start Services

Start local development services.

## Backend

```bash
cd backend
uv sync --group dev
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Verify

- Backend health: `http://127.0.0.1:8000/api/v1/health`
- Backend docs: `http://127.0.0.1:8000/docs`
- Frontend: `http://localhost:3000`
