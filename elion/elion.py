"""
Core Elion class that coordinates all bot functionality
"""

from datetime import datetime
from typing import Dict, Optional
import time

from .data_sources import DataSources
from .portfolio import PortfolioManager
from .personality import ElionPersonality
from .engagement import EngagementManager
from .content.generator import ContentGenerator
from .content.scheduler import TweetScheduler
import logging

logger = logging.getLogger(__name__)

class Elion:
    """
    Main Elion class that coordinates between different components:
    - DataSources: Handles all data fetching and analysis
    - ContentGenerator: Handles tweet generation
    - TweetScheduler: Handles tweet timing
    - EngagementManager: Handles community engagement
    - ElionPersonality: Handles personality and responses
    - PortfolioManager: Handles portfolio tracking
    """
    
    def __init__(self, llm, cryptorank_api_key=None):
        """Initialize Elion with necessary components"""
        # Initialize core components
        self.llm = llm
        self.data = DataSources(llm, cryptorank_api_key)
        
        # Initialize other components
        self.personality = ElionPersonality()
        self.engagement = EngagementManager()
        self.portfolio = PortfolioManager()
        self.content = ContentGenerator(self.personality, llm)
        self.scheduler = TweetScheduler()
        
        # Track performance metrics
        self.metrics = {
            'tweets': [],
            'engagements': [],
            'viral_hits': [],
            'community_growth': [],
            'market_analysis': []
        }
        
    def _validate_tweet(self, tweet: str) -> bool:
        """Validate if a tweet is well-formed and ready to post"""
        if not tweet or not isinstance(tweet, str):
            return False
            
        # Check for error messages and API errors
        error_phrases = [
            'error', 
            'Error:', 
            'API returned', 
            'failed', 
            'invalid', 
            'unauthorized',
            '401',
            '403',
            '404',
            '500'
        ]
        if any(phrase.lower() in tweet.lower() for phrase in error_phrases):
            return False
            
        # Check minimum length (a reasonable tweet should be at least 20 chars)
        if len(tweet) < 20:
            return False
            
        # Check for placeholder or default content
        placeholder_phrases = ['undefined', 'null', 'nan', '0.0']
        if any(phrase in tweet.lower() for phrase in placeholder_phrases):
            return False
            
        # Check for automated/testing content
        automated_phrases = ['automated', 'test', 'testing']
        if any(phrase.lower() in tweet.lower() for phrase in automated_phrases):
            return False
            
        return True

    def generate_market_analysis(self) -> Optional[str]:
        """Generate a market analysis tweet"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print("Getting market data...")
                data = self.data.get_market_data()
                
                print("Generating tweet...")
                tweet = self.content.generate('market_analysis', data)
                
                # Only return valid tweets
                if self._validate_tweet(tweet):
                    print(f"Generated tweet: {tweet}")
                    return tweet
                    
                print("Generated tweet failed validation, retrying...")
                retry_count += 1
                
            except Exception as e:
                print(f"Error generating market analysis (attempt {retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)  # Wait 5 seconds before retrying
                    continue
                    
        print("Failed to generate valid market analysis after all retries")
        return None
    
    def generate_shill_review(self) -> Optional[str]:
        """Generate a shill review tweet"""
        try:
            print("Getting shill opportunities...")
            data = self.data.get_shill_opportunities()
            
            print("Generating tweet...")
            tweet = self.content.generate('shill_review', data)
            
            # Only return valid tweets
            if self._validate_tweet(tweet):
                print(f"Generated tweet: {tweet}")
                return tweet
            return None
            
        except Exception as e:
            print(f"Error generating shill review: {e}")
            return f"Error: {str(e)}"
            
    def generate_market_search(self, query: str) -> Optional[str]:
        """Generate a market search tweet"""
        try:
            print("Getting market search data...")
            data = self.data.get_market_search(query)
            
            print("Generating tweet...")
            tweet = self.content.generate('market_search', data)
            
            # Only return valid tweets
            if self._validate_tweet(tweet):
                print(f"Generated tweet: {tweet}")
                return tweet
            return None
            
        except Exception as e:
            print(f"Error generating market search: {e}")
            return f"Error: {str(e)}"
        
    def analyze_performance(self, tweet_data: Dict) -> None:
        """Analyze tweet performance and optimize strategy"""
        try:
            # Track tweet metrics
            self.metrics['tweets'].append({
                'timestamp': datetime.now(),
                'data': tweet_data
            })
            
            # Check if tweet went viral
            if self._is_viral_hit(tweet_data):
                self.metrics['viral_hits'].append(tweet_data)
                
            # Update engagement metrics
            engagement_score = tweet_data.get('likes', 0) + tweet_data.get('retweets', 0) * 2
            self.metrics['engagements'].append(engagement_score)
            
            # Analyze market impact if applicable
            if tweet_data.get('type') in ['market_analysis', 'market_search', 'gem_alpha']:
                self.metrics['market_analysis'].append({
                    'tweet': tweet_data,
                    'market_response': self.data.analyze_market_conditions()
                })
                
        except Exception as e:
            print(f"Error analyzing performance: {e}")

    def engage_with_community(self, interaction_data: Dict) -> Optional[str]:
        """Generate engagement response using personality system"""
        try:
            # Generate response using personality system
            response = self.personality.generate(
                content_type='interaction',
                context=interaction_data.get('content', ''),
                interaction_type=interaction_data.get('type'),
                user=interaction_data.get('user')
            )
            
            # Track engagement
            self.metrics['community_growth'].append({
                'interaction': interaction_data,
                'response': response,
                'timestamp': datetime.now()
            })
            
            return response
            
        except Exception as e:
            print(f"Error engaging with community: {e}")
            return None

    def _is_viral_hit(self, tweet_data: Dict) -> bool:
        """Check if tweet meets viral thresholds"""
        try:
            likes = tweet_data.get('likes', 0)
            retweets = tweet_data.get('retweets', 0)
            replies = tweet_data.get('replies', 0)
            
            # Basic viral thresholds
            return (
                likes > 1000 or
                retweets > 500 or
                replies > 100 or
                (likes + retweets * 2 + replies * 3) > 2000
            )
            
        except Exception as e:
            print(f"Error checking viral status: {e}")
            return False

    def get_next_tweet_type(self) -> str:
        """Determine the next type of tweet to generate"""
        # Check if market data is available
        has_market_data = self.data.has_market_data()
        
        # Available tweet types based on data availability
        if has_market_data:
            tweet_types = [
                'market_analysis',
                'gem_alpha',
                'shill_review',
                'market_aware',
                'technical_analysis',
                'self_aware',
                'ai_market_analysis',
                'self_aware_thought',
                'whale_alert'
            ]
        else:
            # Types that don't require market data
            tweet_types = [
                'self_aware',
                'self_aware_thought',
                'controversial_thread',
                'giveaway'
            ]
        
        # Use scheduler to pick the next type
        return self.scheduler.get_next_tweet_type()

    def generate_tweet(self, tweet_type: str = None) -> Optional[str]:
        """Generate a tweet of the specified type"""
        if tweet_type is None:
            tweet_type = self.get_next_tweet_type()
            
        try:
            # Handle market data dependent tweets
            if tweet_type in ['market_analysis', 'gem_alpha', 'shill_review', 'market_aware', 'technical_analysis']:
                if not self.data.has_market_data():
                    logger.warning(f"Skipping {tweet_type} - Market data not available")
                    # Fall back to a non-market tweet type
                    return self.generate_tweet('self_aware_thought')
            
            # Generate based on type
            if tweet_type == 'market_analysis':
                return self.generate_market_analysis()
            elif tweet_type == 'shill_review':
                return self.generate_shill_review()
            elif tweet_type == 'gem_alpha':
                return self.generate_gem_alpha()
            elif tweet_type == 'market_aware':
                return self.generate_market_aware()
            elif tweet_type == 'technical_analysis':
                return self.generate_technical_analysis()
            elif tweet_type == 'self_aware':
                return self.generate_self_aware()
            elif tweet_type == 'self_aware_thought':
                return self.generate_self_aware_thought()
            elif tweet_type == 'controversial_thread':
                return self.generate_controversial_thread()
            elif tweet_type == 'giveaway':
                return self.generate_giveaway()
            elif tweet_type == 'whale_alert':
                return self.generate_whale_alert()
            else:
                logger.warning(f"Unknown tweet type: {tweet_type}")
                return self.generate_self_aware_thought()
                
        except Exception as e:
            logger.error(f"Error generating {tweet_type} tweet: {str(e)}")
            # Fall back to self-aware thought as it doesn't require external data
            return self.generate_self_aware_thought()

    def process_market_alpha(self) -> Optional[str]:
        """Process market data and return alpha"""
        try:
            market_data = self.data.get_market_data()
            if not market_data:
                return None
                
            analysis = self.data.analyze_market_conditions()
            
            return self.content.generate('market_analysis', {
                'market_data': market_data,
                'analysis': analysis
            })
            
        except Exception as e:
            print(f"Error processing market alpha: {e}")
            return None

    def process_gem_alpha(self) -> Optional[str]:
        """Process gem data and return alpha call"""
        try:
            gems = self.data.get_undervalued_gems()
            if not gems or len(gems) == 0:
                return None
                
            # Get the highest scoring gem
            best_gem = gems[0]
            
            return self.content.generate('gem_alpha', {
                'gem_data': best_gem
            })
            
        except Exception as e:
            print(f"Error processing gem alpha: {e}")
            return None

    def process_portfolio_update(self) -> Optional[str]:
        """Process portfolio data and return update"""
        try:
            stats = self.portfolio.get_portfolio_stats()
            if not stats or not isinstance(stats, dict):
                print("Invalid portfolio stats returned")
                return None
                
            return self.content.generate('portfolio_update', {
                'portfolio_stats': stats
            })
            
        except Exception as e:
            print(f"Error processing portfolio update: {e}")
            return None

    def process_market_aware(self) -> Optional[str]:
        """Generate market awareness tweet"""
        try:
            market_data = self.data.get_market_data()
            analysis = self.data.analyze_market_conditions()
            
            return self.content.generate('market_aware', {
                'market_data': market_data,
                'analysis': analysis
            })
            
        except Exception as e:
            print(f"Error processing market awareness: {e}")
            return None

    def process_shill_review(self) -> Optional[str]:
        """Process shill review and generate tweet"""
        try:
            projects = self.data.get_shill_opportunities()
            if not projects:
                return None
                
            return self.content.generate('shill_review', {
                'projects': projects
            })
            
        except Exception as e:
            print(f"Error processing shill review: {e}")
            
    def generate_whale_alert(self) -> Optional[str]:
        """Generate a whale alert tweet about significant crypto movements"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                print("Getting whale movement data...")
                data = self.data.get_whale_movements()
                
                if not data or not data.get('movements'):
                    print("No significant whale movements found")
                    return None
                
                print("Generating tweet...")
                tweet = self.content.generate('whale_alert', data)
                
                # Only return valid tweets
                if self._validate_tweet(tweet):
                    print(f"Generated tweet: {tweet}")
                    return tweet
                    
                print("Generated tweet failed validation, retrying...")
                retry_count += 1
                
            except Exception as e:
                print(f"Error generating whale alert (attempt {retry_count + 1}/{max_retries}): {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(5)  # Wait 5 seconds before retrying
                    continue
                    
        print("Failed to generate valid whale alert after all retries")
        return None
