# dashboard/campaign_forensics.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from itertools import combinations
from collections import Counter

def display_campaign_forensics(df: pd.DataFrame):
    """
    An advanced interactive dashboard for deep diving into specific authors
    and analyzing the co-occurrence of hostile narratives.
    """
    st.markdown("### 🕵️ Campaign Forensics")
    st.info(
        "Use this section to conduct a detailed investigation. Analyze the behavior of "
        "specific high-risk authors or uncover the hidden connections between hostile narratives."
    )

    col1, col2 = st.columns([1, 2]) # Make the second column wider

    # --- Part 1: Author Forensics (Left Column) ---
    with col1:
        st.markdown("#### Author Deep Dive")
        
        # Create a list of authors, sorted by their hostility score for the dropdown
        if 'author_hostility_score' in df.columns:
            author_list = df.sort_values(by='author_hostility_score', ascending=False)['author_id'].unique()
        else:
            st.warning("Author metrics not available to perform deep dive.")
            return

        selected_author = st.selectbox("Select a High-Risk Author to Investigate", author_list)

        if selected_author:
            author_data = df[df['author_id'] == selected_author].iloc[0]
            author_tweets = df[df['author_id'] == selected_author]

            # Display key metrics for the selected author
            st.metric("Author Hostility Score", f"{author_data['author_hostility_score']:.1f}%",
                      help="Percentage of this author's tweets that are hostile.")
            if 'bot_score' in author_data and pd.notna(author_data['bot_score']):
                st.metric("Bot Score", f"{author_data['bot_score']:.1f}%",
                          help="Likelihood of being an automated account (based on age & followers).")
            
            st.markdown(f"**Recent Hostile Posts from `{selected_author}`:**")
            hostile_tweets = author_tweets[author_tweets['sentiment_label'] == 'Hostile']

            if hostile_tweets.empty:
                st.success("This author has no hostile tweets in this dataset.")
            else:
                for _, row in hostile_tweets.head(3).iterrows():
                    st.markdown(f"> _{row['text']}_")

    # --- Part 2: Narrative Forensics (Right Column) ---
    with col2:
        st.markdown("#### Narrative Co-occurrence Heatmap")
        
        hostile_df = df[df['sentiment_label'] == 'Hostile']
        
        # Find the top 15 most frequent hashtags in hostile tweets
        top_hashtags = Counter(
            tag for tags_list in hostile_df['hashtags'] if isinstance(tags_list, list) for tag in tags_list
        ).most_common(15)
        
        top_tags_list = [tag for tag, count in top_hashtags]

        if len(top_tags_list) < 2:
            st.warning("Not enough hashtag data to generate a co-occurrence heatmap.")
            return

        # Create a co-occurrence matrix
        co_occurrence_matrix = pd.DataFrame(0, index=top_tags_list, columns=top_tags_list)
        
        for tags_list in hostile_df['hashtags']:
            if isinstance(tags_list, list):
                # For every pair of hashtags in a tweet, increment their counter
                for tag1, tag2 in combinations(set(tags_list) & set(top_tags_list), 2):
                    co_occurrence_matrix.loc[tag1, tag2] += 1
                    co_occurrence_matrix.loc[tag2, tag1] += 1
        
        fig = go.Figure(data=go.Heatmap(
                   z=co_occurrence_matrix.values,
                   x=co_occurrence_matrix.columns,
                   y=co_occurrence_matrix.index,
                   colorscale='Reds'))

        fig.update_layout(
            title='Which Hostile Hashtags are Used Together?',
            xaxis_nticks=36,
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
        st.success(
            "**Insight:** Bright squares show which hashtags are frequently used together, "
            "revealing the core messaging of a coordinated campaign."
        )