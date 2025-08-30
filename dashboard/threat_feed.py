# dashboard/threat_feed.py
import streamlit as st
import pandas as pd

def display_threat_feed(df: pd.DataFrame):
    st.markdown("### 🔥 Top Hostile Tweets")
    st.info("Displaying the most viral hostile tweets, ranked by engagement.")
    
    hostile_df = df[df['sentiment_label'] == 'Hostile']
    
    if hostile_df.empty:
        st.success("✅ No hostile tweets detected in the current filtered dataset.")
        return

    for _, row in hostile_df.head(10).iterrows():
        st.markdown("---")
        author_id = row['author_id']
        tweet_url = f"https://twitter.com/anyuser/status/{row['tweet_id']}"

        # Create a card-like layout
        st.markdown(f"""
        <div style="border: 1px solid #333; border-radius: 10px; padding: 15px; margin-bottom: 10px;">
            <p><strong>Author:</strong> <code>{author_id}</code> | <a href="{tweet_url}" target="_blank">View on X/Twitter</a></p>
            <p><em>"{row['text']}"</em></p>
            <hr style="border-color: #333;">
            <p>
                <strong>Engagement: {row['engagement_score']:.0f}</strong> |
                👍 {row['like_count']:,} |
                🔁 {row['retweet_count']:,} |
                💬 {row['reply_count']:,} |
                🔗 {row['quote_count']:,}
            </p>
        </div>
        """, unsafe_allow_html=True)