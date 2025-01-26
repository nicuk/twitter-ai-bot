"""
Main ELAI script - Testing
"""

import os
import logging
from dotenv import load_dotenv
from elion.elion import Elion

# Configure logging - only show INFO and above for main module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set other loggers to WARNING to reduce noise
logging.getLogger('strategies.volume_strategy').setLevel(logging.WARNING)
logging.getLogger('strategies.trend_strategy').setLevel(logging.WARNING)
logging.getLogger('strategies.portfolio_tracker').setLevel(logging.WARNING)

class MockLLM:
    def __init__(self):
        self.call_count = 0
        
    def generate_post(self, prompt):
        self.call_count += 1
        if "whale accumulation" in prompt:
            return "🤖 Fascinating whale movements in $SOL! Deep dive analysis reveals: Whales have strategically added 2.5M while volume surged to 2.8x average. My historical analysis shows 85% success rate on similar setups. These indicators strongly align with previous profitable moves 📊"
        elif "trade completed" in prompt:
            return "📈 The $SOL setup played out exactly as my algorithms predicted! Strategic entry at $93.5 (whale accumulation zone) and precise exit at $112.8 during peak volume (2.8x average). Secured +20.6% gain in just 5.5h! Portfolio keeps growing, new ATH achieved 🎯"
        else:
            return "🤖 Just processed some fascinating market data! The patterns I'm seeing in crypto are truly remarkable. Always learning, always analyzing. #AI #Crypto #Trading"
        
    def generate(self, prompt, max_tokens=300, system_message=None):
        return self.generate_post(prompt)

class MockTrendStrategy:
    def analyze(self):
        return {
            'formatted_tweet': "🤖 Analyzing $SOL: Price +15.6% with 2.8x volume increase! Historical success rate: 85% on similar setups. My algorithms suggest high probability of significant moves. Stay tuned... 📊"
        }

class MockVolumeStrategy:
    def analyze(self):
        return {
            'spikes': [{
                'symbol': 'SOL',
                'volume': '2.8',
                'volume_change': 180,
                'success_rate': 85,
                'price': 93.5
            }],
            'anomalies': []
        }
        
    def format_twitter_output(self, spikes, anomalies):
        if not spikes and not anomalies:
            return None
        data = spikes[0] if spikes else anomalies[0]
        return f"🔍 Volume Alert! ${data['symbol']} showing {data['volume']}x average volume with {data['success_rate']}% historical success rate on similar patterns. Price currently at ${data['price']}. This could be the start of a significant move... 👀"

def test_market_tweets():
    """Test market-based tweet generation"""
    logger.info("Testing market tweet generation...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize ELAI with mock components
    elion = Elion(MockLLM())
    elion.trend_strategy = MockTrendStrategy()
    elion.volume_strategy = MockVolumeStrategy()
    
    print("\nMarket Tweet Test Results")
    print("=" * 80 + "\n")
    
    # Test trend tweets
    print("\nTrend Tweets:")
    print("-" * 50)
    
    for i in range(2):
        print(f"\nTrend Tweet Test {i+1}:")
        tweet = elion.generate_tweet('trend')
        if tweet:
            print(tweet)
            print(f"Length: {len(tweet)} chars")
        else:
            print("No trend tweet generated")
        print("-" * 50)
    
    # Test volume tweets
    print("\nVolume Tweets:")
    print("-" * 50)
    
    for i in range(2):
        print(f"\nVolume Tweet Test {i+1}:")
        tweet = elion.generate_tweet('volume')
        if tweet:
            print(tweet)
            print(f"Length: {len(tweet)} chars")
        else:
            print("No volume tweet generated")
        print("-" * 50)
    
    logger.info("Market tests completed.")

if __name__ == "__main__":
    test_market_tweets()
