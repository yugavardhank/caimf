# CAIMF Deployment Quick Reference Card

## 🚀 ONE-LINE DEPLOYMENT

### Docker (Recommended)
```bash
docker-compose up -d
```
✓ API on 8000 | ✓ Dashboard on 8501 | ✓ Auto-restart enabled

### Local Development
```bash
python auto_load.py
```
✓ Full pipeline demo | ✓ Real UIDAI data | ✓3 output CSVs generated

---

## 📋 DEPLOYMENT MATRIX

| Method | Command | Best For | Setup Time |
|--------|---------|----------|-----------|
| **Docker** | `docker-compose up -d` | Production | 2-3 min |
| **Local** | `python auto_load.py` | Development | 1-2 min |
| **Manual** | `deploy.bat` or `deploy.sh` | Guided setup | 3-5 min |

---

## 🔗 AFTER DEPLOYMENT ACCESS

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:8501 | Interactive UI |
| **API** | http://localhost:8000 | REST endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Health Check** | http://localhost:8000/health | System status |

---

## 📊 VERIFY DEPLOYMENT

```bash
# Check if running
docker-compose ps

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8000/health

# Stop
docker-compose down
```

---

## 📈 EXPECTED OUTPUT

**Auto-load Results:**
- 500,000 UIDAI records loaded
- 1,000,000 transformed records
- 3,036 state-district aggregations
- 49 states analyzed
- 953 districts covered
- 9 policy alerts generated

---

## 🆘 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Docker not installed | Download from docker.com |
| Port already in use | `docker-compose down` first |
| Out of memory | `docker update --memory 2g caimf-api` |
| Data not loading | Verify `data/raw/*.csv` exists |
| Services won't start | `docker-compose logs -f` to debug |

---

## 📁 KEY FILES

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Multi-service setup |
| `Dockerfile` | Container definition |
| `DEPLOYMENT.md` | Full guide (200+ lines) |
| `deploy.sh` / `deploy.bat` | Interactive scripts |
| `auto_load.py` | Quick demo |

---

## ☁️ CLOUD DEPLOYMENT GUIDE

**AWS EC2**: See DEPLOYMENT.md → AWS EC2 section
**Google Cloud Run**: See DEPLOYMENT.md → Google Cloud Run section
**Azure**: See DEPLOYMENT.md → Azure Container Instances section

---

## 🎯 TYPICAL WORKFLOW

```
1. Verify data in data/raw/
   ↓
2. Run: docker-compose up -d
   ↓
3. Wait 10-15 seconds
   ↓
4. Open http://localhost:8501
   ↓
5. Click "Load UIDAI Enrolment Dataset"
   ↓
6. Explore dashboard!
```

**Total time**: ~5 minutes from start to insights

---

## 💡 PRO TIPS

✨ Keep docker-compose.yml open for reference  
✨ Use `docker-compose logs -f` in separate terminal  
✨ Check disk space: `docker system df`  
✨ Save API responses: `curl URL > output.json`  
✨ Export alerts: Check `data/processed/policy_alerts.csv`

---

## 📞 DOCUMENTATION

- **Full Setup**: DEPLOYMENT.md
- **System Overview**: README.md
- **Real Data Integration**: DEPLOYMENT_READY.md
- **API Reference**: http://localhost:8000/docs

---

**Status**: ✅ Ready to Deploy  
**Version**: 1.0.0  
**Updated**: January 11, 2026
