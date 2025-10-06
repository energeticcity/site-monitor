# 🚂 Complete Railway Setup Guide

## ✅ What You Should Have When Done

Your Railway project should have **TWO services**:
1. 🗄️ **PostgreSQL** (Database)
2. 🚀 **API** (Your FastAPI Application)

---

## 📋 Step-by-Step Setup

### Part 1: Create New Project

#### 1. Go to Railway Dashboard
- Visit: **https://railway.app/dashboard**
- Sign in with GitHub if not already

#### 2. Create New Project
- Click **"New Project"** button
- You'll see several options

#### 3. Choose "Deploy from GitHub repo"
- Click **"Deploy from GitHub repo"**
- Find and select: **`energeticcity/site-monitor`**
- Railway will start analyzing your repo

---

### Part 2: Configure Your API Service

#### 4. Service Will Be Created
- Railway creates a service automatically
- It will show "Deploying..." or building

#### 5. Click on the Service
- Click on the newly created service card
- You'll enter the service settings

#### 6. Configure Root Directory ⚠️ CRITICAL
- Go to **Settings** tab
- Scroll to **"Root Directory"**
- Click **Edit** or type in the field
- Enter: **`apps/api`**
- Press Enter or click Save
- **This is critical!** Without it, Railway won't find your code

#### 7. Set Start Command
- Still in **Settings**
- Find **"Start Command"** or **"Custom Start Command"**
- Enter: **`uvicorn app.main:app --host 0.0.0.0 --port $PORT`**
- Save

#### 8. Wait for Initial Deployment
- Railway will redeploy with correct settings
- Go to **Deployments** tab
- Wait for the build to complete
- You should see ✅ "Success" (it might fail first - that's ok, we'll fix it)

---

### Part 3: Add PostgreSQL Database

#### 9. Add PostgreSQL
- Click the **"+ New"** button in your project
- Select **"Database"**
- Choose **"Add PostgreSQL"**
- Railway creates a PostgreSQL service

#### 10. Name Your Database (Optional)
- You can rename it to something like "postgres-production"
- Or leave it as default

---

### Part 4: Connect Database to API

#### 11. Link Database to API Service
- Click on your **API service** (not the database)
- Go to **Variables** tab
- Click **"+ New Variable"**
- Add these variables:

**Variable 1:**
```
Name: DATABASE_URL
Value: ${{Postgres.DATABASE_URL}}
```
**Note:** Type exactly `${{Postgres.DATABASE_URL}}` - Railway will auto-link it

**Variable 2:**
```
Name: JWT_SECRET
Value: aZHI4VaNjZZKKYqKC55xunz8s9APVJ7ywiCiz_URzyI
```

**Variable 3:**
```
Name: WORKER_BASE_URL
Value: https://placeholder.workers.dev
```

**Variable 4:**
```
Name: CORS_ORIGINS
Value: http://localhost:3000
```

**Variable 5:**
```
Name: SUPER_ADMIN_EMAIL
Value: areaburn@moosemediafsj.ca
```

**Variable 6:**
```
Name: SUPER_ADMIN_NAME
Value: Adam Reaburn
```

#### 12. Service Will Redeploy
- After adding variables, Railway redeploys automatically
- Go to **Deployments** tab
- Wait for it to finish
- Look for ✅ "Success"

---

### Part 5: Generate Public Domain

#### 13. Create Public URL
- Still in your **API service**
- Go to **Settings** tab
- Scroll to **"Networking"** section
- Click **"Generate Domain"** button
- Railway creates: `https://site-monitor-production-xxxx.up.railway.app`

#### 14. Copy Your API URL
- Copy this URL - you'll need it for Vercel!
- Example: `https://site-monitor-production-a1b2c3.up.railway.app`

---

### Part 6: Run Database Migrations

#### 15. Migrate Database Schema
- In your **API service** → **Settings**
- Find **"Start Command"**
- Temporarily change to:
  ```
  alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- Save (triggers redeploy)
- Go to **Deployments** → **View Logs**
- Look for migration messages
- After success, change start command back to:
  ```
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

#### 16. Seed Database (Create Super Admin)
- Again, temporarily change start command to:
  ```
  cd apps/api && python ../infra/db/seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```
- Wait for deployment
- Check logs for: "✅ Database seeded successfully!"
- Change command back to normal

---

### Part 7: Verify Everything Works

#### 17. Test Your API
- Open your API URL in browser
- Example: `https://site-monitor-production-xxxx.up.railway.app`
- You should see JSON:
  ```json
  {
    "name": "SiteWatcher API",
    "version": "0.1.0",
    "docs": "/docs"
  }
  ```

#### 18. Check API Documentation
- Visit: `https://your-api-url.up.railway.app/docs`
- You should see FastAPI Swagger docs
- Try the `/healthz` endpoint
- Should return: `{"status": "ok", "database": "connected"}`

---

## ✅ Final Checklist

Your Railway project should now have:

- [ ] **Two services visible:**
  - [ ] PostgreSQL database
  - [ ] API service (from GitHub repo)

- [ ] **API Service configured with:**
  - [ ] Root Directory: `apps/api`
  - [ ] Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - [ ] Public domain generated
  - [ ] 6 environment variables set

- [ ] **Database:**
  - [ ] Migrations run (tables created)
  - [ ] Super admin seeded

- [ ] **Testing:**
  - [ ] API URL loads in browser
  - [ ] `/docs` shows Swagger UI
  - [ ] `/healthz` shows database connected

---

## 🔧 Environment Variables Summary

Your API service should have these variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | Auto-links to PostgreSQL |
| `JWT_SECRET` | `aZHI4VaNjZZKKYqKC55xunz8s9APVJ7ywiCiz_URzyI` | Secure authentication |
| `WORKER_BASE_URL` | `https://placeholder.workers.dev` | Cloudflare Worker (placeholder) |
| `CORS_ORIGINS` | `http://localhost:3000` | Allow frontend access |
| `SUPER_ADMIN_EMAIL` | `areaburn@moosemediafsj.ca` | Your admin email |
| `SUPER_ADMIN_NAME` | `Adam Reaburn` | Your name |

**Later, update `CORS_ORIGINS` to:**
```
http://localhost:3000,https://your-vercel-app.vercel.app
```

---

## 🆘 Troubleshooting

### "Build failed" Error
- **Check:** Root Directory is set to `apps/api`
- **Check:** Start Command is correct
- **Check:** Look at deployment logs for specific error

### "Database connection failed"
- **Check:** `DATABASE_URL` variable is set
- **Check:** Value is `${{Postgres.DATABASE_URL}}` (with double braces)
- **Check:** PostgreSQL service is running

### "Module not found" Error
- **Check:** Root Directory is `apps/api` not `apps/api/`
- **Check:** Your latest code is pushed to GitHub

### Can't access API URL
- **Check:** Public domain is generated
- **Check:** Deployment shows "Success"
- **Check:** Try `/healthz` endpoint

---

## 🎯 What Happens Next

After Railway is set up correctly:

1. **Update Vercel:**
   - Add `NEXT_PUBLIC_API_URL` environment variable
   - Value: Your Railway API URL
   - Redeploy Vercel

2. **Update Railway CORS:**
   - Add your Vercel URL to `CORS_ORIGINS`
   - Value: `http://localhost:3000,https://your-app.vercel.app`

3. **Test Login:**
   - Visit your Vercel site
   - Sign in with: `areaburn@moosemediafsj.ca`
   - Check Railway logs for magic link
   - Click magic link to log in

---

## 📚 Quick Reference

**Railway Dashboard:** https://railway.app/dashboard

**Your Project Should Look Like:**
```
📦 site-monitor (Project)
├── 🚀 site-monitor-api (Service)
│   ├── Root Dir: apps/api
│   ├── Domain: https://xxx.up.railway.app
│   └── Variables: 6 total
└── 🗄️ postgres (Database)
    └── Linked to API via DATABASE_URL
```

---

## ✨ Success Criteria

You're done when:
- ✅ Visit API URL → See JSON response
- ✅ Visit API URL/docs → See Swagger docs  
- ✅ Visit API URL/healthz → Shows "database: connected"
- ✅ Railway shows 2 services (API + Postgres)
- ✅ Both services show green/active status

---

**If you get stuck at any step, let me know exactly what you see and I'll help!** 🚀
