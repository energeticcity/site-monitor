# SiteWatcher

Production-ready multi-tenant SaaS for detecting new posts on websites.

## Architecture

- **API**: FastAPI (Python 3.11+), SQLAlchemy 2.x, Alembic migrations
- **Web**: Next.js 14 (App Router) + TypeScript + Tailwind
- **DB**: Postgres (Neon/Supabase compatible)
- **Auth**: Email magic-link (JWT for API)
- **Discovery**: Delegates to existing Cloudflare Worker

## Project Structure

```
sitewatcher/
  apps/
    api/                 # FastAPI backend
    web/                 # Next.js dashboard
  packages/
    shared/              # Shared types, schemas, Worker client
  infra/
    db/                  # Alembic migrations & seed scripts
  tests/
    e2e/                 # Playwright end-to-end tests
    contracts/           # Worker contract tests
  docs/
    MASTER_SPEC.md       # Canonical product & technical spec
    ROADMAP.md           # Feature backlog
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker (for Postgres)
- Make

### Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. Install dependencies:
   ```bash
   make install
   ```

3. Start Postgres:
   ```bash
   make db-up
   ```

4. Run migrations:
   ```bash
   make migrate
   ```

5. Seed database:
   ```bash
   make seed
   ```

### Development

Run all services:
```bash
make dev
```

This starts:
- Postgres (Docker)
- API on http://localhost:8000
- Web on http://localhost:3000

### Testing

Run all tests:
```bash
make test
```

Run specific test suites:
```bash
make test-api       # API tests with coverage
make test-web       # Web tests with coverage
make test-e2e       # Playwright E2E tests
make test-contracts # Worker contract tests
```

### Quality Checks

```bash
make lint          # Run all linters
make typecheck     # Run type checkers
make format        # Format all code
```

## Roles & Permissions

- **Super Admin**: Global access, can create tenants and invite users
- **Admin**: Tenant-level admin, can manage sites and invite members
- **Member**: Read-only access to tenant resources

## API Endpoints

See `docs/MASTER_SPEC.md` for full API documentation.

Key endpoints:
- `POST /v1/auth/magic-link` - Request magic link
- `POST /v1/tenants` - Create tenant (super_admin)
- `POST /v1/sites` - Add site to monitor
- `POST /v1/sites/{id}/run` - Trigger discovery run
- `GET /v1/sites/{id}/items` - Get discovered items

## Testing Standards

- API: ≥90% coverage (pytest)
- Web: ≥85% coverage (Vitest)
- E2E: All critical journeys pass (Playwright)
- Contract: Worker responses validated
- Security: RBAC, IDOR, SQL injection tests

## CI/CD

GitHub Actions runs:
1. Install & build
2. Database migrations
3. API tests + coverage
4. Web tests + coverage
5. E2E tests (headless)
6. Contract tests (with fixtures)
7. Lint & typecheck

**Do not deploy until CI is green.**

## License

Proprietary