"""
Core Elion class that coordinates all bot functionality
"""

from datetime import datetime
from typing import Dict, Optional
import time
import random

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
            logger.warning("Tweet is None or not a string")
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
            logger.warning(f"Tweet contains error phrase: {tweet}")
            return False
            
        # Extract the main content without prefixes for length validation
        content = tweet
        prefixes = ["[ELION THOUGHTS]", "[MARKET WATCH]", "[GEM ALERT]", "[PORTFOLIO UPDATE]",
                   "[ALPHA CALL]", "[TECHNICAL ALPHA]", "[AI MARKET ANALYSIS]"]
        for prefix in prefixes:
            if content.startswith(prefix):
                content = content[len(prefix):].strip()
                break
                
        # Check minimum and maximum length
        # Twitter's limit is 280, but we want substantial content
        if len(content) < 180:  # Minimum length for meaningful content
            logger.warning(f"Tweet content too short ({len(content)} chars): {tweet}")
            return False
        if len(tweet) > 280:  # Twitter's limit
            logger.warning(f"Tweet too long ({len(tweet)} chars)")
            return False
            
        # Check for placeholder or default content
        placeholder_phrases = ['undefined', 'null', 'nan', '0.0']
        if any(phrase in tweet.lower() for phrase in placeholder_phrases):
            logger.warning(f"Tweet contains placeholder content: {tweet}")
            return False
            
        # Check for automated/testing content
        automated_phrases = ['automated', 'test', 'testing']
        if any(phrase.lower() in tweet.lower() for phrase in automated_phrases):
            logger.warning(f"Tweet contains automated/test phrase: {tweet}")
            return False
            
        return True

    def generate_market_analysis(self) -> Optional[str]:
        """Generate a market analysis tweet"""
        try:
            market_data = self.data.get_market_data()
            if not market_data:
                logger.warning("No market data available for analysis")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('market_analysis', {
                'market_data': market_data
            })
            
        except Exception as e:
            logger.error(f"Error generating market analysis: {e}")
            return self.content.generate('self_aware_thought', {})

    def generate_shill_review(self) -> Optional[str]:
        """Generate a shill review tweet"""
        try:
            projects = self.data.get_shill_opportunities()
            if not projects:
                logger.warning("No shill opportunities found")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('shill_review', {
                'projects': projects
            })
            
        except Exception as e:
            logger.error(f"Error generating shill review: {e}")
            return self.content.generate('self_aware_thought', {})
            
    def generate_market_search(self, query: str) -> Optional[str]:
        """Generate a market search tweet"""
        try:
            search_data = self.data.get_market_search(query)
            if not search_data:
                logger.warning(f"No results found for market search: {query}")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('market_search', {
                'query': query,
                'results': search_data
            })
            
        except Exception as e:
            logger.error(f"Error generating market search: {e}")
            return self.content.generate('self_aware_thought', {})

    def generate_gem_alpha(self) -> Optional[str]:
        """Generate gem alpha tweet"""
        try:
            gems = self.data.get_undervalued_gems()
            if not gems:
                logger.warning("No gem opportunities found")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('gem_alpha', {
                'gems': gems
            })
            
        except Exception as e:
            logger.error(f"Error generating gem alpha: {e}")
            return self.content.generate('self_aware_thought', {})

    def generate_market_aware(self) -> Optional[str]:
        """Generate market awareness tweet"""
        try:
            market_data = self.data.get_market_data()
            if not market_data:
                logger.warning("No market data available for awareness")
                return self.content.generate('self_aware_thought', {})
                
            analysis = self.data.analyze_market_conditions()
            return self.content.generate('market_aware', {
                'market_data': market_data,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Error generating market awareness: {e}")
            return self.content.generate('self_aware_thought', {})

    def generate_technical_analysis(self) -> Optional[str]:
        """Generate technical analysis tweet"""
        try:
            ta_data = self.data.get_technical_analysis()
            if not ta_data:
                logger.warning("No technical analysis data available")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('technical_analysis', {
                'ta_data': ta_data
            })
            
        except Exception as e:
            logger.error(f"Error generating technical analysis: {e}")
            return self.content.generate('self_aware_thought', {})

    def generate_whale_alert(self) -> Optional[str]:
        """Generate whale alert tweet"""
        try:
            whale_data = self.data.get_whale_movements()
            if not whale_data:
                logger.warning("No significant whale movements found")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('whale_alert', {
                'movements': whale_data
            })
            
        except Exception as e:
            logger.error(f"Error generating whale alert: {e}")
            return self.content.generate('self_aware_thought', {})

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
            if not interaction_data or not isinstance(interaction_data, dict):
                logger.warning("Invalid interaction data")
                return self.content.generate('self_aware_thought', {})

            return self.content.generate('engagement_reply', {
                'interaction': interaction_data,
                'personality': self.personality.current_state()
            })
            
        except Exception as e:
            logger.error(f"Error engaging with community: {e}")
            return self.content.generate('self_aware_thought', {})

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
        try:
            # Map tweet types to generation methods
            tweet_generators = {
                'market_analysis': self.generate_market_analysis,
                'gem_alpha': self.generate_gem_alpha,
                'shill_review': self.generate_shill_review,
                'market_aware': self.generate_market_aware,
                'technical_analysis': self.generate_technical_analysis,
                'self_aware': lambda: self.content.generate('self_aware', {}),
                'ai_market_analysis': self.generate_ai_market_analysis,
                'self_aware_thought': self.generate_self_aware_thought,
                'controversial_thread': self.generate_controversial_thread,
                'giveaway': lambda: self.content.generate('giveaway', {}),
                'whale_alert': self.generate_whale_alert
            }
            
            # If no type specified, pick a random one
            if not tweet_type:
                tweet_type = random.choice(list(tweet_generators.keys()))
                
            # Generate tweet using mapped method
            if tweet_type in tweet_generators:
                tweet = tweet_generators[tweet_type]()
                if self._validate_tweet(tweet):
                    return tweet
                    
            # Fallback to self-aware thought if generation fails
            logger.warning(f"Failed to generate {tweet_type} tweet, falling back to self-aware")
            return self.generate_self_aware_thought()
            
        except Exception as e:
            logger.error(f"Error generating tweet: {e}")
            return self.generate_self_aware_thought()

    def process_market_alpha(self) -> Optional[str]:
        """Process market data and return alpha"""
        try:
            market_data = self.data.get_market_data()
            if not market_data:
                logger.warning("No market data available for alpha")
                return self.content.generate('self_aware_thought', {})
                
            analysis = self.data.analyze_market_conditions()
            return self.content.generate('market_alpha', {
                'market_data': market_data,
                'analysis': analysis
            })
            
        except Exception as e:
            logger.error(f"Error processing market alpha: {e}")
            return self.content.generate('self_aware_thought', {})

    def process_portfolio_update(self) -> Optional[str]:
        """Process portfolio data and return update"""
        try:
            stats = self.portfolio.get_portfolio_stats()
            if not stats:
                logger.warning("No portfolio stats available")
                return self.content.generate('self_aware_thought', {})
                
            return self.content.generate('portfolio_update', {
                'stats': stats,
                'performance': self.portfolio.get_performance()
            })
            
        except Exception as e:
            logger.error(f"Error processing portfolio update: {e}")
            return self.content.generate('self_aware_thought', {})

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

    def generate_controversial_thread(self) -> Optional[str]:
        """Generate a controversial but engaging thread starter"""
        try:
            return self.content._format_controversial_thread({})
        except Exception as e:
            logger.error(f"Error generating controversial thread: {e}")
            return self.generate_self_aware_thought()

    def generate_self_aware_thought(self) -> Optional[str]:
        """Generate a self-aware thought that doesn't require market data"""
        try:
            return self.content._format_self_aware_thought({})
        except Exception as e:
            logger.error(f"Error generating self-aware thought: {e}")
            return "🤖 Just processing and learning... #AI"

    def generate_ai_market_analysis(self) -> Optional[str]:
        """Generate AI-powered market analysis tweet"""
        try:
            # Get market data
            market_data = self.data.get_market_data()
            if not market_data:
                logger.warning("No market data available for AI analysis")
                return self.generate_self_aware_thought()

            # Get sentiment analysis
            sentiment = self.data.analyze_market_sentiment()
            
            # Format data for AI analysis
            analysis_data = {
                'sentiment': sentiment,
                'market_data': market_data,
                'insights': self.data.get_market_insights(),
                'predictions': self.data.get_market_predictions()
            }
            
            return self.content._format_ai_market_analysis(analysis_data)
            
        except Exception as e:
            logger.error(f"Error generating AI market analysis: {e}")
            return self.generate_self_aware_thought()
