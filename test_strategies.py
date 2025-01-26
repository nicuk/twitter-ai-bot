"""Test volume and trend strategies independently"""

import os
from dotenv import load_dotenv
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy
from custom_llm import GeminiComponent

def test_volume_strategy():
    """Test volume strategy"""
    print("\n=== Testing Volume Strategy ===")
    
    # Initialize volume strategy
    api_key = os.getenv('CRYPTORANK_API_KEY')
    llm = GeminiComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    volume_strategy = VolumeStrategy(api_key, llm=llm)
    
    try:
        # Get volume data
        print("\nAnalyzing volume data...")
        volume_data = volume_strategy.analyze()
        
        if volume_data:
            print("\nVolume Data:")
            print(f"Found {len(volume_data.get('spikes', []))} spikes")
            print(f"Found {len(volume_data.get('anomalies', []))} anomalies")
            
            # Generate tweet
            print("\nGenerating tweet...")
            tweet = volume_strategy.format_twitter_output(
                volume_data.get('spikes', []),
                volume_data.get('anomalies', [])
            )
            print("\nTweet Content:")
            print("-" * 50)
            print(tweet)
            print("-" * 50)
            print(f"Character count: {len(tweet)}")
        else:
            print("No volume data found")
            
    except Exception as e:
        print(f"Error testing volume strategy: {e}")

def test_trend_strategy():
    """Test trend strategy"""
    print("\n=== Testing Trend Strategy ===")
    
    try:
        # Initialize trend strategy
        from strategies.trend_strategy import TrendStrategy
        trend_strategy = TrendStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
        trend_data = trend_strategy.analyze()
        
        if trend_data and trend_data.get('trend_tokens'):
            tweet = trend_strategy.format_twitter_output(trend_data['trend_tokens'])
            print("\nTrend Tweet:")
            print("-" * 40)
            print(tweet)
            print(f"Length: {len(tweet)} chars")
            return True
        else:
            print("[X] No trend tokens found")
            return False
            
    except Exception as e:
        print(f"Error testing trend strategy: {e}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Test both strategies
    test_volume_strategy()
    test_trend_strategy()
