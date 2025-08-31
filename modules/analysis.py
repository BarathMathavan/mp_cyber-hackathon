# modules/analysis.py

import pandas as pd
from textblob import TextBlob
import os
import re
import networkx as nx
from pyvis.network import Network
from datetime import datetime, timezone
from networkx.algorithms import community

# --- NEW: Import geopy for location analysis ---
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

class TweetAnalyzer:
    """
    A class to handle all analysis tasks for a DataFrame of tweets.
    """
    def __init__(self, df: pd.DataFrame):
        if df.empty:
            raise ValueError("Input DataFrame cannot be empty.")
        self.df = df.copy()

    # --- (Sections 1 and 2: Core Enrichment and Author Metrics remain identical) ---
    def _calculate_engagement_score(self, row):
        # ... (no changes here)
        weights = {'like_count': 1, 'retweet_count': 2, 'reply_count': 1.5, 'quote_count': 3}
        return (row['like_count']*weights['like_count'] + row['retweet_count']*weights['retweet_count'] +
                row['reply_count']*weights['reply_count'] + row['quote_count']*weights['quote_count'])

    def _get_sentiment(self, text: str):
        # ... (no changes here)
        polarity = TextBlob(text).sentiment.polarity
        threshold = 0.05
        if polarity < -threshold: return polarity, 'Hostile'
        elif polarity > threshold: return polarity, 'Positive'
        else: return polarity, 'Neutral'

    def _extract_entities(self, text: str):
        # ... (no changes here)
        hashtags = re.findall(r"#(\w+)", text)
        mentions = re.findall(r"@(\w+)", text)
        urls = re.findall(r"https?://\S+", text)
        return hashtags, mentions, urls

    def _calculate_author_metrics(self):
        # ... (no changes here)
        author_agg = self.df.groupby('author_id').agg(tweet_count=('tweet_id','count'), total_engagement=('engagement_score','sum')).reset_index()
        hostile_counts = self.df[self.df['sentiment_label'] == 'Hostile'].groupby('author_id').size()
        author_agg['hostile_tweet_count'] = author_agg['author_id'].map(hostile_counts).fillna(0)
        author_agg['author_hostility_score'] = (author_agg['hostile_tweet_count'] / author_agg['tweet_count']) * 100
        self.df = self.df.merge(author_agg, on='author_id', how='left')

    def _calculate_bot_score(self, row):
        # ... (no changes here)
        if 'author_created_at' not in row or pd.isna(row['author_created_at']) or 'author_followers_count' not in row or pd.isna(row['author_followers_count']): return None
        try:
            age_score = max(0, 1 - ((datetime.now(timezone.utc) - pd.to_datetime(row['author_created_at'])).days / 365))
        except (TypeError, ValueError): age_score = 0.5
        follower_score = max(0, 1 - (row['author_followers_count'] / 100))
        return ((age_score + follower_score) / 2) * 100

    # --- NEW: Geocoding method ---
    def _geocode_locations(self):
        """Converts author location strings to lat/lon coordinates using caching."""
        if 'author_location' not in self.df.columns:
            print("-> Skipping geocoding (author_location column not found).")
            self.df['latitude'] = None
            self.df['longitude'] = None
            return
            
        print("-> Geocoding author locations (this may take a moment)...")
        unique_locations = self.df['author_location'].dropna().unique()
        
        if len(unique_locations) == 0:
            print("-> No location data to geocode.")
            self.df['latitude'] = None
            self.df['longitude'] = None
            return

        # In modules/analysis.py, inside the _geocode_locations method

        # Add a timeout of 10 seconds to the geocoder initialization
        geolocator = Nominatim(user_agent=f"project_argus_hackathon_{os.getpid()}", timeout=10)
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1, return_value_on_exception=None)

        location_cache = {}
        for location_str in unique_locations:
            location_obj = geocode(location_str)
            location_cache[location_str] = (location_obj.latitude, location_obj.longitude) if location_obj else (None, None)
        
        coords = self.df['author_location'].map(location_cache)
        self.df[['latitude', 'longitude']] = pd.DataFrame(coords.tolist(), index=self.df.index)
        print(f"-> Geocoding complete. Found coordinates for {self.df['latitude'].notna().sum()} tweets.")

    # --- (Section 3: Network Graph Generation remains identical) ---
    def generate_network_graph(self, output_path_html: str, output_path_gexf: str):
        # ... (no changes here)
        print("Generating network graph...")
        mention_df = self.df[self.df['mentions'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
        if mention_df.empty:
            print("No mention data found to build a graph. Skipping.")
            return
        G = nx.DiGraph()
        for _, row in mention_df.iterrows():
            author = str(row['author_id'])
            for mentioned in row['mentions']:
                G.add_edge(author, mentioned)
        print(f"-> Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")
        try:
            communities = list(community.louvain_communities(G.to_undirected(), seed=123))
            node_community_map = {node: i for i, comm in enumerate(communities) for node in comm}
            nx.set_node_attributes(G, node_community_map, 'group')
            print(f"-> Found {len(communities)} distinct communities.")
        except Exception as e: print(f"Community detection failed: {e}")
        try:
            nx.write_gexf(G, output_path_gexf)
            print(f"-> Network graph for Gephi saved to {output_path_gexf}")
        except Exception as e: print(f"-> Could not save GEXF file for Gephi: {e}")
        try:
            net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', notebook=True, directed=True)
            net.from_nx(G)
            net.save_graph(output_path_html)
            print(f"-> Interactive network graph saved to {output_path_html}")
        except Exception as e: print(f"-> Could not save interactive HTML graph: {e}")

    # --- 4. The Main Execution Method (UPDATED) ---
    def run_full_analysis(self):
        print("Starting full analysis pipeline...")
        self.df['engagement_score'] = self.df.apply(self._calculate_engagement_score, axis=1)
        sentiments = self.df['text'].apply(self._get_sentiment)
        self.df[['sentiment_polarity', 'sentiment_label']] = pd.DataFrame(sentiments.tolist(), index=self.df.index)
        entities = self.df['text'].astype(str).apply(self._extract_entities)
        self.df[['hashtags', 'mentions', 'urls']] = pd.DataFrame(entities.tolist(), index=self.df.index)
        print("-> Core enrichment complete.")
        self._calculate_author_metrics()
        print("-> Author-level metrics calculated.")
        if all(k in self.df for k in ['author_created_at', 'author_followers_count']):
            self.df['bot_score'] = self.df.apply(self._calculate_bot_score, axis=1)
            print("-> Bot scores calculated.")
        else:
            print("-> Skipping bot score (required author data not found).")

        # --- NEW: Call the geocoding function ---
        self._geocode_locations()
        
        self.df = self.df.sort_values(by='engagement_score', ascending=False)
        print("Analysis pipeline finished.")
        return self.df


# --- (The if __name__ == '__main__' block remains identical) ---
if __name__ == '__main__':
    # ... (no changes here)
    print("Running Analysis module as a standalone script...")
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    input_path = os.path.join(project_root, 'data', 'raw_tweets.csv')
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
    else:
        raw_df = pd.read_csv(input_path)
        print(f"Loaded {len(raw_df)} tweets from {input_path}")
        analyzer = TweetAnalyzer(raw_df)
        analyzed_df = analyzer.run_full_analysis()
        output_path_html = os.path.join(project_root, 'data', 'network_graph.html')
        output_path_gexf = os.path.join(project_root, 'data', 'network.gexf')
        analyzer.generate_network_graph(output_path_html, output_path_gexf)
        output_path_csv = os.path.join(project_root, 'data', 'analyzed_data.csv')
        analyzed_df.to_csv(output_path_csv, index=False)
        print(f"Analyzed data saved to {output_path_csv}")