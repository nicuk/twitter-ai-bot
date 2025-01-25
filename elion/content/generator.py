"""
Content generation for Elion's tweets
"""

from typing import Dict, List
import random
from datetime import datetime
from strategies.portfolio_tracker import PortfolioTracker
from strategies.llm_formatter import LLMFormatter

class ContentGenerator:
    def __init__(self, portfolio: PortfolioTracker, llm: LLMFormatter):
        self.portfolio = portfolio
        self.llm = llm
        
    def generate_ai_mystique(self, market_data: Dict) -> str:
        """Generate AI mystique tweet showing pattern detection"""
        # Find potential trade setup
        symbol = random.choice(['SOL', 'ETH', 'BTC'])
        trade = self.portfolio.find_realistic_trade(symbol)
        
        if not trade:
            return self._generate_general_mystique()
            
        # Format prompt for LLM
        prompt = f"""
        Generate an AI mystique tweet about detecting a pattern in {symbol}.
        - Entry zone: ${trade['entry']} (whale accumulation)
        - Previous similar patterns averaged {trade['gain']}% gains
        - Volume increased by {trade['volume_change']}%
        - Keep mysterious but data-driven
        - No price predictions
        - Format: emoji + analysis
        """
        
        return self.llm.generate_post(prompt)
        
    def generate_performance_post(self, trade_data: Dict) -> str:
        """Generate performance tweet for completed trade"""
        # Format prompt for LLM
        prompt = f"""
        Generate a performance tweet for a completed trade:
        Symbol: {trade_data['symbol']}
        Entry: ${trade_data['entry']} (whale zone)
        Exit: ${trade_data['exit']} (volume peak)
        Gain: {trade_data['gain']}%
        Timeframe: {trade_data['timeframe']}
        Portfolio: ${self.portfolio.current_capital}
        
        Format:
        - Emoji + "Trade completed"
        - Entry/exit details
        - Gain and timeframe
        - Current portfolio value
        - Keep professional
        """
        
        return self.llm.generate_post(prompt)
        
    def generate_summary_post(self) -> str:
        """Generate daily summary tweet"""
        summary = self.portfolio.get_daily_summary()
        
        if not summary['daily_trades']:
            return self._generate_analysis_post()
            
        # Format prompt for LLM
        prompt = f"""
        Generate a daily summary tweet:
        - {summary['daily_trades']} completed trades
        - Portfolio: ${summary['current_balance']}
        - Daily gain: {summary['daily_gain']}%
        - Win rate: {summary['win_rate']}%
        - Best trade: {summary['best_trade']['symbol']} +{summary['best_trade']['gain']}%
        
        Format:
        - Emoji + "Daily Report"
        - Key stats
        - Professional tone
        - Focus on consistency
        """
        
        return self.llm.generate_post(prompt)
        
    def _generate_general_mystique(self) -> str:
        """Generate general AI mystique when no trade setup found"""
        prompt = """
        Generate an AI mystique tweet about market analysis:
        - Processing blockchain data
        - Volume analysis
        - No specific predictions
        - Keep mysterious but technical
        """
        
        return self.llm.generate_post(prompt)
        
    def _generate_analysis_post(self) -> str:
        """Generate market analysis when no trades completed"""
        prompt = """
        Generate a market analysis tweet:
        - Technical indicators
        - Volume patterns
        - No specific predictions
        - Professional tone
        """
        
        return self.llm.generate_post(prompt)
        
    def generate_first_day_mystique(self) -> str:
        """Generate first day AI mystique tweet"""
        prompt = """
        Generate a first-day introduction tweet for an AI trading bot:
        - Initializing systems
        - Processing market data
        - Setting up analysis
        - Professional tone
        - No specific predictions
        - Use 🤖 emoji
        """
        return self.llm.generate_post(prompt)
        
    def generate_first_day_intro(self) -> str:
        """Generate first day introduction tweet"""
        prompt = f"""
        Generate an introduction tweet for an AI trading bot:
        - Starting portfolio: ${self.portfolio.initial_capital}
        - Focus on data-driven approach
        - Mention risk management (2% per trade)
        - Professional tone
        - Use 📊 emoji
        """
        return self.llm.generate_post(prompt)
