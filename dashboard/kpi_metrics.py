# dashboard/kpi_metrics.py
import streamlit as st
import pandas as pd

def display_kpi_metrics(df: pd.DataFrame):
    st.markdown("### 📈 Live Campaign Vitals")
    
    total_tweets = len(df)
    hostile_tweets = len(df[df['sentiment_label'] == 'Hostile'])
    hostility_ratio = (hostile_tweets / total_tweets) * 100 if total_tweets > 0 else 0
    
    # Calculate the number of unique authors
    unique_authors = df['author_id'].nunique()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Tweets Analyzed", value=f"{total_tweets:,}")
    
    with col2:
        st.metric(label="Hostile Tweets Detected", value=f"{hostile_tweets:,}")
        
    with col3:
        st.metric(label="Hostility Ratio", value=f"{hostility_ratio:.2f}%")

    with col4:
        st.metric(label="Unique Authors", value=f"{unique_authors:,}")

    if hostility_ratio > 15:
        st.error(f"🚨 **High Threat Alert:** Hostility ratio is at {hostility_ratio:.2f}%, indicating a potential coordinated campaign.")