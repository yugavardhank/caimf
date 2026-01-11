"""
Streamlit Dashboard for CAIMF
Live, interactive visualization of child Aadhaar inclusion metrics
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_handler import DataHandler, create_sample_dataset
from models import InclusionScoringModels
from anomaly_detection import AnomalyDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="CAIMF - Child Aadhaar Inclusion Monitor",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_handler' not in st.session_state:
    st.session_state.data_handler = DataHandler()
    st.session_state.scoring_models = InclusionScoringModels()
    st.session_state.anomaly_detector = AnomalyDetector()
    st.session_state.processed_data = None
    st.session_state.scores_data = None

# Sidebar
with st.sidebar:
    st.title("👶 CAIMF Configuration")
    
    st.markdown("---")
    data_source = st.radio(
        "Data Source",
        ["📊 Load UIDAI Dataset", "📤 Upload CSV"]
    )
    
    if data_source == "📤 Upload CSV":
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            st.session_state.processed_data = None  # Reset
            try:
                with st.spinner("Processing data..."):
                    raw_data = pd.read_csv(uploaded_file)
                    st.session_state.data_handler.validate_schema(raw_data)
                    clean_data = st.session_state.data_handler.clean_data_pipeline(raw_data)
                    normalized_data = st.session_state.data_handler.normalize_data(clean_data)
                    params = st.session_state.data_handler.extract_parameters(normalized_data)
                    st.session_state.processed_data = params['parameters']
                    st.session_state.scores_data = st.session_state.scoring_models.compute_all_scores(
                        st.session_state.processed_data
                    )
                st.success("✅ Data loaded and processed!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        if st.button("🔄 Load UIDAI Enrolment Dataset"):
            with st.spinner("Loading and processing UIDAI data..."):
                try:
                    # Don't pass file path - let it use default and auto-generate if needed
                    raw_data = st.session_state.data_handler.load_uidai_enrolment_data()
                    clean_data = st.session_state.data_handler.clean_data_pipeline(raw_data)
                    normalized_data = st.session_state.data_handler.normalize_data(clean_data)
                    params = st.session_state.data_handler.extract_parameters(normalized_data)
                    st.session_state.processed_data = params['parameters']
                    st.session_state.scores_data = st.session_state.scoring_models.compute_all_scores(
                        st.session_state.processed_data
                    )
                    st.success("✅ UIDAI dataset loaded and processed!")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    st.markdown("---")
    st.info("""
    ### System Overview
    - **CEPS**: Child Enrolment Penetration Score
    - **IGI**: Inclusion Gap Index
    - **LISS**: Long-Term Stability Score
    - **FERS**: Future Exclusion Risk Score
    """)
    
    st.markdown("---")
    st.text(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Main dashboard
if st.session_state.scores_data is not None:
    df = st.session_state.scores_data
    
    # Title and overview
    st.title("👶 Child Aadhaar Inclusion Monitoring Framework (CAIMF)")
    st.markdown("A Live, Data-Driven Decision Support System for UIDAI")
    
    # 1. NATIONAL GAUGE
    st.markdown("---")
    st.header("🔴 1. National Child Inclusion Gauge")
    
    col1, col2, col3, col4 = st.columns(4)
    
    national_ceps = df['CEPS'].mean()
    national_igi = df['IGI'].mean()
    national_liss = df['LISS'].mean()
    national_fers = df['FERS'].mean()
    
    with col1:
        st.metric(
            "CEPS (Penetration %)",
            f"{national_ceps:.1f}%",
            delta=None,
            help="Child Enrolment Penetration Score"
        )
        if national_ceps < 30:
            st.error("🔴 Critical Gap")
        elif national_ceps < 60:
            st.warning("🟡 Moderate")
        else:
            st.success("🟢 Healthy")
    
    with col2:
        st.metric(
            "IGI (Gap Index)",
            f"{national_igi:.2f}",
            help="Inclusion Gap Index (lower is better)"
        )
    
    with col3:
        st.metric(
            "LISS (Stability)",
            f"{national_liss:.2f}",
            help="Long-Term Inclusion Stability Score"
        )
    
    with col4:
        st.metric(
            "FERS (Risk Score)",
            f"{national_fers:.2f}",
            help="Future Exclusion Risk Score"
        )
    
    # Additional national stats
    col1, col2, col3 = st.columns(3)
    with col1:
        total_child = int(df['C'].sum())
        st.metric("Total Child Enrolments", f"{total_child:,}")
    with col2:
        total_adult = int(df['A'].sum())
        st.metric("Total Adult Enrolments", f"{total_adult:,}")
    with col3:
        child_share = (total_child / (total_child + total_adult)) * 100
        st.metric("Child Share %", f"{child_share:.1f}%")
    
    # 2. STATE-WISE HEATMAP
    st.markdown("---")
    st.header("🟡 2. State-Wise Heatmap (Inclusion Gap Index)")
    
    state_summary = st.session_state.scoring_models.get_state_summary(df)
    
    # Create heatmap data
    heatmap_data = state_summary[['State', 'Avg_IGI']].copy()
    heatmap_data = heatmap_data.sort_values('Avg_IGI', ascending=False)
    
    fig_heatmap = go.Figure(data=go.Bar(
        y=heatmap_data['State'],
        x=heatmap_data['Avg_IGI'],
        orientation='h',
        marker=dict(
            color=heatmap_data['Avg_IGI'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title="IGI")
        )
    ))
    fig_heatmap.update_layout(
        title="State-wise Inclusion Gap Index (Higher = More Gap Risk)",
        xaxis_title="Average IGI",
        yaxis_title="State",
        height=600
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # 3. TREND EXPLORER
    st.markdown("---")
    st.header("📈 3. Trend Explorer (Child vs Adult Enrolment)")
    
    # Select state for trend analysis
    selected_state = st.selectbox(
        "Select State for Trend Analysis",
        df['State'].unique(),
        key='state_select'
    )
    
    state_trend = df[df['State'] == selected_state].sort_values(['Year', 'Month']).copy()
    state_trend['YearMonth'] = state_trend['Year'].astype(str) + '-' + state_trend['Month'].astype(str).str.zfill(2)
    
    if len(state_trend) > 0:
        trend_summary = state_trend.groupby('YearMonth').agg({'C': 'sum', 'A': 'sum'}).reset_index()
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=trend_summary['YearMonth'],
            y=trend_summary['C'],
            name='Child Enrolments',
            mode='lines+markers',
            line=dict(color='green', width=2)
        ))
        fig_trend.add_trace(go.Scatter(
            x=trend_summary['YearMonth'],
            y=trend_summary['A'],
            name='Adult Enrolments',
            mode='lines+markers',
            line=dict(color='blue', width=2)
        ))
        fig_trend.update_layout(
            title=f"Child vs Adult Enrolment Trends - {selected_state}",
            xaxis_title="Time Period",
            yaxis_title="Enrolments",
            hovermode='x unified',
            height=500
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # 4. RISK RANKING TABLE
    st.markdown("---")
    st.header("⚠️ 4. Risk Ranking Table (Top Exclusion Risk Regions)")
    
    top_n = st.slider("Show top N regions", 5, 50, 15)
    risk_ranking = st.session_state.scoring_models.get_top_risk_regions(df, top_n=top_n)
    
    # Format for display
    risk_display = risk_ranking[['State', 'District', 'Avg_CEPS', 'Avg_IGI', 'Avg_FERS']].copy()
    risk_display.columns = ['State', 'District', 'CEPS (%)', 'IGI', 'FERS (Risk)']
    risk_display['CEPS (%)'] = risk_display['CEPS (%)'].round(1)
    risk_display['IGI'] = risk_display['IGI'].round(2)
    risk_display['FERS (Risk)'] = risk_display['FERS (Risk)'].round(2)
    
    st.dataframe(risk_display, use_container_width=True, hide_index=True)
    
    # 5. POLICY ALERT PANEL
    st.markdown("---")
    st.header("🚨 5. Policy Alert Panel (Regions Needing Intervention)")
    
    alerts = st.session_state.anomaly_detector.create_policy_alerts(
        st.session_state.processed_data, 
        df
    )
    
    # Organize alerts by type
    critical_alerts = [a for a in alerts if a['type'] == 'CRITICAL_INCLUSION_GAP']
    risk_alerts = [a for a in alerts if a['type'] == 'HIGH_EXCLUSION_RISK']
    unstable_alerts = [a for a in alerts if a['type'] == 'UNSTABLE_ENROLMENT']
    
    alert_col1, alert_col2, alert_col3 = st.columns(3)
    
    with alert_col1:
        st.error(f"🔴 Critical Gap: {len(critical_alerts)}")
        for alert in critical_alerts[:3]:
            st.write(f"• {alert['region']}")
    
    with alert_col2:
        st.warning(f"🟠 High Risk: {len(risk_alerts)}")
        for alert in risk_alerts[:3]:
            st.write(f"• {alert['region']}")
    
    with alert_col3:
        st.info(f"🟡 Unstable: {len(unstable_alerts)}")
        for alert in unstable_alerts[:3]:
            st.write(f"• {alert['region']}")
    
    # Detailed alerts table
    if alerts:
        st.subheader("Detailed Alert Actions")
        alerts_df = pd.DataFrame([{
            'Type': a['type'],
            'Region': a['region'],
            'Message': a['message'],
            'Action': a['action']
        } for a in alerts])
        st.dataframe(alerts_df, use_container_width=True, hide_index=True)
    
    # Additional Analytics
    st.markdown("---")
    st.header("📊 Additional Analytics")
    
    tab1, tab2, tab3 = st.tabs(["CEPS Distribution", "State Summary", "Anomaly Detection"])
    
    with tab1:
        fig_ceps_dist = px.histogram(df, x='CEPS', nbins=20, title="Distribution of CEPS Scores")
        fig_ceps_dist.add_vline(x=30, line_dash="dash", annotation_text="Critical Threshold (30%)")
        fig_ceps_dist.add_vline(x=60, line_dash="dash", annotation_text="Moderate Threshold (60%)")
        st.plotly_chart(fig_ceps_dist, use_container_width=True)
    
    with tab2:
        state_stats = st.session_state.scoring_models.get_state_summary(df)
        st.dataframe(state_stats, use_container_width=True, hide_index=True)
    
    with tab3:
        anomalies = st.session_state.anomaly_detector.detect_all_anomalies(st.session_state.processed_data)
        anomaly_counts = {
            'Low Child Ratio': len(anomalies['low_child_ratio']),
            'Declining Growth': len(anomalies['declining_growth']),
            'High Volatility': len(anomalies['high_volatility']),
            'Stagnation': len(anomalies['stagnation']),
            'Seasonal Deviation': len(anomalies['seasonal_deviation'])
        }
        
        fig_anomalies = px.bar(
            x=list(anomaly_counts.keys()),
            y=list(anomaly_counts.values()),
            title="Anomaly Detection Summary",
            labels={'x': 'Anomaly Type', 'y': 'Count'}
        )
        st.plotly_chart(fig_anomalies, use_container_width=True)
        
        st.subheader("Anomaly Counts")
        for anomaly_type, count in anomaly_counts.items():
            st.metric(anomaly_type, count)

else:
    st.warning("⚠️ Please load data using the sidebar to begin!")
    st.info("""
    ## Getting Started
    1. Use the sidebar to either upload a CSV file or load sample data
    2. The system will process the data and compute all metrics
    3. Explore the 5 main dashboard modules:
       - National Gauge (CEPS, IGI, LISS, FERS)
       - State-wise Heatmap
       - Trend Analysis
       - Risk Rankings
       - Policy Alerts
    """)
