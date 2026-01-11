# Child Aadhaar Inclusion Monitoring Framework (CAIMF)
## A Live, Data-Driven Decision Support System

![CAIMF Architecture](docs/architecture.png)

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Mathematical Models](#mathematical-models)
6. [API Documentation](#api-documentation)
7. [Dashboard Features](#dashboard-features)
8. [Data Requirements](#data-requirements)
9. [Configuration](#configuration)
10. [Deployment](#deployment)

---

## 🎯 System Overview

### Purpose
CAIMF continuously measures, scores, and visualizes child Aadhaar enrolment inclusion across regions using UIDAI datasets, enabling early detection of future service exclusion risks.

### Key Features
- **Real-time Monitoring**: Live enrolment metrics and trend analysis
- **Predictive Scoring**: FERS (Future Exclusion Risk Score) for early warning
- **Multi-level Analysis**: National, state, and district granularity
- **Anomaly Detection**: Identifies erratic patterns and policy gaps
- **Policy Alerts**: Actionable intervention recommendations

### Target Users
- UIDAI Management
- State and District Policy Makers
- Regional Enrolment Coordinators
- Data Analysts and Researchers

---

## 🏗️ Architecture

### End-to-End Pipeline

```
UIDAI Datasets (CSV)
        ↓
Data Ingestion Layer (CSV batch/streaming)
        ↓
Cleaning & Normalisation (schema validation, standardisation)
        ↓
Parameter Extraction (C, A, T, derived metrics)
        ↓
Mathematical Scoring Models (CEPS, IGI, LISS, FERS)
        ↓
Anomaly & Gap Detection (threshold-based, statistical)
        ↓
Live Dashboard & API (REST endpoints, interactive visualizations)
        ↓
Policy Outputs (alerts, rankings, recommendations)
```

### Technology Stack
- **Data Processing**: Python 3.9+, Pandas, NumPy
- **API**: FastAPI, Uvicorn
- **Dashboard**: Streamlit
- **Visualization**: Plotly
- **Database**: CSV (easily extendable to SQL)

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- 2GB RAM minimum

### Setup Steps

```bash
# 1. Clone or download the project
cd uidai_prototype

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify installation
python -c "import caimf; print('CAIMF installed successfully')"
```

---

## 🚀 Usage

### Quick Start: Dashboard

```bash
# Launch dashboard with real UIDAI data
python -m streamlit run caimf/dashboard.py
```

Then:
1. Open browser to `http://localhost:8501`
2. Click "Load UIDAI Enrolment Dataset" in sidebar
3. Explore the 5 dashboard modules with 500K+ real records

### Quick Start: API

```bash
# Start API server with real data support
python -m uvicorn caimf.api:app --reload --host 0.0.0.0 --port 8000
```

Then:
1. API available at `http://localhost:8000`
2. Interactive docs at `http://localhost:8000/docs`
3. All endpoints automatically use UIDAI data from data/raw/

### Sample Usage: Python Script

```python
from caimf.data_handler import DataHandler
from caimf.models import InclusionScoringModels
from caimf.anomaly_detection import AnomalyDetector

# 1. Load and process real UIDAI data
handler = DataHandler()
uidai_data = handler.load_uidai_enrolment_data('data/raw/api_data_aadhar_enrolment_0_500000.csv')
clean_data = handler.clean_data_pipeline(uidai_data)
normalized = handler.normalize_data(clean_data)
params = handler.extract_parameters(normalized)
processed = params['parameters']

# 2. Compute scores
models = InclusionScoringModels()
scored_data = models.compute_all_scores(processed)

# 3. Get insights
state_summary = models.get_state_summary(scored_data)
risk_ranking = models.get_top_risk_regions(scored_data, top_n=15)

# 4. Detect anomalies
detector = AnomalyDetector()
anomalies = detector.detect_all_anomalies(processed)
alerts = detector.create_policy_alerts(processed, scored_data)

print(f'States analyzed: {len(state_summary)}')
print(f'Critical alerts: {len([a for a in alerts if a["type"] == "CRITICAL_INCLUSION_GAP"])}')
print(state_summary)
print(alerts)
```

---

## 🧮 Mathematical Models

### 1. Child Enrolment Penetration Score (CEPS)

**Formula:**
$$CEPS_r = \frac{C_r}{C_r + A_r} \times 100$$

**Interpretation:**
- **0-30%**: Critical inclusion gap
- **30-60%**: Moderate inclusion
- **60%+**: Healthy inclusion

**Use Case**: Primary metric for inclusion assessment

---

### 2. Inclusion Gap Index (IGI)

**Formula:**
$$IGI_r = 1 - \frac{C_r}{A_r}$$

**Interpretation:**
- Measures structural imbalance
- Higher IGI = Higher exclusion risk
- Negative values indicate child dominance

**Use Case**: Structural assessment of regional patterns

---

### 3. Long-Term Inclusion Stability Score (LISS)

**Formula:**
$$LISS_r = 1 - \frac{Var(CEPS_r(t))}{Var_{max}}$$

**Interpretation:**
- **0.8-1.0**: Highly stable
- **0.6-0.8**: Stable
- **0.4-0.6**: Unstable
- **<0.4**: Highly unstable

**Use Case**: Identifies erratic regions needing administrative support

---

### 4. Future Exclusion Risk Score (FERS)

**Formula:**
$$FERS = w_1(1 - \frac{CEPS}{100}) + w_2(IGI) + w_3(Volatility)$$

**Default Weights:**
- $w_1 = 0.40$ (Penetration)
- $w_2 = 0.35$ (Gap Index)
- $w_3 = 0.25$ (Volatility)

**Interpretation:**
- **0.0-0.4**: Low Risk
- **0.4-0.6**: Medium Risk
- **0.6-0.8**: High Risk
- **0.8-1.0**: Critical Risk

**Use Case**: Predictive indicator for resource allocation

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
None (use in secured network)

### Endpoints

#### Health Check
```
GET /health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-11T10:30:45",
  "data_loaded": true
}
```

#### Data Ingestion
```
POST /api/v1/ingest
```
Request:
```json
{
  "file_path": "path/to/data.csv"
}
```
Response:
```json
{
  "status": "success",
  "records_processed": 5000,
  "summary": {
    "total_enrolments": 2500000,
    "child_enrolments": 625000,
    "child_share_percentage": 25.0
  }
}
```

#### National Metrics
```
GET /api/v1/metrics/national
```
Response:
```json
{
  "status": "success",
  "data": {
    "ceps": 35.5,
    "igi": 1.82,
    "liss": 0.72,
    "fers": 0.45,
    "child_share_percentage": 35.5
  }
}
```

#### State Metrics
```
GET /api/v1/metrics/state?state=Maharashtra
```

#### Regional Metrics
```
GET /api/v1/metrics/region?state=Maharashtra&top_n=50
```

#### Risk Ranking
```
GET /api/v1/risk-ranking?top_n=15
```

#### Policy Alerts
```
GET /api/v1/alerts
```
Response:
```json
{
  "status": "success",
  "count": 25,
  "data": [
    {
      "type": "CRITICAL_INCLUSION_GAP",
      "region": "Uttar Pradesh, Lucknow",
      "message": "Critical child Aadhaar gap (18.5% penetration)",
      "action": "Deploy intensive child enrolment drive"
    }
  ]
}
```

#### Anomaly Detection
```
GET /api/v1/anomalies
```

---

## 📊 Dashboard Features

### Module 1: National Child Inclusion Gauge
- **CEPS**: Real-time penetration percentage
- **IGI**: Current gap index
- **LISS**: Stability assessment
- **FERS**: Exclusion risk prediction
- **Enrolment Counts**: Child and adult totals

### Module 2: State-wise Heatmap
- Color-coded by IGI (red = high gap)
- Interactive state selection
- Comparison across regions

### Module 3: Trend Explorer
- Time-series visualization
- Child vs Adult enrolment lines
- Monthly/quarterly granularity
- State-specific deep dives

### Module 4: Risk Ranking Table
- Top N regions by FERS
- Sortable columns
- Filtering by state/district
- Export capabilities

### Module 5: Policy Alert Panel
- Real-time alert generation
- Priority levels (P0, P1, P2)
- Actionable recommendations
- Intervention tracker

---

## 📥 Data Requirements

### UIDAI Data Integration
The system automatically loads UIDAI CSV files from `data/raw/` with format:
```csv
date,state,district,pincode,age_0_5,age_5_17,age_18_greater
11-01-2025,Maharashtra,Mumbai,400001,250,180,1200
11-01-2025,Maharashtra,Pune,411001,220,160,1050
...
```

### Transformed Format (Internal)
```csv
Year,Month,State,District,Age_Group,Enrolment_Count
2025,01,Maharashtra,Mumbai,Child,430
2025,01,Maharashtra,Mumbai,Adult,1200
2025,01,Maharashtra,Pune,Child,380
2025,01,Maharashtra,Pune,Adult,1050
...
```

### UIDAI Source Columns (Auto-Converted)
1. **date** (STR): DD-MM-YYYY format
2. **state** (STR): State name
3. **district** (STR): District name
4. **pincode** (STR): PIN code
5. **age_0_5** (INT): Children aged 0-5
6. **age_5_17** (INT): Children aged 5-17 (combined = Child enrolments)
7. **age_18_greater** (INT): Adults 18+ (= Adult enrolments)

### Data Transformation Rules
- **Child Enrolments**: age_0_5 + age_5_17
- **Adult Enrolments**: age_18_greater
- **Temporal**: Date parsed to Year/Month
- **Geographic**: State/District standardized

### Data Quality Standards
- ✅ Auto-detects UIDAI format
- ✅ Handles missing values
- ✅ Validates numeric fields
- ✅ Standardizes state/district names

---

## ⚙️ Configuration

### Default Parameters

**Data Handler** (`caimf/data_handler.py`)
```python
REQUIRED_COLUMNS = [
    'Year', 'Month', 'State', 'District', 
    'Age_Group', 'Enrolment_Count'
]
```

**Anomaly Detector** (`caimf/anomaly_detection.py`)
```python
volatility_threshold = 0.3      # 30% volatility
growth_threshold = -0.1         # -10% growth
min_child_ratio = 0.2           # Min 20% child ratio
```

**FERS Weights** (`caimf/models.py`)
```python
w1 = 0.40  # CEPS (penetration)
w2 = 0.35  # IGI (gap)
w3 = 0.25  # Volatility
```

### Customization
Edit parameter values in respective module files before running.

---

## 🚢 Deployment

### Local Development
```bash
# Dashboard
python -m streamlit run caimf/dashboard.py

# API (separate terminal)
python -m uvicorn caimf.api:app --reload
```

### Docker Deployment

**Single Service (API):**
```bash
docker build -t caimf .
docker run -d -p 8000:8000 -v $(pwd)/data/raw:/app/data/raw:ro caimf
```

**Multi-Service (API + Dashboard):**
```bash
docker-compose up -d
# Dashboard: http://localhost:8501
# API: http://localhost:8000/docs
```

### Cloud Deployment
- **AWS EC2**: See [DEPLOYMENT.md](DEPLOYMENT.md) - Nginx reverse proxy with SSL
- **Google Cloud Run**: Docker image deployment with auto-scaling
- **Azure Container Instances**: Containerized deployment
- **AWS Lambda**: Serverless endpoints

### Production Checklist
- ✅ HTTPS with SSL certificate
- ✅ API authentication (JWT)
- ✅ Database migration (PostgreSQL)
- ✅ Redis caching
- ✅ Monitoring & alerts
- ✅ Log aggregation
- ✅ Regular backups

**Full deployment guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📈 Metrics Summary

| Metric | Range | Better If | Use Case |
|--------|-------|-----------|----------|
| CEPS   | 0-100 | Higher    | Inclusion assessment |
| IGI    | -∞ to 1 | Lower     | Gap detection |
| LISS   | 0-1   | Higher    | Stability check |
| FERS   | 0-1   | Lower     | Risk prediction |

---

## 🔍 Anomaly Types

1. **Low Child Ratio**: Child enrolments <20% of total
2. **Declining Growth**: Negative growth for 3+ consecutive periods
3. **High Volatility**: Erratic enrolment patterns
4. **Stagnation**: Near-zero growth for 6+ months
5. **Seasonal Deviation**: Unusual monthly patterns

---

## 📞 Support & Documentation

- **API Docs**: `http://localhost:8000/docs`
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Real Data**: `data/raw/api_data_aadhar_enrolment_0_500000.csv`
- **Auto-Load Demo**: `python auto_load.py`
- **Example Scripts**: `tests/example_*.py`

---

## 📄 License & Compliance

- **Privacy**: Only aggregated data (no individual records)
- **Compliance**: UIDAI data handling guidelines
- **Open Source**: MIT License

---

## 🤝 Contributing

For improvements:
1. Test locally with sample data
2. Follow PEP 8 style guide
3. Add docstrings to new functions
4. Update README for new features

---

**Last Updated**: January 11, 2026  
**Version**: 1.0.0  
**Author**: UIDAI Data Hackathon Team
