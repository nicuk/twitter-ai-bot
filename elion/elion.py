"""
Core ELAI class - Streamlined for better maintainability
"""

from datetime import datetime, timedelta
import random
from typing import Dict, Optional, Any
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

from elion.content.generator import ContentGenerator
from elion.personality.traits import PersonalityManager
from elion.content.tweet_formatters import TweetFormatters
from strategies.trend_strategy import TrendStrategy
from strategies.volume_strategy import VolumeStrategy
from strategies.portfolio_tracker import PortfolioTracker
from elion.token_monitor import TokenMonitor

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
        self.portfolio_tracker = PortfolioTracker(initial_capital=100, api_key=api_key)
        
        # Initialize token monitor
        self.token_monitor = TokenMonitor(api_key)
        
        # Initialize content generator with portfolio and LLM
        self.content = ContentGenerator(self.portfolio_tracker, self.llm)
        
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
        
        # List of excluded tokens (top market cap coins)
        self.excluded_tokens = {'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX'}
        
        # Price validation limits
        self.max_price = 1000  # Max price for any token
        self.max_volume_change = 500  # Max 500% volume change
        self.max_price_change = 30  # Max 30% price change
        self.min_volume = 1000000  # $1M minimum volume
        
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
    
    def _validate_token(self, token: Dict) -> bool:
        """Validate token data against rules"""
        try:
            if not token or not isinstance(token, dict):
                return False
                
            symbol = token.get('symbol')
            if not symbol or symbol in self.excluded_tokens:
                return False
                
            # Price validation
            price = float(token.get('price', 0))
            if not (0 < price < self.max_price):
                return False
                
            # Volume validation
            volume = float(token.get('volume24h', 0))
            if volume < self.min_volume:
                return False
                
            # Volume change validation
            volume_change = float(token.get('volumeChange24h', 0))
            if not (-100 <= volume_change <= self.max_volume_change):
                return False
                
            # Price change validation
            price_change = float(token.get('priceChange24h', 0))
            if abs(price_change) > self.max_price_change:
                return False
                
            return True
            
        except (ValueError, TypeError):
            return False
            
    def get_market_data(self) -> Dict:
        """Get combined market data from all strategies"""
        try:
            # Get trend data
            trend_data = self.trend_strategy.analyze()
            
            # Get volume data
            volume_data = self.volume_strategy.analyze()
            
            # Get portfolio data
            portfolio_data = self.portfolio_tracker.get_portfolio_summary()
            
            # Track tokens while getting market data
            for token in trend_data.get('trend_tokens', []):
                if 'symbol' in token:
                    self.token_monitor.track_token(
                        token['symbol'],
                        price=token.get('price'),
                        volume=token.get('volume24h')
                    )
            
            # Combine all data
            market_data = {
                'trend': trend_data,
                'volume': volume_data,
                'portfolio': portfolio_data,
                'timestamp': datetime.now()
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
            
    def get_latest_trade(self) -> Optional[Dict]:
        """Get latest trade data for performance posts"""
        try:
            # Find potential trade in trending tokens
            for token in self.state['trend_tokens']:
                if not self._validate_token(token):
                    continue
                    
                symbol = token.get('symbol')
                if symbol in self.state['used_tokens']:
                    continue
                    
                trade = self.portfolio_tracker.find_realistic_trade(symbol)
                if trade:
                    self.state['used_tokens'].add(symbol)
                    return trade
                    
            # Try volume tokens if no trend trades found
            for token in self.state['volume_tokens']:
                if not self._validate_token(token):
                    continue
                    
                symbol = token.get('symbol')
                if symbol in self.state['used_tokens']:
                    continue
                    
                trade = self.portfolio_tracker.find_realistic_trade(symbol)
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
        symbol = token.get('symbol', '')
        if not symbol or not self._validate_token(token):
            return None
            
        return f"🤖 Analyzing ${symbol}: Price +{token['price_change']}% with {token['volume']}x volume increase! Historical success rate: {token['success_rate']}% on similar setups. My algorithms suggest high probability of significant moves. Stay tuned... 📊"

    def format_volume_output(self, spikes, anomalies):
        """Format volume data into a tweet"""
        data = spikes[0] if spikes else anomalies[0]  # Use first item
        symbol = data.get('symbol', '')
        if not symbol or not self._validate_token(data):
            return None
            
        return f"🔍 Volume Alert! ${symbol} showing {data['volume']}x average volume with {data['success_rate']}% historical success rate on similar patterns. Price currently at ${data['price']}. This could be the start of a significant move... 👀"

    def format_tweet(self, tweet_type: str, market_data: Dict, variant: str = 'A') -> str:
        """Format a tweet using market data"""
        try:
            # Get personality trait
            trait = self.personality.get_trait()
            
            # Core A/B formats
            if tweet_type in ['performance_compare', 'volume_breakout', 'trend_momentum',
                            'winners_recap', 'vmc_alert', 'pattern_alert']:
                # Get method from tweet_formatters
                method_name = f'format_{tweet_type}'
                if hasattr(self.tweet_formatters, method_name):
                    format_method = getattr(self.tweet_formatters, method_name)
                    return format_method(market_data, variant=variant)
                
            # Additional types
            elif tweet_type == 'self_aware':
                return self.tweet_formatters.format_self_aware(trait)
            elif tweet_type == 'alpha':
                return self.tweet_formatters.format_alpha(market_data, trait)
            elif tweet_type == 'personal':
                return self.tweet_formatters.format_personal(trait)
            elif tweet_type == 'volume_alert':
                return self.tweet_formatters.format_volume_alert(market_data, trait)
            elif tweet_type == 'performance_update':
                return self.tweet_formatters.format_performance_update(market_data, trait)
            else:
                logger.error(f"Unknown tweet type: {tweet_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error formatting {tweet_type} tweet: {e}")
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
