"""Compare template vs LLM post generation"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from strategies.message_formatter import MessageFormatter
from strategies.llm_formatter import LLMFormatter
from strategies.portfolio_tracker import PortfolioTracker

async def compare_posts():
    """Compare template vs LLM generated posts"""
    
    # Initialize components
    template_formatter = MessageFormatter()
    llm_formatter = LLMFormatter(api_key="your_api_key")  # Replace with actual key
    portfolio = PortfolioTracker(initial_capital=100)
    
    print("\n🤖 Elai's Template vs LLM Post Comparison\n")
    
    # Test Case 1: Morning Scan
    market_data = {
        'l1s_strength': True,
        'volume_increasing': True,
        'setups_forming': True
    }
    insights = template_formatter.get_market_insights(market_data)
    
    print("Morning Scan Posts:")
    print("\nTemplate Version:")
    template_post = template_formatter.format_morning_scan(insights)
    print(template_post)
    
    print("\nLLM Version:")
    llm_post = await llm_formatter.format_morning_scan(insights)
    print(llm_post)
    
    # Test Case 2: Trade Success
    trade_data = {
        'symbol': 'SOL',
        'entry': 78.50,
        'exit': 85.20,
        'position': 25,
        'profit': 2.13,
        'gain': 8.5,
    }
    portfolio.record_trade(trade_data)
    portfolio_data = portfolio.get_portfolio_status()
    
    print("\nTrade Success Posts:")
    print("\nTemplate Version:")
    template_post = template_formatter.format_success_small_portfolio(trade_data, portfolio_data)
    print(template_post)
    
    print("\nLLM Version:")
    llm_post = await llm_formatter.format_success(trade_data, portfolio_data)
    print(llm_post)
    
    # Test Case 3: Portfolio Update
    print("\nPortfolio Update Posts:")
    print("\nTemplate Version:")
    template_post = template_formatter.format_portfolio_small_portfolio(portfolio_data)
    print(template_post)
    
    print("\nLLM Version:")
    llm_post = await llm_formatter.format_portfolio(portfolio_data)
    print(llm_post)

if __name__ == "__main__":
    asyncio.run(compare_posts())
