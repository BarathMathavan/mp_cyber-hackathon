# app.py

import streamlit as st
import pandas as pd
import os

# Import dashboard components
from dashboard.kpi_metrics import display_kpi_metrics
from dashboard.threat_feed import display_threat_feed
from dashboard.analytics_charts import display_analytics_charts
from dashboard.network_graph import display_network_graph
from dashboard.campaign_forensics import display_campaign_forensics
# --- NEW: Import the map view component ---
from dashboard.map_view import display_map_view

# Page Config
st.set_page_config(
    page_title="Project Argus - Hostile Narrative Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load custom CSS
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Data Caching
@st.cache_data(ttl=600)
def load_data(filepath: str) -> pd.DataFrame:
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        for col in ['hashtags', 'mentions', 'urls']:
            if col in df.columns:
                try:
                    df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith('[') else [])
                except Exception: df[col] = df[col].apply(lambda x: [])
        return df
    return pd.DataFrame()

# Main Application
def main():
    load_css("style/style.css")

    # --- Sidebar ---
    with st.sidebar:
        st.title("🛡️ Project Argus")
        st.info("An early warning system for detecting and analyzing hostile digital campaigns.")
        
        data_path = os.path.join('data', 'analyzed_data.csv')
        full_df = load_data(data_path)
        
        if not full_df.empty:
            latest_tweet_time = pd.to_datetime(full_df['created_at']).max()
            st.success(f"Data last updated:\n{latest_tweet_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            st.error("Data file not found. Please run the data pipeline.")

        st.header("Filters")
        # In app.py, inside the sidebar
        min_engagement = st.slider(
            "Filter by Minimum Engagement",
            min_value=0,
            max_value=175,  # <-- THIS IS THE CHANGE
            value=0,       # Default starting value
            help="Filters the Threat Feed and Analytics tabs to focus on viral content."
        )
    
    # --- Main Page ---
    st.title("Hostile Narrative Intelligence Dashboard")

    if not full_df.empty:
        filtered_df = full_df[full_df['engagement_score'] >= min_engagement]
        st.write(f"Showing **{len(filtered_df)}** of **{len(full_df)}** total tweets based on filter.")
        
        # --- UPDATED TABS ---
        tab_titles = [
            "📈 **Vitals & KPIs**", 
            "🔥 **Threat Feed**", 
            "📊 **Analytical Charts**", 
            "🌍 **Map View**",
            "🕸️ **Network Graph**",
            "🕵️ **Campaign Forensics**"
        ]
        tab1, tab2, tab3, tab_map, tab4, tab5 = st.tabs(tab_titles)
        
        with tab1:
            display_kpi_metrics(filtered_df)
        with tab2:
            display_threat_feed(filtered_df)
        with tab3:
            display_analytics_charts(filtered_df)
        with tab_map:
            display_map_view(full_df) # Use the full dataset for a comprehensive map
        with tab4:
            st.info("This is a live, interactive graph of the mention network.")
            display_network_graph()
        with tab5:
            display_campaign_forensics(full_df)
            
    else:
        st.warning("No data to display. Please run the collector and analyzer scripts.")

if __name__ == "__main__":
    main()