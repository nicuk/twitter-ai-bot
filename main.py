"""
Main ELAI script
"""

import os
from dotenv import load_dotenv
from elion.core.elion import Elion

def main():
    """Main entry point"""
    print("Starting ELAI...\n")
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    
    # Initialize ELAI
    elai = Elion(api_key)
    
    # Test personal tweets
    print("Generating personal tweet...")
    tweet = elai.generate_tweet('personal')
    
    if tweet:
        print("\nTweet Generated:")
        print(tweet)
        print(f"\nTweets today: {elai.state['tweets_today']}/16")
    else:
        print("No personal tweet generated")

if __name__ == "__main__":
    main()
