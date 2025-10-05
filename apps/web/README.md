# SiteWatcher Web Application

This is the Next.js frontend for SiteWatcher - a multi-tenant SaaS platform for detecting new posts on websites.

## Features

- Business dashboard with statistics
- Recent discoveries from monitored sites
- Team member management
- Add and manage websites to monitor
- Site detail pages with items and run history

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **UI:** React 18, Tailwind CSS
- **Language:** TypeScript
- **Testing:** Vitest, Playwright

## Environment Variables

Required:
- `NEXT_PUBLIC_API_URL` - API endpoint URL

## Development

```bash
npm install
npm run dev
```

## Building

```bash
npm run build
npm start
```

## Deploying to Vercel

**Important:** This is part of a monorepo. In Vercel:
1. Set **Root Directory** to `apps/web`
2. Let Vercel auto-detect Next.js
3. Add environment variable: `NEXT_PUBLIC_API_URL`

See `../../DEPLOY_VERCEL.md` for complete instructions.

