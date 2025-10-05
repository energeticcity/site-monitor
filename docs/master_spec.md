# SiteWatcher - Master Specification

**Version:** 0.1.0  
**Last Updated:** 2025-10-05

## Overview

SiteWatcher is a production-ready, multi-tenant SaaS platform that detects new posts on websites. Discovery and crawling are delegated to an existing Cloudflare Worker.

## Architecture

### Technology Stack

- **API**: FastAPI (Python 3.11+), SQLAlchemy 2.x, Alembic migrations, httpx
- **Database**: Postgres (Neon/Supabase compatible)
- **Web**: Next.js 14 (App Router), TypeScript, Tailwind CSS
- **Auth**: Email magic-link (JWT for API sessions)
- **Notifications**: Slack webhooks, Email (Postmark/SES), Outgoing webhooks
- **Discovery**: Existing Cloudflare Worker (not part of this codebase)

### Worker Integration

We integrate with an existing Cloudflare Worker with these endpoints:

1. **POST {WORKER_BASE_URL}/discover**
   - Body: `{ "url": "https://example.com" }`
   - Response: `{ source: string, links?: string[], feeds?: string[], count: number, diagnostics?: object }`

2. **POST {WORKER_BASE_URL}/profiles/rcmp-fsj**
   - Body (optional): `{ "monthsBack": number }`
   - Response: Same shape as /discover

## Data Model

### Tenancy & Roles

**Roles:**
- `super_admin`: Global access, can create tenants and invite users
- `admin`: Tenant-level admin, can manage sites and invite members
- `member`: Read-only access to tenant resources

### Tables

#### tenants
- `id` (UUID, PK)
- `name` (VARCHAR, NOT NULL)
- `plan` (VARCHAR, DEFAULT 'free')
- `created_at` (TIMESTAMP)

#### users
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE, NOT NULL)
- `name` (VARCHAR)
- `created_at` (TIMESTAMP)

#### user_tenants
- `user_id` (UUID, FK → users)
- `tenant_id` (UUID, FK → tenants)
- `role` (ENUM: super_admin, admin, member)
- PK: (user_id, tenant_id)

#### sites
- `id` (UUID, PK)
- `tenant_id` (UUID, FK → tenants)
- `url` (VARCHAR, NOT NULL)
- `profile_key` (VARCHAR, NULLABLE) # e.g., 'rcmp_fsj'
- `keywords` (TEXT[], NULLABLE)
- `enabled` (BOOLEAN, DEFAULT true)
- `interval_minutes` (INTEGER, DEFAULT 60)
- `last_run_at` (TIMESTAMP, NULLABLE)
- `created_at` (TIMESTAMP)

#### runs
- `id` (UUID, PK)
- `site_id` (UUID, FK → sites)
- `status` (ENUM: running, success, error)
- `method` (VARCHAR) # 'profile', 'discover'
- `pages_scanned` (INTEGER)
- `duration_ms` (INTEGER)
- `diagnostics_json` (JSONB)
- `started_at` (TIMESTAMP)
- `finished_at` (TIMESTAMP, NULLABLE)

#### items
- `id` (UUID, PK)
- `site_id` (UUID, FK → sites)
- `url` (VARCHAR, NOT NULL)
- `canonical_url` (VARCHAR)
- `title` (VARCHAR)
- `published_at` (TIMESTAMP, NULLABLE)
- `discovered_at` (TIMESTAMP, NOT NULL)
- `source` (VARCHAR) # 'feed', 'html', 'sitemap'
- `meta_json` (JSONB)
- UNIQUE(site_id, canonical_url)

#### webhooks
- `id` (UUID, PK)
- `tenant_id` (UUID, FK → tenants)
- `endpoint_url` (VARCHAR, NOT NULL)
- `secret` (VARCHAR)
- `active` (BOOLEAN, DEFAULT true)
- `created_at` (TIMESTAMP)

#### api_keys
- `id` (UUID, PK)
- `tenant_id` (UUID, FK → tenants)
- `name` (VARCHAR)
- `token_hash` (VARCHAR, NOT NULL)
- `scopes` (VARCHAR[])
- `created_at` (TIMESTAMP)
- `last_used_at` (TIMESTAMP, NULLABLE)

#### invites
- `id` (UUID, PK)
- `email` (VARCHAR, NOT NULL)
- `tenant_id` (UUID, FK → tenants)
- `role` (ENUM: admin, member)
- `token_hash` (VARCHAR, NOT NULL)
- `expires_at` (TIMESTAMP)
- `accepted_at` (TIMESTAMP, NULLABLE)
- `created_at` (TIMESTAMP)

## API Endpoints (v1)

### Authentication

#### POST /v1/auth/magic-link
Request magic link for email.
- Body: `{ email: string }`
- Response: `{ success: true, message: string }`
- Dev stub: Always succeeds, logs link to console

#### POST /v1/auth/magic-link/callback
Exchange magic link token for JWT.
- Body: `{ token: string }`
- Response: `{ access_token: string, user: {...} }`
- Sets httpOnly cookie

#### GET /v1/me
Get current user info.
- Response: `{ id, email, name, tenants: [...] }`

### Tenants

#### POST /v1/tenants
Create tenant (super_admin only).
- Body: `{ name: string, plan?: string }`
- Response: `{ id, name, plan, created_at }`

#### GET /v1/tenants
List all tenants (super_admin only).
- Response: `{ tenants: [...], total: number }`

### Users & Invites

#### POST /v1/invites
Invite user to tenant (admin role).
- Body: `{ email: string, role: 'admin' | 'member', tenant_id: UUID }`
- Response: `{ id, email, role, invite_link: string }`

#### POST /v1/invites/accept
Accept invitation.
- Body: `{ token: string, name?: string }`
- Response: `{ success: true, tenant: {...} }`

### Sites

#### POST /v1/sites
Add site to monitor.
- Body: `{ url: string, profile_key?: string, interval_minutes?: number, keywords?: string[] }`
- Response: `{ id, url, profile_key, enabled, ... }`
- Tenant scoped

#### GET /v1/sites
List sites for tenant.
- Query: `?page=1&limit=20`
- Response: `{ sites: [...], total: number }`

#### GET /v1/sites/{id}
Get site details.
- Response: `{ id, url, last_run_at, ... }`

#### POST /v1/sites/{id}/run
Trigger discovery run.
- Response: `{ run_id, status: 'running' }`
- Async: calls Worker, persists Run + Items, triggers notifications

#### GET /v1/sites/{id}/items
Get discovered items (paginated).
- Query: `?cursor=<id>&limit=20`
- Response: `{ items: [...], next_cursor?: string }`

#### GET /v1/sites/{id}/runs
Get run history.
- Query: `?page=1&limit=10`
- Response: `{ runs: [...], total: number }`

### Webhooks

#### POST /v1/webhooks
Create outgoing webhook.
- Body: `{ endpoint_url: string, secret?: string }`
- Response: `{ id, endpoint_url, active, ... }`

#### GET /v1/webhooks
List webhooks for tenant.
- Response: `{ webhooks: [...] }`

### API Keys

#### POST /v1/keys
Create API key.
- Body: `{ name: string, scopes?: string[] }`
- Response: `{ id, name, token: string } // token shown once`

#### GET /v1/keys
List API keys.
- Response: `{ keys: [...] } // tokens are hashed`

### Health

#### GET /healthz
Health check.
- Response: `{ status: 'ok', database: 'connected' }`

## Authentication & Security

### JWT Flow
1. User requests magic link via email
2. Dev stub logs link to console
3. User clicks link with token
4. API validates token, creates JWT
5. JWT stored in httpOnly cookie
6. All API requests include cookie or `Authorization: Bearer <token>`

### RBAC Middleware
- Every endpoint validates tenant membership
- Queries automatically scoped to user's tenant(s)
- Super admin can access all tenants
- IDOR protection: validate resource ownership

### Security Tests
- SQL injection: parameterized queries only
- IDOR: attempt cross-tenant access (must 403)
- Role enforcement: member cannot create sites

## Web Application

### Pages

#### Auth
- `/auth/signin` - Magic link request
- `/auth/callback` - Magic link validation

#### Super Admin
- `/admin/tenants` - List/create tenants
- `/admin/metrics` - System metrics

#### Tenant Admin/Member
- `/dashboard` - Overview
- `/sites` - Sites list + Add Site modal
- `/sites/[id]` - Site detail (Run Now, Items, Runs)
- `/settings` - Slack/email/webhook config

### UI Components
- `<SiteForm>` - Add/edit site
- `<ItemsTable>` - Discovered items with pagination
- `<RunsHistory>` - Run history with status badges
- `<RunNowButton>` - Trigger discovery
- `<NotificationSettings>` - Configure notifications

## Discovery Flow

1. Admin adds Site with URL and optional `profile_key: 'rcmp_fsj'`
2. Admin clicks "Run Now" or cron triggers
3. API creates Run record (status: 'running')
4. API calls Worker:
   - If profile_key: POST /profiles/{profile_key}
   - Else: POST /discover with URL
5. Worker returns links/feeds and count
6. API:
   - Parses response
   - Creates/updates Items (deduped by canonical_url)
   - Updates Run (status: 'success'/'error')
   - Triggers notifications (Slack, email, webhooks)
7. Web polls or receives update, shows new Items

## Notifications

### Slack
- POST to webhook URL with formatted message
- Includes site name, item count, link to dashboard

### Email
- Postmark or SES
- Recipients configured per tenant
- Template: "X new items found on Site Y"

### Webhooks
- POST to tenant's webhook URL
- HMAC signature in header
- Payload: `{ event: 'items.discovered', site_id, items: [...] }`

### Test Transports
- In tests: use mock transports, assert payloads
- No actual network calls during test runs

## Testing Strategy

### API Tests (pytest)
- **Unit**: Services, auth, RBAC, deduplication
- **Integration**: Full request → response with test DB
- **Worker mocks**: respx for success/empty/error cases
- **Security**: RBAC isolation, IDOR, SQL injection
- **Coverage**: ≥90% statements/branches

### Web Tests (Vitest)
- **Unit**: Components with React Testing Library
- **Coverage**: ≥85%

### E2E Tests (Playwright)
- Login → create tenant → invite admin → accept
- Add RCMP FSJ site → run now → items appear
- Add generic site → discover → items saved
- Mock Worker responses for speed
- Optional nightly: real Worker with rate limiting

### Contract Tests
- Validate Worker responses against JSON schema
- Run against fixtures in CI
- Optional nightly against real Worker

## Quality Gates (CI)

All must pass for green CI:
1. API tests ≥90% coverage
2. Web tests ≥85% coverage
3. E2E tests pass (mocked Worker)
4. Contract tests pass (fixtures)
5. Lint: ruff (Python), ESLint (TS)
6. Typecheck: mypy --strict, tsc --strict
7. Security tests pass

## Development Workflow

1. `make install` - Install dependencies
2. `make db-up` - Start Postgres
3. `make migrate` - Run migrations
4. `make seed` - Seed database
5. `make dev` - Start all services
6. `make test` - Run all tests

## Deployment

**Not yet implemented.** Deployment to Vercel/Railway will happen after CI is green.

## Roadmap

See `ROADMAP.md` for planned features and backlog.