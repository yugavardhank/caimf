# CAIMF Deployment Guide
## Child Aadhaar Inclusion Monitoring Framework - Production Deployment

---

## 📋 Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Monitoring & Logs](#monitoring--logs)
5. [Troubleshooting](#troubleshooting)

---

## 🖥️ Local Development

### Prerequisites
- Python 3.9+
- Virtual environment (venv)
- Git

### Quick Start

```bash
# 1. Clone project
cd uidai_prototype

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Prepare data (ensure data/raw/ contains UIDAI CSV files)
ls data/raw/

# 6. Run auto-load to test
python auto_load.py

# 7. Launch dashboard
python -m streamlit run caimf/dashboard.py
# Visit: http://localhost:8501

# 8. In another terminal, launch API
python -m uvicorn caimf.api:app --reload --host 0.0.0.0 --port 8000
# Visit: http://localhost:8000/docs
```

---

## 🐳 Docker Deployment

### Prerequisites
- Docker installed (v20.10+)
- Docker Compose (v1.29+)
- UIDAI CSV files in `data/raw/`

### Single Container (API Only)

```bash
# Build image
docker build -t caimf:latest .

# Run container
docker run -d \
  --name caimf-api \
  -p 8000:8000 \
  -v $(pwd)/data/raw:/app/data/raw:ro \
  -v $(pwd)/data/processed:/app/data/processed \
  caimf:latest

# View logs
docker logs -f caimf-api

# Stop container
docker stop caimf-api
```

### Multi-Service (API + Dashboard)

```bash
# Start both services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop services
docker-compose down
```

**Access:**
- Dashboard: http://localhost:8501
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ☁️ Production Deployment

### AWS EC2 Deployment

#### 1. Launch EC2 Instance
```bash
# Ubuntu 22.04 LTS, t3.large (2 vCPU, 8GB RAM minimum)
# Security Group: Allow 8000 (API), 8501 (Dashboard), 22 (SSH)
```

#### 2. Connect & Setup
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 3. Deploy Application
```bash
# Clone repository
git clone your-repo.git caimf
cd caimf

# Copy data files
# (Ensure data/raw/api_data_aadhar_enrolment_*.csv is present)

# Create production env file
cp .env.example .env
# Edit .env with production settings

# Start services
docker-compose up -d

# Verify
docker-compose ps
```

#### 4. Setup Reverse Proxy (Nginx)

```bash
sudo apt-get install nginx -y

# Create nginx config
sudo nano /etc/nginx/sites-available/caimf
```

```nginx
upstream caimf_api {
    server localhost:8000;
}

upstream caimf_dashboard {
    server localhost:8501;
}

server {
    listen 80;
    server_name your-domain.com;

    location /api {
        proxy_pass http://caimf_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        proxy_pass http://caimf_dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
    }
}
```

```bash
# Enable config
sudo ln -s /etc/nginx/sites-available/caimf /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### 5. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

### Google Cloud Run Deployment

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT/caimf

# Deploy
gcloud run deploy caimf \
  --image gcr.io/YOUR_PROJECT/caimf:latest \
  --platform managed \
  --region us-central1 \
  --port 8000 \
  --memory 2Gi \
  --timeout 3600
```

### Azure Container Instances

```bash
# Push to Container Registry
az acr build --registry your-registry --image caimf:latest .

# Deploy
az container create \
  --resource-group your-rg \
  --name caimf \
  --image your-registry.azurecr.io/caimf:latest \
  --cpu 2 \
  --memory 2 \
  --port 8000
```

---

## 📊 Monitoring & Logs

### Docker Logs

```bash
# View logs
docker-compose logs -f caimf-api
docker-compose logs -f caimf-dashboard

# Export logs
docker-compose logs > logs.txt
```

### Health Check

```bash
# API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "timestamp": "2026-01-11T10:30:45",
#   "data_loaded": true
# }
```

### Performance Monitoring

```bash
# Container stats
docker stats caimf-api caimf-dashboard

# Memory usage, CPU, network I/O
```

### Data Processing Validation

```bash
# Check processed outputs
ls -lh data/processed/

# Verify latest state summary
head data/processed/state_summary.csv

# Verify alerts
wc -l data/processed/policy_alerts.csv
```

---

## 🔧 Troubleshooting

### Common Issues

#### Issue: "Streamlit not found"
```bash
# Solution: Use Python module syntax
python -m streamlit run caimf/dashboard.py
```

#### Issue: Port already in use
```bash
# Find process on port
netstat -tulpn | grep :8000

# Kill process
kill -9 <PID>

# Or use different port
docker-compose -f docker-compose.yml up -d -e API_PORT=9000
```

#### Issue: Out of memory
```bash
# Check memory
free -h

# Reduce Docker memory limit
docker update --memory 2g caimf-api
```

#### Issue: Data not loading
```bash
# Verify data files exist
ls -l data/raw/*.csv

# Check permissions
chmod 644 data/raw/*.csv

# Test data loading
python auto_load.py
```

#### Issue: Dashboard won't start
```bash
# Clear Streamlit cache
rm -rf ~/.streamlit

# Restart
python -m streamlit run caimf/dashboard.py --logger.level=debug
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
python -m uvicorn caimf.api:app --reload --log-level debug
```

---

## 📈 Performance Tuning

### API Performance
```python
# In caimf/api.py, adjust workers
uvicorn caimf.api:app --workers 8 --worker-class uvicorn.workers.UvicornWorker
```

### Dashboard Performance
```bash
# Streamlit config (~/.streamlit/config.toml)
[client]
maxMessageSize = 200
dataFrameSerialization = "arrow"

[server]
enableXsrfProtection = false
enableCORS = false
```

### Data Processing
```python
# Increase chunk size for large datasets
# In caimf/data_handler.py
chunk_size = 50000  # Default: 10000
```

---

## 🔐 Security Best Practices

### Production Checklist
- [ ] Change all default credentials
- [ ] Enable API authentication (JWT)
- [ ] Use HTTPS with SSL certificate
- [ ] Configure firewall rules
- [ ] Set up log aggregation
- [ ] Enable database encryption
- [ ] Regular security audits
- [ ] Backup data regularly

### API Authentication (Optional)

```python
# In caimf/api.py, add JWT middleware
from fastapi.security import HTTPBearer
from jose import jwt

security = HTTPBearer()

@app.get("/api/v1/metrics/national", security=Depends(security))
async def get_national_metrics(credentials):
    token = credentials.credentials
    # Validate token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return metrics
```

---

## 📞 Support

- **Documentation**: See [README.md](README.md)
- **API Docs**: http://localhost:8000/docs
- **Issues**: Check logs with `docker-compose logs`
- **Email**: support@uidai.gov.in

---

**Last Updated**: January 11, 2026  
**Version**: 1.0.0
