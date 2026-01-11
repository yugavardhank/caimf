"""
Anomaly Detection and Inclusion Gap Detection Module
Identifies early warning signals for exclusion risks
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies and inclusion gaps in enrolment data"""
    
    def __init__(self, volatility_threshold: float = 0.3,
                 growth_threshold: float = -0.1,
                 min_child_ratio: float = 0.2):
        """
        Initialize anomaly detector
        
        Args:
            volatility_threshold: Flag regions with volatility above this
            growth_threshold: Flag regions with growth rate below this (negative)
            min_child_ratio: Minimum acceptable child enrolment ratio
        """
        self.volatility_threshold = volatility_threshold
        self.growth_threshold = growth_threshold
        self.min_child_ratio = min_child_ratio
        self.anomalies = None
    
    def detect_high_adult_enrolment_anomaly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect: High adult enrolment + Low child enrolment
        
        This is a critical inclusion gap indicator
        """
        logger.info("Detecting high adult + low child enrolment anomalies...")
        
        df = df.copy()
        
        # Calculate child ratio
        df['Child_Ratio'] = df['C'] / (df['C'] + df['A'] + 1e-8)
        
        # Flag anomalies: low child ratio
        df['Anomaly_LowChildRatio'] = df['Child_Ratio'] < self.min_child_ratio
        
        anomalies = df[df['Anomaly_LowChildRatio']].copy()
        logger.info(f"Found {len(anomalies)} records with low child enrolment ratio")
        
        return anomalies
    
    def detect_declining_growth_anomaly(self, df: pd.DataFrame, 
                                       consecutive_periods: int = 3) -> pd.DataFrame:
        """
        Detect: Declining child growth for N consecutive periods
        
        This indicates stagnation or regression in child enrolment
        """
        logger.info(f"Detecting declining growth anomalies ({consecutive_periods}+ consecutive periods)...")
        
        df = df.sort_values(['State', 'District', 'Year', 'Month']).copy()
        
        # Ensure growth rate exists
        if 'Child_Growth_Rate' not in df.columns:
            df['Child_Growth_Rate'] = df.groupby(['State', 'District'])['C'].pct_change()
        
        # Find negative growth periods
        df['Negative_Growth'] = df['Child_Growth_Rate'] < self.growth_threshold
        
        # Count consecutive negative growth periods
        df['Consecutive_Negative'] = df.groupby(['State', 'District'])['Negative_Growth'].transform(
            lambda x: x.rolling(window=consecutive_periods, min_periods=1).sum()
        )
        
        # Flag anomalies
        df['Anomaly_DecliningGrowth'] = df['Consecutive_Negative'] >= consecutive_periods
        
        anomalies = df[df['Anomaly_DecliningGrowth']].copy()
        logger.info(f"Found {len(anomalies)} records with declining growth patterns")
        
        return anomalies
    
    def detect_volatility_anomaly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect: High volatility in child enrolments
        
        Erratic patterns indicate unstable/unreliable enrolment systems
        """
        logger.info("Detecting high volatility anomalies...")
        
        df = df.copy()
        
        # Ensure volatility exists
        if 'Enrolment_Volatility' not in df.columns:
            df['Enrolment_Volatility'] = df.groupby(['State', 'District'])['C'].transform(
                lambda x: x.rolling(window=3, min_periods=1).std()
            )
        
        # Normalize volatility to [0, 1]
        vol_max = df['Enrolment_Volatility'].max() + 1e-8
        df['Volatility_Normalized'] = df['Enrolment_Volatility'] / vol_max
        
        # Flag high volatility
        df['Anomaly_HighVolatility'] = df['Volatility_Normalized'] > self.volatility_threshold
        
        anomalies = df[df['Anomaly_HighVolatility']].copy()
        logger.info(f"Found {len(anomalies)} records with high volatility")
        
        return anomalies
    
    def detect_stagnation_anomaly(self, df: pd.DataFrame, 
                                  stagnation_months: int = 6) -> pd.DataFrame:
        """
        Detect: Zero or near-zero child enrolment growth for extended period
        
        Indicates potential policy failure or administrative issues
        """
        logger.info(f"Detecting stagnation anomalies ({stagnation_months}+ months)...")
        
        df = df.sort_values(['State', 'District', 'Year', 'Month']).copy()
        
        # Count periods with minimal growth
        df['Near_Zero_Growth'] = (df['C'] - df['C'].shift(1)).abs() < 10  # Threshold: <10 enrollments
        
        # Check for consecutive stagnation
        df['Stagnation_Period'] = df.groupby(['State', 'District'])['Near_Zero_Growth'].transform(
            lambda x: x.rolling(window=stagnation_months, min_periods=1).sum()
        )
        
        df['Anomaly_Stagnation'] = df['Stagnation_Period'] >= stagnation_months
        
        anomalies = df[df['Anomaly_Stagnation']].copy()
        logger.info(f"Found {len(anomalies)} records with stagnation patterns")
        
        return anomalies
    
    def detect_seasonal_anomaly(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect: Unusual seasonal patterns
        
        E.g., sharp spikes/drops in specific months across multiple years
        """
        logger.info("Detecting seasonal anomalies...")
        
        df = df.copy()
        
        # Calculate month-over-month seasonality
        monthly_avg = df.groupby(['State', 'District', 'Month'])['C'].transform('mean')
        df['Seasonal_Baseline'] = monthly_avg
        
        # Calculate deviation from seasonal baseline
        df['Seasonal_Deviation'] = (df['C'] - df['Seasonal_Baseline']).abs()
        
        # Normalize deviation
        dev_max = df['Seasonal_Deviation'].max() + 1e-8
        df['Seasonal_Deviation_Normalized'] = df['Seasonal_Deviation'] / dev_max
        
        # Flag large deviations (>2 std from seasonal mean)
        df['Anomaly_SeasonalDeviation'] = df['Seasonal_Deviation_Normalized'] > 0.5
        
        anomalies = df[df['Anomaly_SeasonalDeviation']].copy()
        logger.info(f"Found {len(anomalies)} records with seasonal anomalies")
        
        return anomalies
    
    def detect_all_anomalies(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Run all anomaly detection methods
        
        Returns:
            Dictionary with anomaly types as keys
        """
        logger.info("Running comprehensive anomaly detection...")
        
        anomalies = {
            'low_child_ratio': self.detect_high_adult_enrolment_anomaly(df),
            'declining_growth': self.detect_declining_growth_anomaly(df),
            'high_volatility': self.detect_volatility_anomaly(df),
            'stagnation': self.detect_stagnation_anomaly(df),
            'seasonal_deviation': self.detect_seasonal_anomaly(df)
        }
        
        self.anomalies = anomalies
        return anomalies
    
    def create_policy_alerts(self, df: pd.DataFrame, scores_df: pd.DataFrame = None) -> List[Dict]:
        """
        Generate actionable policy alerts
        
        Args:
            df: Processed data
            scores_df: DataFrame with CEPS/IGI/FERS scores
        
        Returns:
            List of alert dictionaries
        """
        logger.info("Generating policy alerts...")
        
        alerts = []
        
        if scores_df is not None:
            # Alert 1: Critical inclusion gap
            critical_regions = scores_df[scores_df['CEPS'] < 20]
            for _, row in critical_regions.iterrows():
                alerts.append({
                    'type': 'CRITICAL_INCLUSION_GAP',
                    'region': f"{row['State']}, {row['District']}",
                    'ceps': row['CEPS'],
                    'message': f"Critical child Aadhaar gap ({row['CEPS']:.1f}% penetration)",
                    'action': 'Deploy intensive child enrolment drive'
                })
            
            # Alert 2: High exclusion risk
            high_risk_regions = scores_df[scores_df['FERS'] > 0.75]
            for _, row in high_risk_regions.iterrows():
                alerts.append({
                    'type': 'HIGH_EXCLUSION_RISK',
                    'region': f"{row['State']}, {row['District']}",
                    'fers': row['FERS'],
                    'message': f"High future exclusion risk (FERS: {row['FERS']:.2f})",
                    'action': 'Initiate policy review and capacity assessment'
                })
            
            # Alert 3: Unstable enrolment
            unstable_regions = scores_df[scores_df['LISS'] < 0.4]
            for _, row in unstable_regions.iterrows():
                alerts.append({
                    'type': 'UNSTABLE_ENROLMENT',
                    'region': f"{row['State']}, {row['District']}",
                    'liss': row['LISS'],
                    'message': f"Unstable enrolment pattern (LISS: {row['LISS']:.2f})",
                    'action': 'Investigate root cause and stabilize processes'
                })
        
        logger.info(f"Generated {len(alerts)} policy alerts")
        return alerts
    
    def get_priority_intervention_regions(self, df: pd.DataFrame, 
                                         scores_df: pd.DataFrame,
                                         top_n: int = 10) -> pd.DataFrame:
        """
        Get regions that need urgent policy intervention
        
        Combines multiple anomaly indicators into priority ranking
        """
        logger.info(f"Computing top {top_n} priority intervention regions...")
        
        # Combine indicators
        intervention_score = (
            (1 - scores_df['CEPS'] / 100) * 0.3 +  # Low inclusion
            scores_df['FERS'] * 0.4 +  # High risk
            (1 - scores_df['LISS']) * 0.3  # Low stability
        )
        
        scores_df['Intervention_Priority'] = intervention_score
        
        priority_regions = scores_df.nlargest(top_n, 'Intervention_Priority')[
            ['State', 'District', 'CEPS', 'FERS', 'LISS', 'Intervention_Priority']
        ]
        
        return priority_regions
