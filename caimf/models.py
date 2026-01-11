"""
Mathematical Scoring Models for CAIMF
Implements CEPS, IGI, LISS, and FERS scoring systems
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InclusionScoringModels:
    """Implements all CAIMF mathematical models"""
    
    def __init__(self):
        """Initialize scoring models"""
        self.ceps_scores = None
        self.igi_scores = None
        self.liss_scores = None
        self.fers_scores = None
    
    def calculate_ceps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Child Enrolment Penetration Score (CEPS)
        
        Formula: CEPS_r = (C_r / (C_r + A_r)) * 100
        
        Range: 0-100
        - 0-30: Critical inclusion gap
        - 30-60: Moderate inclusion
        - 60+: Healthy inclusion
        
        Args:
            df: DataFrame with columns [C, A, State, District]
        
        Returns:
            DataFrame with CEPS scores
        """
        logger.info("Computing Child Enrolment Penetration Score (CEPS)...")
        
        df = df.copy()
        
        # Ensure C and A columns exist
        if 'C' not in df.columns or 'A' not in df.columns:
            raise ValueError("DataFrame must contain 'C' (Child) and 'A' (Adult) columns")
        
        # Calculate CEPS
        df['CEPS'] = (df['C'] / (df['C'] + df['A'] + 1e-8)) * 100
        
        # Classify inclusion level
        def classify_inclusion(ceps_val):
            if ceps_val < 30:
                return 'Critical'
            elif ceps_val < 60:
                return 'Moderate'
            else:
                return 'Healthy'
        
        df['Inclusion_Level'] = df['CEPS'].apply(classify_inclusion)
        
        self.ceps_scores = df
        logger.info(f"CEPS computed for {len(df)} records")
        return df
    
    def calculate_igi(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Inclusion Gap Index (IGI)
        
        Formula: IGI_r = 1 - (C_r / A_r)
        
        Measures structural imbalance in enrolments
        Higher IGI ⇒ higher future exclusion risk
        
        Args:
            df: DataFrame with columns [C, A, State, District]
        
        Returns:
            DataFrame with IGI scores
        """
        logger.info("Computing Inclusion Gap Index (IGI)...")
        
        df = df.copy()
        
        # Handle division by zero
        df['IGI'] = 1 - (df['C'] / (df['A'] + 1e-8))
        
        # Clip to valid range
        df['IGI'] = df['IGI'].clip(-10, 1)
        
        # Classify risk level
        def classify_gap_risk(igi_val):
            if igi_val > 0.7:
                return 'Critical_Gap'
            elif igi_val > 0.4:
                return 'High_Gap'
            elif igi_val > 0.1:
                return 'Moderate_Gap'
            else:
                return 'Low_Gap'
        
        df['Gap_Risk_Level'] = df['IGI'].apply(classify_gap_risk)
        
        logger.info(f"IGI computed for {len(df)} records")
        return df
    
    def calculate_liss(self, df: pd.DataFrame, groupby_cols=['State', 'District']) -> pd.DataFrame:
        """
        Long-Term Inclusion Stability Score (LISS)
        
        Formula: LISS_r = 1 - Variance(CEPS_r(t))
        
        Tracks consistency over time
        Low stability = erratic enrolment = policy concern
        
        Args:
            df: DataFrame with CEPS already calculated
            groupby_cols: Columns to group by (State, District)
        
        Returns:
            DataFrame with LISS scores
        """
        logger.info("Computing Long-Term Inclusion Stability Score (LISS)...")
        
        if 'CEPS' not in df.columns:
            logger.warning("CEPS not found, calculating it first...")
            df = self.calculate_ceps(df)
        
        df = df.copy()
        
        # Calculate variance of CEPS over time for each region
        variance_series = df.groupby(groupby_cols)['CEPS'].transform('var')
        
        # Handle NaN values (regions with < 2 time periods)
        variance_series = variance_series.fillna(0)
        
        # Calculate LISS: 1 - normalized variance
        max_variance = variance_series.max() + 1e-8
        df['LISS'] = 1 - (variance_series / max_variance)
        
        # Clip to [0, 1]
        df['LISS'] = df['LISS'].clip(0, 1)
        
        # Classify stability
        def classify_stability(liss_val):
            if liss_val > 0.8:
                return 'Highly_Stable'
            elif liss_val > 0.6:
                return 'Stable'
            elif liss_val > 0.4:
                return 'Unstable'
            else:
                return 'Highly_Unstable'
        
        df['Stability_Level'] = df['LISS'].apply(classify_stability)
        
        logger.info(f"LISS computed for {len(df)} records")
        return df
    
    def calculate_fers(self, df: pd.DataFrame, 
                      w1: float = 0.4, w2: float = 0.35, w3: float = 0.25) -> pd.DataFrame:
        """
        Future Exclusion Risk Score (FERS)
        
        Formula: FERS = w1(1 - CEPS) + w2(IGI) + w3(Volatility)
        
        Composite predictive indicator for exclusion risk
        
        Args:
            df: DataFrame with base metrics
            w1, w2, w3: Weights (must sum to 1.0)
        
        Returns:
            DataFrame with FERS scores
        """
        logger.info(f"Computing Future Exclusion Risk Score (FERS) with weights w1={w1}, w2={w2}, w3={w3}...")
        
        # Verify weights
        if abs(w1 + w2 + w3 - 1.0) > 0.01:
            logger.warning(f"Weights don't sum to 1: {w1 + w2 + w3}, normalizing...")
            total = w1 + w2 + w3
            w1, w2, w3 = w1/total, w2/total, w3/total
        
        df = df.copy()
        
        # Ensure all required scores exist
        if 'CEPS' not in df.columns:
            df = self.calculate_ceps(df)
        if 'IGI' not in df.columns:
            df = self.calculate_igi(df)
        if 'Enrolment_Volatility' not in df.columns:
            df['Enrolment_Volatility'] = 0
        
        # Normalize components to [0, 1] range
        ceps_normalized = df['CEPS'] / 100  # CEPS is already 0-100
        
        # IGI normalization
        igi_min, igi_max = df['IGI'].min(), df['IGI'].max()
        igi_normalized = (df['IGI'] - igi_min) / (igi_max - igi_min + 1e-8)
        
        # Volatility normalization
        vol_max = df['Enrolment_Volatility'].max() + 1e-8
        volatility_normalized = df['Enrolment_Volatility'] / vol_max
        
        # Calculate FERS
        df['FERS'] = (w1 * (1 - ceps_normalized) + 
                      w2 * igi_normalized + 
                      w3 * volatility_normalized)
        
        # Clip to [0, 1]
        df['FERS'] = df['FERS'].clip(0, 1)
        
        # Classify risk level
        def classify_exclusion_risk(fers_val):
            if fers_val > 0.8:
                return 'Critical_Risk'
            elif fers_val > 0.6:
                return 'High_Risk'
            elif fers_val > 0.4:
                return 'Medium_Risk'
            else:
                return 'Low_Risk'
        
        df['Exclusion_Risk_Level'] = df['FERS'].apply(classify_exclusion_risk)
        
        self.fers_scores = df
        logger.info(f"FERS computed for {len(df)} records")
        return df
    
    def compute_all_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compute all scoring metrics at once
        
        Args:
            df: DataFrame with [C, A, State, District, Year, Month]
        
        Returns:
            DataFrame with all scores
        """
        logger.info("Computing all inclusion metrics...")
        
        df = self.calculate_ceps(df)
        df = self.calculate_igi(df)
        df = self.calculate_liss(df)
        df = self.calculate_fers(df)
        
        return df
    
    def get_regional_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get summary statistics by region (State, District)
        
        Args:
            df: DataFrame with computed scores
        
        Returns:
            Regional summary DataFrame
        """
        logger.info("Computing regional summary...")
        
        summary = df.groupby(['State', 'District']).agg({
            'CEPS': 'mean',
            'IGI': 'mean',
            'LISS': 'mean',
            'FERS': 'mean',
            'C': 'sum',
            'A': 'sum',
            'T': 'sum'
        }).reset_index()
        
        summary.columns = ['State', 'District', 'Avg_CEPS', 'Avg_IGI', 'Avg_LISS', 
                          'Avg_FERS', 'Total_Child', 'Total_Adult', 'Total_Enrolments']
        
        summary = summary.sort_values('Avg_FERS', ascending=False)
        
        return summary
    
    def get_state_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get summary statistics by state"""
        logger.info("Computing state-level summary...")
        
        summary = df.groupby('State').agg({
            'CEPS': 'mean',
            'IGI': 'mean',
            'LISS': 'mean',
            'FERS': 'mean',
            'C': 'sum',
            'A': 'sum'
        }).reset_index()
        
        summary.columns = ['State', 'Avg_CEPS', 'Avg_IGI', 'Avg_LISS', 
                          'Avg_FERS', 'Total_Child', 'Total_Adult']
        
        summary['Child_Share'] = (summary['Total_Child'] / 
                                 (summary['Total_Child'] + summary['Total_Adult'])) * 100
        
        return summary.sort_values('Avg_FERS', ascending=False)
    
    def get_top_risk_regions(self, df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        """
        Get top N regions with highest exclusion risk
        
        Args:
            df: Processed DataFrame
            top_n: Number of top regions to return
        
        Returns:
            Top risk regions
        """
        regional_summary = self.get_regional_summary(df)
        return regional_summary.head(top_n)
    
    def get_top_low_inclusion_regions(self, df: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
        """Get top N regions with lowest child inclusion"""
        regional_summary = self.get_regional_summary(df)
        return regional_summary.nsmallest(top_n, 'Avg_CEPS')
