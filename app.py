# app.py

import streamlit as st
import pandas as pd
import os

# Import your dashboard components
from dashboard.kpi_metrics import display_kpi_metrics
from dashboard.threat_feed import display_threat_feed
from dashboard.analytics_charts import display_analytics_charts
from dashboard.network_graph import display_network_graph

# --- Page Configuration ---
st.set_page_config(
    page_title="Project Argus - Hostile Narrative Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Caching ---
@st.cache_data(ttl=600) # Cache data for 10 minutes
def load_data(filepath: str) -> pd.DataFrame:
    """Loads the analyzed data from a CSV file."""
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        # No need for an error here in the final version, the main app will handle it
        return pd.DataFrame()

# --- Main Application ---
def main():
    st.title("🛡️ Project Argus")
    st.subheader("A Real-Time Dashboard for Detecting Hostile Digital Campaigns")

    # --- Sidebar for Controls ---
    st.sidebar.title("Controls")
    st.sidebar.info(
        "This dashboard analyzes Twitter data to identify and track potentially "
        "hostile narratives and the key actors spreading them."
    )
    
    if st.sidebar.button("🔄 Refresh Data"):
        # This button will clear the cache, forcing the app to re-run load_data()
        st.cache_data.clear()
        st.sidebar.success("Data cache cleared. Rerunning...")
        # A full version would trigger the collector/analyzer here
    
    # --- Load Data ---
    data_path = os.path.join('data', 'analyzed_data.csv')
    df = load_data(data_path)

    if not df.empty:
        # --- Display Dashboard Components ---
        display_kpi_metrics(df)
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🔥 Threat Feed", "📊 Analytics", "🕸️ Network Graph"])
        
        with tab1:
            display_threat_feed(df)
            
        with tab2:
            display_analytics_charts(df)

        with tab3:
            display_network_graph()
    
    else:
        st.warning("Data file not found or is empty. Please run the collector and analyzer scripts to generate data.")

if __name__ == "__main__":
    main()