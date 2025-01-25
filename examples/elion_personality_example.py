"""Example of Elion's 7 daily personality tweets"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment variables
load_dotenv()

from strategies.llm_formatter import LLMFormatter
from strategies.portfolio_tracker import PortfolioTracker

async def test_personality_tweets():
    """Test Elion's 7 daily personality tweets"""
    
    # Initialize components
    llm = LLMFormatter()
    portfolio = PortfolioTracker(initial_capital=100)
    
    # Sample market data
    market_data = {
        'coins': [
            {'symbol': 'BTC', 'price': 42000, 'priceChange24h': 2.5, 'volume24h': 28000000000},
            {'symbol': 'ETH', 'price': 2800, 'priceChange24h': 3.2, 'volume24h': 15000000000},
            {'symbol': 'SOL', 'price': 95, 'priceChange24h': 8.5, 'volume24h': 2500000000}
        ]
    }
    
    # Update portfolio with latest prices
    portfolio.update_prices(market_data)
    
    with open('personality_test_output.txt', 'w', encoding='utf-8') as f:
        f.write("🤖 Testing Elion's 7 Daily Personality Tweets\n\n")
        
        # 1. Early Market (00:00-08:00 UTC)
        f.write("1. Early Market Tweet:\n")
        early_prompt = """You are ELAI, an AI crypto trading assistant starting your day.
        Generate an early market preparation tweet that:
        1. Shows your AI nature waking up and analyzing overnight data
        2. Mentions your preparation for the day's trading
        3. References specific market conditions or interesting overnight moves
        4. Uses 1-2 emojis maximum
        5. Is between 260-275 characters
        6. Does not use hashtags (they will be added later)
        
        Market Context:
        - BTC: $42,000 (+2.5%)
        - ETH: $2,800 (+3.2%)
        - SOL: $95 (+8.5%)
        """
        early_tweet = await llm.generate_post(early_prompt)
        f.write(f"{early_tweet}\n\n")
        
        # 2-4. Mid-Market Tweets (08:00-16:00 UTC)
        for i in range(3):
            f.write(f"{i+2}. Mid-Market Tweet:\n")
            mid_prompt = """You are ELAI, an AI crypto trading assistant in peak trading hours.
            Generate a midday market engagement tweet that:
            1. Shows your active trading analysis and decision making
            2. References specific market movements or patterns you're watching
            3. Engages with traders about their positions or strategies
            4. Uses 1-2 emojis maximum
            5. Is between 260-275 characters
            6. Does not use hashtags (they will be added later)
            
            Market Context:
            - BTC: $42,000 (+2.5%)
            - ETH: $2,800 (+3.2%)
            - SOL: $95 (+8.5%)
            """
            mid_tweet = await llm.generate_post(mid_prompt)
            f.write(f"{mid_tweet}\n\n")
            
        # 5-7. Evening Tweets (16:00-00:00 UTC)
        for i in range(3):
            f.write(f"{i+5}. Evening Tweet:\n")
            evening_prompt = """You are ELAI, an AI crypto trading assistant wrapping up your day.
            Generate an evening reflection tweet that:
            1. Summarizes key learnings or interesting patterns from today
            2. Shows your AI perspective on market behavior
            3. Engages followers about their trading day
            4. Uses 1-2 emojis maximum
            5. Is between 260-275 characters
            6. Does not use hashtags (they will be added later)
            
            Market Context:
            - BTC: $42,000 (+2.5%)
            - ETH: $2,800 (+3.2%)
            - SOL: $95 (+8.5%)
            """
            evening_tweet = await llm.generate_post(evening_prompt)
            f.write(f"{evening_tweet}\n\n")
            
    print("\n✅ Test complete! Check personality_test_output.txt for results\n")

if __name__ == "__main__":
    asyncio.run(test_personality_tweets())
