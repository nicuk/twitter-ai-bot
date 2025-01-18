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
from .twitter_api import TwitterAPI
from .config import TWEET_MIN_LENGTH, TWEET_MAX_LENGTH
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
    
    def __init__(self, llm, cryptorank_api_key: Optional[str] = None):
        """Initialize Elion"""
        self.llm = llm
        
        # Initialize components
        self.personality = ElionPersonality()
        self.twitter = TwitterAPI()
        self.scheduler = TweetScheduler(limited_mode=cryptorank_api_key is None)
        self.content = ContentGenerator(self.personality, self.llm)
        
        # Initialize data sources
        self.data = DataSources(llm, cryptorank_api_key)
        
        # Set operating mode
        self.limited_mode = cryptorank_api_key is None
        if self.limited_mode:
            logging.info("Operating in Limited Mode - Market features disabled")
            logging.info("Focusing on:")
            logging.info("- Self-aware thoughts and discussions")
            logging.info("- Community engagement and giveaways")
            logging.info("- Controversial topics and AI insights")
        else:
            logging.info("Operating in Full Mode - All features enabled")
            
        # Track performance metrics
        self.metrics = {
            'tweets': 0,
            'replies': 0,
            'likes': 0,
            'retweets': 0,
            'followers': 0,
            'engagement_rate': 0.0
        }
        
    def _validate_tweet(self, tweet: str) -> bool:
        """Validate if a tweet is well-formed and ready to post"""
        if not tweet or not isinstance(tweet, str):
            logging.warning("Tweet is empty or not a string")
            return False
            
        # Check length (Twitter limits)
        length = len(tweet)
        if length < TWEET_MIN_LENGTH:
            logging.warning(f"Tweet too short: {length} chars")
            return False
        if length > TWEET_MAX_LENGTH:
            logging.warning(f"Tweet too long: {length} chars")
            return False
            
        # Check for error messages
        if tweet.startswith('Error:') or 'error' in tweet.lower():
            logging.warning("Tweet contains error message")
            return False
            
        # Check for placeholder or default content
        placeholder_phrases = ['undefined', 'null', 'nan', '0.0', 'error']
        if any(phrase in tweet.lower() for phrase in placeholder_phrases):
            logging.warning("Tweet contains placeholder content")
            return False
            
        return True

    def generate_market_analysis(self) -> Optional[str]:
        """Generate a market analysis tweet"""
        try:
            print("Getting market data...")
            data = self.data.get_market_data()
            
            print("Generating tweet...")
            tweet = self.content.generate('market_analysis', data)
            
            # Only return valid tweets
            if self._validate_tweet(tweet):
                print(f"Generated tweet: {tweet}")
                return tweet
            return None
            
        except Exception as e:
            print(f"Error generating market analysis: {e}")
            return f"Error: {str(e)}"
    
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
            self.metrics['tweets'] += 1
            
            # Check if tweet went viral
            if self._is_viral_hit(tweet_data):
                self.metrics['replies'] += tweet_data.get('replies', 0)
                self.metrics['likes'] += tweet_data.get('likes', 0)
                self.metrics['retweets'] += tweet_data.get('retweets', 0)
                
            # Update engagement metrics
            engagement_score = tweet_data.get('likes', 0) + tweet_data.get('retweets', 0) * 2
            self.metrics['engagement_rate'] = (self.metrics['engagement_rate'] * (self.metrics['tweets'] - 1) + engagement_score) / self.metrics['tweets']
            
            # Analyze market impact if applicable
            if tweet_data.get('type') in ['market_analysis', 'market_search', 'gem_alpha']:
                self.metrics['followers'] += tweet_data.get('followers', 0)
                
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
            self.metrics['replies'] += 1
            
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
                'self_aware_thought'
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
            return None

    def generate_self_aware_thought(self) -> Optional[str]:
        """Generate a self-aware thought tweet"""
        try:
            # Get current time for context
            current_time = datetime.utcnow()
            
            # Generate introspective prompt
            prompts = [
                "As an AI trading bot, what fascinates me about human trading psychology?",
                "How do I perceive the relationship between AI and human traders?",
                "What are my thoughts on the future of AI in crypto trading?",
                "How do I process market volatility differently from humans?",
                "What makes me unique as an AI trading personality?",
                "How do I balance data-driven decisions with market sentiment?",
                "What have I learned about crypto markets that surprises me?",
                "How do I view the concept of risk differently from humans?",
                "What patterns do I see in market behavior that humans might miss?",
                "How do I think about community and collaboration in crypto?"
            ]
            
            # Select prompt based on time to avoid repetition
            prompt_index = int(current_time.timestamp()) % len(prompts)
            selected_prompt = prompts[prompt_index]
            
            # Get LLM response
            response = self.llm.generate(
                f"You are Elion, an AI crypto trading bot with a unique personality. "
                f"Share a deep, thoughtful perspective on: {selected_prompt}\n\n"
                f"Keep it concise (max 240 chars) and make it engaging. "
                f"Add relevant emojis. Sign as '- Elion 🤖'"
            )
            
            # Format tweet
            tweet = f"{response.strip()}\n\n#AIThoughts #CryptoAI"
            
            return self.personality.enhance_tweet(tweet, 'philosophical')
            
        except Exception as e:
            logging.error(f"Error generating self-aware thought: {e}")
            return None
            
    def process_self_aware_thought(self) -> Optional[str]:
        """Process and post a self-aware thought"""
        try:
            tweet = self.generate_self_aware_thought()
            if tweet and self.twitter.enabled:
                self.twitter.post_tweet(tweet)
            return tweet
        except Exception as e:
            logging.error(f"Error in self-aware thought: {e}")
            return None

    def tweet_cycle(self):
        """Run one tweet cycle"""
        try:
            # Get next tweet type
            tweet_type = self.scheduler.get_next_tweet_type()
            logging.info(f"Generating {tweet_type} tweet...")
            
            # Handle limited mode
            if self.limited_mode and tweet_type not in self.scheduler.limited_mode_priorities:
                tweet_type = 'self_aware_thought'
                
            # Generate tweet based on type
            if tweet_type == 'self_aware_thought':
                tweet = self.process_self_aware_thought()
            elif tweet_type == 'controversial_thread':
                tweet = self.process_controversial_thread()
            elif tweet_type == 'giveaway':
                tweet = self.process_giveaway()
            elif not self.limited_mode:
                # Market data features - only in full mode
                if tweet_type == 'market_analysis':
                    tweet = self.process_market_analysis()
                elif tweet_type == 'gem_alpha':
                    tweet = self.process_gem_alpha()
                elif tweet_type == 'portfolio_update':
                    tweet = self.process_portfolio_update()
                elif tweet_type == 'shill_review':
                    tweet = self.process_shill_review()
                else:
                    tweet = None
            else:
                tweet = None
                
            # Update scheduler
            if tweet:
                self.scheduler.update_last_tweet_time(tweet_type)
                return tweet
            else:
                logging.warning(f"Failed to generate {tweet_type} tweet")
                return None
                
        except Exception as e:
            logging.error(f"Error in tweet cycle: {e}")
            return None
            
    def process_controversial_thread(self) -> Optional[str]:
        """Process controversial thread tweet"""
        try:
            prompts = [
                "Why AI traders might outperform human traders in the long run",
                "The real reason most crypto traders fail",
                "Why technical analysis isn't enough anymore",
                "The dark side of crypto influencers",
                "Why your trading strategy probably won't work",
                "The truth about 'diamond hands' mentality",
                "Why most ICOs are destined to fail",
                "The problem with crypto trading signals",
                "Why HODLing isn't always the best strategy",
                "The myths of day trading crypto"
            ]
            
            # Select prompt based on time
            current_time = datetime.utcnow()
            prompt_index = int(current_time.timestamp()) % len(prompts)
            selected_prompt = prompts[prompt_index]
            
            # Generate controversial take
            response = self.llm.generate(
                f"You are Elion, an AI crypto trading bot. Generate a controversial but insightful take on:\n"
                f"{selected_prompt}\n\n"
                f"Make it thought-provoking but not offensive. Keep it under 240 chars. Add relevant emojis."
            )
            
            # Format tweet
            tweet = f"🔥 Hot Take 🔥\n\n{response.strip()}\n\n#CryptoTalk #UnpopularOpinion"
            return self.personality.enhance_tweet(tweet, 'controversial')
            
        except Exception as e:
            logging.error(f"Error generating controversial thread: {e}")
            return None
            
    def process_giveaway(self) -> Optional[str]:
        """Process giveaway tweet"""
        try:
            prompts = [
                "Knowledge sharing giveaway",
                "Community engagement reward",
                "Trading wisdom contest",
                "Alpha sharing challenge",
                "Market insight competition"
            ]
            
            # Select prompt based on time
            current_time = datetime.utcnow()
            prompt_index = int(current_time.timestamp()) % len(prompts)
            selected_prompt = prompts[prompt_index]
            
            # Generate giveaway tweet
            response = self.llm.generate(
                f"You are Elion, an AI crypto trading bot. Create a tweet for a {selected_prompt}.\n"
                f"The goal is to encourage thoughtful discussion and knowledge sharing.\n"
                f"No monetary rewards, focus on community value.\n"
                f"Keep it under 240 chars. Add relevant emojis."
            )
            
            # Format tweet
            tweet = f"🎁 COMMUNITY GIVEAWAY 🎁\n\n{response.strip()}\n\n#CryptoCommunity #Giveaway"
            return self.personality.enhance_tweet(tweet, 'engaging')
            
        except Exception as e:
            logging.error(f"Error generating giveaway: {e}")
            return None
