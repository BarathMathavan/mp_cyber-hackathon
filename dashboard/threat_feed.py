# dashboard/threat_feed.py
import streamlit as st
import pandas as pd

def display_threat_feed(df: pd.DataFrame):
    """Displays the most engaging and hostile tweets."""
    st.header("🔥 Top Hostile Tweets (by Engagement)")
    
    hostile_df = df[df['sentiment_label'] == 'Hostile'].copy()
    
    if hostile_df.empty:
        st.info("No hostile tweets detected in the current dataset.")
        return

    # Select and rename columns for a cleaner display
    display_cols = {
        'text': 'Tweet Content',
        'engagement_score': 'Engagement',
        'author_id': 'Author ID',
        'retweet_count': 'Retweets',
        'like_count': 'Likes'
    }
    
    hostile_df_display = hostile_df[list(display_cols.keys())].rename(columns=display_cols)
    
    st.dataframe(hostile_df_display.head(10), use_container_width=True)