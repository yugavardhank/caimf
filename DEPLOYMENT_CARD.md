# 🎯 GitHub + Netlify Deployment - Quick Reference Card

## 📋 Three Commands to Deploy

### Command 1: Push to GitHub (Copy & Paste)

**Option A - Using GitHub CLI** (Fastest)
```bash
gh auth login
gh repo create caimf --source=. --remote=origin --push --public --description="Child Aadhaar Inclusion Monitoring Framework"
```

**Option B - Manual Git** (If no GitHub CLI)
```bash
git remote add origin https://github.com/YOUR_USERNAME/caimf.git
git branch -M main  
git push -u origin main
```

✓ **Result**: Code on GitHub at `github.com/YOUR_USERNAME/caimf`

---

### Command 2: Deploy API to Render

**Goto render.com → New Web Service**
```
Repository: caimf
Build command: pip install -r requirements.txt
Start command: uvicorn caimf.api:app --host 0.0.0.0 --port 10000
Environment variables:
  - LOG_LEVEL=info
  - PYTHONUNBUFFERED=true
```

✓ **Result**: API live at `https://caimf-api.onrender.com`

---

### Command 3: Deploy Dashboard to Streamlit

**Go to streamlit.io/cloud**
```
Repository: caimf
Main file: caimf/dashboard.py
```

✓ **Result**: Dashboard at `https://caimf.streamlit.app`

---

### Command 4: Deploy to Netlify

**Go to netlify.com → Add new site → Import from Git**
```
Repository: caimf
Build command: npm install
Environment variable:
  - API_URL = https://caimf-api.onrender.com
```

✓ **Result**: Frontend at `https://caimf.netlify.app`

---

## 🔗 Your Live URLs (After Deployment)

| Service | URL | Status |
|---------|-----|--------|
| **GitHub** | https://github.com/YOUR_USERNAME/caimf | Created |
| **API** | https://caimf-api.onrender.com | To Deploy |
| **Docs** | https://caimf-api.onrender.com/docs | Auto |
| **Dashboard** | https://caimf.streamlit.app | To Deploy |
| **Frontend** | https://caimf.netlify.app | To Deploy |

---

## ⏱️ Time Breakdown

| Step | Platform | Time | Status |
|------|----------|------|--------|
| 1 | GitHub | 5 min | ✓ Ready |
| 2 | Render | 10 min | ✓ Ready |
| 3 | Streamlit | 5 min | ✓ Ready |
| 4 | Netlify | 10 min | ✓ Ready |
| **Total** | **All** | **~30 min** | **🟢** |

---

## ✅ Pre-Deployment Checklist

- [x] Git repo initialized
- [x] .gitignore configured
- [x] All commits created
- [x] netlify.toml added
- [x] Procfile added
- [x] package.json added
- [x] Documentation complete
- [x] **Ready to push!**

---

## 🚀 Start Deployment Now

1. **Read**: `START_DEPLOYMENT.md` (in your repo)
2. **Follow**: Step-by-step instructions
3. **Copy**: Commands from above
4. **Deploy**: Watch services go live

---

## 📞 Need Help?

**Before Deploying**:
- Check `START_DEPLOYMENT.md` - numbered steps
- Review `GITHUB_NETLIFY_DEPLOYMENT.md` - detailed guide

**During Deployment**:
- Render logs: dashboard.render.com
- Netlify logs: app.netlify.com
- Streamlit logs: share.streamlit.io

**After Deployment**:
- Test health: `curl https://caimf-api.onrender.com/health`
- Visit dashboard: https://caimf.streamlit.app
- Check API docs: https://caimf-api.onrender.com/docs

---

## 💾 What's Already Done for You

✅ `.gitignore` - excludes venv, data/processed, etc.  
✅ `netlify.toml` - production ready  
✅ `Procfile` - backend ready  
✅ `package.json` - frontend ready  
✅ `runtime.txt` - Python 3.9  
✅ All commits ready to push  

---

## 🎊 That's It!

Your CAIMF system is production-ready.

**Next Step**: 
```bash
# Push to GitHub
git push origin main
```

Then follow the 4 deployment steps above.

**Time to Live**: ~40 minutes total

---

**Version**: 1.0.0 | **Status**: 🟢 Ready | **Date**: Jan 11, 2026
