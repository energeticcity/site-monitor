# 🚀 Deployment Checklist

## ✅ What You've Completed

- [x] Frontend deployed to Vercel
- [x] API deployed to Railway
- [x] PostgreSQL database added

---

## 📋 Next Steps to Complete

### 1. Add API URL to Vercel ⚠️ REQUIRED

**Where:** Vercel Dashboard → Your Project → Settings → Environment Variables

**Add:**
```
Name: NEXT_PUBLIC_API_URL
Value: https://your-railway-api-url.up.railway.app
```

**Then:** Redeploy Vercel (it will rebuild with the new environment variable)

---

### 2. Update CORS in API ⚠️ REQUIRED

**What:** Allow your Vercel frontend to call your Railway API

**Where:** `apps/api/app/main.py`

**Current code (line ~17):**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ← UPDATE THIS
```

**Change to:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-vercel-app.vercel.app",  # ← ADD YOUR VERCEL URL
        "https://yourdomain.com",              # ← IF YOU HAVE CUSTOM DOMAIN
    ],
```

**Then:**
- Commit and push to GitHub
- Railway will auto-deploy the update

---

### 3. Run Database Migrations ⚠️ REQUIRED

**In Railway Dashboard:**
1. Go to your API service
2. Click **Settings** → **Deploy**
3. Under "Custom Start Command" temporarily change to:
   ```
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Save (will trigger redeploy)
5. After it deploys, change back to:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

**OR via Railway CLI:**
```bash
railway run alembic upgrade head
```

---

### 4. Seed the Database (Create Super Admin) ⚠️ REQUIRED

**In Railway Dashboard:**
1. Go to your API service
2. Click **Settings** → **Deploy**
3. Temporarily change start command to:
   ```
   python ../infra/db/seed.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Save and wait for deploy
5. Check logs - you should see: "✅ Database seeded successfully!"
6. Change command back to normal:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

**OR via Railway CLI:**
```bash
railway run python infra/db/seed.py
```

---

## 🎯 URLs You Need

Fill these in:

- **Vercel Frontend:** https://_____.vercel.app
- **Railway API:** https://_____.up.railway.app
- **Database URL:** (auto-set in Railway)

---

## ✅ Testing Checklist

After completing the above steps, test:

1. **Visit your Vercel site:**
   - [ ] Homepage loads
   - [ ] Click "Sign In"
   
2. **Test Login:**
   - [ ] Enter: `areaburn@moosemediafsj.ca`
   - [ ] Click "Send Magic Link"
   - [ ] Should see success message (not error!)
   
3. **Check Railway Logs:**
   - [ ] Railway → Your Service → Deployments → View Logs
   - [ ] Look for: "🔗 Magic Link for areaburn@moosemediafsj.ca:"
   - [ ] Copy the magic link URL
   
4. **Complete Login:**
   - [ ] Paste magic link in browser
   - [ ] Should redirect to dashboard
   - [ ] Dashboard shows "Your Business Name"
   - [ ] Can see team members, sites, etc.

5. **Test Site Management:**
   - [ ] Click "Add Site"
   - [ ] Fill in form with a test website
   - [ ] Submit
   - [ ] Should redirect to dashboard
   - [ ] New site appears in list

---

## 🐛 Common Issues

### "Cannot connect to API" error
- Check: NEXT_PUBLIC_API_URL is set in Vercel
- Check: You redeployed Vercel after adding env var

### "CORS policy blocked" error
- Check: Your Vercel URL is in allow_origins list
- Check: You pushed the CORS update to GitHub
- Check: Railway redeployed after the push

### "Magic link" not appearing
- Check: Railway logs (Deployments → View Logs)
- Check: Database was seeded (super admin exists)

### Dashboard shows errors fetching data
- Check: Database migrations ran successfully
- Check: DATABASE_URL is set in Railway
- Check: API is running (Railway service shows "Active")

---

## 🎉 Success Criteria

You're done when:
- ✅ Can log in with magic link
- ✅ Dashboard loads with your tenant name
- ✅ Can add a new site
- ✅ Site appears in dashboard
- ✅ Team members section shows you

---

## 📚 Quick Reference

**Vercel Dashboard:** https://vercel.com/dashboard
**Railway Dashboard:** https://railway.app/dashboard
**Your GitHub Repo:** https://github.com/energeticcity/site-monitor

**Super Admin Email:** areaburn@moosemediafsj.ca
**JWT Secret:** (stored in Railway environment variables)
