"""
Test all three tweet types: volume, trend, and personal
"""
import os
from dotenv import load_dotenv
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy
from custom_llm import GeminiComponent
from elion.elion import Elion
from twitter.api_client import TwitterAPI

def test_volume_tweet():
    """Test volume tweet generation and posting"""
    print("\nTesting VOLUME Tweet:")
    print("=" * 80)
    
    # Initialize components
    llm = GeminiComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    elion = Elion(llm)
    api = TwitterAPI()
    
    try:
        # Generate volume tweet
        tweet = elion.generate_tweet('volume')
        if not tweet:
            print("[X] Failed to generate volume tweet")
            return False
            
        print("[+] Volume tweet generated:")
        print(tweet)
        
        # Post tweet
        response = api.create_tweet(tweet)
        if response:
            print("[+] Volume tweet posted successfully")
            return True
        else:
            print("[X] Failed to post volume tweet")
            return False
            
    except Exception as e:
        print(f"[X] Error in volume tweet: {e}")
        return False

def test_trend_tweet():
    """Test trend tweet generation and posting"""
    print("\nTesting TREND Tweet:")
    print("=" * 80)
    
    # Initialize components
    llm = GeminiComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    elion = Elion(llm)
    api = TwitterAPI()
    
    try:
        # Generate trend tweet
        tweet = elion.generate_tweet('trend')
        if not tweet:
            print("[X] Failed to generate trend tweet")
            return False
            
        print("[+] Trend tweet generated:")
        print(tweet)
        
        # Post tweet
        response = api.create_tweet(tweet)
        if response:
            print("[+] Trend tweet posted successfully")
            return True
        else:
            print("[X] Failed to post trend tweet")
            return False
            
    except Exception as e:
        print(f"[X] Error in trend tweet: {e}")
        return False

def test_twitter_api():
    """Test Twitter API connection"""
    print("\nTesting Twitter API:")
    print("=" * 80)
    
    try:
        api = TwitterAPI()
        # Just initialize the client to check credentials
        print("[+] Twitter API client initialized")
        return True
    except Exception as e:
        print(f"[X] Twitter API error: {e}")
        return False

def test_personal_tweet():
    """Test personal tweet generation"""
    print("\nTesting PERSONAL Tweet:")
    print("=" * 80)
    
    llm = GeminiComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    elion = Elion(llm)
    
    try:
        market_data = elion.get_market_data()
        if not market_data:
            print("[X] No market data for personal tweet")
            return False
            
        tweet = elion.content.generate_ai_mystique(market_data)
        if not tweet:
            print("[X] Failed to generate personal tweet")
            return False
            
        print("[+] Personal tweet generated")
        return True
    except Exception as e:
        print(f"[X] Error generating personal tweet: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting Tweet Tests")
    print("=" * 80)
    
    # Load environment variables
    load_dotenv()
    
    # Test Twitter API first
    if not test_twitter_api():
        print("[X] Twitter API test failed, stopping tests")
        return
        
    # Run tests
    results = {
        'volume': test_volume_tweet(),
        'trend': test_trend_tweet(),
        'personal': test_personal_tweet(),
        'twitter': test_twitter_api()
    }
    
    # Print summary
    print("\nTest Summary:")
    print("=" * 80)
    for test, passed in results.items():
        status = "[+] PASS" if passed else "[X] FAIL"
        print(f"{test.upper()}: {status}")

if __name__ == "__main__":
    main()
