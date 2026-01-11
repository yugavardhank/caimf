"""
CAIMF Auto-Loader for Real UIDAI Data
Automatically loads and processes UIDAI enrolment dataset
"""

import sys
from pathlib import Path
import pandas as pd

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from caimf.data_handler import DataHandler
from caimf.models import InclusionScoringModels
from caimf.anomaly_detection import AnomalyDetector

def auto_load_and_process():
    """Automatically load and process UIDAI data"""
    
    print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║     CAIMF AUTO-LOADER - Processing Real UIDAI Data                 ║
    ║     Child Aadhaar Inclusion Monitoring Framework                   ║
    ╚════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # Step 1: Load UIDAI data
        print("\n[1/6] Loading UIDAI enrolment dataset...")
        handler = DataHandler()
        uidai_data = handler.load_uidai_enrolment_data("data/raw/api_data_aadhar_enrolment_0_500000.csv")
        print(f"✓ Loaded {len(uidai_data):,} records")
        print(f"  States: {uidai_data['State'].nunique()}")
        print(f"  Districts: {uidai_data['District'].nunique()}")
        
        # Step 2: Clean data
        print("\n[2/6] Cleaning data...")
        clean_data = handler.clean_data_pipeline(uidai_data)
        print(f"✓ Cleaned to {len(clean_data):,} valid records")
        
        # Step 3: Normalize
        print("\n[3/6] Normalizing data...")
        normalized_data = handler.normalize_data(clean_data)
        print(f"✓ Applied Z-score and Min-Max normalization")
        
        # Step 4: Extract parameters
        print("\n[4/6] Extracting parameters...")
        params = handler.extract_parameters(normalized_data)
        processed_data = params['parameters']
        print(f"✓ Extracted parameters for {len(processed_data):,} records")
        
        # Step 5: Compute scores
        print("\n[5/6] Computing inclusion scores...")
        models = InclusionScoringModels()
        scored_data = models.compute_all_scores(processed_data)
        print(f"✓ Computed CEPS, IGI, LISS, FERS scores")
        
        # Step 6: Generate insights
        print("\n[6/6] Generating insights...")
        
        # National metrics
        print("\n  📊 NATIONAL METRICS:")
        print(f"     CEPS (Penetration): {scored_data['CEPS'].mean():.1f}%")
        print(f"     IGI (Gap Index):    {scored_data['IGI'].mean():.2f}")
        print(f"     LISS (Stability):   {scored_data['LISS'].mean():.2f}")
        print(f"     FERS (Risk Score):  {scored_data['FERS'].mean():.2f}")
        
        # Total enrolments
        total_child = int(scored_data['C'].sum())
        total_adult = int(scored_data['A'].sum())
        print(f"\n  👶 ENROLMENT COUNTS:")
        print(f"     Child Enrolments:   {total_child:,}")
        print(f"     Adult Enrolments:   {total_adult:,}")
        print(f"     Child Share:        {(total_child/(total_child+total_adult)*100):.1f}%")
        
        # Top risk regions
        print(f"\n  ⚠️  TOP 10 HIGHEST-RISK REGIONS:")
        top_risk = models.get_top_risk_regions(scored_data, top_n=10)
        for idx, (_, row) in enumerate(top_risk.iterrows(), 1):
            print(f"     {idx:2d}. {row['State']:20s} {row['District']:25s} FERS: {row['Avg_FERS']:.3f}")
        
        # Anomalies
        detector = AnomalyDetector()
        anomalies = detector.detect_all_anomalies(processed_data)
        print(f"\n  🔍 ANOMALIES DETECTED:")
        print(f"     Low child ratio:    {len(anomalies['low_child_ratio']):4d}")
        print(f"     Declining growth:   {len(anomalies['declining_growth']):4d}")
        print(f"     High volatility:    {len(anomalies['high_volatility']):4d}")
        print(f"     Stagnation:         {len(anomalies['stagnation']):4d}")
        print(f"     Seasonal deviation: {len(anomalies['seasonal_deviation']):4d}")
        
        # Alerts
        alerts = detector.create_policy_alerts(processed_data, scored_data)
        print(f"\n  🚨 POLICY ALERTS GENERATED: {len(alerts)}")
        
        # Alert breakdown
        critical = [a for a in alerts if a['type'] == 'CRITICAL_INCLUSION_GAP']
        risk = [a for a in alerts if a['type'] == 'HIGH_EXCLUSION_RISK']
        unstable = [a for a in alerts if a['type'] == 'UNSTABLE_ENROLMENT']
        
        print(f"     Critical Gaps:      {len(critical):4d}")
        print(f"     High Risk Regions:  {len(risk):4d}")
        print(f"     Unstable Patterns:  {len(unstable):4d}")
        
        # Export results
        print("\n  💾 EXPORTING RESULTS:")
        Path("data/processed").mkdir(parents=True, exist_ok=True)
        
        state_summary = models.get_state_summary(scored_data)
        state_summary.to_csv("data/processed/state_summary.csv", index=False)
        print(f"     ✓ data/processed/state_summary.csv ({len(state_summary)} states)")
        
        regional_summary = models.get_regional_summary(scored_data)
        regional_summary.to_csv("data/processed/regional_summary.csv", index=False)
        print(f"     ✓ data/processed/regional_summary.csv ({len(regional_summary)} regions)")
        
        alerts_df = pd.DataFrame(alerts)
        alerts_df.to_csv("data/processed/policy_alerts.csv", index=False)
        print(f"     ✓ data/processed/policy_alerts.csv ({len(alerts)} alerts)")
        
        # Final summary
        print("""
    ╔════════════════════════════════════════════════════════════════════╗
    ║ ✅ AUTO-LOAD COMPLETE!                                              ║
    ║                                                                     ║
    ║ Real UIDAI Data Processing Summary:                                ║
    """)
        print(f"    │  Records Processed:  {len(processed_data):,}")
        print(f"    │  States Covered:     {processed_data['State'].nunique()}")
        print(f"    │  Districts Covered:  {processed_data['District'].nunique()}")
        print(f"    │  Policy Alerts:      {len(alerts)}")
        print("""    │
    │ Next Steps:
    │  1. Dashboard:    streamlit run caimf/dashboard.py
    │  2. API:          python -m uvicorn caimf.api:app --reload
    │  3. View Results: Check data/processed/ folder
    ╚════════════════════════════════════════════════════════════════════╝
        """)
        
        return scored_data, processed_data, alerts
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None, None


if __name__ == "__main__":
    auto_load_and_process()
