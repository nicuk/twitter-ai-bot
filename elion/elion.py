"""
Core ELAI class - Streamlined for better maintainability
"""

from datetime import datetime, timedelta
import random
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import os

from elion.content.generator import ContentGenerator
from elion.personality.traits import PersonalityManager
from elion.content.tweet_formatters import TweetFormatters
from strategies.trend_strategy import TrendStrategy
from strategies.volume_strategy import VolumeStrategy
from strategies.portfolio_tracker import PortfolioTracker

class Elion:
    """ELAI Agent for Crypto Twitter - Core functionality"""
    
    def __init__(self, llm: Any):
        """Initialize ELAI with core components"""
        # Store LLM
        self.llm = llm
        
        # Initialize components
        self.personality = PersonalityManager()
        self.tweet_formatters = TweetFormatters()
        
        # Initialize market analyzers with API key
        api_key = os.getenv('CRYPTORANK_API_KEY')
        self.trend_strategy = TrendStrategy(api_key)
        self.volume_strategy = VolumeStrategy(api_key, llm=self.llm)
        
        # Initialize portfolio tracker with real market data
        self.portfolio = PortfolioTracker(initial_capital=100, api_key=api_key)
        
        # Initialize content generator with portfolio and LLM
        self.content = ContentGenerator(self.portfolio, self.llm)
        
        # Initialize state
        self.state = {
            'last_tweet_time': None,
            'tweets_today': 0,
            'last_strategy': 'volume',  # Start with trend next
            'trend_tokens': [],  # Store filtered trend tokens
            'volume_tokens': [],  # Store filtered volume tokens
            'used_tokens': set(),  # Track used tokens to avoid repetition
            'last_reset': datetime.now().date()  # Track when to reset used tokens
        }
        
        # Tweet type weights (out of 100)
        self.tweet_weights = {
            'trend': 40,  # Market trend analysis
            'volume': 30,  # Volume analysis
            'mystique': 20,  # AI mystique
            'personal': 10  # Personal/engagement
        }
        
    def _get_next_tweet_type(self) -> str:
        """Get next tweet type based on weights"""
        # Get available types
        types = list(self.tweet_weights.keys())
        weights = [self.tweet_weights[t] for t in types]
        
        # Use last strategy to influence weights
        if self.state['last_strategy'] in types:
            idx = types.index(self.state['last_strategy'])
            weights[idx] *= 0.5  # Reduce weight of last used strategy
            
        # Normalize weights
        total = sum(weights)
        weights = [w/total for w in weights]
        
        # Choose type
        return random.choices(types, weights=weights)[0]
    
    def filter_used_tokens(self, tokens):
        """Filter out previously used tokens"""
        if not tokens:
            return tokens
            
        filtered = []
        for token in tokens:
            symbol = token.get('symbol', '').upper()
            if symbol and symbol not in self.state['used_tokens']:
                filtered.append(token)
                self.state['used_tokens'].add(symbol)
                
        return filtered if filtered else tokens  # Fall back to all tokens if all used
    
    def get_market_data(self) -> Dict:
        """Get current market data from strategies"""
        try:
            # Get trend data
            trend_data = self.trend_strategy.analyze()
            if trend_data and 'trend_tokens' in trend_data:
                self.state['trend_tokens'] = trend_data['trend_tokens']
                
            # Get volume data
            volume_data = self.volume_strategy.analyze()
            if volume_data and ('spikes' in volume_data or 'anomalies' in volume_data):
                self.state['volume_tokens'] = volume_data.get('spikes', []) + volume_data.get('anomalies', [])
                
            # Combine data
            market_data = {
                'trend': trend_data if trend_data else {},
                'volume': volume_data if volume_data else {},
                'portfolio': self.portfolio.get_portfolio_stats()
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error getting market data: {e}")
            return {}
            
    def get_latest_trade(self) -> Optional[Dict]:
        """Get latest trade data for performance posts"""
        try:
            # Find potential trade in trending tokens
            for token in self.state['trend_tokens']:
                symbol = token.get('symbol')
                if not symbol or symbol in self.state['used_tokens']:
                    continue
                    
                trade = self.portfolio.find_realistic_trade(symbol)
                if trade:
                    self.state['used_tokens'].add(symbol)
                    return trade
                    
            # Try volume tokens if no trend trades found
            for token in self.state['volume_tokens']:
                symbol = token.get('symbol')
                if not symbol or symbol in self.state['used_tokens']:
                    continue
                    
                trade = self.portfolio.find_realistic_trade(symbol)
                if trade:
                    self.state['used_tokens'].add(symbol)
                    return trade
                    
            return None
            
        except Exception as e:
            print(f"Error getting latest trade: {e}")
            return None
            
    def format_trend_output(self, tokens):
        """Format trend data into a tweet"""
        if not tokens:
            return None
        token = tokens[0]  # Use first token
        return f"🤖 Analyzing $SOL: Price +{token['price_change']}% with {token['volume']}x volume increase! Historical success rate: {token['success_rate']}% on similar setups. My algorithms suggest high probability of significant moves. Stay tuned... 📊"

    def format_volume_output(self, spikes, anomalies):
        """Format volume data into a tweet"""
        data = spikes[0] if spikes else anomalies[0]  # Use first item
        return f"🔍 Volume Alert! $SOL showing {data['volume']}x average volume with {data['success_rate']}% historical success rate on similar patterns. Price currently at ${data['price']}. This could be the start of a significant move... 👀"

    def format_tweet(self, tweet_type: str, market_data: Dict) -> str:
        """Format a tweet using cached market data"""
        try:
            # Get personality trait
            trait = self.personality.get_trait()
            
            # Format tweet based on type
            if tweet_type == 'trend':
                return self.tweet_formatters.format_trend_insight(market_data['trend'], trait)
            elif tweet_type == 'volume':
                return self.tweet_formatters.format_volume_insight(market_data['volume'], trait)
            else:
                return self.tweet_formatters.format_personal(trait)
                
        except Exception as e:
            print(f"Error formatting {tweet_type} tweet: {e}")
            return None
            
    def generate_tweet(self, tweet_type: str = None) -> Optional[str]:
        """Generate a tweet of the specified type"""
        try:
            # Reset used tokens daily
            today = datetime.now().date()
            if today > self.state['last_reset']:
                self.state['used_tokens'].clear()
                self.state['last_reset'] = today
                
            # Get tweet type if not specified
            if not tweet_type:
                tweet_type = self._get_next_tweet_type()
                
            tweet = None
            
            # Handle trend tweets
            if tweet_type == 'trend':
                try:
                    trend_data = self.trend_strategy.analyze()
                    if trend_data:
                        tweet = self.tweet_formatters.format_trend_insight(trend_data, self.personality.get_trait())
                except Exception as e:
                    print(f"Error in trend strategy: {e}")
                    tweet_type = 'personal'  # Fallback to personal
                    
            # Handle volume tweets
            if tweet_type == 'volume':
                try:
                    volume_data = self.volume_strategy.analyze()
                    if volume_data:
                        tweet = self.tweet_formatters.format_volume_insight(volume_data, self.personality.get_trait())
                except Exception as e:
                    print(f"Error in volume strategy: {e}")
                    tweet_type = 'personal'  # Fallback to personal
                    
            # Handle personal tweets
            if tweet_type == 'personal':
                try:
                    tweet = self.content.generate('self_aware')  # Already formatted by generator
                    if not tweet:
                        print("Failed to generate personal tweet")
                        return None
                except Exception as e:
                    print(f"Error generating personal tweet: {e}")
                    return None
                    
            # Only update state if tweet was successfully generated
            if tweet:
                self.state['last_strategy'] = tweet_type
                self.state['last_tweet_time'] = datetime.now()
                self.state['tweets_today'] += 1
                return tweet
                
            return None
                
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def engage_with_community(self) -> Optional[str]:
        """Generate a community engagement tweet"""
        try:
            return self.content.generate('self_aware')
        except Exception as e:
            print(f"Error generating engagement tweet: {e}")
            return None
