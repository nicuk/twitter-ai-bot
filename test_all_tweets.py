"""Test all tweet types: trend, volume, and performance"""

import os
import sys
from dotenv import load_dotenv
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy
from custom_llm import GeminiComponent
from elion.elion import Elion
from twitter.api_client import TwitterAPI

# Force UTF-8 encoding for emoji support
sys.stdout.reconfigure(encoding='utf-8')

def test_trend_tweet():
    """Test trend tweet generation"""
    print("\nTesting TREND Tweet:")
    print("=" * 80)
    
    trend_strategy = TrendStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
    trend_data = trend_strategy.analyze()
    
    if not trend_data:
        print("[X] No trend data returned")
        return False
        
    if 'trend_tokens' not in trend_data:
        print("[X] No trend tokens found")
        return False
        
    tweet = trend_strategy.format_twitter_output(trend_data['trend_tokens'])
    if not tweet:
        print("[X] Failed to format trend tweet")
        return False
        
    print("\nTrend Tweet:")
    print("-" * 40)
    print(tweet)
    print(f"Length: {len(tweet)} chars")
    return True

def test_volume_tweet():
    """Test volume tweet generation"""
    print("\nTesting VOLUME Tweet:")
    print("=" * 80)
    
    volume_strategy = VolumeStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
    volume_data = volume_strategy.analyze()
    
    if not volume_data:
        print("[X] No volume data returned")
        return False
        
    spikes = volume_data.get('spikes', [])
    anomalies = volume_data.get('anomalies', [])
    
    if not spikes and not anomalies:
        print("[X] No volume spikes or anomalies found")
        return False
        
    tweet = volume_strategy.format_twitter_output(spikes, anomalies)
    if not tweet:
        print("[X] Failed to format volume tweet")
        return False
        
    print("\nVolume Tweet:")
    print("-" * 40)
    print(tweet)
    print(f"Length: {len(tweet)} chars")
    return True

def test_performance_tweet():
    """Test performance tweet generation"""
    print("\nTesting PERFORMANCE Tweet:")
    print("=" * 80)
    
    # Initialize components
    llm = GeminiComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    elion = Elion(llm)
    
    # Get market data first
    print("\nGetting market data...")
    market_data = elion.get_market_data()
    if not market_data:
        print("[X] Failed to get market data")
        return False
    
    # Get trade data
    print("\nGetting latest trade data...")
    trade_data = elion.get_latest_trade()
    
    if not trade_data:
        print("[X] No trade data available")
        return False
        
    print("\nTrade Data:")
    print("-" * 40)
    for key, value in trade_data.items():
        print(f"{key}: {value}")
    
    # Generate tweet
    print("\nGenerating tweet...")
    content = elion.content.generate_performance_post(trade_data)
    
    if not content:
        print("[X] Failed to generate performance tweet")
        return False
        
    print("\nPerformance Tweet:")
    print("=" * 40)
    print(content)
    print("-" * 40)
    print(f"Tweet length: {len(content)} chars")
    
    return True

def main():
    """Run all tests"""
    # Load environment variables
    load_dotenv()
    
    # Test each tweet type
    trend_ok = test_trend_tweet()
    volume_ok = test_volume_tweet()
    performance_ok = test_performance_tweet()
    
    # Print summary
    print("\nTest Summary:")
    print("=" * 80)
    print(f"Trend Tweet: {'✓' if trend_ok else 'X'}")
    print(f"Volume Tweet: {'✓' if volume_ok else 'X'}")
    print(f"Performance Tweet: {'✓' if performance_ok else 'X'}")

if __name__ == "__main__":
    main()
