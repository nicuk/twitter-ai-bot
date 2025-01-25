"""Example of Elion's structured daily tweets"""

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

async def test_structured_tweets():
    """Test Elion's structured daily tweets"""
    
    # Initialize components
    llm = LLMFormatter()
    portfolio = PortfolioTracker(initial_capital=100)
    
    # Sample market and portfolio data
    market_data = {
        'coins': [
            {'symbol': 'BTC', 'price': 42000, 'priceChange24h': 2.5, 'volume24h': 28000000000},
            {'symbol': 'ETH', 'price': 2800, 'priceChange24h': 3.2, 'volume24h': 15000000000},
            {'symbol': 'SOL', 'price': 95, 'priceChange24h': 8.5, 'volume24h': 2500000000}
        ]
    }
    
    portfolio_data = {
        'starting_balance': 100,
        'current_balance': 150,
        'total_trades': 15,
        'winning_trades': 12,
        'best_trade': {'symbol': 'SOL', 'gain': 8.5}
    }
    
    with open('structured_test_output.txt', 'w', encoding='utf-8') as f:
        f.write("🤖 Testing Elion's Structured Daily Tweets\n\n")
        
        # 1-2. AI Mystique Posts
        f.write("1. Morning AI Mystique:\n")
        mystique1_prompt = """You are ELAI, an AI crypto trading assistant.
        Generate a morning market analysis that focuses on your AI capabilities:
        1. Mention your overnight pattern analysis
        2. Reference specific data points you've processed
        3. Hint at potential setups forming
        4. Use 🤖 emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Market Context:
        - Processed 2.5M price points
        - Detected 3 high-probability setups
        - BTC showing bullish divergence
        - ETH volume spike at key level
        """
        mystique1 = await llm.generate_post(mystique1_prompt)
        f.write(f"{mystique1}\n\n")
        
        f.write("2. Mid-day AI Mystique:\n")
        mystique2_prompt = """You are ELAI, an AI crypto trading assistant.
        Generate a tweet showcasing your unique analysis:
        1. Reference your real-time pattern detection
        2. Mention specific indicators only AI could process
        3. Show confidence in your analysis
        4. Use ✨ emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Analysis Context:
        - Processing 150k transactions/minute
        - Detected unusual whale movement
        - Cross-chain correlation at 85%
        - Volume profile showing accumulation
        """
        mystique2 = await llm.generate_post(mystique2_prompt)
        f.write(f"{mystique2}\n\n")
        
        # 3-5. Performance Posts
        f.write("3. First Performance Post:\n")
        perf1_prompt = f"""You are ELAI, an AI crypto trading assistant.
        Generate a tweet about a confirmed trade:
        1. Show entry and exit prices
        2. Include time taken
        3. Reference portfolio growth
        4. Use 📈 emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Trade Details:
        - Symbol: SOL
        - Entry: $87.5
        - Exit: $95
        - Gain: +8.5%
        - Time: 4 hours
        - Portfolio now: ${portfolio_data['current_balance']}
        """
        perf1 = await llm.generate_post(perf1_prompt)
        f.write(f"{perf1}\n\n")
        
        f.write("4. Second Performance Post:\n")
        perf2_prompt = f"""You are ELAI, an AI crypto trading assistant.
        Generate a tweet about your trading accuracy:
        1. Show win rate
        2. Reference total trades
        3. Include portfolio growth
        4. Use 🎯 emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Stats:
        - Trades: {portfolio_data['total_trades']}
        - Wins: {portfolio_data['winning_trades']}
        - Win Rate: {(portfolio_data['winning_trades']/portfolio_data['total_trades'])*100:.1f}%
        - Starting: ${portfolio_data['starting_balance']}
        - Current: ${portfolio_data['current_balance']}
        """
        perf2 = await llm.generate_post(perf2_prompt)
        f.write(f"{perf2}\n\n")
        
        f.write("5. Third Performance Post:\n")
        perf3_prompt = f"""You are ELAI, an AI crypto trading assistant.
        Generate a tweet about a new setup forming:
        1. Reference previous success
        2. Show specific levels
        3. Keep it verifiable
        4. Use 🔍 emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Setup Details:
        - Symbol: ETH
        - Current: $2,800
        - Key Level: $2,850
        - Volume: +120%
        - Similar to previous +3.2% trade
        """
        perf3 = await llm.generate_post(perf3_prompt)
        f.write(f"{perf3}\n\n")
        
        # 6-7. Success/Summary Posts
        f.write("6. First Summary Post:\n")
        summary1_prompt = f"""You are ELAI, an AI crypto trading assistant.
        Generate a tweet summarizing today's success:
        1. Reference best trade
        2. Show portfolio growth
        3. Keep it verifiable
        4. Use 📊 emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Day Summary:
        - Best: SOL +8.5%
        - Portfolio: ${portfolio_data['current_balance']}
        - Growth: +{((portfolio_data['current_balance']-portfolio_data['starting_balance'])/portfolio_data['starting_balance'])*100:.1f}%
        - Trades: {portfolio_data['total_trades']}
        """
        summary1 = await llm.generate_post(summary1_prompt)
        f.write(f"{summary1}\n\n")
        
        f.write("7. Final Summary Post:\n")
        summary2_prompt = f"""You are ELAI, an AI crypto trading assistant.
        Generate a final tweet for the day:
        1. Show consistent growth
        2. Reference tomorrow's preparation
        3. Keep it professional
        4. Use 🤖 emoji only
        5. Keep under 280 chars
        6. No hashtags
        
        Overall Summary:
        - Started: ${portfolio_data['starting_balance']}
        - Now: ${portfolio_data['current_balance']}
        - Growth: +{((portfolio_data['current_balance']-portfolio_data['starting_balance'])/portfolio_data['starting_balance'])*100:.1f}%
        - Win Rate: {(portfolio_data['winning_trades']/portfolio_data['total_trades'])*100:.1f}%
        """
        summary2 = await llm.generate_post(summary2_prompt)
        f.write(f"{summary2}\n\n")
            
    print("\n✅ Test complete! Check structured_test_output.txt for results\n")

if __name__ == "__main__":
    asyncio.run(test_structured_tweets())
