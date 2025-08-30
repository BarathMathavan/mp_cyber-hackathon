# modules/analysis.py

import pandas as pd
from textblob import TextBlob
import os
import re
import networkx as nx
from pyvis.network import Network
from datetime import datetime, timezone

# --- A more organized approach using a class ---

class TweetAnalyzer:
    """
    A class to handle all analysis tasks for a DataFrame of tweets.
    """
    def __init__(self, df: pd.DataFrame):
        if df.empty:
            raise ValueError("Input DataFrame cannot be empty.")
        self.df = df.copy() # Use a copy to avoid modifying the original DataFrame

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
        """Calculates per-author statistics and merges them back."""
        author_agg = self.df.groupby('author_id').agg(
            tweet_count=('tweet_id', 'count'),
            total_engagement=('engagement_score', 'sum')
        ).reset_index()

        # Calculate hostility score per author
        hostile_counts = self.df[self.df['sentiment_label'] == 'Hostile'].groupby('author_id').size()
        author_agg['hostile_tweet_count'] = author_agg['author_id'].map(hostile_counts).fillna(0)
        author_agg['author_hostility_score'] = (author_agg['hostile_tweet_count'] / author_agg['tweet_count']) * 100

        # Merge these metrics back into the main DataFrame
        self.df = self.df.merge(author_agg, on='author_id', how='left')

    def _calculate_bot_score(self, row):
        """
        Calculates a simple bot score. Requires 'author_created_at' and 'author_followers_count'.
        Fails gracefully if columns are not present.
        """
        # Check if necessary columns exist
        if 'author_created_at' not in row or 'author_followers_count' not in row:
            return None # Not enough data to calculate

        # Score based on account age (newer accounts are more suspicious)
        try:
            # Ensure the timestamp is timezone-aware for correct calculation
            account_age_days = (datetime.now(timezone.utc) - pd.to_datetime(row['author_created_at'])).days
            age_score = max(0, 1 - (account_age_days / 365)) # Score is high if account is < 1 year old
        except (TypeError, ValueError):
            age_score = 0.5 # Default score if date format is weird

        # Score based on follower count (very few followers is suspicious)
        follower_score = max(0, 1 - (row['author_followers_count'] / 100)) # Score is high if followers < 100

        # Combine scores (simple average) and scale to 100
        bot_score = ((age_score + follower_score) / 2) * 100
        return bot_score

    # --- 3. Network Graph Generation ---

    def generate_network_graph(self, output_path: str):
        """Creates and saves an interactive network graph of user mentions."""
        print("Generating network graph...")
        net = Network(height='750px', width='100%', bgcolor='#222222', font_color='white', notebook=True, directed=True)
        
        # Filter for rows that have at least one mention
        mention_df = self.df[self.df['mentions'].apply(lambda x: len(x) > 0)]

        for index, row in mention_df.iterrows():
            author = str(row['author_id'])
            mentioned_users = row['mentions']
            
            # Add the author as a node
            net.add_node(author, label=author, title=f"Author ID: {author}", color='#00a1e4')

            for mentioned_user in mentioned_users:
                # Add the mentioned user as a node
                net.add_node(mentioned_user, label=mentioned_user, title=f"Mentioned User: @{mentioned_user}", color='#ff756e')
                # Add an edge from the author to the mentioned user
                net.add_edge(author, mentioned_user)
        
        # Save the graph to an HTML file
        try:
            net.save_graph(output_path)
            print(f"Network graph saved to {output_path}")
        except Exception as e:
            print(f"Could not save graph: {e}")

    # --- 4. The Main Execution Method ---
    
    def run_full_analysis(self):
        """
        Executes all analysis steps in the correct order.
        """
        print("Starting full analysis pipeline...")
        
        # Step 1: Core tweet enrichment
        self.df['engagement_score'] = self.df.apply(self._calculate_engagement_score, axis=1)
        sentiments = self.df['text'].apply(self._get_sentiment)
        self.df[['sentiment_polarity', 'sentiment_label']] = pd.DataFrame(sentiments.tolist(), index=self.df.index)
        
        entities = self.df['text'].apply(self._extract_entities)
        self.df[['hashtags', 'mentions', 'urls']] = pd.DataFrame(entities.tolist(), index=self.df.index)
        print("-> Core enrichment complete (engagement, sentiment, entities).")

        # Step 2: Author-level analysis
        self._calculate_author_metrics()
        print("-> Author-level metrics calculated.")
        
        # Step 3: Bot score (optional, depends on data)
        if all(k in self.df for k in ['author_created_at', 'author_followers_count']):
            self.df['bot_score'] = self.df.apply(self._calculate_bot_score, axis=1)
            print("-> Bot scores calculated.")
        else:
            print("-> Skipping bot score (required author data not found).")

        # Step 4: Final sorting
        self.df = self.df.sort_values(by='engagement_score', ascending=False)
        
        print("Analysis pipeline finished.")
        return self.df


# --- This part is for testing your script directly ---
if __name__ == '__main__':
    print("Running Analysis module as a standalone script...")

    # Define paths
    input_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_tweets.csv')
    output_path_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'analyzed_data.csv')
    output_path_graph = os.path.join(os.path.dirname(__file__), '..', 'data', 'network_graph.html')

    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}")
    else:
        # Load raw data
        raw_df = pd.read_csv(input_path)
        print(f"Loaded {len(raw_df)} tweets from {input_path}")

        # Initialize and run the analyzer
        analyzer = TweetAnalyzer(raw_df)
        analyzed_df = analyzer.run_full_analysis()
        
        # Generate the network graph
        analyzer.generate_network_graph(output_path_graph)

        # Save the enriched data
        analyzed_df.to_csv(output_path_csv, index=False)
        print(f"Analyzed data saved to {output_path_csv}")