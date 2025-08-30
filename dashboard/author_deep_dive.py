# dashboard/author_deep_dive.py
import streamlit as st
import pandas as pd

def display_author_deep_dive(df: pd.DataFrame):
    """Creates an interactive section to analyze a specific author."""
    st.markdown("### 🕵️ Author Deep Dive")
    
    # Get a list of unique authors, sorted by their hostility score
    if 'author_hostility_score' in df.columns:
        author_list = df.sort_values(by='author_hostility_score', ascending=False)['author_id'].unique()
    else:
        st.warning("Author metrics not available.")
        return

    # Create a searchable select box
    selected_author = st.selectbox("Select an Author to Investigate", author_list)

    if selected_author:
        author_data = df[df['author_id'] == selected_author].iloc[0]
        author_tweets = df[df['author_id'] == selected_author]

        st.markdown(f"#### Analysis for Author: `{selected_author}`")
        
        cols = st.columns(4)
        cols[0].metric("Total Tweets", f"{author_data['tweet_count']:.0f}")
        cols[1].metric("Hostility Score", f"{author_data['author_hostility_score']:.1f}%")
        cols[2].metric("Total Engagement", f"{author_data['total_engagement']:.0f}")
        if 'bot_score' in author_data and pd.notna(author_data['bot_score']):
            cols[3].metric("Bot Score", f"{author_data['bot_score']:.1f}%")
        
        st.markdown("##### Recent Hostile Tweets from this Author:")
        hostile_tweets = author_tweets[author_tweets['sentiment_label'] == 'Hostile']
        if hostile_tweets.empty:
            st.success("This author has no hostile tweets in this dataset.")
        else:
            for _, row in hostile_tweets.iterrows():
                st.markdown(f"> {row['text']}")