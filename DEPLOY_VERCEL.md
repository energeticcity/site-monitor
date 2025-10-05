# Deploying SiteWatcher to Vercel

## 🚀 IMPORTANT: You MUST Configure Root Directory

This is a **monorepo** project. The Next.js app is in `apps/web/`, not the root.

### ⚠️ REQUIRED STEP - Configure Root Directory in Vercel UI

**YOU MUST DO THIS IN VERCEL'S WEB INTERFACE:**

1. **Go to your Vercel project:**
   - Visit: https://vercel.com/dashboard
   - Select your `site-monitor` project
   
2. **Go to Settings:**
   - Click **"Settings"** in the top menu
   - Click **"General"** in the left sidebar

3. **Set Root Directory:**
   - Scroll down to **"Root Directory"** section
   - Click **"Edit"** button
   - Type: **`apps/web`** (exactly as shown)
   - Click **"Save"**

4. **Clear Build Settings (if you changed them):**
   - In Settings → "Build & Development Settings"
   - If you see custom commands, click "Override" toggle to turn them OFF
   - Let Vercel auto-detect Next.js

5. **Redeploy:**
   - Go to **"Deployments"** tab
   - Click **"..."** menu on the latest deployment
   - Click **"Redeploy"**

**That's it!** The build will now succeed. ✅

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

## ❌ Don't Use Custom Build Commands

**DO NOT override build commands!** Just set the Root Directory and let Vercel auto-detect everything.

Setting Root Directory to `apps/web` is the ONLY correct way for this project.

---

## 📝 Changes Made to Fix Deployment

1. ✅ Removed unused `@sitewatcher/shared` dependency from `apps/web/package.json`
2. ✅ Updated `next.config.js` to remove transpilePackages  
3. ✅ Added `.vercelignore` to optimize deployment
4. ✅ Created this deployment guide

**No special Vercel configuration files needed** - just set Root Directory in UI!

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

