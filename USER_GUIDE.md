# CAIMF System - User Guide & Workflows

## 1. Dashboard User Workflows

### Workflow 1: Daily Monitoring (5 minutes)
**Goal**: Check national metrics and any new alerts

1. Open Dashboard (http://localhost:8501)
2. View National Gauge (4 main metrics)
3. Review Policy Alert Panel
4. Note any P0 (Critical) alerts
5. Export daily summary if needed

### Workflow 2: Regional Deep Dive (15 minutes)
**Goal**: Analyze specific state/district performance

1. Navigate to State-wise Heatmap
2. Select state in Trend Explorer
3. View historical trends
4. Check Risk Ranking for this state
5. Identify intervention targets

### Workflow 3: Policy Planning (30 minutes)
**Goal**: Plan intervention strategies

1. Review Top Risk Regions (FERS ranking)
2. Examine Low Inclusion Regions (CEPS ranking)
3. Analyze Anomaly Detection results
4. Generate comprehensive alerts report
5. Create action plan for identified regions

---

## 2. API User Workflows

### Workflow A: System Integration
**Goal**: Integrate CAIMF into other UIDAI systems

```python
import requests

# 1. Ingest data
response = requests.post(
    'http://localhost:8000/api/v1/ingest',
    json={'file_path': 'path/to/data.csv'}
)
assert response.status_code == 200

# 2. Get national metrics
response = requests.get('http://localhost:8000/api/v1/metrics/national')
data = response.json()['data']
print(f"National CEPS: {data['ceps']}%")

# 3. Get alerts
response = requests.get('http://localhost:8000/api/v1/alerts')
alerts = response.json()['data']
for alert in alerts:
    send_notification(alert)  # Your system
```

### Workflow B: Automated Reporting
**Goal**: Generate daily/weekly reports automatically

```bash
#!/bin/bash
# Daily Report Generation

# 1. Ingest latest data
curl -X POST http://localhost:8000/api/v1/ingest \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/data/latest.csv"}'

# 2. Get metrics
curl http://localhost:8000/api/v1/metrics/national > national_metrics.json

# 3. Get alerts
curl http://localhost:8000/api/v1/alerts > alerts.json

# 4. Generate report
python generate_report.py national_metrics.json alerts.json

# 5. Send email
python send_email.py report.pdf
```

---

## 3. Data Preparation Guide

### Input Data Format

**Required CSV Structure:**
```csv
Year,Month,State,District,Age_Group,Enrolment_Count
2025,01,Maharashtra,Mumbai,Child,1500
2025,01,Maharashtra,Mumbai,Adult,4200
2025,02,Maharashtra,Mumbai,Child,1550
2025,02,Maharashtra,Mumbai,Adult,4250
...
```

### Data Quality Checklist
- [ ] All 6 columns present
- [ ] No null values in mandatory columns
- [ ] Year between 2010-2026
- [ ] Month between 1-12
- [ ] Age_Group is "Child" or "Adult" (case-insensitive)
- [ ] Enrolment_Count ≥ 0
- [ ] States match Indian standard names
- [ ] No duplicate records for same Year/Month/State/District/Age_Group

### Data Cleaning Script
```python
import pandas as pd

df = pd.read_csv('raw_data.csv')

# Remove duplicates
df = df.drop_duplicates(
    subset=['Year', 'Month', 'State', 'District', 'Age_Group'],
    keep='first'
)

# Remove nulls
df = df.dropna(subset=['Year', 'Month', 'State', 'District', 'Age_Group', 'Enrolment_Count'])

# Standardize Age_Group
df['Age_Group'] = df['Age_Group'].str.title()
df['Age_Group'] = df['Age_Group'].map({'Child': 'Child', 'Adult': 'Adult'})

# Ensure numeric
df['Enrolment_Count'] = pd.to_numeric(df['Enrolment_Count'], errors='coerce')
df = df[df['Enrolment_Count'] >= 0]

# Save cleaned data
df.to_csv('cleaned_data.csv', index=False)
```

---

## 4. Configuration & Customization

### Changing Anomaly Detection Thresholds

Edit `caimf/anomaly_detection.py`:
```python
detector = AnomalyDetector(
    volatility_threshold=0.35,      # Default: 0.3
    growth_threshold=-0.15,         # Default: -0.1
    min_child_ratio=0.25            # Default: 0.2
)
```

### Changing FERS Weights

Edit `caimf/models.py`:
```python
# Default: w1=0.4, w2=0.35, w3=0.25
# Custom weights favoring penetration:
scores_df = models.calculate_fers(
    processed_data,
    w1=0.50,  # Increase penetration weight
    w2=0.30,  # Decrease gap weight
    w3=0.20   # Decrease volatility weight
)
```

---

## 5. Troubleshooting Guide

### Issue: "No data loaded"
**Solution**: Use `/api/v1/ingest` endpoint first or load data in dashboard

### Issue: "CEPS values are NaN"
**Solution**: Check that C and A columns exist in processed_data

### Issue: Dashboard is slow
**Solution**: Reduce data size or use filtering options (top_n parameter)

### Issue: Metrics suddenly change
**Solution**: Check if new data was ingested with different ranges

---

## 6. Performance Optimization

### For Large Datasets (>100K records)
```python
# Use batch processing
chunk_size = 10000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    processed = handler.clean_data_pipeline(chunk)
    scored = models.compute_all_scores(processed)
    # Process chunk
```

### For Real-time Updates
- Cache metrics using Redis
- Pre-compute common aggregations
- Use materialized views for dashboards

---

## 7. Export & Reporting

### Export Regional Summary
```python
regional_summary = models.get_regional_summary(scored_data)
regional_summary.to_csv('regional_analysis.csv', index=False)
regional_summary.to_excel('regional_analysis.xlsx', index=False)
```

### Export Alerts
```python
alerts_df = pd.DataFrame(alerts)
alerts_df.to_csv('policy_alerts.csv', index=False)

# Create pivot for state comparison
pivot = alerts_df.pivot_table(
    index='region',
    columns='type',
    aggfunc='size',
    fill_value=0
)
```

---

## 8. Scheduled Tasks

### Setup Cron Job for Daily Processing
```bash
0 6 * * * /usr/bin/python3 /path/to/run_pipeline.py >> /var/log/caimf_daily.log
```

### Setup API for Monthly Data Refresh
```python
# caimf/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('cron', hour=6, day=1)
def monthly_refresh():
    data_handler.load_csv('latest_data.csv')
    clean_data = data_handler.clean_data_pipeline(raw_data)
    # ...save to cache

scheduler.start()
```

---

## 9. Best Practices

### Do's ✓
- ✓ Validate input data before ingestion
- ✓ Monitor LISS for system stability
- ✓ Track FERS trends for early warnings
- ✓ Review alerts within 24 hours
- ✓ Update data monthly or more frequently
- ✓ Keep backup of raw data

### Don'ts ✗
- ✗ Don't use data older than 3 years
- ✗ Don't ignore critical alerts (CEPS < 20%)
- ✗ Don't change scoring weights without documentation
- ✗ Don't process duplicate records
- ✗ Don't trust single metric - use all 4 together

---

## 10. Integration Checklist

- [ ] Environment setup (Python 3.9+, dependencies installed)
- [ ] Data source configured and tested
- [ ] API running on port 8000
- [ ] Dashboard running on port 8501
- [ ] Sample data ingested successfully
- [ ] All 4 metrics computing correctly
- [ ] Alerts generating and actionable
- [ ] Export functionality working
- [ ] Monitoring/logging configured
- [ ] Backup strategy in place
