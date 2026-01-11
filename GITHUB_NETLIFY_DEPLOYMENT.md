# GitHub + Netlify Deployment Guide

## Step 1: Push to GitHub

### Option A: GitHub CLI (Easiest)

```bash
# 1. Install GitHub CLI from: https://cli.github.com/

# 2. Authenticate
gh auth login

# 3. Create new repository
gh repo create caimf \
  --source=. \
  --remote=origin \
  --push \
  --description="Child Aadhaar Inclusion Monitoring Framework - Real-time enrolment monitoring system"

# Done! Your repo is now on GitHub
```

### Option B: Web + Git (Manual)

```bash
# 1. Create repo on GitHub.com
#    - Go to github.com/new
#    - Name: caimf
#    - Description: Child Aadhaar Inclusion Monitoring Framework
#    - Public (for Netlify deployment)
#    - Create repository

# 2. Add remote and push
git remote add origin https://github.com/YOUR_USERNAME/caimf.git
git branch -M main
git push -u origin main

# Done!
```

---

## Step 2: Deploy with Netlify

### Option A: Netlify CLI (Fastest)

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Login to Netlify
netlify login

# 3. Deploy from git
netlify sites:create --name=caimf --git

# During setup:
# - Repository: your-username/caimf
# - Build command: (leave empty or: npm install)
# - Publish directory: /

# 4. Configure environment variables
netlify env:set API_URL https://caimf-api.herokuapp.com

# Done! Site deployed at: caimf.netlify.app
```

### Option B: Netlify Web UI (Recommended)

```
1. Go to netlify.com
2. Click "New site from Git"
3. Choose "GitHub" provider
4. Authorize GitHub
5. Select your repository: caimf
6. Configure build settings:
   - Build command: (leave empty)
   - Publish directory: /
   - Environment variables:
     API_URL=https://caimf-api.herokuapp.com
7. Click "Deploy site"

Your site is now live at: caimf.netlify.app
```

---

## Step 3: Deploy API Backend (Separate Services)

### Option A: Deploy API to Render (Recommended)

```bash
# 1. Go to render.com
# 2. Click "New" → "Web Service"
# 3. Connect GitHub repository
# 4. Configure:
#    - Environment: Python 3.9
#    - Build command: pip install -r requirements.txt
#    - Start command: uvicorn caimf.api:app --host 0.0.0.0 --port 10000
#    - Environment variables:
#      - API_PORT=10000
#      - LOG_LEVEL=info
#      - ENABLE_API_AUTH=false

# 5. Deploy
# 6. Note the API URL: https://caimf-api.onrender.com

# 7. Update Netlify environment variable:
#    netlify env:set API_URL https://caimf-api.onrender.com
```

### Option B: Deploy API to Heroku

```bash
# 1. Create Procfile in project root:
echo "web: uvicorn caimf.api:app --host 0.0.0.0 --port \$PORT" > Procfile

# 2. Deploy to Heroku
heroku create caimf-api
git push heroku main

# 3. Set environment variables
heroku config:set API_PORT=5000

# 4. Update Netlify env var:
#    API_URL=https://caimf-api.herokuapp.com
```

### Option C: Deploy to AWS Lambda

```bash
# Use Serverless Framework
npm install -g serverless
serverless create --template aws-python
serverless deploy
```

---

## Step 4: Deploy Dashboard with Streamlit Cloud

### Deploy Streamlit Dashboard

```bash
# 1. Go to streamlit.io/cloud
# 2. Connect GitHub account
# 3. Click "New app"
# 4. Select repository: your-username/caimf
# 5. Branch: main
# 6. Main file path: caimf/dashboard.py
# 7. Deploy

# Dashboard live at: caimf.streamlit.app
```

---

## Complete Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Users                                      │
└──────────────┬──────────────────────────┬────────────────────┘
               │                          │
               ▼                          ▼
        ┌─────────────────┐      ┌──────────────────┐
        │ Netlify Pages   │      │ Streamlit Cloud  │
        │ (Static Site)   │      │ (Dashboard)      │
        │ caimf.netlify.. │      │ caimf.streamlit. │
        └────────┬────────┘      └────────┬─────────┘
                 │                        │
                 │                        │
        ┌────────▼────────────────────────▼──────────┐
        │    API Routing Layer (Functions)           │
        │    (netlify/functions/api.py)              │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │  Backend API (Render)  │
        │ caimf-api.onrender.com │
        │ (FastAPI + UIDAI Data) │
        └────────────────────────┘
```

---

## Environment Variables to Set

### Netlify
```
API_URL=https://caimf-api.onrender.com
ENABLE_CORS=true
LOG_LEVEL=info
```

### Render (API Backend)
```
PYTHONUNBUFFERED=1
LOG_LEVEL=info
ENABLE_API_AUTH=false
DATA_RAW_PATH=/app/data/raw
```

---

## Post-Deployment Verification

### Check Netlify Deployment
```bash
# View deployment logs
netlify open --admin

# Test site
curl https://caimf.netlify.app

# View functions
netlify functions:list
```

### Check API Backend
```bash
# Test API health
curl https://caimf-api.onrender.com/health

# Expected response:
# {"status":"healthy","data_loaded":true}
```

### Check Dashboard
```bash
# Access at: https://caimf.streamlit.app
# Click "Load UIDAI Enrolment Dataset"
```

---

## Troubleshooting

### Build Fails on Netlify
```
- Check netlify.toml syntax
- Verify all required environment variables are set
- Check build logs: netlify open --admin
```

### API Connection Issues
```
- Ensure API_URL environment variable is set correctly
- Check API backend status on Render dashboard
- Verify CORS settings in FastAPI
```

### Dashboard Not Loading
```
- Check Streamlit Cloud deployment status
- Verify GitHub token has correct permissions
- Ensure main.py or dashboard.py exists in root
```

---

## GitHub Repository Best Practices

### 1. Add GitHub Topics
Go to repo settings and add:
- `uidai` `aadhar` `child-enrolment` `monitoring`

### 2. Update README.md
Include deployment URLs:
```markdown
## Live Deployment
- Dashboard: https://caimf.streamlit.app
- API Docs: https://caimf-api.onrender.com/docs
- Web UI: https://caimf.netlify.app
```

### 3. Create GitHub Actions for CI/CD
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest
```

### 4. Add Badges to README
```markdown
[![Netlify Status](https://api.netlify.com/api/v1/badges/YOUR_ID/deploy-status)](https://app.netlify.com/sites/caimf/deploys)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

---

## Domain Configuration (Optional)

### Point Custom Domain to Netlify
1. Go to Netlify dashboard
2. Domain settings
3. Add custom domain
4. Point DNS to Netlify nameservers

### SSL Certificate
Netlify auto-generates and renews SSL certificates ✓

---

## Monitoring & Maintenance

### Weekly Checks
- [ ] API health endpoint responds
- [ ] Dashboard loads data
- [ ] No build errors on Netlify
- [ ] Environment variables up-to-date

### Monthly Tasks
- [ ] Review logs for errors
- [ ] Update dependencies
- [ ] Backup data
- [ ] Test recovery procedures

---

## Quick Reference: Deployment URLs

| Service | URL | Status |
|---------|-----|--------|
| GitHub Repo | github.com/YOUR_USERNAME/caimf | ✓ |
| Netlify | caimf.netlify.app | ✓ |
| API Backend | caimf-api.onrender.com | ✓ |
| Dashboard | caimf.streamlit.app | ✓ |
| API Docs | caimf-api.onrender.com/docs | ✓ |

---

**Last Updated**: January 11, 2026  
**Version**: 1.0.0
