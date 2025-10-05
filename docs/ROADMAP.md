# SiteWatcher - Roadmap

## MVP (Current Sprint)

### Phase 1: Core Infrastructure ✅
- [x] Monorepo scaffold
- [x] Database schema & migrations
- [x] API structure with FastAPI
- [x] Auth (magic-link stub + JWT)
- [x] RBAC middleware

### Phase 2: Discovery & Monitoring
- [ ] Worker client with zod validation
- [ ] Sites CRUD endpoints
- [ ] Run trigger & Worker integration
- [ ] Item deduplication & storage
- [ ] Notifications (Slack, email, webhooks)

### Phase 3: Web Dashboard
- [ ] Next.js setup with Tailwind
- [ ] Auth pages
- [ ] Super Admin UI (tenants, metrics)
- [ ] Tenant UI (sites, runs, items)
- [ ] Settings (notifications config)

### Phase 4: Testing & Quality
- [ ] API tests (≥90% coverage)
- [ ] Web tests (≥85% coverage)
- [ ] E2E Playwright tests
- [ ] Contract tests for Worker
- [ ] Security tests (RBAC, IDOR, SQL injection)

### Phase 5: CI/CD
- [ ] GitHub Actions workflow
- [ ] Coverage enforcement
- [ ] Lint & typecheck gates
- [ ] Green CI ✓

## Post-MVP Features

### V1.1: Enhanced Monitoring
- [ ] Keyword filtering (highlight items matching keywords)
- [ ] Custom notification rules (only notify if keywords match)
- [ ] Pause/resume sites
- [ ] Bulk actions (enable/disable multiple sites)

### V1.2: Scheduling & Background Jobs
- [ ] Cron scheduler for automated runs
- [ ] Celery/Dramatiq for async tasks
- [ ] Job queue UI (view pending/failed jobs)
- [ ] Retry logic for failed runs

### V1.3: Advanced Discovery
- [ ] Multiple profiles support (not just RCMP FSJ)
- [ ] Custom selectors (CSS/XPath for specific elements)
- [ ] JavaScript rendering for SPA sites
- [ ] Archive.org fallback for historical data

### V1.4: Analytics & Insights
- [ ] Dashboard metrics (items per day, run success rate)
- [ ] Site health scores
- [ ] Trend detection (unusual activity alerts)
- [ ] Export to CSV/JSON

### V1.5: Collaboration
- [ ] Comments on items
- [ ] Tag items (reviewed, important, false positive)
- [ ] Share items via link
- [ ] Activity log (who did what when)

### V1.6: Integrations
- [ ] Zapier/Make webhooks
- [ ] Slack app (interactive commands)
- [ ] Discord notifications
- [ ] RSS feed generation per site

### V2.0: AI & Automation
- [ ] LLM summarization of new items
- [ ] Smart categorization (auto-tag by content)
- [ ] Duplicate detection (semantic similarity)
- [ ] Sentiment analysis

### V2.1: Enterprise Features
- [ ] SSO (SAML, OAuth)
- [ ] Audit logs
- [ ] Custom roles & permissions
- [ ] Whitelabel branding
- [ ] SLA monitoring

## Technical Debt & Improvements

### Performance
- [ ] Implement caching (Redis)
- [ ] Database query optimization
- [ ] CDN for static assets
- [ ] Lazy loading for large item lists

### Reliability
- [ ] Circuit breaker for Worker calls
- [ ] Exponential backoff for retries
- [ ] Dead letter queue for failed jobs
- [ ] Database connection pooling

### Observability
- [ ] Structured logging (JSON)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Metrics (Prometheus/Grafana)
- [ ] Error tracking (Sentry)

### Security
- [ ] Rate limiting per tenant/API key
- [ ] CAPTCHA for sign-in
- [ ] 2FA for admins
- [ ] Secrets rotation
- [ ] Penetration testing

### Developer Experience
- [ ] API documentation (OpenAPI/Swagger)
- [ ] SDK clients (Python, JavaScript)
- [ ] Postman collection
- [ ] Docker Compose for local dev
- [ ] Hot reload improvements

## Known Limitations

1. **No background jobs**: Runs are synchronous (blocks HTTP request)
   - Mitigation: Implement job queue in V1.2

2. **No rate limiting**: Worker can be overwhelmed
   - Mitigation: Add rate limits per tenant

3. **No caching**: Every request hits DB/Worker
   - Mitigation: Add Redis in performance sprint

4. **Single region**: No geo-distribution
   - Mitigation: Multi-region deployment in enterprise tier

5. **Magic link dev stub**: Not production-ready
   - Mitigation: Integrate real email service (Postmark/SES)

## Test Coverage Goals

| Area | Current | Target | V2.0 Goal |
|------|---------|--------|-----------|
| API | 0% | ≥90% | ≥95% |
| Web | 0% | ≥85% | ≥90% |
| E2E | 0% | Critical paths | All journeys |
| Contracts | 0% | Core endpoints | All endpoints |

## Backlog Prioritization

### P0 (MVP Blockers)
- All Phase 1-5 items above

### P1 (Next Sprint)
- Scheduling & background jobs
- Keyword filtering
- Real magic link emails

### P2 (Nice to Have)
- Analytics dashboard
- CSV export
- Collaboration features

### P3 (Future)
- AI/LLM features
- Enterprise SSO
- Multi-region deployment

## Feedback & Feature Requests

Track issues and feature requests in GitHub Issues with labels:
- `bug` - Something broken
- `enhancement` - New feature
- `documentation` - Docs improvement
- `performance` - Speed/efficiency
- `security` - Security concern

## Changelog

### 0.1.0 (2025-10-05)
- Initial MVP scaffold
- Database schema
- API structure
- Auth skeleton

---

**Last Updated:** 2025-10-05  
**Next Review:** After MVP CI green

