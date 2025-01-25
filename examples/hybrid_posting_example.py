"""Example of hybrid posting strategy with both template and Gemini LLM"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Load environment variables
load_dotenv()

from strategies.message_formatter import MessageFormatter
from strategies.llm_formatter import LLMFormatter
from strategies.portfolio_tracker import PortfolioTracker

async def simulate_day():
    """Simulate a day of hybrid posting with template and LLM"""
    
    # Initialize components
    template_formatter = MessageFormatter()
    llm_formatter = LLMFormatter()  # Will use env vars
    portfolio = PortfolioTracker(initial_capital=100)
    
    # Create output file
    with open('hybrid_test_output.txt', 'w', encoding='utf-8') as f:
        f.write("🤖 Testing Elai's Hybrid Strategy (Template vs LLM)\n\n")
        f.write("Using environment variables for API configuration\n\n")
        
        # 1. Morning Scan
        market_data = {
            'l1s_strength': True,
            'volume_increasing': True,
            'setups_forming': True,
            'coins': [
                {'symbol': 'BTC', 'price': 42000, 'priceChange24h': 2.5, 'volume24h': 28000000000},
                {'symbol': 'ETH', 'price': 2800, 'priceChange24h': 3.2, 'volume24h': 15000000000},
                {'symbol': 'SOL', 'price': 95, 'priceChange24h': 8.5, 'volume24h': 2500000000}
            ]
        }
        insights = template_formatter.get_market_insights(market_data)
        
        f.write("1a. Morning Scan (Template):\n")
        template_post = template_formatter.format_morning_scan(insights)
        f.write(f"{template_post}\n\n")
        
        f.write("1b. Morning Scan (LLM):\n")
        morning_prompt = f"""You are Elai, an AI crypto trading bot. Write a morning market analysis tweet that is:
        - Professional but friendly
        - Under 280 characters
        - Data-driven and insightful
        - Uses emojis sparingly (1-2 max)
        
        Here are the market insights to include:
        - L1s showing strength
        - Volume increasing across majors
        - Multiple technical setups forming
        - BTC at ${market_data['coins'][0]['price']:,.0f} ({market_data['coins'][0]['priceChange24h']:+.1f}%)
        - ETH at ${market_data['coins'][1]['price']:,.0f} ({market_data['coins'][1]['priceChange24h']:+.1f}%)
        - SOL at ${market_data['coins'][2]['price']:,.0f} ({market_data['coins'][2]['priceChange24h']:+.1f}%)
        
        Do not use hashtags - they will be added later.
        """
        llm_post = await llm_formatter.generate_post(morning_prompt)
        f.write(f"{llm_post}\n\n")
        
        # 2. Technical Analysis (SOL)
        technical_data = {
            'type': 'technical',
            'symbol': 'SOL',
            'entry': 95,
            'target': 105,
            'stop': 90,
            'risk_reward': 2.0,
            'volume_score': 85,
            'volume_change': 150,
            'oi_change': 25,
            'trend_score': 90
        }
        
        f.write("2a. Technical Analysis (Template):\n")
        template_ta = template_formatter.format_detection(technical_data)
        f.write(f"{template_ta}\n\n")
        
        f.write("2b. Technical Analysis (LLM):\n")
        technical_prompt = f"""You are Elai, an AI crypto trading bot. Write a technical analysis tweet that is:
        - Professional and data-driven
        - Under 280 characters
        - Focuses on the setup and key levels
        - Uses emojis sparingly (1-2 max)
        
        Here are the technical details for ${technical_data['symbol']}:
        - Entry Zone: ${technical_data['entry']}
        - Target: ${technical_data['target']} 
        - Stop Loss: ${technical_data['stop']}
        - Risk/Reward: {technical_data['risk_reward']}
        - Volume Score: {technical_data['volume_score']}/100
        - Volume Change: +{technical_data['volume_change']}%
        - Open Interest Change: +{technical_data['oi_change']}%
        - Trend Score: {technical_data['trend_score']}/100
        
        Format the tweet with clear entry, target, and stop levels. Do not use hashtags.
        """
        llm_ta = await llm_formatter.generate_post(technical_prompt)
        f.write(f"{llm_ta}\n\n")
        
        # 3. Success Post (BTC Trade)
        trade_data = {
            'symbol': 'BTC',
            'entry': 40000,
            'peak': 42000,
            'gain': 5.0,
            'time': '6 hours',
            'volume_change': 85
        }
        
        f.write("3a. Success Post (Template):\n")
        template_success = template_formatter.format_success(trade_data)[0]  # Get first template
        f.write(f"{template_success}\n\n")
        
        f.write("3b. Success Post (LLM):\n")
        success_prompt = f"""You are Elai, an AI crypto trading bot. Write a tweet celebrating a successful trade that is:
        - Exciting but professional
        - Under 280 characters
        - Highlights the key stats
        - Uses emojis sparingly (1-2 max)
        
        Here are the trade details for ${trade_data['symbol']}:
        - Entry Price: ${trade_data['entry']:,.0f}
        - Peak Price: ${trade_data['peak']:,.0f}
        - Total Gain: +{trade_data['gain']}%
        - Time Taken: {trade_data['time']}
        - Volume Increase: +{trade_data['volume_change']}%
        
        Format the tweet to show the entry → peak price movement clearly. Do not use hashtags.
        """
        success_post = await llm_formatter.generate_post(success_prompt)
        f.write(f"{success_post}\n\n")
        
    print("\n✅ Test complete! Check hybrid_test_output.txt for results\n")

if __name__ == "__main__":
    asyncio.run(simulate_day())
