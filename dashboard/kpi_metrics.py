# dashboard/kpi_metrics.py
import streamlit as st
import pandas as pd

def display_kpi_metrics(df: pd.DataFrame):
    st.markdown("### 📈 Live Campaign Vitals")
    
    total_tweets = len(df)
    hostile_tweets = len(df[df['sentiment_label'] == 'Hostile'])
    hostility_ratio = (hostile_tweets / total_tweets) * 100 if total_tweets > 0 else 0
    unique_authors = df['author_id'].nunique()
    
    # Calculate Bot-Like Accounts if bot_score column exists
    bot_like_accounts = "N/A"
    if 'bot_score' in df.columns:
        bot_like_accounts = len(df[df['bot_score'] > 75]) # Threshold for a high bot score

    cols = st.columns(5)
    with cols[0]:
        st.metric("Total Tweets", f"{total_tweets:,}")
    with cols[1]:
        st.metric("🔴 Hostile Tweets", f"{hostile_tweets:,}")
    with cols[2]:
        st.metric("Hostility Ratio", f"{hostility_ratio:.2f}%")
    with cols[3]:
        st.metric("👥 Unique Authors", f"{unique_authors:,}")
    with cols[4]:
        st.metric("🤖 Bot-Like Activity", str(bot_like_accounts), help="Number of tweets from accounts with a bot score > 75")

    if hostility_ratio > 15:
        st.error(f"🚨 **High Threat Alert:** Hostility ratio is at **{hostility_ratio:.2f}%**, exceeding the 15% threshold.")