"""
Core ELAI class - Streamlined for better maintainability
"""

from datetime import datetime, timedelta
import random
from typing import Optional
from dotenv import load_dotenv

from custom_llm import MetaLlamaComponent
from strategies.trend_strategy import TrendStrategy
from strategies.volume_strategy import VolumeStrategy
from elion.personality.traits import PersonalityManager
from elion.content.generator import ContentGenerator

class Elion:
    """ELAI Agent for Crypto Twitter - Core functionality"""
    
    def __init__(self, api_key: str = None):
        """Initialize ELAI with core components"""
        self.api_key = api_key
        
        # Initialize LLM
        self.llm = MetaLlamaComponent()  # Will load its own env vars
        
        # Initialize strategies
        self.trend_strategy = TrendStrategy(api_key)
        self.volume_strategy = VolumeStrategy(api_key)
        self.personality = PersonalityManager()
        self.content_generator = ContentGenerator(self.personality, self.llm)
        
        # Initialize state
        self.state = {
            'last_tweet_time': None,
            'tweets_today': 0,
            'last_strategy': 'volume',  # Start with trend next
            'trend_tokens': [],  # Store filtered trend tokens
            'volume_tokens': []  # Store filtered volume tokens
        }
        
        # Tweet type weights (out of 100)
        self.tweet_weights = {
            'trend': 35,    # Market trend analysis
            'volume': 35,   # Volume analysis
            'personal': 30  # Personality-driven tweets
        }
        
    def get_next_tweet_type(self):
        """Determine next tweet type based on weights and last tweet"""
        # Reset daily tweet count if needed
        now = datetime.now()
        if self.state['last_tweet_time']:
            last_tweet_day = self.state['last_tweet_time'].date()
            if now.date() > last_tweet_day:
                self.state['tweets_today'] = 0
        
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
                    self.state['trend_tokens'] = trend_data['trend_tokens']
                    self.content_generator.update_recent_tokens(trend_data['trend_tokens'])
                tweet = self.trend_strategy.generate_tweet()
                
            elif tweet_type == 'volume':
                # Get volume analysis and update state
                volume_data = self.volume_strategy.analyze()
                if 'volume_tokens' in volume_data:
                    self.state['volume_tokens'] = volume_data['volume_tokens']
                    self.content_generator.update_recent_tokens(volume_data['volume_tokens'])
                tweet = self.volume_strategy.generate_tweet()
                
            elif tweet_type == 'personal':
                # Use most recent tokens from either strategy
                recent_tokens = self.state['trend_tokens'] or self.state['volume_tokens']
                if recent_tokens:
                    self.content_generator.update_recent_tokens(recent_tokens)
                tweet = self.content_generator.generate('self_aware')
            
            # Clean up tweet if generated
            if tweet:
                # Remove extra whitespace and newlines
                tweet = tweet.strip()
                tweet_lines = tweet.split('\n')
                tweet_lines = [line.strip() for line in tweet_lines if line.strip()]
                tweet = ' '.join(tweet_lines)
                
                # Update state
                self.state['last_tweet_time'] = datetime.now()
                self.state['tweets_today'] += 1
                self.state['last_strategy'] = tweet_type
                
            return tweet
            
        except Exception as e:
            print(f"Error generating tweet: {str(e)}")
            return None
