"""
Core ELAI class - Streamlined for better maintainability
"""

from datetime import datetime, timedelta
import random
from typing import Optional
from dotenv import load_dotenv
import os

from custom_llm import MetaLlamaComponent
from strategies.trend_strategy import TrendStrategy
from strategies.volume_strategy import VolumeStrategy
from elion.personality.traits import PersonalityManager
from elion.content.generator import ContentGenerator

class Elion:
    """ELAI Agent for Crypto Twitter - Core functionality"""
    
    def __init__(self, llm: MetaLlamaComponent):
        """Initialize ELAI with core components"""
        # Load API keys
        load_dotenv()
        self.api_key = os.getenv('CRYPTORANK_API_KEY')
        
        # Store LLM
        self.llm = llm
        
        # Initialize strategies
        self.trend_strategy = TrendStrategy(self.api_key)
        self.volume_strategy = VolumeStrategy(self.api_key)
        self.personality = PersonalityManager()
        self.content_generator = ContentGenerator(self.personality, self.llm)
        
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
            'trend': 35,    # Market trend analysis
            'volume': 35,   # Volume analysis
            'personal': 30  # Personality-driven tweets
        }
        
    def get_next_tweet_type(self):
        """Determine next tweet type based on weights and last tweet"""
        # Reset daily tweet count and used tokens if needed
        now = datetime.now()
        if self.state['last_tweet_time']:
            last_tweet_day = self.state['last_tweet_time'].date()
            if now.date() > last_tweet_day:
                self.state['tweets_today'] = 0
                # Reset used tokens list at start of day
                if now.date() > self.state['last_reset']:
                    self.state['used_tokens'] = set()
                    self.state['last_reset'] = now.date()
        
        # Don't exceed 16 tweets per day
        if self.state['tweets_today'] >= 16:
            return None
            
        # Get weighted random tweet type
        choices = []
        weights = []
        for tweet_type, weight in self.tweet_weights.items():
            choices.append(tweet_type)
            # Adjust weight based on last tweet type
            if self.state['last_strategy'] == tweet_type:
                weights.append(weight * 0.5)  # Reduce chance of same type
            else:
                weights.append(weight)
                
        return random.choices(choices, weights=weights, k=1)[0]
    
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
    
    def generate_tweet(self, tweet_type: str = None) -> Optional[str]:
        """Generate a tweet based on type or weights"""
        try:
            # Get tweet type if not specified
            if not tweet_type:
                tweet_type = self.get_next_tweet_type()
            
            # Generate tweet based on type
            tweet = None
            if tweet_type == 'trend':
                # Get trend analysis and update state
                trend_data = self.trend_strategy.analyze()
                if 'trend_tokens' in trend_data:
                    # Filter out previously used tokens
                    trend_data['trend_tokens'] = self.filter_used_tokens(trend_data['trend_tokens'])
                    self.state['trend_tokens'] = trend_data['trend_tokens']
                    self.content_generator.update_recent_tokens(trend_data['trend_tokens'])
                tweet = self.trend_strategy.generate_tweet()
                
            elif tweet_type == 'volume':
                # Get volume analysis and update state
                volume_data = self.volume_strategy.analyze()
                if 'volume_tokens' in volume_data:
                    # Filter out previously used tokens
                    volume_data['volume_tokens'] = self.filter_used_tokens(volume_data['volume_tokens'])
                    self.state['volume_tokens'] = volume_data['volume_tokens']
                    self.content_generator.update_recent_tokens(volume_data['volume_tokens'])
                tweet = self.volume_strategy.generate_tweet()
                
            elif tweet_type == 'personal':
                # Generate personality-driven tweet
                tweet = self.content_generator.generate_tweet()
            
            # Update state if tweet generated
            if tweet:
                self.state['last_tweet_time'] = datetime.now()
                self.state['tweets_today'] += 1
                self.state['last_strategy'] = tweet_type
                
            return tweet
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None
