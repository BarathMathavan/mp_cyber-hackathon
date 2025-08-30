# modules/twitter_collector.py
import time
import tweepy
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the project root
# This line looks for the .env file in the parent directory of 'modules'
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Get the Bearer Token from the environment variables
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# modules/twitter_collector.py

# ... (imports and BEARER_TOKEN definition stay the same) ...

def collect_tweets(keywords: list, limit_per_chunk: int = 100) -> pd.DataFrame:
    """
    Collects recent tweets from Twitter by breaking a large keyword list into smaller chunks,
    pausing between requests, and intelligently handling rate limit errors by waiting and retrying.

    Args:
        keywords (list): A list of keywords/hashtags to search for.
        limit_per_chunk (int): The max number of tweets to fetch FOR EACH CHUNK.

    Returns:
        pd.DataFrame: A DataFrame containing the combined results of all searches.
    """
    
    # ... (API connection and keyword chunking logic is correct and stays the same) ...
    if not BEARER_TOKEN:
        raise ValueError("TWITTER_BEARER_TOKEN is not set in the .env file.")
        
    try:
        client = tweepy.Client(BEARER_TOKEN, wait_on_rate_limit=True) # <-- IMPORTANT CHANGE
    except Exception as e:
        print(f"Error authenticating with Twitter API: {e}")
        return pd.DataFrame()

    all_tweets_df = pd.DataFrame()
    
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

    print(f"Split {len(keywords)} keywords into {len(keyword_chunks)} chunks to respect API limits.")

    # --- Loop Through Chunks and Fetch Data ---
    for i, chunk in enumerate(keyword_chunks):
        
        query = f'({" OR ".join(chunk)}) lang:en -is:retweet'
        print(f"\n--- Fetching Chunk {i+1}/{len(keyword_chunks)} ---")
        
        try:
            # Tweepy's built-in wait_on_rate_limit will handle the 429 error automatically!
            response = client.search_recent_tweets(
                query=query,
                max_results=limit_per_chunk,
                tweet_fields=["id", "text", "created_at", "public_metrics", "author_id"]
            )
            
            # Check if the response or data is None
            if not response or not response.data:
                print("No tweets found for this chunk.")
                continue

            tweets = response.data
            tweet_data = []
            for tweet in tweets:
                metrics = tweet.public_metrics
                tweet_info = {
                    "tweet_id": tweet.id, "author_id": tweet.author_id, "text": tweet.text,
                    "created_at": tweet.created_at, "retweet_count": metrics['retweet_count'],
                    "reply_count": metrics['reply_count'], "like_count": metrics['like_count'],
                    "quote_count": metrics['quote_count']
                }
                tweet_data.append(tweet_info)
            
            chunk_df = pd.DataFrame(tweet_data)
            all_tweets_df = pd.concat([all_tweets_df, chunk_df], ignore_index=True)
            print(f"Collected {len(chunk_df)} tweets for this chunk.")

        except tweepy.errors.TweepyException as e:
            print(f"An error occurred for this chunk: {e}")
            # Optional: Add a small sleep even on other errors before continuing
            time.sleep(2)
            continue

    # --- Final Processing ---
    all_tweets_df = all_tweets_df.drop_duplicates(subset=['tweet_id'])
    print(f"\nSuccessfully collected a total of {len(all_tweets_df)} unique tweets.")
    return all_tweets_df

# ... The if __name__ == '__main__': block at the bottom stays exactly the same ...
# But you might want to change the limit to a smaller number per chunk for testing, e.g.,
# raw_tweets_df = collect_tweets(keywords=KEYWORDS, limit_per_chunk=20)

# --- This part is for testing your script directly ---
if __name__ == '__main__':
    # This block will only run when you execute `python modules/twitter_collector.py`
    
    # Import keywords from the root directory
    # To do this, we need to temporarily add the root directory to our Python path
    import sys
    # sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from keywords import KEYWORDS # Assuming your keywords.py has a list named KEYWORDS

    print("Running Twitter Collector as a standalone script...")
    
    # Call your main function
    raw_tweets_df = collect_tweets(keywords=KEYWORDS, limit_per_chunk=100)

    # If the DataFrame is not empty, save it to a CSV file
    if not raw_tweets_df.empty:
        # Define the path to the 'data' folder in the project root
        output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw_tweets.csv')
        
        # Ensure the 'data' directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save the DataFrame to CSV
        raw_tweets_df.to_csv(output_path, index=False)
        
        print(f"Sample data saved to {output_path}")