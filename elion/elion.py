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
from .personality.traits import PersonalityManager
from .content.generator import ContentGenerator

class Elion:
    """ELAI Agent for Crypto Twitter - Core functionality"""
    
    def __init__(self, llm: MetaLlamaComponent):
        """Initialize ELAI with core components"""
        # Store LLM
        self.llm = llm
        
        # Initialize components
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
    
    def generate_tweet(self, tweet_type: str = None) -> Optional[str]:
        """Generate tweet based on type"""
        try:
            # Get next tweet type from weights if not specified
            if not tweet_type:
                tweet_type = self._get_next_tweet_type()
                
            # Generate tweet based on type
            tweet = None
            if tweet_type == 'trend':
                # Generate trend analysis tweet
                tweet = self.content_generator.generate('trend')
                
            elif tweet_type == 'volume':
                # Generate volume analysis tweet
                tweet = self.content_generator.generate('volume')
                
            elif tweet_type == 'personal':
                # Generate personality-driven tweet
                tweet = self.content_generator.generate('self_aware')
                
            # Update state
            if tweet:
                self.state['last_tweet_time'] = datetime.now()
                self.state['tweets_today'] += 1
                self.state['last_strategy'] = tweet_type
                
            return tweet
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def engage_with_community(self) -> Optional[str]:
        """Generate a community engagement tweet"""
        try:
            # Use personality-driven content for engagement
            tweet = self.content_generator.generate('self_aware')
            if tweet:
                return tweet
            return None
        except Exception as e:
            print(f"Error generating engagement tweet: {str(e)}")
            return None
