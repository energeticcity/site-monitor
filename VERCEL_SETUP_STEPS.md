# ⚠️ REQUIRED: Vercel Configuration Steps

## The Problem

Your error: `"No Next.js version detected"`

**Cause:** Vercel is looking at the wrong directory. Your Next.js app is in `apps/web/` but Vercel is checking the root.

## The Solution (5 Minutes)

### Step 1: Open Your Vercel Project
Go to: https://vercel.com/dashboard

Click on your **`site-monitor`** project

---

### Step 2: Go to Settings
Click **"Settings"** in the top navigation menu

Then click **"General"** in the left sidebar

---

### Step 3: Find Root Directory Setting
Scroll down to the section labeled **"Root Directory"**

You'll see it says: `./` or is empty

---

### Step 4: Edit Root Directory
Click the **"Edit"** button next to Root Directory

In the text box that appears, type exactly:
```
apps/web
```

Click **"Save"**

---

### Step 5: Verify Build Settings (Important!)
Still in Settings, click **"Build & Development Settings"** in the left sidebar

**Make sure these are set:**
- Framework Preset: **Next.js** (should auto-detect)
- Build Command: Leave as `next build` or empty (auto-detected)
- Output Directory: Leave as `.next` or empty (auto-detected)
- Install Command: Leave as `npm install` or empty (auto-detected)

**If you see "Override" toggles turned ON**, turn them **OFF** to use auto-detection.

---

### Step 6: Redeploy
1. Click **"Deployments"** in the top menu
2. Find your latest (failed) deployment
3. Click the **"..."** menu button on the right
4. Click **"Redeploy"**
5. Confirm by clicking **"Redeploy"** again

---

## ✅ Expected Result

The build should now:
1. ✅ Detect Next.js version correctly
2. ✅ Install dependencies from `apps/web/package.json`
3. ✅ Build successfully
4. ✅ Deploy your dashboard

**Build time:** ~2-3 minutes

---

## 🎯 Quick Checklist

Before redeploying, verify:
- [ ] Root Directory is set to `apps/web`
- [ ] Framework Preset shows "Next.js"
- [ ] No custom build commands (let Vercel auto-detect)
- [ ] Latest code is pushed to GitHub (commit `fc3afd8`)

---

## 🔧 If Build Still Fails

1. **Check the build log** for the exact error
2. **Verify Root Directory** is exactly `apps/web` (no spaces, no leading `/`)
3. **Clear the build cache**: 
   - Settings → General → scroll to bottom
   - Click "Clear Build Cache"
   - Redeploy

4. **Double-check package.json**:
   - Make sure `apps/web/package.json` exists
   - Has `"next"` in dependencies
   - Has `"build": "next build"` in scripts

---

## 📧 Still Having Issues?

The most common mistakes:
1. ❌ Typing `apps/web/` (with trailing slash) - should be `apps/web`
2. ❌ Typing `/apps/web` (with leading slash) - should be `apps/web`
3. ❌ Having custom build commands enabled
4. ❌ Not saving the Root Directory change

**Remember:** Just set Root Directory to `apps/web` and let Vercel do the rest!

---

## 🎉 After Successful Deployment

Once deployed, you'll need to:
1. Add environment variable: `NEXT_PUBLIC_API_URL` (your API endpoint)
2. Deploy your API separately (Railway, Fly.io, or Render)
3. Update CORS in API to allow your Vercel domain

See `DEPLOY_VERCEL.md` for complete post-deployment setup.

