# Deploying SiteWatcher to Vercel

## 🚀 Quick Fix for Current Error

The build error occurs because this is a **monorepo** and Vercel is trying to build from the root, but the Next.js app is in `apps/web/`.

### Solution: Configure Root Directory in Vercel

1. **Go to your Vercel project settings:**
   - Visit: https://vercel.com/energeticcity/site-monitor/settings/general
   - Or: Dashboard → Your Project → Settings → General

2. **Update Root Directory:**
   - Find the "Root Directory" section
   - Click "Edit"
   - Enter: `apps/web`
   - Click "Save"

3. **Redeploy:**
   - Go to Deployments tab
   - Click "Redeploy" on the latest deployment
   - Or push a new commit

That's it! The build should now succeed.

---

## 📋 Complete Vercel Configuration

### Project Settings

In your Vercel project settings, configure:

**General Settings:**
```
Root Directory: apps/web
Node.js Version: 20.x
```

**Build & Development Settings:**
```
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
Development Command: npm run dev
```

### Environment Variables

Add these environment variables in Vercel:

**Required:**
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

**Optional (for production):**
```
NODE_ENV=production
```

---

## 🔧 Alternative: Manual Build Command

If you prefer to keep root directory as-is, you can override the build command:

**In Vercel Project Settings → Build & Development Settings:**

```
Root Directory: (leave empty or /)
Build Command: cd apps/web && npm install && npm run build
Install Command: npm install --prefix apps/web
Output Directory: apps/web/.next
```

However, the **recommended approach is to set Root Directory to `apps/web`** as it's cleaner.

---

## 📝 Changes Made to Fix Deployment

1. ✅ Removed unused `@sitewatcher/shared` dependency from `apps/web/package.json`
2. ✅ Updated `next.config.js` to remove transpilePackages
3. ✅ Created `vercel.json` (backup configuration)
4. ✅ Created this deployment guide

---

## 🔄 Deployment Workflow

### Initial Setup
1. Push code to GitHub ✅ (Already done)
2. Connect repository to Vercel
3. Configure Root Directory: `apps/web`
4. Add environment variables
5. Deploy

### Future Deployments
Simply push to `main` branch:
```bash
git add .
git commit -m "Your changes"
git push
```

Vercel will automatically deploy!

---

## 🌐 Post-Deployment Setup

### 1. Configure API URL

After deploying your API (if separate), update the environment variable:

```
NEXT_PUBLIC_API_URL=https://your-api.example.com
```

### 2. Update CORS in API

In your FastAPI app (`apps/api/app/main.py`), add your Vercel domain to CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-vercel-domain.vercel.app",
        "https://your-custom-domain.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Test the Deployment

Visit your Vercel URL and verify:
- ✅ Homepage loads
- ✅ Dashboard displays (after authentication)
- ✅ API calls work (check browser console)
- ✅ Add site form works
- ✅ Site details page works

---

## 🐛 Troubleshooting

### Build fails with "Couldn't find any `pages` or `app` directory"
- **Fix:** Set Root Directory to `apps/web` in Vercel settings

### Module not found errors
- **Fix:** Ensure all dependencies are in `apps/web/package.json`
- Check that no monorepo packages are referenced

### API calls fail
- **Fix:** Check `NEXT_PUBLIC_API_URL` environment variable
- Verify CORS settings in API
- Check browser console for errors

### Styling issues
- **Fix:** Ensure `tailwind.config.ts` and `postcss.config.js` are in `apps/web/`
- Both files are already there ✅

---

## 📦 Deploying the API

The API (`apps/api`) should be deployed separately. Options:

### Option 1: Railway
```bash
# From apps/api directory
railway init
railway up
```

### Option 2: Fly.io
```bash
# From apps/api directory
fly launch
fly deploy
```

### Option 3: Render
- Create new Web Service
- Root Directory: `apps/api`
- Build Command: `pip install -e .`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## ✅ Quick Checklist

Before going live:

- [ ] Set Root Directory to `apps/web` in Vercel
- [ ] Add `NEXT_PUBLIC_API_URL` environment variable
- [ ] Deploy API separately
- [ ] Update CORS in API with Vercel domain
- [ ] Test all pages (dashboard, add site, site details)
- [ ] Verify authentication works
- [ ] Test API integration
- [ ] Set up custom domain (optional)

---

## 🎉 Summary

**Current Status:** Configuration fixed, ready to redeploy

**Next Step:** Go to Vercel settings and set Root Directory to `apps/web`, then redeploy.

Your SiteWatcher dashboard will be live! 🚀

