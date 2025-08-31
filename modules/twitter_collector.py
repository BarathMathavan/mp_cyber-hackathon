# modules/twitter_collector.py
import time
import tweepy
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

def collect_tweets(keywords: list, limit_per_chunk: int = 100) -> pd.DataFrame:
    """
    Collects tweets using a robust retry mechanism with exponential backoff to handle
    rate limits dynamically and efficiently.
    """
    if not BEARER_TOKEN:
        raise ValueError("TWITTER_BEARER_TOKEN is not set in the .env file.")
        
    try:
        # We will manage rate limits manually for full control
        client = tweepy.Client(BEARER_TOKEN)
    except Exception as e:
        print(f"Error authenticating with Twitter API: {e}")
        return pd.DataFrame()

    all_tweets_df = pd.DataFrame()
    
    # Keyword chunking logic remains the same
    MAX_QUERY_LENGTH = 480
    keyword_chunks = []
    current_chunk = []
    current_length = 0
    for keyword in keywords:
        if current_length + len(keyword) + 4 > MAX_QUERY_LENGTH:
            keyword_chunks.append(current_chunk)
            current_chunk = [keyword]
            current_length = len(keyword)
        else:
            current_chunk.append(keyword)
            current_length += len(keyword) + 4
    if current_chunk:
        keyword_chunks.append(current_chunk)
    print(f"Split {len(keywords)} keywords into {len(keyword_chunks)} chunks.")

    # --- Loop Through Chunks and Fetch Data with Retry Logic ---
    for i, chunk in enumerate(keyword_chunks):
        query = f'({" OR ".join(chunk)}) lang:en -is:retweet'
        print(f"\n--- Attempting to Fetch Chunk {i+1}/{len(keyword_chunks)} ---")
        
        # --- NEW: DYNAMIC RETRY LOGIC ---
        max_retries = 5
        base_wait_time = 1 # Start with a 1-second wait

        for attempt in range(max_retries):
            try:
                response = client.search_recent_tweets(
                    query=query,
                    max_results=limit_per_chunk,
                    # Requesting all necessary fields for full analysis
                    tweet_fields=["id", "text", "created_at", "public_metrics", "author_id", "source"],
                    expansions=["author_id"],
                    user_fields=["created_at", "public_metrics", "verified", "location"]
                )
                
                # If the request was successful, process the data and break the retry loop
                if not response or not response.data:
                    print("No tweets found for this chunk.")
                else:
                    users = {user["id"]: user for user in response.includes.get('users', [])}
                    tweet_data = []
                    for tweet in response.data:
                        author_info = users.get(tweet.author_id, {})
                        metrics = tweet.public_metrics
                        author_metrics = author_info.get('public_metrics', {})
                        tweet_info = {
                            "tweet_id": tweet.id, "author_id": tweet.author_id, "text": tweet.text,
                            "created_at": tweet.created_at, "source": tweet.source,
                            "retweet_count": metrics['retweet_count'], "reply_count": metrics['reply_count'],
                            "like_count": metrics['like_count'], "quote_count": metrics['quote_count'],
                            "author_created_at": author_info.get('created_at'),
                            "author_followers_count": author_metrics.get('followers_count'),
                            "author_tweet_count": author_metrics.get('tweet_count'),
                            "author_verified": author_info.get('verified'),
                            "author_location": author_info.get('location')
                        }
                        tweet_data.append(tweet_info)
                    
                    chunk_df = pd.DataFrame(tweet_data)
                    all_tweets_df = pd.concat([all_tweets_df, chunk_df], ignore_index=True)
                    print(f"Successfully collected {len(chunk_df)} tweets for this chunk.")
                
                break # Exit the retry loop on success

            except tweepy.errors.TooManyRequests:
                # This is where the intelligent waiting happens
                if attempt < max_retries - 1:
                    wait_time = base_wait_time * (2 ** attempt) # Exponential backoff: 1, 2, 4, 8 seconds
                    print(f"Rate limit hit. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    # After many failed short retries, assume the 15-minute limit is hit
                    print("Hit persistent rate limit. Waiting for 15 minutes...")
                    time.sleep(905) # Wait for the full 15 minutes
                    # After this long wait, we will retry this same chunk one last time
                    # by letting the loop continue
            
            except tweepy.errors.TweepyException as e:
                print(f"An unexpected API error occurred: {e}")
                break # Break the loop for other errors

    # Final Processing
    all_tweets_df = all_tweets_df.drop_duplicates(subset=['tweet_id'])
    print(f"\nSuccessfully collected a total of {len(all_tweets_df)} unique tweets.")
    return all_tweets_df

# The test block remains the same
if __name__ == '__main__':
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from keywords import KEYWORDS
    print("Running Twitter Collector as a standalone script...")
    raw_tweets_df = collect_tweets(keywords=KEYWORDS, limit_per_chunk=100)
    if not raw_tweets_df.empty:
        output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_tweets.csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        raw_tweets_df.to_csv(output_path, index=False)
        print(f"Sample data saved to {output_path}")