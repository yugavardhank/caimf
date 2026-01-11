# Deploy CAIMF Dashboard to Streamlit Cloud

## Step-by-Step Instructions

### 1. Go to Streamlit Cloud
Visit: **https://share.streamlit.io/**

### 2. Sign In
- Click "Sign in"
- Choose "Continue with GitHub"
- Authorize with your GitHub account (yugavardhank)

### 3. Create New App
- Click "New app" button
- You'll see a form with three fields:

### 4. Fill in the Deployment Form

**Repository:**
```
yugavardhank/caimf
```

**Branch:**
```
main
```

**Main file path:**
```
caimf/dashboard.py
```

### 5. Advanced Settings (Optional but Recommended)

Click "Advanced settings" and set:

**Python version:**
```
3.9
```

**App URL (optional custom subdomain):**
```
caimf-dashboard
```
(This will make your app available at: `caimf-dashboard.streamlit.app`)

### 6. Deploy!

Click the **"Deploy!"** button

### 7. Wait for Deployment

- Streamlit will install dependencies from `requirements.txt`
- This takes 2-3 minutes
- You'll see logs showing the installation progress

### 8. Your App Will Be Live At:

```
https://yugavardhank-caimf-caimf-dashboard-[hash].streamlit.app
```

Or if you set custom subdomain:
```
https://caimf-dashboard.streamlit.app
```

## Troubleshooting

### If you get dependency errors:

The app might need data files. If you see errors about missing CSV files:

1. Make sure `data/processed/` folder is in your repo (it's in .gitignore currently)
2. You may need to modify the dashboard to handle missing data gracefully

### If authentication fails:

- Make sure your GitHub account has access to the repository
- The repository must be public OR you need to grant Streamlit Cloud access to private repos

## After Deployment

Once deployed, update the `index.html` file with the actual Streamlit URL:

Replace `https://caimf.streamlit.app` with your actual deployed URL.

---

**Note:** Your local Streamlit app (running on localhost:8501) is different from the cloud deployment. The cloud version needs to be set up separately through Streamlit Cloud's interface.
