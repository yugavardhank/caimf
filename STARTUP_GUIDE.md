# 🚀 CAIMF STARTUP GUIDE

## Welcome to the Child Aadhaar Inclusion Monitoring Framework!

This guide will get you up and running in minutes.

---

## ⚡ 5-MINUTE QUICKSTART

### Step 1: Install Dependencies (2 minutes)
```bash
# Navigate to project directory
cd uidai_prototype

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Or activate (Linux/Mac)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Run Quick Demo (2 minutes)
```bash
python quick_start.py
```

This will:
- Generate sample data
- Process through the pipeline
- Display metrics and alerts
- Confirm everything is working

### Step 3: Launch Dashboard (1 minute)
```bash
streamlit run caimf/dashboard.py
```

Then open: **http://localhost:8501**

---

## 📊 DASHBOARD QUICK TOUR

### First Time Using Dashboard?

1. **Load Sample Data**
   - Click sidebar button "Load Sample Dataset"
   - Wait for processing (takes ~10 seconds)
   - You'll see ✅ confirmation message

2. **View National Gauge**
   - See 4 main metrics: CEPS, IGI, LISS, FERS
   - Check child share percentage
   - Note the color-coded status

3. **Explore State Heatmap**
   - Red = High gap (risky)
   - Green = Low gap (healthy)
   - Hover to see exact values

4. **Check Trend Explorer**
   - Pick a state from dropdown
   - See child vs adult trends over time
   - Identify patterns

5. **Review Risk Rankings**
   - Top regions needing intervention
   - Adjust top_n slider to see more/less
   - Click to sort by different columns

6. **Read Policy Alerts**
   - Red alerts (Critical Gap) = Highest priority
   - Orange alerts (High Risk) = Secondary priority
   - Yellow alerts (Unstable) = Monitoring needed

---

## 🔧 API QUICK START

### Start API Server
```bash
python -m uvicorn caimf.api:app --reload --host 0.0.0.0 --port 8000
```

### Test API
Open browser: **http://localhost:8000/docs**

This shows interactive API documentation.

### Example: Get National Metrics
```bash
# First ingest data
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "data/raw/sample_uidai_data.csv"}'

# Then get metrics
curl http://localhost:8000/api/v1/metrics/national
```

---

## 📂 UNDERSTANDING THE STRUCTURE

```
uidai_prototype/
├── caimf/                  ← Core system modules
│   ├── data_handler.py    ← Data ingestion
│   ├── models.py          ← Scoring algorithms
│   ├── anomaly_detection.py ← Anomaly detection
│   ├── api.py             ← REST API
│   └── dashboard.py       ← Dashboard UI
│
├── data/
│   ├── raw/               ← Input CSV files go here
│   └── processed/         ← Output results go here
│
├── tests/                 ← Test suite
├── README.md              ← Full documentation
├── ARCHITECTURE.md        ← System design
├── USER_GUIDE.md          ← Workflows
└── run_pipeline.py        ← Full pipeline script
```

---

## 📋 CHECKLIST: First Time Setup

- [ ] Python 3.9+ installed
- [ ] Created virtual environment
- [ ] Installed dependencies (pip install -r requirements.txt)
- [ ] Ran quick_start.py successfully
- [ ] Launched dashboard (streamlit run ...)
- [ ] Loaded sample data
- [ ] Viewed national metrics
- [ ] Reviewed policy alerts
- [ ] Started API server
- [ ] Tested API endpoints

---

## 🎯 COMMON TASKS

### Task 1: Analyze Your Own Data
```python
# 1. Prepare CSV with these columns:
# Year, Month, State, District, Age_Group, Enrolment_Count

# 2. Place file in data/raw/ folder

# 3. Run pipeline:
python run_pipeline.py

# 4. Check results in data/processed/
```

### Task 2: Generate Daily Report
```bash
# Edit this to automate:
# 1. Data ingestion
# 2. Metric computation
# 3. Alert generation
# 4. Email results

python run_pipeline.py > report.txt
python send_email.py report.txt recipient@example.com
```

### Task 3: Integrate into Your System
```python
import requests

# 1. Call API
response = requests.get('http://localhost:8000/api/v1/metrics/national')

# 2. Get metrics
metrics = response.json()['data']
print(f"National CEPS: {metrics['ceps']}%")

# 3. Use in your app
if metrics['ceps'] < 30:
    send_alert("Critical inclusion gap detected!")
```

### Task 4: Customize Scoring Weights
```python
from caimf.models import InclusionScoringModels

models = InclusionScoringModels()

# Use custom weights
scored = models.calculate_fers(
    data,
    w1=0.50,  # Higher weight for penetration
    w2=0.30,
    w3=0.20
)
```

---

## ❓ TROUBLESHOOTING

### "No data loaded" in dashboard
**Solution**: Click "Load Sample Dataset" button in sidebar

### Dashboard is slow
**Solution**: Reduce data size or filter by state

### API returns error
**Solution**: Make sure you've called `/api/v1/ingest` first

### Can't connect to API
**Solution**: Check if running on port 8000:
```bash
netstat -an | grep 8000  # Windows
lsof -i :8000            # Linux/Mac
```

### Module import error
**Solution**: Ensure you're in project directory and virtual env is activated

---

## 📚 LEARNING PATH

### Beginner (15 minutes)
1. ✓ Run quick_start.py
2. ✓ Open dashboard
3. ✓ Explore sample data
4. ✓ Read popup help text

### Intermediate (1 hour)
1. ✓ Read README.md
2. ✓ Test API endpoints
3. ✓ Load your own data
4. ✓ Review output files

### Advanced (2 hours)
1. ✓ Study caimf modules
2. ✓ Customize thresholds
3. ✓ Read ARCHITECTURE.md
4. ✓ Integrate into system

---

## 🎓 KEY CONCEPTS

### CEPS (Child Enrolment Penetration Score)
- **What**: % of enrolments that are children
- **Range**: 0-100%
- **Good**: >60%
- **Bad**: <30%

### FERS (Future Exclusion Risk Score)
- **What**: Composite risk prediction
- **Range**: 0-1
- **Good**: <0.4
- **Bad**: >0.7

### IGI (Inclusion Gap Index)
- **What**: Ratio of child vs adult imbalance
- **Range**: -∞ to 1
- **Good**: Close to 0 (balanced)
- **Bad**: >0.5 (imbalanced)

### LISS (Long-Term Inclusion Stability)
- **What**: Consistency of enrolments over time
- **Range**: 0-1
- **Good**: >0.8 (stable)
- **Bad**: <0.4 (erratic)

---

## 🔗 IMPORTANT LINKS

- **Dashboard**: http://localhost:8501 (after running streamlit)
- **API Docs**: http://localhost:8000/docs (after starting API)
- **Main Documentation**: [README.md](README.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **User Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **File Inventory**: [FILE_INVENTORY.md](FILE_INVENTORY.md)

---

## 📞 GETTING HELP

### Check These First
1. [README.md](README.md) - Comprehensive documentation
2. [USER_GUIDE.md](USER_GUIDE.md) - Workflows and examples
3. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
4. Run: `python quick_start.py` - Live demo

### Test Your Setup
```bash
# Verify Python and dependencies
python --version  # Should be 3.9+
pip list | grep -E "pandas|fastapi|streamlit"

# Run tests
pytest tests/test_integration.py -v

# Quick validation
python quick_start.py
```

---

## ✅ SUCCESS INDICATORS

Your setup is working if:
- ✓ `python quick_start.py` completes without errors
- ✓ Dashboard loads at http://localhost:8501
- ✓ You can load sample data
- ✓ Metrics display correctly
- ✓ API responds at http://localhost:8000/health
- ✓ All 5 dashboard modules appear

---

## 🎉 YOU'RE READY!

Congratulations! The CAIMF system is now running on your machine.

**Next Steps**:
1. Explore the dashboard
2. Read the documentation
3. Prepare your own data
4. Generate insights
5. Take action on alerts

---

## 📝 System Info

- **Version**: 1.0.0
- **Status**: Production Ready ✓
- **Setup Time**: 5 minutes
- **Learning Curve**: 30 minutes
- **Full Implementation**: Complete

---

**Happy Monitoring! 👶**

For any issues, refer to [USER_GUIDE.md](USER_GUIDE.md) troubleshooting section.
