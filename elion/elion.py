"""
Core ELAI class - Streamlined for better maintainability
"""

from datetime import datetime, timedelta
import random
from typing import Dict, Optional
from dotenv import load_dotenv
import os

from custom_llm import MetaLlamaComponent
from elion.content.generator import ContentGenerator
from elion.personality.traits import PersonalityManager
from elion.content.tweet_formatters import TweetFormatters
from strategies.trend_strategy import TrendStrategy, format_twitter_output as format_trend_output
from strategies.volume_strategy import VolumeStrategy, format_twitter_output as format_volume_output

class Elion:
    """ELAI Agent for Crypto Twitter - Core functionality"""
    
    def __init__(self, llm: MetaLlamaComponent):
        """Initialize ELAI with core components"""
        # Store LLM
        self.llm = llm
        
        # Initialize components
        self.personality = PersonalityManager()
        self.content_generator = ContentGenerator(self.personality, self.llm)
        
        # Initialize market analyzers
        self.trend_strategy = TrendStrategy(os.getenv('CRYPTORANK_API_KEY'))
        self.volume_strategy = VolumeStrategy(os.getenv('CRYPTORANK_API_KEY'), llm=self.llm)
        
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
    
    def get_market_data(self) -> Dict:
        """Get market data from strategies"""
        try:
            # Get trend data
            trend_data = self.trend_strategy.analyze()
            if trend_data:
                self.state['trend_tokens'] = trend_data.get('trend_tokens', [])

            # Get volume data
            volume_data = self.volume_strategy.analyze()
            if volume_data:
                self.state['volume_tokens'] = volume_data.get('volume_tokens', [])

            return {
                'trend_data': {'trend_tokens': self.state['trend_tokens']},
                'volume_data': {'spikes': volume_data.get('spikes', []), 'anomalies': volume_data.get('anomalies', [])}
            }
        except Exception as e:
            print(f"Error getting market data: {str(e)}")
            return {'trend_data': {}, 'volume_data': {}}
        
    def format_tweet(self, tweet_type: str, market_data: Dict) -> str:
        """Format a tweet using cached market data"""
        try:
            # Get formatter
            formatter = TweetFormatters()
            
            # Get personality trait
            trait = self.personality.get_trait()
            
            # Format tweet based on type
            if tweet_type == 'trend':
                return formatter.format_trend_insight(market_data['trend_data'], trait)
            elif tweet_type == 'volume':
                return formatter.format_volume_insight(market_data['volume_data'], trait)
            else:
                return formatter.format_personal(trait)
                
        except Exception as e:
            print(f"Error formatting {tweet_type} tweet: {str(e)}")
            return None
            
    def generate_tweet(self, tweet_type: str = None) -> Optional[str]:
        """Generate a tweet of the specified type"""
        try:
            # Get next tweet type from weights if not specified
            if not tweet_type:
                tweet_type = self._get_next_tweet_type()
                
            # Get tweet based on type
            tweet = None
            if tweet_type == 'trend':
                try:
                    trend_data = self.trend_strategy.analyze()
                    if trend_data and 'trend_tokens' in trend_data:
                        tweet = format_trend_output(trend_data['trend_tokens'])
                    if not tweet:
                        print("Trend strategy failed to generate tweet, trying volume strategy")
                        tweet_type = 'volume'  # Fallback to volume
                except Exception as e:
                    print(f"Error in trend strategy: {str(e)}")
                    tweet_type = 'volume'  # Fallback to volume
                    
            if tweet_type == 'volume':
                try:
                    volume_data = self.volume_strategy.analyze()
                    if volume_data and ('spikes' in volume_data or 'anomalies' in volume_data):
                        tweet = format_volume_output(volume_data.get('spikes', []), volume_data.get('anomalies', []))
                    if not tweet:
                        print("Volume strategy failed to generate tweet, trying personal")
                        tweet_type = 'personal'  # Fallback to personal
                except Exception as e:
                    print(f"Error in volume strategy: {str(e)}")
                    tweet_type = 'personal'  # Fallback to personal
                    
            if tweet_type == 'personal':
                tweet = self.content_generator.generate('self_aware')
                
            # Only update state if tweet was successfully generated
            if tweet:
                self.state['last_strategy'] = tweet_type
                self.state['last_tweet_time'] = datetime.now()
                self.state['tweets_today'] += 1
                return tweet
                
            return None
                
        except Exception as e:
            print(f"Error generating tweet: {str(e)}")
            return None

    def engage_with_community(self) -> Optional[str]:
        """Generate a community engagement tweet"""
        try:
            return self.content_generator.generate('self_aware')
        except Exception as e:
            print(f"Error generating engagement tweet: {str(e)}")
            return None
