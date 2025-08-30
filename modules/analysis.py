# modules/analysis.py

import pandas as pd
from textblob import TextBlob
import os
import re
import networkx as nx
from pyvis.network import Network
from datetime import datetime, timezone

# NEW: Import the community detection library
# Make sure to run: pip install python-louvain
from networkx.algorithms import community

class TweetAnalyzer:
    """
    A class to handle all analysis tasks for a DataFrame of tweets.
    """
    def __init__(self, df: pd.DataFrame):
        if df.empty:
            raise ValueError("Input DataFrame cannot be empty.")
        self.df = df.copy()

    # --- 1. Core Enrichment Functions ---
    def _calculate_engagement_score(self, row):
        weights = {'like_count': 1, 'retweet_count': 2, 'reply_count': 1.5, 'quote_count': 3}
        score = (
            row['like_count'] * weights['like_count'] +
            row['retweet_count'] * weights['retweet_count'] +
            row['reply_count'] * weights['reply_count'] +
            row['quote_count'] * weights['quote_count']
        )
        return score

    def _get_sentiment(self, text: str):
        polarity = TextBlob(text).sentiment.polarity
        threshold = 0.05
        if polarity < -threshold:
            label = 'Hostile'
        elif polarity > threshold:
            label = 'Positive'
        else:
            label = 'Neutral'
        return polarity, label

    def _extract_entities(self, text: str):
        hashtags = re.findall(r"#(\w+)", text)
        mentions = re.findall(r"@(\w+)", text)
        urls = re.findall(r"https?://\S+", text)
        return hashtags, mentions, urls
    
    # --- 2. Author-Level and Bot Score Analysis ---
    def _calculate_author_metrics(self):
        author_agg = self.df.groupby('author_id').agg(
            tweet_count=('tweet_id', 'count'),
            total_engagement=('engagement_score', 'sum')
        ).reset_index()

        hostile_counts = self.df[self.df['sentiment_label'] == 'Hostile'].groupby('author_id').size()
        author_agg['hostile_tweet_count'] = author_agg['author_id'].map(hostile_counts).fillna(0)
        author_agg['author_hostility_score'] = (author_agg['hostile_tweet_count'] / author_agg['tweet_count']) * 100
        self.df = self.df.merge(author_agg, on='author_id', how='left')

    def _calculate_bot_score(self, row):
        if 'author_created_at' not in row or pd.isna(row['author_created_at']) or \
           'author_followers_count' not in row or pd.isna(row['author_followers_count']):
            return None
        try:
            account_age_days = (datetime.now(timezone.utc) - pd.to_datetime(row['author_created_at'])).days
            age_score = max(0, 1 - (account_age_days / 365))
        except (TypeError, ValueError):
            age_score = 0.5
        follower_score = max(0, 1 - (row['author_followers_count'] / 100))
        bot_score = ((age_score + follower_score) / 2) * 100
        return bot_score

    # --- 3. Network Graph Generation ---
    def generate_network_graph(self, output_path_html: str, output_path_gexf: str):
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

        print("-> Performing community detection...")
        try:
            communities_generator = community.louvain_communities(G.to_undirected(), seed=123)
            communities = list(communities_generator)
            node_community_map = {node: i for i, comm in enumerate(communities) for node in comm}
            nx.set_node_attributes(G, node_community_map, 'group')
            print(f"-> Found {len(communities)} distinct communities.")
        except Exception as e:
            print(f"Community detection failed: {e}")

        try:
            nx.write_gexf(G, output_path_gexf)
            print(f"-> Network graph for Gephi saved to {output_path_gexf}")
        except Exception as e:
            print(f"-> Could not save GEXF file for Gephi: {e}")

        try:
            net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', notebook=True, directed=True)
            net.from_nx(G)
            net.save_graph(output_path_html)
            print(f"-> Interactive network graph saved to {output_path_html}")
        except Exception as e:
            print(f"-> Could not save interactive HTML graph: {e}")

    # --- 4. The Main Execution Method ---
    def run_full_analysis(self):
        print("Starting full analysis pipeline...")
        self.df['engagement_score'] = self.df.apply(self._calculate_engagement_score, axis=1)
        sentiments = self.df['text'].apply(self._get_sentiment)
        self.df[['sentiment_polarity', 'sentiment_label']] = pd.DataFrame(sentiments.tolist(), index=self.df.index)
        
        # The 'entities' column can be tricky if some values are not strings. Let's ensure they are.
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

        self.df = self.df.sort_values(by='engagement_score', ascending=False)
        print("Analysis pipeline finished.")
        return self.df


# --- This is the final, corrected test block ---
if __name__ == '__main__':
    print("Running Analysis module as a standalone script...")

    # Define all paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    input_path = os.path.join(project_root, 'data', 'raw_tweets.csv')
    output_path_csv = os.path.join(project_root, 'data', 'analyzed_data.csv')
    output_path_html = os.path.join(project_root, 'data', 'network_graph.html')
    output_path_gexf = os.path.join(project_root, 'data', 'network.gexf')

    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
    else:
        raw_df = pd.read_csv(input_path)
        print(f"Loaded {len(raw_df)} tweets from {input_path}")

        analyzer = TweetAnalyzer(raw_df)
        analyzed_df = analyzer.run_full_analysis()
        
        # Call the graph function with BOTH required output paths
        analyzer.generate_network_graph(output_path_html, output_path_gexf)

        analyzed_df.to_csv(output_path_csv, index=False)
        print(f"Analyzed data saved to {output_path_csv}")