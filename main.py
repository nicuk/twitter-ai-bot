"""
Main ELAI script
"""

import os
from dotenv import load_dotenv
from custom_llm import MetaLlamaComponent
from elion.core.elion import Elion

def main():
    """Main entry point"""
    print("Starting ELAI...\n")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize LLM
    api_url = os.getenv('AI_API_URL')
    access_token = os.getenv('AI_ACCESS_TOKEN')
    
    print(f"API URL: {'Set' if api_url else 'Missing'}")
    print(f"Access Token: {'Set' if access_token else 'Missing'}")
    
    llm = MetaLlamaComponent(
        api_key=access_token,
        api_base=api_url
    )
    
    # Initialize ELAI with LLM
    elai = Elion(llm)
    
    # Test tweet generation
    print("\nGenerating market analysis tweet...")
    tweet_type = elai.get_next_tweet_type()
    print(f"Selected tweet type: {tweet_type}")
    
    tweet = elai.generate_tweet(tweet_type)
    
    if tweet:
        print("\nTweet Generated:")
        print(tweet)
        print(f"\nTweets today: {elai.state['tweets_today']}/16")
    else:
        print("No tweet generated - Check if CRYPTORANK_API_KEY is set")

if __name__ == "__main__":
    main()
