.PHONY: dev-backend dev-frontend test-backend lint-backend test-frontend lint-frontend verify

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

verify: test-backend lint-backend test-frontend lint-frontend
