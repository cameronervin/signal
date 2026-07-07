COMPOSE_FILES = -f deploy/compose/base.yml -f deploy/compose/local.yml
COMPOSE_ENV_FILES = $(if $(wildcard deploy/envs/.env.local),--env-file deploy/envs/.env.local,) $(if $(wildcard deploy/envs/.env.litellm.local),--env-file deploy/envs/.env.litellm.local,)
COMPOSE = docker compose $(COMPOSE_ENV_FILES) $(COMPOSE_FILES)

.PHONY: compose-up compose-down compose-logs compose-reset dev-backend dev-frontend test-backend lint-backend test-frontend lint-frontend docs-check verify

compose-up:
	$(COMPOSE) up -d postgres valkey litellm

compose-down:
	$(COMPOSE) down

compose-logs:
	$(COMPOSE) logs -f postgres valkey litellm

compose-reset:
	$(COMPOSE) down -v

dev-backend:
	cd backend && uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

dev-frontend:
	pnpm --dir frontend dev

test-backend:
	cd backend && uv run pytest -v

lint-backend:
	cd backend && uv run ruff check .

test-frontend:
	pnpm --dir frontend test

lint-frontend:
	pnpm --dir frontend lint

docs-check:
	! rg -n "demo-safe|take-home|deterministic fallback|fixture fallback" README.md AGENTS.md backend deploy backstage -S

verify: test-backend lint-backend test-frontend lint-frontend docs-check
