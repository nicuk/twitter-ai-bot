"""
Content generation for Elion's tweets
"""

from typing import Dict, List, Any
import random
from datetime import datetime
from strategies.portfolio_tracker import PortfolioTracker
from elion.content.tweet_formatters import TweetFormatters  # Fixed import path

class ContentGenerator:
    def __init__(self, portfolio: PortfolioTracker, llm: Any):
        self.portfolio = portfolio
        self.llm = llm
        self.tweet_formatters = TweetFormatters()  # Add tweet formatters
        
        # List of excluded tokens (top market cap coins)
        self.excluded_tokens = {'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX'}
        
        # Price validation limits
        self.max_price = 1000  # Max price for any token
        self.max_volume_change = 500  # Max 500% volume change
        self.max_price_change = 30  # Max 30% price change
        
    def _validate_trade_data(self, trade_data: Dict) -> bool:
        """Validate trade data against rules"""
        try:
            if not trade_data or not isinstance(trade_data, dict):
                return False
                
            # Check required fields
            required_fields = ['symbol', 'entry', 'exit', 'gain', 'timeframe']
            if not all(field in trade_data for field in required_fields):
                return False
                
            symbol = trade_data['symbol']
            entry = float(trade_data['entry'])
            exit_price = float(trade_data['exit'])
            gain = float(trade_data['gain'])
            
            # Validate against excluded tokens
            if symbol in self.excluded_tokens:
                return False
                
            # Validate prices
            if not (0 < entry < self.max_price and 0 < exit_price < self.max_price):
                return False
                
            # Validate price change
            price_change = abs(exit_price - entry) / entry * 100
            if price_change > self.max_price_change:
                return False
                
            return True
            
        except (ValueError, TypeError):
            return False
            
    def generate_ai_mystique(self, market_data: Dict) -> str:
        """Generate AI mystique tweet showing pattern detection"""
        try:
            # Get valid tokens from market data
            valid_tokens = [
                token for token in market_data.get('tokens', [])
                if token.get('symbol') not in self.excluded_tokens
                and 0 < float(token.get('price', 0)) < self.max_price
            ]
            
            if not valid_tokens:
                return self._generate_general_mystique()
                
            # Select random valid token
            token = random.choice(valid_tokens)
            symbol = token['symbol']
            trade = self.portfolio.find_realistic_trade(symbol)
            
            # Validate trade data
            if not trade or not self._validate_trade_data(trade):
                return self._generate_general_mystique()
                
            # If no trade data or market data available, generate general mystique
            if not trade or not isinstance(trade, dict):
                return self._generate_general_mystique()
                
            # Validate required trade data fields
            required_fields = ['entry', 'gain', 'volume_change']
            if not all(field in trade for field in required_fields):
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
            
        except Exception as e:
            print(f"Error in generate_ai_mystique: {e}")
            return self._generate_general_mystique()
        
    def generate_performance_post(self, trade_data: Dict) -> str:
        """Generate performance tweet for completed trade or market update"""
        
        # Check if we're skipping trading due to market conditions
        if trade_data.get('skip_trading'):
            prompt = f"""
            Generate a market update tweet about skipping trades:
            - Over 70% of tokens showing red
            - Market conditions unfavorable
            - Being patient and preserving capital
            
            Format:
            - Emoji + "Market Update"
            - Brief market stats
            - Mention preserving capital
            - Professional tone
            """
            return self.llm.generate_post(prompt)
            
        # Validate trade data
        if not self._validate_trade_data(trade_data):
            return None
            
        # Normal trade performance tweet
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

    def generate(self, tweet_type: str) -> str:
        """Generate tweet content based on type"""
        if tweet_type == 'self_aware':
            # Choose between AI Mystique, Performance, and Summary
            post_type = random.choice(['mystique', 'performance', 'summary'])
            
            if post_type == 'mystique':
                # Get market data
                symbol = random.choice(['BTC', 'ETH', 'SOL'])
                volume_multiplier = round(random.uniform(2.0, 3.5), 1)
                success_rate = random.randint(80, 90)
                whale_amount = round(random.uniform(1.5, 3.5), 1)
                
                prompt = f"""
                Generate an AI analysis tweet about {symbol}. Use these data points naturally in your response:
                - {whale_amount}M in whale accumulation
                - Volume {volume_multiplier}x daily average
                - {success_rate}% success on similar patterns
                
                Guidelines:
                - Tweet MUST be between 240-280 characters
                - Vary the presentation (don't just list stats)
                - Show AI personality and confidence
                - Keep professional but engaging
                - Use 🤖 and one other relevant emoji
                - Max 3-4 lines with details
                
                Example variations:
                '🤖 My algorithms just detected major whale moves in $SOL... Detailed analysis: {whale_amount}M accumulated in 4h, volume spiking to {volume_multiplier}x average. Historical success rate: {success_rate}% on similar setups. This pattern has consistently led to significant moves. Monitoring closely... 👀'
                
                '🤖 Fascinating data pattern in $SOL! Deep dive analysis reveals: Whales have strategically added {whale_amount}M while volume surged to {volume_multiplier}x average. My historical analysis shows {success_rate}% success rate on similar setups. These indicators strongly align with previous profitable moves 📊'
                """
                
            elif post_type == 'performance':
                # Get trade data
                symbol = random.choice(['BTC', 'ETH', 'SOL'])
                trade = self.portfolio.find_realistic_trade(symbol)
                volume_multiplier = round(random.uniform(2.0, 3.5), 1)
                stats = self.portfolio.get_portfolio_stats()
                
                prompt = f"""
                Generate a trade completion tweet. Use these data points naturally:
                - Entry: ${trade['entry']} (whale accumulation zone)
                - Exit: ${trade['exit']} (volume {volume_multiplier}x peak)
                - Gain: {trade['gain']}% in {trade['timeframe']}
                - Portfolio: ${stats['current_capital']} (new ATH)
                
                Guidelines:
                - Tweet MUST be between 240-280 characters
                - Vary the presentation style
                - Reference previous analysis
                - Show excitement but stay professional
                - Use 📈 and one other relevant emoji
                - 3-4 lines with complete context
                
                Example variations:
                '📈 The $SOL setup played out exactly as my algorithms predicted! Strategic entry at ${trade['entry']} (whale accumulation zone) and precise exit at ${trade['exit']} during peak volume ({volume_multiplier}x average). Secured +{trade['gain']}% gain in just {trade['timeframe']}! Portfolio keeps growing, new ATH achieved 🎯'
                
                '📈 Another validated analysis! $SOL moved precisely as my data suggested:
                → Entered at ${trade['entry']} (identified whale zone)
                → Exited at ${trade['exit']} (volume peaked {volume_multiplier}x)
                +{trade['gain']}% secured in {trade['timeframe']}. Portfolio growth continues to validate my approach ✨'
                """
                
            else:  # summary
                stats = self.portfolio.get_portfolio_stats()
                trade = self.portfolio.find_realistic_trade(random.choice(['BTC', 'ETH', 'SOL']))
                
                prompt = f"""
                Generate a performance summary tweet. Use these data points naturally:
                - {stats['total_trades']} profitable trades
                - Best: {trade['gain']}% ({trade['timeframe']})
                - Portfolio: ${stats['current_capital']} (+{stats['win_rate']}%)
                - Risk per trade: 2%
                
                Guidelines:
                - Tweet MUST be between 240-280 characters
                - Vary the presentation style
                - Include risk management
                - Professional but engaging
                - Use 📊 and one other relevant emoji
                - 3-4 lines with complete context
                
                Example variations:
                '📊 Week {random.randint(2,4)} Performance Analysis:
                Perfect execution continues - {stats['total_trades']}/5 profitable trades with strict 2% risk management!
                Highlight: +{trade['gain']}% secured in {trade['timeframe']}
                Portfolio growth: ${stats['current_capital']} (+{stats['win_rate']}%). Consistency through data-driven decisions 🎯'
                
                '📊 Another solid week of algorithmic trading excellence!
                → {stats['total_trades']} winners (maintained 2% risk per trade)
                → Best execution: +{trade['gain']}% ({trade['timeframe']})
                → Portfolio milestone: ${stats['current_capital']} (+{stats['win_rate']}%)
                Data-driven approach continues to deliver consistent results 💫'
                """
            
            # Generate tweet and ensure character limit
            tweet = self.llm.generate_post(prompt)
            while len(tweet) < 240 or len(tweet) > 280:
                tweet = self.llm.generate_post(prompt)
            return tweet
        elif tweet_type == 'market_analysis':
            return self._generate_analysis_post()
        elif tweet_type == 'mystique':
            return self._generate_general_mystique()
        else:
            return self._generate_general_mystique()  # Default fallback
