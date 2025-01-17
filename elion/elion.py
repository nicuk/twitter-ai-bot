"""
Core Elion class that coordinates all bot functionality
"""

from datetime import datetime
from typing import Dict, Optional

from .data_sources import DataSources
from .portfolio import PortfolioManager
from .personality import ElionPersonality
from .engagement import EngagementManager
from .content.generator import ContentGenerator
from .content.scheduler import TweetScheduler
from .market_analyzer import MarketAnalyzer

class Elion:
    """
    Main Elion class that coordinates between different components:
    - MarketAnalyzer: Handles all market analysis
    - ContentGenerator: Handles tweet generation
    - TweetScheduler: Handles tweet timing
    - EngagementManager: Handles community engagement
    - ElionPersonality: Handles personality and responses
    - PortfolioManager: Handles portfolio tracking
    - DataSources: Handles data fetching
    """
    
    def __init__(self, llm):
        """Initialize Elion with necessary components"""
        # Initialize core components
        self.data_sources = DataSources()
        self.market_analyzer = MarketAnalyzer(self.data_sources)
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
        
    def analyze_performance(self, tweet_data: Dict) -> None:
        """Analyze tweet performance and optimize strategy"""
        try:
            # Track tweet metrics
            self.metrics['tweets'].append(tweet_data)
            
            # Check if tweet went viral
            if self._is_viral_hit(tweet_data):
                self.metrics['viral_hits'].append(tweet_data)
                
            # Update engagement metrics
            engagement_score = tweet_data.get('likes', 0) + tweet_data.get('retweets', 0) * 2
            self.metrics['engagements'].append(engagement_score)
            
            # Analyze market impact if applicable
            if tweet_data.get('type') in ['market_alpha', 'gem_alpha']:
                self.metrics['market_analysis'].append({
                    'tweet': tweet_data,
                    'market_response': self.market_analyzer.analyze_market_conditions()
                })
                
        except Exception as e:
            print(f"Error analyzing performance: {e}")

    def engage_with_community(self, interaction_data: Dict) -> Optional[str]:
        """Generate engagement response using personality system"""
        try:
            # Generate response using personality system
            response = self.personality.generate(
                interaction_type=interaction_data.get('type'),
                user=interaction_data.get('user'),
                content=interaction_data.get('content')
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
        """Get the next tweet type based on timing and distribution rules"""
        return self.scheduler.get_next_tweet_type()

    def process_market_alpha(self) -> Optional[str]:
        """Process market data and return alpha"""
        try:
            market_data = self.data_sources.get_market_data()
            if not market_data:
                return None
                
            analysis = self.market_analyzer.analyze_market_conditions()
            
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
            gems = self.data_sources.get_undervalued_gems()
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
            market_data = self.data_sources.get_market_data()
            analysis = self.market_analyzer.analyze_market_conditions()
            
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
            projects = self.data_sources.get_projects()
            if not projects:
                return None
                
            return self.content.generate('shill_review', {
                'projects': projects
            })
            
        except Exception as e:
            print(f"Error processing shill review: {e}")
            return None
