"""
Data Ingestion, Cleaning, and Normalisation Module
Handles CSV ingestion, data validation, and preprocessing
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataHandler:
    """Manages data ingestion, validation, and normalisation"""
    
    REQUIRED_COLUMNS = ['Year', 'Month', 'State', 'District', 'Age_Group', 'Enrolment_Count']
    VALID_STATES = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
        'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
        'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan',
        'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
        'Uttarakhand', 'West Bengal'
    ]
    VALID_AGE_GROUPS = ['Child', 'Adult']
    
    def __init__(self, data_path: str = None):
        """Initialize DataHandler with optional data path"""
        self.data_path = Path(data_path) if data_path else None
        self.raw_data = None
        self.clean_data = None
        self.normalized_data = None
    
    def load_csv(self, file_path: str) -> pd.DataFrame:
        """Load CSV file with validation"""
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded data from {file_path}: {df.shape[0]} rows")
            self.raw_data = df
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_uidai_enrolment_data(self, file_path: str = "data/raw/api_data_aadhar_enrolment_0_500000.csv") -> pd.DataFrame:
        """Load and transform UIDAI enrolment dataset"""
        # Always generate sample data for cloud deployment
        import os
        if not os.path.isfile(file_path):
            logger.warning(f"Data file not found: {file_path}. Generating sample dataset...")
            return self._generate_sample_uidai_data()
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded UIDAI enrolment data: {df.shape[0]} rows")
            
            # Parse date column
            df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y')
            df['year'] = df['date'].dt.year
            df['month'] = df['date'].dt.month
            
            # Age 0-5 and 5-17 are children (Child Aadhaar eligible)
            # Age 18+ are adults
            df['Child'] = df['age_0_5'] + df['age_5_17']
            df['Adult'] = df['age_18_greater']
            
            # Standardize column names
            df['State'] = df['state'].str.strip().str.title()
            df['District'] = df['district'].str.strip().str.title()
            
            # Create the required format
            result_data = []
            for idx, row in df.iterrows():
                result_data.append({
                    'Year': row['year'],
                    'Month': row['month'],
                    'State': row['State'],
                    'District': row['District'],
                    'Age_Group': 'Child',
                    'Enrolment_Count': row['Child']
                })
                result_data.append({
                    'Year': row['year'],
                    'Month': row['month'],
                    'State': row['State'],
                    'District': row['District'],
                    'Age_Group': 'Adult',
                    'Enrolment_Count': row['Adult']
                })
            
            result_df = pd.DataFrame(result_data)
            self.raw_data = result_df
            logger.info(f"Transformed UIDAI data to standard format: {len(result_df)} records")
            return result_df
        except Exception as e:
            logger.error(f"Error loading UIDAI enrolment data: {e}")
            logger.warning("Falling back to sample data generation...")
            return self._generate_sample_uidai_data()
    
    def _generate_sample_uidai_data(self) -> pd.DataFrame:
        """Generate realistic sample UIDAI data for demonstration"""
        np.random.seed(42)
        
        states = self.VALID_STATES[:15]  # Use subset of states
        years = [2023, 2024, 2025]
        months = range(1, 13)
        
        data = []
        for state in states:
            # 3-5 districts per state
            num_districts = np.random.randint(3, 6)
            for dist_num in range(num_districts):
                district = f"{state.split()[0]} District {dist_num + 1}"
                
                for year in years:
                    for month in months:
                        # Generate realistic child enrolment counts
                        child_base = np.random.randint(5000, 50000)
                        child_trend = (year - 2023) * 2000 + month * 100
                        child_count = max(child_base + child_trend + np.random.normal(0, 1000), 100)
                        
                        # Adult enrolments are typically higher
                        adult_base = np.random.randint(20000, 150000)
                        adult_trend = (year - 2023) * 5000 + month * 200
                        adult_count = max(adult_base + adult_trend + np.random.normal(0, 3000), 500)
                        
                        # Child record
                        data.append({
                            'Year': year,
                            'Month': month,
                            'State': state,
                            'District': district,
                            'Age_Group': 'Child',
                            'Enrolment_Count': int(child_count)
                        })
                        
                        # Adult record
                        data.append({
                            'Year': year,
                            'Month': month,
                            'State': state,
                            'District': district,
                            'Age_Group': 'Adult',
                            'Enrolment_Count': int(adult_count)
                        })
        
        result_df = pd.DataFrame(data)
        self.raw_data = result_df
        logger.info(f"Generated sample UIDAI data: {len(result_df)} records, {result_df['State'].nunique()} states, {result_df['District'].nunique()} districts")
        return result_df
    
    def validate_schema(self, df: pd.DataFrame) -> bool:
        """Validate dataframe schema"""
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            logger.warning(f"Missing columns: {missing_cols}")
            return False
        return True
    
    def clean_data_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute full data cleaning pipeline"""
        logger.info("Starting data cleaning pipeline...")
        
        # 1. Remove null/invalid dates
        df = df.dropna(subset=['Year', 'Month'])
        df = df[(df['Year'] >= 2010) & (df['Year'] <= 2026)]
        df = df[(df['Month'] >= 1) & (df['Month'] <= 12)]
        
        # 2. Remove null regions and enrolment counts
        df = df.dropna(subset=['State', 'District', 'Enrolment_Count'])
        
        # 3. Standardize state names
        df['State'] = df['State'].str.strip().str.title()
        df['State'] = df['State'].replace({
            'Andaman And Nicobar': 'Andaman and Nicobar',
            'Dadra And Nagar Haveli': 'Dadra and Nagar Haveli',
            'Daman And Diu': 'Daman and Diu'
        })
        
        # 4. Standardize district names
        df['District'] = df['District'].str.strip().str.title()
        
        # 5. Standardize age groups
        df['Age_Group'] = df['Age_Group'].str.strip().str.title()
        age_group_map = {
            'Child': 'Child',
            'Children': 'Child',
            'Adult': 'Adult',
            'Adults': 'Adult'
        }
        df['Age_Group'] = df['Age_Group'].replace(age_group_map)
        
        # 6. Validate numeric enrolment counts
        df['Enrolment_Count'] = pd.to_numeric(df['Enrolment_Count'], errors='coerce')
        df = df[df['Enrolment_Count'] >= 0]
        
        # 7. Create temporal key
        df['YearMonth'] = df['Year'].astype(str) + '-' + df['Month'].astype(str).str.zfill(2)
        
        logger.info(f"Cleaning complete: {df.shape[0]} valid records")
        self.clean_data = df
        return df
    
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data using Z-score and Min-Max scaling
        Returns normalized features for comparison
        """
        logger.info("Starting normalisation...")
        df = df.copy()
        
        # Group by State-District-AgeGroup to compute statistics
        grouped = df.groupby(['State', 'District', 'Age_Group'])
        
        # Z-score normalization for temporal analysis
        df['Enrolment_ZScore'] = grouped['Enrolment_Count'].transform(
            lambda x: (x - x.mean()) / (x.std() + 1e-8)
        )
        
        # Min-Max scaling (0-1 range) for index construction
        df['Enrolment_MinMax'] = grouped['Enrolment_Count'].transform(
            lambda x: (x - x.min()) / (x.max() - x.min() + 1e-8)
        )
        
        self.normalized_data = df
        logger.info("Normalisation complete")
        return df
    
    def extract_parameters(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Extract base and derived analytical parameters
        
        Returns:
            Dict with DataFrames for different parameter groupings
        """
        logger.info("Extracting parameters...")
        
        # Pivot to get Child and Adult enrolments side by side
        pivot_df = df.pivot_table(
            index=['Year', 'Month', 'State', 'District'],
            columns='Age_Group',
            values='Enrolment_Count',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Base parameters
        pivot_df['C'] = pivot_df.get('Child', 0)  # Child enrolments
        pivot_df['A'] = pivot_df.get('Adult', 0)  # Adult enrolments
        pivot_df['T'] = pivot_df['C'] + pivot_df['A']  # Total enrolments
        
        # Derived parameters
        pivot_df['Child_Enrolment_Share'] = (pivot_df['C'] / (pivot_df['T'] + 1e-8)) * 100
        pivot_df['Adult_Dominance_Ratio'] = (pivot_df['A'] / (pivot_df['C'] + 1e-8))
        
        # Growth rate (month-over-month)
        pivot_df = pivot_df.sort_values(['State', 'District', 'Year', 'Month'])
        pivot_df['Child_Growth_Rate'] = pivot_df.groupby(['State', 'District'])['C'].pct_change()
        
        # Volatility (rolling standard deviation)
        pivot_df['Enrolment_Volatility'] = pivot_df.groupby(['State', 'District'])['C'].transform(
            lambda x: x.rolling(window=3, min_periods=1).std()
        )
        
        logger.info(f"Extracted parameters for {len(pivot_df)} records")
        return {
            'parameters': pivot_df,
            'base': pivot_df[['Year', 'Month', 'State', 'District', 'C', 'A', 'T']],
            'derived': pivot_df[['State', 'District', 'Child_Enrolment_Share', 
                                  'Adult_Dominance_Ratio', 'Child_Growth_Rate', 
                                  'Enrolment_Volatility']]
        }
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Get summary statistics of processed data"""
        return {
            'total_records': len(df),
            'states': df['State'].nunique(),
            'districts': df['District'].nunique(),
            'date_range': f"{df['Year'].min()}-{df['Month'].min()} to {df['Year'].max()}-{df['Month'].max()}",
            'child_enrolments': df[df['Age_Group'] == 'Child']['Enrolment_Count'].sum(),
            'adult_enrolments': df[df['Age_Group'] == 'Adult']['Enrolment_Count'].sum(),
            'total_enrolments': df['Enrolment_Count'].sum()
        }


def create_sample_dataset(output_path: str, num_records: int = 5000):
    """Create realistic sample dataset for testing"""
    np.random.seed(42)
    
    states = DataHandler.VALID_STATES
    months = range(1, 13)
    years = range(2018, 2027)
    age_groups = ['Child', 'Adult']
    
    data = []
    for _ in range(num_records):
        state = np.random.choice(states)
        district = f"{state}_District_{np.random.randint(1, 6)}"
        year = np.random.choice(years)
        month = np.random.choice(months)
        age_group = np.random.choice(age_groups)
        
        # Generate realistic counts with trend
        base_count = np.random.randint(100, 5000)
        if age_group == 'Child':
            trend = (year - 2018) * 50  # Increasing trend
        else:
            trend = (year - 2018) * 30
        
        enrolment = max(base_count + trend + np.random.normal(0, 200), 1)
        
        data.append({
            'Year': year,
            'Month': month,
            'State': state,
            'District': district,
            'Age_Group': age_group,
            'Enrolment_Count': int(enrolment)
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    logger.info(f"Sample dataset created: {output_path}")
    return df
