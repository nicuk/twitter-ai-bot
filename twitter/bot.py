"""Main Twitter bot class"""

import os
import time
import random
import logging
import schedule
from datetime import datetime, timedelta
import sys
from logging.handlers import RotatingFileHandler

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('tweet_activity.log', maxBytes=5*1024*1024, backupCount=3),  # 5MB per file, keep 3 backup files
        logging.StreamHandler(sys.stdout)  # Add console output
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting Twitter bot...")

from custom_llm import GeminiComponent
from twitter.api_client import TwitterAPI
from twitter.rate_limiter import RateLimiter
from twitter.history_manager import TweetHistory
from elion.elion import Elion

class AIGamingBot:
    """Twitter bot for AI-powered crypto insights"""
    
    # Tokens to exclude from all analysis
    EXCLUDED_TOKENS = {'BTC', 'ETH'}
    
    def __init__(self):
        """Initialize Twitter bot"""
        logger.info("\nInitializing Twitter bot...")
        
        # Initialize retry settings
        self.max_retries = 3
        self.base_wait = 5  # Base wait time in minutes
        self.retry_count = 0
        
        # Initialize core components
        self.api = TwitterAPI()
        self.rate_limiter = RateLimiter()
        self.history = TweetHistory()
        
        # Initialize Elion
        logger.info("Initializing Elion...")
        self.elion = Elion(GeminiComponent(
            api_key=os.getenv('AI_ACCESS_TOKEN'),
            api_base=os.getenv('AI_API_URL')
        ))
        
        # Setup tweet schedule
        logger.info("Setting up tweet schedule...")
        self._schedule_tweets()

    def _schedule_tweets(self):
        """Schedule Elion's structured daily tweets"""
        # === Asian Trading Session (00:00-08:00 UTC) ===
        
        # Early Asian Market (00:00-03:00)
        schedule.every().day.at("00:00").do(self.post_trend)    # Opening trends
        schedule.every().day.at("01:30").do(self.post_volume)   # Early volume check
        schedule.every().day.at("02:30").do(self.post_ai_mystique)  # AI insights
        
        # Main Asian Market (03:00-08:00)
        schedule.every().day.at("04:00").do(self.post_trend)    # Mid-Asian trends
        schedule.every().day.at("05:30").do(self.post_volume)   # Volume analysis
        schedule.every().day.at("06:00").do(self.post_performance)  # Performance update
        schedule.every().day.at("07:30").do(self.post_trend)    # Late Asian trends

        # === US Trading Session (11:00-21:00 UTC) ===
        
        # Pre-market (11:00-14:30)
        schedule.every().day.at("11:30").do(self.post_trend)    # Pre-market trends
        schedule.every().day.at("12:30").do(self.post_volume)   # Pre-market volume
        schedule.every().day.at("13:30").do(self.post_ai_mystique)  # Market insights
        
        # Main US Session (14:30-21:00)
        schedule.every().day.at("15:00").do(self.post_performance)  # Mid-day performance
        schedule.every().day.at("16:30").do(self.post_trend)    # Mid-session trends
        schedule.every().day.at("17:30").do(self.post_volume)   # Volume check
        schedule.every().day.at("18:30").do(self.post_performance)  # Performance update
        schedule.every().day.at("19:30").do(self.post_trend)    # Late session trends
        
        # Evening wrap-up (20:00-23:00)
        schedule.every().day.at("20:30").do(self.post_summary)    # Evening summary
        schedule.every().day.at("22:30").do(self.post_summary)    # Final summary

    def is_valid_token(self, symbol: str) -> bool:
        """Check if token should be included in analysis"""
        if not symbol:
            return False
        return symbol.upper() not in self.EXCLUDED_TOKENS

    def post_ai_mystique(self):
        """Post AI mystique tweet"""
        try:
            # Get market data
            market_data = self.elion.get_market_data()
            
            # Generate mystique tweet
            content = self.elion.content.generate_ai_mystique(market_data)
            if not content:
                logger.warning("Failed to generate AI mystique tweet, using fallback")
                content = "🤖 *Processing market data... neural nets recalibrating* Meanwhile, stay sharp and watch those charts! 👀"
                
            # Post tweet using correct method name
            response = self.api.create_tweet(content)
            if response:
                logger.info("Posted AI mystique tweet")
            else:
                logger.error("Failed to post AI mystique tweet")
            
        except Exception as e:
            logger.error(f"Error posting AI mystique tweet: {e}")
            
    def post_performance(self):
        """Post performance update, alternating between token and portfolio performance"""
        try:
            # Get portfolio data
            portfolio = self.elion.portfolio_tracker.get_portfolio_summary()
            
            # Alternate between token and portfolio updates
            if random.random() < 0.5:  # 50% chance for each type
                # Token performance update
                token_data = self.elion.token_history.get_recent_performance()
                tweet = self.elion.format_tweet('performance_compare', token_data, variant='A')
            else:
                # Portfolio performance update
                tweet = self.elion.format_tweet('performance_compare', portfolio, variant='B')
            
            # Post tweet with rate limiting
            self.rate_limiter.wait()
            self.api.post_tweet(tweet)
            
            logger.info(f"Posted performance update: {tweet[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error posting performance update: {str(e)}")
            return False

    def post_summary(self):
        """Post summary tweet"""
        try:
            # Generate summary tweet
            content = self.elion.content.generate_summary_post()
            if not content:
                logger.warning("Failed to generate summary tweet")
                return
                
            # Post tweet
            response = self.api.create_tweet(content)
            if response:
                logger.info("Posted summary tweet")
            else:
                logger.error("Failed to post summary tweet")
            
        except Exception as e:
            logger.error(f"Error posting summary tweet: {e}")
            
    def post_volume(self):
        """Post volume analysis tweet"""
        try:
            # Get volume analysis
            volume_data = self.elion.volume_strategy.analyze()
            if not volume_data:
                logger.warning("No volume data available")
                return
            
            # Filter out excluded tokens
            if 'spikes' in volume_data:
                volume_data['spikes'] = [
                    (score, data) for score, data in volume_data['spikes']
                    if self.is_valid_token(data.get('symbol'))
                ]
            
            if 'anomalies' in volume_data:
                volume_data['anomalies'] = [
                    (score, data) for score, data in volume_data['anomalies']
                    if self.is_valid_token(data.get('symbol'))
                ]
            
            # Skip if no valid tokens after filtering
            if not (volume_data.get('spikes') or volume_data.get('anomalies')):
                logger.warning("No valid tokens after filtering")
                return
            
            # Format volume tweet using filtered data
            tweet = self.elion.tweet_formatters.format_volume_insight(volume_data, self.elion.personality.get_trait())
            if not tweet:
                logger.warning("Failed to format volume tweet")
                return
                
            # Post tweet
            response = self.api.create_tweet(tweet)
            if response:
                logger.info("Posted volume analysis tweet")
                
                # Track tokens mentioned in tweet
                for token_list in [volume_data.get('spikes', []), volume_data.get('anomalies', [])]:
                    for _, token_data in token_list:
                        if 'symbol' in token_data:
                            self.elion.token_monitor.track_token(token_data['symbol'])
            else:
                logger.error("Failed to post volume tweet")
                
        except Exception as e:
            logger.error(f"Error posting volume tweet: {e}")

    def post_trend(self):
        """Post portfolio performance update"""
        try:
            # Get portfolio data
            portfolio = self.elion.portfolio_tracker.get_portfolio_summary()
            
            # Generate portfolio performance tweet
            tweet = self.elion.format_tweet('performance_compare', portfolio, variant='B')
            if not tweet:
                logger.warning("Failed to format portfolio tweet")
                return
                
            # Post tweet using TwitterAPI's create_tweet method
            response = self.api.create_tweet(tweet)
            if response:
                logger.info("Posted portfolio performance tweet")
            else:
                logger.error("Failed to post portfolio tweet")
                
        except Exception as e:
            logger.error(f"Error posting portfolio tweet: {e}")

    def run(self):
        """Run the bot"""
        logger.info("Starting bot...")
        
        while True:
            try:
                schedule.run_pending()
                next_job = schedule.next_run()
                if next_job:
                    minutes_until = int((next_job - datetime.now()).total_seconds() / 60)
                    logger.info(f"Next tweet in {minutes_until} minutes")
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    bot = AIGamingBot()
    bot.run()
