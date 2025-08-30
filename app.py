# app.py

import streamlit as st
import pandas as pd
import os

# Import your dashboard components
from dashboard.kpi_metrics import display_kpi_metrics
from dashboard.threat_feed import display_threat_feed
from dashboard.analytics_charts import display_analytics_charts
from dashboard.network_graph import display_network_graph

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="Project Argus - Hostile Narrative Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Function to load custom CSS ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Data Caching ---
@st.cache_data(ttl=600)
def load_data(filepath: str) -> pd.DataFrame:
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return pd.DataFrame()

# --- Main Application ---
def main():
    # Load the custom CSS
    load_css("style/style.css")

    # --- Sidebar ---
    with st.sidebar:
        st.image("https://i.imgur.com/gJt3eN1.png", width=100) # A sample logo/icon
        st.title("🛡️ Project Argus")
        st.info(
            "This dashboard is an early warning system for detecting and analyzing "
            "hostile digital campaigns on social media."
        )
        
        # --- Data Source Information ---
        data_path = os.path.join('data', 'analyzed_data.csv')
        df = load_data(data_path)
        if not df.empty:
            latest_tweet_time = pd.to_datetime(df['created_at']).max()
            st.success(f"Data last updated:\n{latest_tweet_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        else:
            st.error("Data file not found. Please run the data pipeline.")

        # --- Interactivity in Sidebar ---
        st.header("Filters")
        min_engagement = st.slider("Minimum Engagement Score", 0, int(df['engagement_score'].max()) if not df.empty else 100, 10)
        
    # --- Main Page ---
    st.title("Hostile Narrative Intelligence Dashboard")

    if not df.empty:
        # Filter the dataframe based on the slider
        filtered_df = df[df['engagement_score'] >= min_engagement]

        # --- Display Dashboard Components ---
        display_kpi_metrics(filtered_df)
        
        st.markdown("---")
        
        tab1, tab2, tab3 = st.tabs(["🔥 Threat Feed", "📊 Analytics", "🕸️ Network Graph"])
        
        with tab1:
            display_threat_feed(filtered_df)
        with tab2:
            display_analytics_charts(filtered_df)
        with tab3:
            st.info("This graph shows which users mention others. Larger nodes are more influential.")
            from dashboard.network_graph import display_network_graph
            display_network_graph()
    else:
        st.warning("No data to display. Please run the collector and analyzer scripts.")

if __name__ == "__main__":
    main()