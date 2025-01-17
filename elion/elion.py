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
        
    def generate_market_analysis(self) -> str:
        """Generate a market analysis tweet"""
        data = self.market_analyzer.analyze_market_conditions()
        return self.content.generate('market_analysis', data)
    
    def generate_shill_review(self) -> str:
        """Generate a shill review tweet"""
        data = self.data_sources.get_shill_opportunities()
        return self.content.generate('shill_review', data)
    
    def generate_market_search(self) -> str:
        """Generate a market search tweet"""
        data = self.market_analyzer.analyze_market_conditions()
        return self.content.generate('market_search', data)
        
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
                    'market_response': self.market_analyzer.analyze_market_conditions()
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
        """Get the next tweet type based on timing and distribution rules"""
        return self.scheduler.get_next_tweet_type()

    def generate_tweet(self, tweet_type: str) -> Optional[str]:
        """Generate tweet content based on type"""
        try:
            data = None
            
            # Regular Scheduled Posts (50%)
            if tweet_type == 'market_analysis':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                data = {'market_data': market_data, 'analysis': analysis}
            elif tweet_type == 'market_search':
                data = self.data_sources._get_viral_tweets()
            elif tweet_type == 'gem_alpha':
                data = self.data_sources.get_alpha_opportunities()
            elif tweet_type == 'portfolio_update':
                data = self.portfolio.get_portfolio_update()
            elif tweet_type == 'market_aware':
                data = self.market_analyzer.analyze_market_conditions()
            elif tweet_type == 'shill_review':
                data = self.data_sources.get_shill_opportunities()
            
            # Special Event Posts (30%)
            elif tweet_type == 'breaking_alpha':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                news = self.data_sources.get_latest_news()
                data = {
                    'market_data': market_data,
                    'analysis': analysis,
                    'news': news,
                    'is_breaking': True
                }
            elif tweet_type == 'whale_alert':
                market_data = self.data_sources.get_market_alpha()
                # Look for large transactions in market data
                data = {
                    'market_data': market_data,
                    'transaction_type': 'whale_movement'
                }
            elif tweet_type == 'technical_analysis':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                data = {
                    'market_data': market_data,
                    'analysis': analysis,
                    'technical_indicators': True
                }
            elif tweet_type == 'controversial_thread':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                news = self.data_sources.get_latest_news()
                data = {
                    'market_data': market_data,
                    'analysis': analysis,
                    'news': news,
                    'controversial': True
                }
            elif tweet_type == 'giveaway':
                data = {
                    'type': 'giveaway',
                    'market_condition': self.market_analyzer.analyze_market_conditions()
                }
            elif tweet_type == 'self_aware':
                data = {
                    'type': 'self_aware',
                    'market_condition': self.market_analyzer.analyze_market_conditions(),
                    'personality': self.personality.get_current_state()
                }
            elif tweet_type == 'ai_market_analysis':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                news = self.data_sources.get_latest_news()
                data = {
                    'market_data': market_data,
                    'analysis': analysis,
                    'news': news,
                    'ai_perspective': True
                }
            elif tweet_type == 'self_aware_thought':
                data = {
                    'type': 'self_aware_thought',
                    'market_condition': self.market_analyzer.analyze_market_conditions(),
                    'personality': self.personality.get_current_state()
                }
            
            # Reactive Posts (20%)
            elif tweet_type == 'market_response':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                news = self.data_sources.get_latest_news()
                data = {
                    'market_data': market_data,
                    'analysis': analysis,
                    'news': news,
                    'is_response': True
                }
            elif tweet_type == 'engagement_reply':
                data = {
                    'type': 'engagement',
                    'market_condition': self.market_analyzer.analyze_market_conditions(),
                    'personality': self.personality.get_current_state()
                }
            elif tweet_type == 'alpha_call':
                opportunities = self.data_sources.get_alpha_opportunities()
                analysis = self.market_analyzer.analyze_market_conditions()
                data = {
                    'opportunities': opportunities,
                    'analysis': analysis,
                    'is_alpha_call': True
                }
            elif tweet_type == 'technical_alpha':
                market_data = self.data_sources.get_market_alpha()
                analysis = self.market_analyzer.analyze_market_conditions()
                data = {
                    'market_data': market_data,
                    'analysis': analysis,
                    'is_technical': True
                }
                
            if data:
                content = self.content.generate(tweet_type, data)
                if content and not content.startswith("Error"):
                    return content
                    
            # If we get here, the tweet type failed
            self.scheduler.mark_type_failed(tweet_type)
            return None
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            self.scheduler.mark_type_failed(tweet_type)
            return None

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
