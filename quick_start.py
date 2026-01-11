"""
Quick Start Guide for CAIMF
Get up and running in 5 minutes
"""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from caimf.data_handler import DataHandler, create_sample_dataset
from caimf.models import InclusionScoringModels
from caimf.anomaly_detection import AnomalyDetector

def quick_demo():
    """Run a quick 5-minute demo of CAIMF"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║     CAIMF QUICK START DEMO (5 Minutes)                             ║
    ║     Child Aadhaar Inclusion Monitoring Framework                   ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Load real data
    print("\n[1/5] Loading real UIDAI enrolment data...")
    handler = DataHandler()
    handler.load_uidai_enrolment_data("data/raw/api_data_aadhar_enrolment_0_500000.csv")
    print(f"✓ Loaded {len(handler.raw_data)} records from UIDAI dataset")
    
    # Step 2: Clean and normalize
    print("\n[2/5] Loading and cleaning data...")
    clean = handler.clean_data_pipeline(handler.raw_data)
    print(f"✓ Cleaned {len(clean)} records")
    
    # Step 3: Extract parameters
    print("\n[3/5] Extracting parameters...")
    normalized = handler.normalize_data(clean)
    params = handler.extract_parameters(normalized)
    processed = params['parameters']
    print(f"✓ Extracted parameters for {len(processed)} records")
    
    # Step 4: Compute scores
    print("\n[4/5] Computing inclusion scores...")
    models = InclusionScoringModels()
    scored = models.compute_all_scores(processed)
    print(f"✓ Scores computed: CEPS, IGI, LISS, FERS")
    
    # Step 5: Generate insights
    print("\n[5/5] Generating insights...")
    
    # National metrics
    print("\n  📊 NATIONAL METRICS:")
    print(f"     Child Inclusion (CEPS): {scored['CEPS'].mean():.1f}%")
    print(f"     Inclusion Gap (IGI):     {scored['IGI'].mean():.2f}")
    print(f"     Stability (LISS):        {scored['LISS'].mean():.2f}")
    print(f"     Risk Score (FERS):       {scored['FERS'].mean():.2f}")
    
    # Top risk regions
    print("\n  ⚠️  TOP 5 HIGHEST-RISK REGIONS:")
    top_risk = models.get_top_risk_regions(scored, top_n=5)
    for idx, (_, row) in enumerate(top_risk.iterrows(), 1):
        print(f"     {idx}. {row['State']:20s} {row['District']:25s} Risk: {row['Avg_FERS']:.3f}")
    
    # Anomalies
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(processed)
    print("\n  🔍 ANOMALIES DETECTED:")
    print(f"     Low child ratio:        {len(anomalies['low_child_ratio']):3d}")
    print(f"     Declining growth:       {len(anomalies['declining_growth']):3d}")
    print(f"     High volatility:        {len(anomalies['high_volatility']):3d}")
    
    # Alerts
    alerts = detector.create_policy_alerts(processed, scored)
    print(f"\n  🚨 POLICY ALERTS GENERATED: {len(alerts)}")
    if alerts:
        print(f"     Sample: {alerts[0]['region']}")
        print(f"     Action: {alerts[0]['action']}")
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║ ✓ DEMO COMPLETE!                                                   ║
    ║                                                                     ║
    ║ Next Steps:                                                        ║
    ║  1. Dashboard:  streamlit run caimf/dashboard.py                   ║
    ║  2. API:        python -m uvicorn caimf.api:app --reload           ║
    ║  3. Full Run:   python run_pipeline.py                             ║
    ║  4. Tests:      pytest tests/                                      ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    quick_demo()
