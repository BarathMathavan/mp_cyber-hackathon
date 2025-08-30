# dashboard/kpi_metrics.py
import streamlit as st
import pandas as pd

def display_kpi_metrics(df: pd.DataFrame):
    """Displays the key performance indicators at the top of the dashboard."""
    st.header("📈 Live Campaign Overview")
    
    # Calculate KPIs
    total_tweets = len(df)
    hostile_tweets = len(df[df['sentiment_label'] == 'Hostile'])
    hostility_ratio = (hostile_tweets / total_tweets) * 100 if total_tweets > 0 else 0
    
    # Find the most impactful hostile tweet
    most_impactful_tweet = df[df['sentiment_label'] == 'Hostile'].iloc[0] if hostile_tweets > 0 else None
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Total Tweets Analyzed", value=f"{total_tweets:,}")
    
    with col2:
        st.metric(label="Hostile Tweets Detected", value=f"{hostile_tweets:,}",
                  help="Tweets with a sentiment polarity score below -0.05")
        
    with col3:
        st.metric(label="Hostility Ratio", value=f"{hostility_ratio:.2f}%",
                  help="The percentage of all analyzed tweets that are classified as hostile.")

    # Display an alert if the ratio is high
    if hostility_ratio > 15: # Set your own threshold
        st.error(f"🚨 ALERT: High hostility ratio detected at {hostility_ratio:.2f}%. Potential coordinated campaign in progress.")