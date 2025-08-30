# dashboard/analytics_charts.py
import streamlit as st
import pandas as pd
import plotly.express as px

def display_analytics_charts(df: pd.DataFrame):
    st.markdown("### 📊 Deeper Analytics")

    # Let's use a two-column layout for a cleaner look
    col1, col2 = st.columns([1, 2]) # Make the second column wider

    with col1:
        st.markdown("#### Sentiment Distribution")
        sentiment_counts = df['sentiment_label'].value_counts()
        fig_pie = px.pie(sentiment_counts, 
                         values=sentiment_counts.values, 
                         names=sentiment_counts.index,
                         title="Overall Sentiment",
                         color=sentiment_counts.index,
                         color_discrete_map={'Hostile':'#e74c3c', 'Positive':'#2ecc71', 'Neutral':'#95a5a6'})
        fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        fig_pie.update_traces(textinfo='percent+label', textfont_size=14)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("#### Top Hostile Accounts")
        author_df = df[df['sentiment_label'] == 'Hostile'].groupby('author_id').agg(
            tweet_count=('tweet_id', 'count')
        ).sort_values(by='tweet_count', ascending=False).head(10)
        
        fig_bar = px.bar(author_df, 
                         x=author_df.index.astype(str), 
                         y='tweet_count',
                         title="Authors with Most Hostile Tweets",
                         labels={'x': 'Author ID', 'y': 'Number of Hostile Tweets'},
                         color_discrete_sequence=['#ff7f0e']) # Orange color
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_bar, use_container_width=True)