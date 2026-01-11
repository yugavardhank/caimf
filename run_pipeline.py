"""
Complete End-to-End Example Script for CAIMF
Demonstrates all system capabilities
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Import CAIMF modules
from caimf.data_handler import DataHandler, create_sample_dataset
from caimf.models import InclusionScoringModels
from caimf.anomaly_detection import AnomalyDetector

def main():
    """Run complete CAIMF pipeline"""
    
    print("\n" + "="*70)
    print("CHILD AADHAAR INCLUSION MONITORING FRAMEWORK (CAIMF)")
    print("End-to-End Pipeline Demonstration")
    print("="*70 + "\n")
    
    # Step 1: Load Real Data
    print("STEP 1: Loading Real UIDAI Data")
    print("-" * 70)
    data_path = "data/raw/api_data_aadhar_enrolment_0_500000.csv"
    
    print(f"Loading UIDAI enrolment dataset from {data_path}...")
    handler = DataHandler()
    handler.load_uidai_enrolment_data(data_path)
    raw_df = handler.raw_data
    print(f"✓ Loaded {len(raw_df)} records from UIDAI dataset")
    print(f"  States: {raw_df['State'].nunique()}")
    print(f"  Districts: {raw_df['District'].nunique()}")
    print(f"  Date range: {raw_df['Year'].min()}-{raw_df['Month'].min()} to {raw_df['Year'].max()}-{raw_df['Month'].max()}\n")
    
    # Step 2: Data Ingestion and Cleaning
    print("STEP 2: Data Ingestion & Cleaning")
    print("-" * 70)
    handler = DataHandler()
    handler.load_csv(data_path)
    print(f"✓ Loaded {len(handler.raw_data)} records")
    
    is_valid = handler.validate_schema(handler.raw_data)
    print(f"✓ Schema validation: {'PASSED' if is_valid else 'FAILED'}")
    
    clean_data = handler.clean_data_pipeline(handler.raw_data)
    print(f"✓ Cleaned data: {len(clean_data)} valid records")
    print(f"  Removed {len(handler.raw_data) - len(clean_data)} invalid rows\n")
    
    # Step 3: Data Normalisation
    print("STEP 3: Data Normalisation")
    print("-" * 70)
    normalized_data = handler.normalize_data(clean_data)
    print(f"✓ Applied Z-score and Min-Max normalization")
    print(f"  Features added: Enrolment_ZScore, Enrolment_MinMax\n")
    
    # Step 4: Parameter Extraction
    print("STEP 4: Parameter Extraction")
    print("-" * 70)
    params = handler.extract_parameters(normalized_data)
    processed_data = params['parameters']
    print(f"✓ Extracted parameters for {len(processed_data)} records")
    print(f"  Base parameters: C (Child), A (Adult), T (Total)")
    print(f"  Derived metrics: Child_Enrolment_Share, Adult_Dominance_Ratio,")
    print(f"                   Child_Growth_Rate, Enrolment_Volatility\n")
    
    # Step 5: Mathematical Scoring
    print("STEP 5: Mathematical Scoring Models")
    print("-" * 70)
    models = InclusionScoringModels()
    
    scored_data = models.compute_all_scores(processed_data)
    print(f"✓ Computed all scoring metrics:")
    print(f"  - CEPS (Child Enrolment Penetration Score)")
    print(f"  - IGI (Inclusion Gap Index)")
    print(f"  - LISS (Long-Term Inclusion Stability Score)")
    print(f"  - FERS (Future Exclusion Risk Score)\n")
    
    # Display national metrics
    print("  NATIONAL-LEVEL METRICS:")
    print(f"  Average CEPS: {scored_data['CEPS'].mean():.2f}%")
    print(f"  Average IGI:  {scored_data['IGI'].mean():.2f}")
    print(f"  Average LISS: {scored_data['LISS'].mean():.2f}")
    print(f"  Average FERS: {scored_data['FERS'].mean():.2f}\n")
    
    # Step 6: Regional Analysis
    print("STEP 6: Regional Analysis")
    print("-" * 70)
    state_summary = models.get_state_summary(scored_data)
    print(f"✓ State-level summary computed\n")
    print("  TOP 5 STATES BY CHILD ENROLMENT SHARE:")
    top_states = state_summary.nlargest(5, 'Child_Share')
    for idx, row in top_states.iterrows():
        print(f"    {row['State']:20s} - {row['Child_Share']:5.1f}% child share, FERS: {row['Avg_FERS']:.2f}")
    print()
    
    # Step 7: Risk Ranking
    print("STEP 7: Risk Ranking (Exclusion Risk)")
    print("-" * 70)
    risk_regions = models.get_top_risk_regions(scored_data, top_n=10)
    print(f"✓ Top 10 highest-risk regions:\n")
    for idx, (_, row) in enumerate(risk_regions.iterrows(), 1):
        print(f"    {idx:2d}. {row['State']:20s} {row['District']:25s} FERS: {row['Avg_FERS']:.3f}")
    print()
    
    # Step 8: Anomaly Detection
    print("STEP 8: Anomaly Detection")
    print("-" * 70)
    detector = AnomalyDetector()
    anomalies = detector.detect_all_anomalies(processed_data)
    print(f"✓ Anomaly detection complete:\n")
    for anomaly_type, anom_data in anomalies.items():
        print(f"    {anomaly_type.replace('_', ' ').title():30s}: {len(anom_data):4d} records")
    print()
    
    # Step 9: Policy Alerts
    print("STEP 9: Policy Alert Generation")
    print("-" * 70)
    alerts = detector.create_policy_alerts(processed_data, scored_data)
    print(f"✓ Generated {len(alerts)} policy intervention alerts\n")
    
    # Categorize alerts
    critical_alerts = [a for a in alerts if a['type'] == 'CRITICAL_INCLUSION_GAP']
    risk_alerts = [a for a in alerts if a['type'] == 'HIGH_EXCLUSION_RISK']
    unstable_alerts = [a for a in alerts if a['type'] == 'UNSTABLE_ENROLMENT']
    
    print(f"  ALERT DISTRIBUTION:")
    print(f"    Critical Gaps:      {len(critical_alerts):3d}")
    print(f"    High Risk Regions:  {len(risk_alerts):3d}")
    print(f"    Unstable Patterns:  {len(unstable_alerts):3d}\n")
    
    print("  SAMPLE ALERTS:")
    for alert in alerts[:3]:
        print(f"    [{alert['type']}]")
        print(f"      Region:  {alert['region']}")
        print(f"      Message: {alert['message']}")
        print(f"      Action:  {alert['action']}\n")
    
    # Step 10: Insights
    print("STEP 10: Key Insights & Recommendations")
    print("-" * 70)
    
    low_inclusion = scored_data[scored_data['CEPS'] < 30]
    high_risk = scored_data[scored_data['FERS'] > 0.7]
    unstable = scored_data[scored_data['LISS'] < 0.4]
    
    print(f"✓ CRITICAL FINDINGS:\n")
    print(f"  • Regions with CRITICAL child inclusion gap (<30%): {len(low_inclusion)}")
    print(f"  • Regions with HIGH exclusion risk (FERS>0.7):     {len(high_risk)}")
    print(f"  • Regions with UNSTABLE enrolment (LISS<0.4):      {len(unstable)}\n")
    
    print(f"  RECOMMENDATIONS:")
    print(f"  ✓ Deploy intensive child enrolment drives in {len(low_inclusion)} critical regions")
    print(f"  ✓ Stabilize administrative processes in {len(unstable)} unstable regions")
    print(f"  ✓ Conduct capacity assessment in {len(high_risk)} high-risk regions")
    print(f"  ✓ Monitor growth trends for early intervention\n")
    
    # Export Results
    print("STEP 11: Export Results")
    print("-" * 70)
    
    # Save state summary
    state_summary.to_csv("data/processed/state_summary.csv", index=False)
    print(f"✓ Saved state summary to data/processed/state_summary.csv")
    
    # Save regional summary
    regional_summary = models.get_regional_summary(scored_data)
    regional_summary.to_csv("data/processed/regional_summary.csv", index=False)
    print(f"✓ Saved regional summary to data/processed/regional_summary.csv")
    
    # Save alerts
    alerts_df = pd.DataFrame(alerts)
    alerts_df.to_csv("data/processed/policy_alerts.csv", index=False)
    print(f"✓ Saved policy alerts to data/processed/policy_alerts.csv\n")
    
    # Final Summary
    print("="*70)
    print("PIPELINE EXECUTION COMPLETE")
    print("="*70)
    print(f"\nProcessed {len(processed_data)} enrolment records")
    print(f"Covered {processed_data['State'].nunique()} states and {processed_data['District'].nunique()} districts")
    print(f"Generated {len(alerts)} actionable policy alerts")
    print(f"\nAll outputs saved to 'data/processed/' directory")
    print("\nNext Steps:")
    print("  1. Review policy alerts for immediate intervention")
    print("  2. Analyze regional summaries for pattern identification")
    print("  3. Launch targeted enrolment drives in critical regions")
    print("  4. Monitor LISS scores for administrative stability")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
