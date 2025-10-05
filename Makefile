.PHONY: help install dev test test-api test-web test-e2e test-contracts lint typecheck format db-up db-down migrate seed clean

help:
	@echo "SiteWatcher - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       Install all dependencies"
	@echo "  make db-up         Start Postgres in Docker"
	@echo "  make db-down       Stop Postgres"
	@echo "  make migrate       Run database migrations"
	@echo "  make seed          Seed database with initial data"
	@echo ""
	@echo "Development:"
	@echo "  make dev           Run all services (DB + API + Web)"
	@echo ""
	@echo "Testing:"
	@echo "  make test          Run all tests"
	@echo "  make test-api      Run API tests with coverage"
	@echo "  make test-web      Run Web tests with coverage"
	@echo "  make test-e2e      Run E2E tests"
	@echo "  make test-contracts Run Worker contract tests"
	@echo ""
	@echo "Quality:"
	@echo "  make lint          Run all linters"
	@echo "  make typecheck     Run type checkers"
	@echo "  make format        Format all code"
	@echo "  make clean         Clean build artifacts"

install:
	@echo "Installing Python dependencies..."
	cd apps/api && pip install -e ".[dev]"
	@echo "Installing Node dependencies..."
	npm install
	@echo "Done!"

db-up:
	@echo "Starting Postgres..."
	docker run -d \
		--name sitewatcher-postgres \
		-e POSTGRES_USER=postgres \
		-e POSTGRES_PASSWORD=postgres \
		-e POSTGRES_DB=sitewatcher \
		-p 5432:5432 \
		postgres:16-alpine || docker start sitewatcher-postgres
	@echo "Postgres running on localhost:5432"

db-down:
	docker stop sitewatcher-postgres || true

migrate:
	@echo "Running migrations..."
	cd apps/api && alembic upgrade head

seed:
	@echo "Seeding database..."
	cd infra/db && python seed.py

dev:
	@echo "Starting all services..."
	@echo "Use Ctrl+C to stop"
	docker start sitewatcher-postgres 2>/dev/null || make db-up
	@sleep 2
	@make migrate
	@echo "Starting API and Web..."
	@(cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000) & \
	(cd apps/web && npm run dev) & \
	wait

test:
	@echo "Running all tests..."
	@make test-api
	@make test-web
	@make test-contracts
	@make test-e2e

test-api:
	@echo "Running API tests..."
	cd apps/api && pytest -v --cov=app --cov-report=term-missing --cov-report=html --cov-fail-under=90

test-web:
	@echo "Running Web tests..."
	cd apps/web && npm run test:coverage

test-e2e:
	@echo "Running E2E tests..."
	cd tests/e2e && npx playwright test

test-contracts:
	@echo "Running contract tests..."
	cd tests/contracts && pytest -v

lint:
	@echo "Linting Python..."
	cd apps/api && ruff check .
	@echo "Linting TypeScript..."
	cd apps/web && npm run lint
	cd packages/shared && npm run lint

typecheck:
	@echo "Type checking Python..."
	cd apps/api && mypy app
	@echo "Type checking TypeScript..."
	cd apps/web && npm run typecheck
	cd packages/shared && npm run typecheck

format:
	@echo "Formatting Python..."
	cd apps/api && ruff format .
	@echo "Formatting TypeScript..."
	cd apps/web && npm run format
	cd packages/shared && npm run format

clean:
	@echo "Cleaning build artifacts..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -rf apps/api/htmlcov
	@echo "Done!"

