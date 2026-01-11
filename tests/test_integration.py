"""
Integration tests for CAIMF system
Tests all major components
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile

from caimf.data_handler import DataHandler, create_sample_dataset
from caimf.models import InclusionScoringModels
from caimf.anomaly_detection import AnomalyDetector


@pytest.fixture
def sample_data():
    """Create sample dataset for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    create_sample_dataset(temp_path, num_records=500)
    yield temp_path
    
    Path(temp_path).unlink()


class TestDataHandler:
    """Test data ingestion and cleaning"""
    
    def test_load_csv(self, sample_data):
        handler = DataHandler()
        df = handler.load_csv(sample_data)
        assert len(df) > 0
        assert 'Enrolment_Count' in df.columns
    
    def test_validate_schema(self, sample_data):
        handler = DataHandler()
        df = handler.load_csv(sample_data)
        assert handler.validate_schema(df) == True
    
    def test_clean_data(self, sample_data):
        handler = DataHandler()
        handler.load_csv(sample_data)
        clean_df = handler.clean_data_pipeline(handler.raw_data)
        assert len(clean_df) > 0
        assert clean_df['Enrolment_Count'].min() >= 0
        assert clean_df['Year'].min() >= 2010
    
    def test_normalize_data(self, sample_data):
        handler = DataHandler()
        handler.load_csv(sample_data)
        clean_df = handler.clean_data_pipeline(handler.raw_data)
        norm_df = handler.normalize_data(clean_df)
        
        assert 'Enrolment_ZScore' in norm_df.columns
        assert 'Enrolment_MinMax' in norm_df.columns
        assert norm_df['Enrolment_MinMax'].max() <= 1.0
        assert norm_df['Enrolment_MinMax'].min() >= 0.0


class TestScoringModels:
    """Test mathematical scoring models"""
    
    @pytest.fixture
    def processed_data(self, sample_data):
        handler = DataHandler()
        handler.load_csv(sample_data)
        clean_df = handler.clean_data_pipeline(handler.raw_data)
        norm_df = handler.normalize_data(clean_df)
        params = handler.extract_parameters(norm_df)
        return params['parameters']
    
    def test_ceps_calculation(self, processed_data):
        models = InclusionScoringModels()
        result = models.calculate_ceps(processed_data)
        
        assert 'CEPS' in result.columns
        assert result['CEPS'].min() >= 0
        assert result['CEPS'].max() <= 100
        assert result['Inclusion_Level'].isin(['Critical', 'Moderate', 'Healthy']).all()
    
    def test_igi_calculation(self, processed_data):
        models = InclusionScoringModels()
        result = models.calculate_igi(processed_data)
        
        assert 'IGI' in result.columns
        assert result['Gap_Risk_Level'].isin(['Critical_Gap', 'High_Gap', 'Moderate_Gap', 'Low_Gap']).all()
    
    def test_liss_calculation(self, processed_data):
        models = InclusionScoringModels()
        result = models.calculate_liss(processed_data)
        
        assert 'LISS' in result.columns
        assert result['LISS'].min() >= 0
        assert result['LISS'].max() <= 1
    
    def test_fers_calculation(self, processed_data):
        models = InclusionScoringModels()
        result = models.calculate_fers(processed_data)
        
        assert 'FERS' in result.columns
        assert result['FERS'].min() >= 0
        assert result['FERS'].max() <= 1
        assert result['Exclusion_Risk_Level'].isin(['Critical_Risk', 'High_Risk', 'Medium_Risk', 'Low_Risk']).all()
    
    def test_compute_all_scores(self, processed_data):
        models = InclusionScoringModels()
        result = models.compute_all_scores(processed_data)
        
        assert all(col in result.columns for col in ['CEPS', 'IGI', 'LISS', 'FERS'])
    
    def test_regional_summary(self, processed_data):
        models = InclusionScoringModels()
        scored = models.compute_all_scores(processed_data)
        summary = models.get_regional_summary(scored)
        
        assert len(summary) > 0
        assert 'State' in summary.columns
        assert 'District' in summary.columns
        assert 'Avg_FERS' in summary.columns
    
    def test_state_summary(self, processed_data):
        models = InclusionScoringModels()
        scored = models.compute_all_scores(processed_data)
        summary = models.get_state_summary(scored)
        
        assert len(summary) > 0
        assert 'State' in summary.columns
        assert 'Child_Share' in summary.columns


class TestAnomalyDetection:
    """Test anomaly detection"""
    
    @pytest.fixture
    def processed_data(self, sample_data):
        handler = DataHandler()
        handler.load_csv(sample_data)
        clean_df = handler.clean_data_pipeline(handler.raw_data)
        norm_df = handler.normalize_data(clean_df)
        params = handler.extract_parameters(norm_df)
        return params['parameters']
    
    def test_low_child_ratio_detection(self, processed_data):
        detector = AnomalyDetector()
        result = detector.detect_high_adult_enrolment_anomaly(processed_data)
        assert isinstance(result, pd.DataFrame)
    
    def test_volatility_detection(self, processed_data):
        detector = AnomalyDetector()
        result = detector.detect_volatility_anomaly(processed_data)
        assert isinstance(result, pd.DataFrame)
    
    def test_all_anomalies(self, processed_data):
        detector = AnomalyDetector()
        result = detector.detect_all_anomalies(processed_data)
        
        assert isinstance(result, dict)
        assert all(key in result for key in [
            'low_child_ratio',
            'declining_growth',
            'high_volatility',
            'stagnation',
            'seasonal_deviation'
        ])
    
    def test_policy_alerts(self, processed_data, sample_data):
        models = InclusionScoringModels()
        handler = DataHandler()
        handler.load_csv(sample_data)
        clean_df = handler.clean_data_pipeline(handler.raw_data)
        norm_df = handler.normalize_data(clean_df)
        params = handler.extract_parameters(norm_df)
        scored = models.compute_all_scores(params['parameters'])
        
        detector = AnomalyDetector()
        alerts = detector.create_policy_alerts(processed_data, scored)
        
        assert isinstance(alerts, list)
        if len(alerts) > 0:
            assert all(key in alerts[0] for key in ['type', 'region', 'message', 'action'])


class TestIntegration:
    """End-to-end integration tests"""
    
    def test_full_pipeline(self, sample_data):
        """Test complete pipeline from raw data to alerts"""
        # Data processing
        handler = DataHandler()
        handler.load_csv(sample_data)
        clean_data = handler.clean_data_pipeline(handler.raw_data)
        normalized = handler.normalize_data(clean_data)
        params = handler.extract_parameters(normalized)
        processed = params['parameters']
        
        # Scoring
        models = InclusionScoringModels()
        scored = models.compute_all_scores(processed)
        
        # Analysis
        state_summary = models.get_state_summary(scored)
        regional_summary = models.get_regional_summary(scored)
        
        # Anomalies and alerts
        detector = AnomalyDetector()
        anomalies = detector.detect_all_anomalies(processed)
        alerts = detector.create_policy_alerts(processed, scored)
        
        # Assertions
        assert len(processed) > 0
        assert len(state_summary) > 0
        assert len(regional_summary) > 0
        assert all(key in anomalies for key in [
            'low_child_ratio', 'declining_growth', 'high_volatility', 
            'stagnation', 'seasonal_deviation'
        ])
        assert isinstance(alerts, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
