# dashboard/network_graph.py
import streamlit as st
import os

def display_network_graph():
    """Displays the interactive network graph of user mentions."""
    st.header("🕸️ Influence & Mention Network")
    
    graph_path = os.path.join('data', 'network_graph.html')
    
    if os.path.exists(graph_path):
        with open(graph_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=800, scrolling=True)
    else:
        st.warning("Network graph not found. Please run the analysis script to generate it.")