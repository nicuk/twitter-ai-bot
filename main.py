"""
Main script to run Elion AI
"""

import os
from dotenv import load_dotenv
from custom_llm import MetaLlamaComponent
from elion.elion import Elion
from tweet_history_manager import TweetHistoryManager
from elion.data_sources import CryptoRankAPI
import requests
import json

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize LLM
    api_url = "https://api-user.ai.aitech.io/api/v1/user/products/209/use/chat/completions"
    access_token = os.getenv('AI_ACCESS_TOKEN')
    
    llm = MetaLlamaComponent(
        api_key=access_token,
        api_base=api_url
    )
    
    # Initialize Elion
    elion = Elion(llm)
    history_manager = TweetHistoryManager()
    
    # Generate test tweets
    test_tweets = []
    for _ in range(10):  # Start with 10 tweets
        try:
            # Get next tweet type
            tweet_type = elion.get_next_tweet_type()
            print(f"\nGenerating {tweet_type} tweet...")
            
            # Generate tweet
            tweet = elion.generate_tweet(tweet_type)
            if tweet:
                test_tweets.append({
                    'type': tweet_type,
                    'content': tweet
                })
                print(f"Generated tweet ({tweet_type}):")
                print("-" * 40)
                print(tweet)
                print("-" * 40)
            else:
                print(f"Failed to generate {tweet_type} tweet")
                
        except Exception as e:
            print(f"Error generating tweet: {e}")
            continue
    
    # Save tweets to history
    for tweet in test_tweets:
        history_manager.add_tweet(tweet['content'], tweet['type'])
    
    print(f"\nGenerated {len(test_tweets)} test tweets")
    print("\nTweet type distribution:")
    type_counts = {}
    for tweet in test_tweets:
        type_counts[tweet['type']] = type_counts.get(tweet['type'], 0) + 1
    for tweet_type, count in type_counts.items():
        print(f"- {tweet_type}: {count}")

def test_api():
    api = CryptoRankAPI()
    
    # Test v1 explicitly with all params
    params = {
        'api_key': api.api_key,
        'limit': 10
    }
    
    print("\nTesting v1...")
    v1_response = requests.get('https://api.cryptorank.io/v1/currencies', params=params)
    print(f"V1 Status: {v1_response.status_code}")
    if v1_response.status_code == 200:
        print("Full response:")
        print(json.dumps(v1_response.json(), indent=2)[:500])  # Print first 500 chars
    else:
        print(f"Error: {v1_response.text}")
    
if __name__ == "__main__":
    test_api()
