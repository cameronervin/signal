Start Signal's local development services.

## Services

1. Compose dependencies: Postgres on `localhost:5433`, Valkey on `localhost:6379`, LiteLLM on `localhost:4000`.
2. Backend: FastAPI on `http://127.0.0.1:8000`.
3. Frontend: Next.js on `http://localhost:3000`.
4. Optional worker: Celery worker for queued agent execution.

## Command Sequence

Run from the repo root unless a working directory is specified.

### 1. Start Compose Dependencies

```bash
cp deploy/envs/.env.local.example deploy/envs/.env.local
cp deploy/envs/.env.litellm.local.example deploy/envs/.env.litellm.local
cp backend/.env.example backend/.env
make compose-up
```

Do not commit any real `.env` files.

### 2. Apply Backend Migrations

```bash
cd backend
uv run alembic upgrade head
```

### 3. Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Start Frontend

```bash
pnpm --dir frontend dev
```

### 5. Optional Worker

```bash
cd backend
uv run celery -A app.workers.app:celery_app worker --loglevel=INFO
```

## Verification

- Frontend: `http://localhost:3000`
- Backend API: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Compose logs: `make compose-logs`
