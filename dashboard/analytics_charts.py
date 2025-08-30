# dashboard/analytics_charts.py
import streamlit as st
import pandas as pd
import plotly.express as px

def display_analytics_charts(df: pd.DataFrame):
    """Displays charts for deeper analysis of narratives and authors."""
    st.header("📊 Deeper Analytics")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sentiment Distribution")
        sentiment_counts = df['sentiment_label'].value_counts()
        fig_pie = px.pie(sentiment_counts, 
                         values=sentiment_counts.values, 
                         names=sentiment_counts.index,
                         title="Overall Sentiment of Conversation",
                         color=sentiment_counts.index,
                         color_discrete_map={'Hostile':'#e74c3c', 'Positive':'#2ecc71', 'Neutral':'#95a5a6'})
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Top Hostile Accounts")
        author_df = df.groupby('author_id').agg(
            hostile_tweets=('sentiment_label', lambda x: (x == 'Hostile').sum()),
            total_engagement=('engagement_score', 'sum')
        ).sort_values(by='hostile_tweets', ascending=False)
        
        # Filter for authors with at least one hostile tweet
        top_authors = author_df[author_df['hostile_tweets'] > 0].head(10)
        
        fig_bar = px.bar(top_authors, 
                         x=top_authors.index.astype(str), 
                         y='hostile_tweets',
                         title="Authors with Most Hostile Tweets",
                         labels={'x': 'Author ID', 'y': 'Number of Hostile Tweets'})
        st.plotly_chart(fig_bar, use_container_width=True)