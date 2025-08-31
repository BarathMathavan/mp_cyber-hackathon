# dashboard/map_view.py
import streamlit as st
import pandas as pd
import plotly.express as px

def display_map_view(df: pd.DataFrame):
    """
    Displays a highly advanced and interactive map of hostile tweet origins.
    This version uses Plotly Express for rich visuals and has enhanced navigation controls
    for intuitive zooming and panning.
    """
    st.markdown("### 🌍 Geographic Threat & Vulnerability Analysis")
    st.info(
        "This map plots the self-reported profile locations of hostile authors. **Size** and **Color Intensity** "
        "of each point represent a calculated **Threat Score**. Use your mouse/trackpad to pan and zoom."
    )

    # Check if the necessary columns for the map exist
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        st.error("Location coordinate data not found. Please re-run the analysis script to generate latitude and longitude columns.")
        return

    # Filter for hostile tweets that have valid coordinates for plotting
    hostile_geo_df = df[
        (df['sentiment_label'] == 'Hostile') & 
        df['latitude'].notna() & 
        df['longitude'].notna()
    ].copy()
    
    if hostile_geo_df.empty:
        st.warning("No plottable location data found for hostile tweets in this dataset.")
        return

    # --- Create a "Threat Score" for enhanced vulnerability analysis ---
    # This combines the tweet's engagement with the author's overall hostility.
    max_engagement = hostile_geo_df['engagement_score'].max()
    if max_engagement > 0:
        # Normalize scores to be on a similar scale before averaging
        hostile_geo_df['threat_score'] = (
            (hostile_geo_df['engagement_score'] / max_engagement) * 100 + 
            hostile_geo_df['author_hostility_score']
        ) / 2
    else:
        # Fallback if there's no engagement data
        hostile_geo_df['threat_score'] = hostile_geo_df['author_hostility_score']
        
    # Create a 'size_for_map' column to ensure a minimum visible dot size
    hostile_geo_df['size_for_map'] = hostile_geo_df['threat_score'].apply(lambda x: max(x, 5))

    # --- The Advanced Interactive Map using Plotly Express ---
    fig = px.scatter_mapbox(
        hostile_geo_df,
        lat="latitude",
        lon="longitude",
        size="size_for_map",              # Size dots by the new threat score
        color="threat_score",             # Color dots by the new threat score
        color_continuous_scale="YlOrRd",  # Yellow -> Orange -> Red color scale for threat level
        hover_name="author_location",     # Show location name on hover
        hover_data={                      # Define what extra data to show on hover
            "threat_score": ":.2f",
            "engagement_score": True,
            "author_hostility_score": ":.2f",
            "text": True,
            # Hide technical columns from the tooltip for a cleaner look
            "latitude": False,
            "longitude": False,
            "size_for_map": False
        },
        zoom=1.5,                               # Set the initial zoom level
        center={"lat": 20.5937, "lon": 78.9629}, # Center the map on India
        mapbox_style="carto-darkmatter"         # Use a dark theme that makes dots stand out
    )

    # --- Configure Layout and Controls for better interactivity ---
    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        mapbox=dict(
            accesstoken=None, # Use the default open-source map tiles
            bearing=0,
            pitch=0
        ),
        coloraxis_colorbar=dict(
            title="Threat Score"
        )
    )

    # --- Display the chart with scroll-to-zoom enabled ---
    # This is the key to enabling intuitive mouse/trackpad zooming
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
    
    st.markdown("---")

    # --- The summary table remains the same ---
    st.markdown("#### Top Hostile Locations (Self-Reported)")
    location_counts = hostile_geo_df['author_location'].value_counts().reset_index()
    location_counts.columns = ['author_location', 'count']
    st.table(location_counts.head(10))