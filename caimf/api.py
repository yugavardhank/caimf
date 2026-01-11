"""
FastAPI Backend for CAIMF
Provides REST API endpoints for metrics and analytics
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

from caimf.data_handler import DataHandler
from caimf.models import InclusionScoringModels
from caimf.anomaly_detection import AnomalyDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CAIMF API",
    description="Child Aadhaar Inclusion Monitoring Framework API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
data_handler = DataHandler()
scoring_models = InclusionScoringModels()
anomaly_detector = AnomalyDetector()
processed_data = None
scores_data = None


# Pydantic models for requests/responses
class RegionalMetric(BaseModel):
    state: str
    district: str
    ceps: float
    igi: float
    liss: float
    fers: float
    inclusion_level: str
    exclusion_risk_level: str


class StateMetric(BaseModel):
    state: str
    avg_ceps: float
    avg_igi: float
    avg_liss: float
    avg_fers: float
    child_share_percentage: float


class PolicyAlert(BaseModel):
    type: str
    region: str
    message: str
    action: str
    priority: str


class DataIngestionRequest(BaseModel):
    file_path: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CAIMF API",
        "version": "1.0.0",
        "status": "operational",
        "description": "Child Aadhaar Inclusion Monitoring Framework",
        "endpoints": {
            "health": "/health",
            "ingest": "/api/v1/ingest",
            "metrics/national": "/api/v1/metrics/national",
            "metrics/state": "/api/v1/metrics/state",
            "metrics/region": "/api/v1/metrics/region",
            "alerts": "/api/v1/alerts",
            "risk-ranking": "/api/v1/risk-ranking"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": processed_data is not None
    }


@app.post("/api/v1/ingest")
async def ingest_data(request: DataIngestionRequest):
    """Ingest data from CSV file"""
    try:
        global processed_data, scores_data
        
        logger.info(f"Ingesting data from {request.file_path}")
        
        # Load and clean data
        raw_data = data_handler.load_csv(request.file_path)
        data_handler.validate_schema(raw_data)
        clean_data = data_handler.clean_data_pipeline(raw_data)
        normalized_data = data_handler.normalize_data(clean_data)
        
        # Extract parameters
        params = data_handler.extract_parameters(normalized_data)
        processed_data = params['parameters']
        
        # Compute all scores
        scores_data = scoring_models.compute_all_scores(processed_data)
        
        summary = data_handler.get_summary_stats(clean_data)
        
        return {
            "status": "success",
            "message": f"Data ingested successfully",
            "records_processed": len(processed_data),
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Data ingestion error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/metrics/national")
async def get_national_metrics():
    """Get national-level inclusion metrics"""
    if scores_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        national_stats = {
            'ceps': float(scores_data['CEPS'].mean()),
            'igi': float(scores_data['IGI'].mean()),
            'liss': float(scores_data['LISS'].mean()),
            'fers': float(scores_data['FERS'].mean()),
            'total_child_enrolments': int(scores_data['C'].sum()),
            'total_adult_enrolments': int(scores_data['A'].sum()),
            'child_share_percentage': float((scores_data['C'].sum() / (scores_data['C'].sum() + scores_data['A'].sum())) * 100),
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "data": national_stats
        }
    except Exception as e:
        logger.error(f"Error computing national metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics/state")
async def get_state_metrics(state: Optional[str] = None):
    """Get state-level metrics"""
    if scores_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        state_summary = scoring_models.get_state_summary(scores_data)
        
        if state:
            state_summary = state_summary[state_summary['State'].str.lower() == state.lower()]
            if state_summary.empty:
                raise HTTPException(status_code=404, detail=f"State '{state}' not found")
        
        result = state_summary.to_dict('records')
        
        return {
            "status": "success",
            "count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"Error computing state metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/metrics/region")
async def get_region_metrics(state: Optional[str] = None, 
                             district: Optional[str] = None,
                             top_n: Optional[int] = 50):
    """Get regional (state-district) metrics"""
    if scores_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        regional_summary = scoring_models.get_regional_summary(scores_data)
        
        if state:
            regional_summary = regional_summary[regional_summary['State'].str.lower() == state.lower()]
        
        if district:
            regional_summary = regional_summary[regional_summary['District'].str.lower() == district.lower()]
        
        regional_summary = regional_summary.head(top_n)
        result = regional_summary.to_dict('records')
        
        return {
            "status": "success",
            "count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"Error computing regional metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk-ranking")
async def get_risk_ranking(top_n: int = Query(15, ge=1, le=100)):
    """Get top N regions ranked by exclusion risk (FERS)"""
    if scores_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        risk_regions = scoring_models.get_top_risk_regions(scores_data, top_n=top_n)
        result = risk_regions.to_dict('records')
        
        return {
            "status": "success",
            "count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"Error computing risk ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/low-inclusion-ranking")
async def get_low_inclusion_ranking(top_n: int = Query(15, ge=1, le=100)):
    """Get top N regions with lowest child inclusion"""
    if scores_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        low_inclusion = scoring_models.get_top_low_inclusion_regions(scores_data, top_n=top_n)
        result = low_inclusion.to_dict('records')
        
        return {
            "status": "success",
            "count": len(result),
            "data": result
        }
    except Exception as e:
        logger.error(f"Error computing low inclusion ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/alerts")
async def get_policy_alerts():
    """Generate policy intervention alerts"""
    if scores_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        alerts = anomaly_detector.create_policy_alerts(processed_data, scores_data)
        
        # Add priority level
        for alert in alerts:
            if alert['type'] == 'CRITICAL_INCLUSION_GAP':
                alert['priority'] = 'P0'
            elif alert['type'] == 'HIGH_EXCLUSION_RISK':
                alert['priority'] = 'P1'
            else:
                alert['priority'] = 'P2'
        
        # Sort by priority
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
        alerts.sort(key=lambda x: priority_order.get(x['priority'], 3))
        
        return {
            "status": "success",
            "count": len(alerts),
            "data": alerts
        }
    except Exception as e:
        logger.error(f"Error generating alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/anomalies")
async def detect_anomalies():
    """Detect anomalies in enrolment data"""
    if processed_data is None:
        raise HTTPException(status_code=400, detail="No data loaded. Use /api/v1/ingest first")
    
    try:
        anomalies = anomaly_detector.detect_all_anomalies(processed_data)
        
        result = {
            "low_child_ratio": len(anomalies['low_child_ratio']),
            "declining_growth": len(anomalies['declining_growth']),
            "high_volatility": len(anomalies['high_volatility']),
            "stagnation": len(anomalies['stagnation']),
            "seasonal_deviation": len(anomalies['seasonal_deviation'])
        }
        
        return {
            "status": "success",
            "anomaly_counts": result
        }
    except Exception as e:
        logger.error(f"Error detecting anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
