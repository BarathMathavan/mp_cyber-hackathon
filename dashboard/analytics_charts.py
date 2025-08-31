# dashboard/analytics_charts.py
import streamlit as st
import pandas as pd
import plotly.express as px
from keywords import KEYWORDS

def display_analytics_charts(df: pd.DataFrame):
    """Displays charts for deeper analysis with robust checks for empty data."""
    st.markdown("### 📊 Deeper Analytics")

    if df.empty:
        st.info("No data available to display for the current filter settings.")
        return

    # --- Row 1: Sentiment and Velocity ---
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("<h5>Sentiment Distribution</h5>", unsafe_allow_html=True)
        if not df['sentiment_label'].empty:
            sentiment_counts = df['sentiment_label'].value_counts()
            fig_pie = px.pie(sentiment_counts, values=sentiment_counts.values, names=sentiment_counts.index,
                             title="Overall Sentiment", color=sentiment_counts.index, hole=0.4,
                             color_discrete_map={'Hostile':'#e74c3c', 'Positive':'#2ecc71', 'Neutral':'#95a5a6'})
            fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            fig_pie.update_traces(textinfo='percent+label', textfont_size=14, pull=[0.05, 0, 0])
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.warning("No sentiment data to display.")

    with col2:
        st.markdown("<h5>Hostile Tweet Velocity (per Hour)</h5>", unsafe_allow_html=True)
        hostile_df_velocity = df[df['sentiment_label'] == 'Hostile'].copy()
        if not hostile_df_velocity.empty:
            hostile_df_velocity['created_at'] = pd.to_datetime(hostile_df_velocity['created_at'])
            velocity = hostile_df_velocity.set_index('created_at').resample('h').size().rename('tweet_count').reset_index()
            fig_velocity = px.area(velocity, x='created_at', y='tweet_count',
                                  labels={'created_at': 'Time', 'tweet_count': 'Hostile Tweet Count'},
                                  color_discrete_sequence=['#ff4b4b'])
            fig_velocity.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_velocity, use_container_width=True)
        else:
            st.info("No hostile tweets in this selection to plot velocity.")

    st.markdown("---")

    # --- Row 2: Top Accounts and Narratives ---
    col3, col4 = st.columns(2)
    hostile_df_charts = df[df['sentiment_label'] == 'Hostile']

    with col3:
        st.markdown("<h5>Top Hostile Accounts</h5>", unsafe_allow_html=True)
        if not hostile_df_charts.empty:
            author_df = hostile_df_charts['author_id'].value_counts().head(10)
            fig_bar_authors = px.bar(author_df, y=author_df.index.astype(str), x=author_df.values,
                                    orientation='h', title="Authors with Most Hostile Tweets",
                                    labels={'y': 'Author ID', 'x': 'Number of Hostile Tweets'},
                                    color_discrete_sequence=['#ff7f0e'])
            fig_bar_authors.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar_authors, use_container_width=True)
        else:
            st.info("No hostile accounts to display in this selection.")

    with col4:
        st.markdown("<h5>Top Hostile Narratives</h5>", unsafe_allow_html=True)
        if not hostile_df_charts.empty:
            hostile_texts = " ".join(hostile_df_charts['text'].astype(str).str.lower())
            narrative_counts = {kw: hostile_texts.count(kw.lower()) for kw in KEYWORDS if kw.lower() in hostile_texts}
            if narrative_counts:
                narrative_series = pd.Series(narrative_counts).sort_values(ascending=False).head(10)
                narrative_df = narrative_series.reset_index()
                narrative_df.columns = ['Narrative', 'Frequency']
                fig_bar_narratives = px.bar(narrative_df, y='Narrative', x='Frequency', orientation='h',
                                            title="Most Frequent Keywords in Hostile Tweets",
                                            labels={'Narrative': 'Keyword/Narrative', 'Frequency': 'Frequency Count'},
                                            color_discrete_sequence=['#17becf'])
                fig_bar_narratives.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_bar_narratives, use_container_width=True)
            else:
                st.info("No tracked narratives found in this selection.")
        else:
            st.info("No hostile narratives to display in this selection.")