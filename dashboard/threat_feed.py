# dashboard/threat_feed.py
import streamlit as st
import pandas as pd

def display_threat_feed(df: pd.DataFrame):
    st.markdown("### 🔥 Top Hostile Tweets")
    st.info("Displaying the most viral hostile tweets, ranked by engagement score.")
    
    hostile_df = df[df['sentiment_label'] == 'Hostile'].copy()
    
    if hostile_df.empty:
        st.success("✅ No hostile tweets detected in the current dataset.")
        return

    # Use st.expander to show tweets without cluttering the UI
    for index, row in hostile_df.head(5).iterrows():
        with st.expander(f"**Author {row['author_id']}** | Engagement: **{row['engagement_score']:.0f}**"):
            st.markdown(f"> {row['text']}")
            st.markdown(f"**Metrics:** 👍 {row['like_count']} | 🔁 {row['retweet_count']} | 💬 {row['reply_count']} | 引用 {row['quote_count']}")
            # Create a clickable link to the tweet
            tweet_url = f"https://twitter.com/anyuser/status/{row['tweet_id']}"
            st.markdown(f"[View on X/Twitter]({tweet_url})")