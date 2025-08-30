# dashboard/analytics_charts.py

import streamlit as st
import pandas as pd
import plotly.express as px

# We need to import the keyword list to build the narrative chart
from keywords import KEYWORDS

def display_analytics_charts(df: pd.DataFrame):
    """Displays charts for deeper analysis with all warnings and errors fixed."""
    st.markdown("### 📊 Deeper Analytics")

    # --- Row 1: Sentiment and Velocity ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<h5>Sentiment Distribution</h5>", unsafe_allow_html=True)
        sentiment_counts = df['sentiment_label'].value_counts()
        fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index,
                         title="Overall Sentiment", color=sentiment_counts.index, hole=0.4,
                         color_discrete_map={'Hostile':'#e74c3c', 'Positive':'#2ecc71', 'Neutral':'#95a5a6'})
        fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        fig_pie.update_traces(textinfo='percent+label', textfont_size=14, pull=[0.05, 0, 0])
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("<h5>Hostile Tweet Velocity (per Hour)</h5>", unsafe_allow_html=True)
        # Ensure 'created_at' is a datetime object
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # FIX 3: Use .copy() to avoid the SettingWithCopyWarning
        hostile_df = df[df['sentiment_label'] == 'Hostile'].copy()
        
        # FIX 2: Use lowercase 'h' for hourly resampling
        velocity = hostile_df.set_index('created_at').resample('h').size().rename('tweet_count').reset_index()
        
        fig_velocity = px.area(velocity, x='created_at', y='tweet_count',
                              labels={'created_at': 'Time', 'tweet_count': 'Hostile Tweet Count'},
                              color_discrete_sequence=['#ff4b4b'])
        fig_velocity.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_velocity, use_container_width=True)

    st.markdown("---")

    # --- Row 2: Top Accounts and Narratives side-by-side ---
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("<h5>Top Hostile Accounts</h5>", unsafe_allow_html=True)
        author_df = df[df['sentiment_label'] == 'Hostile']['author_id'].value_counts().head(10)
        fig_bar_authors = px.bar(author_df, y=author_df.index.astype(str), x=author_df.values,
                                orientation='h', title="Authors with Most Hostile Tweets",
                                labels={'y': 'Author ID', 'x': 'Number of Hostile Tweets'},
                                color_discrete_sequence=['#ff7f0e'])
        fig_bar_authors.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_authors, use_container_width=True)

    with col4:
        st.markdown("<h5>Top Hostile Narratives</h5>", unsafe_allow_html=True)
        # Filter for hostile tweets before joining text, which is more efficient
        hostile_texts = " ".join(df[df['sentiment_label'] == 'Hostile']['text'].str.lower())
        
        # Calculate counts only for keywords that appear at least once
        narrative_counts = {kw: hostile_texts.count(kw.lower()) for kw in KEYWORDS if kw.lower() in hostile_texts}
        
        # FIX 1: Convert the series to a proper DataFrame before plotting
        narrative_series = pd.Series(narrative_counts).sort_values(ascending=False).head(10)
        narrative_df = narrative_series.reset_index()
        narrative_df.columns = ['Narrative', 'Frequency']

        fig_bar_narratives = px.bar(
            narrative_df,           # Use the new DataFrame
            y='Narrative',          # Refer to columns by name
            x='Frequency',          # Refer to columns by name
            orientation='h',
            title="Most Frequent Keywords in Hostile Tweets",
            labels={'Narrative': 'Keyword/Narrative', 'Frequency': 'Frequency Count'},
            color_discrete_sequence=['#17becf']
        )
        fig_bar_narratives.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar_narratives, use_container_width=True)