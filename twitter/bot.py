"""Main Twitter bot class"""

import os
import time
import random
import logging
import schedule
import threading
from datetime import datetime, timedelta
import sys
from logging.handlers import RotatingFileHandler
import tempfile
import atexit

# Optional Redis import
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    
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

def is_bot_running():
    """Check if another instance is running using Redis lock"""
    try:
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, skipping lock check")
            return False
            
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            logger.warning("REDIS_URL not set, skipping lock check")
            return False
            
        redis_client = redis.from_url(redis_url)
        lock = redis_client.setnx('twitter_bot_lock', 'locked')
        if lock:
            # Set expiry to avoid deadlock if process crashes
            redis_client.expire('twitter_bot_lock', 300)  # 5 minute expiry
            return False
        return True
    except Exception as e:
        logger.error(f"Error checking Redis lock: {e}")
        return False

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
        
        # Track which format to use next
        self.current_format_index = 0  # 0-11 for A/B formats
        self.current_extra_index = 0   # 0-4 for additional types
        
        # Initialize Elion
        logger.info("Initializing Elion...")
        self.elion = Elion(GeminiComponent(
            api_key=os.getenv('AI_ACCESS_TOKEN'),
            api_base=os.getenv('AI_API_URL')
        ))
        
        # Setup tweet schedule
        logger.info("Setting up tweet schedule...")
        self._schedule_tweets()

    def _get_next_format(self) -> tuple:
        """Get next format to use and increment counter"""
        formats = [
            ('performance_compare', 'A'), ('performance_compare', 'B'),
            ('volume_breakout', 'A'), ('volume_breakout', 'B'),
            ('trend_momentum', 'A'), ('trend_momentum', 'B'),
            ('winners_recap', 'A'), ('winners_recap', 'B'),
            ('vmc_alert', 'A'), ('vmc_alert', 'B'),
            ('pattern_alert', 'A'), ('pattern_alert', 'B')
        ]
        
        format_type, variant = formats[self.current_format_index]
        self.current_format_index = (self.current_format_index + 1) % len(formats)
        logger.info(f"Using A/B format: {format_type} (variant {variant}), next index: {self.current_format_index}")
        return format_type, variant

    def _get_next_extra_type(self) -> str:
        """Get next additional type to use and increment counter"""
        extra_types = [
            'volume_alert',        # High volume signals
            'performance_update',  # Weekly stats
            'alpha',              # Trading opportunities
            'winners_recap',      # Recent successful calls
            'vmc_alert'          # Volume/MCap analysis
        ]
        
        extra_type = extra_types[self.current_extra_index]
        self.current_extra_index = (self.current_extra_index + 1) % len(extra_types)
        logger.info(f"Using extra type: {extra_type}, next index: {self.current_extra_index}")
        return extra_type

    def _schedule_tweets(self):
        """Schedule Elion's structured daily tweets"""
        # Clear existing schedule
        schedule.clear()
        logger.info("Cleared existing schedule")
        
        # === Trend Posts (6 per day) ===
        schedule.every().day.at("01:00").do(self.post_trend)     # Early Asian
        schedule.every().day.at("05:00").do(self.post_trend)     # Mid Asian
        schedule.every().day.at("09:00").do(self.post_trend)     # Early EU
        schedule.every().day.at("13:00").do(self.post_trend)     # Mid EU
        schedule.every().day.at("17:00").do(self.post_trend)     # Early US
        schedule.every().day.at("21:00").do(self.post_trend)     # Mid US

        # === Volume Posts (4 per day) ===
        schedule.every().day.at("03:00").do(self.post_volume)    # Asian
        schedule.every().day.at("11:00").do(self.post_volume)    # European
        schedule.every().day.at("15:00").do(self.post_volume)    # Early US
        schedule.every().day.at("19:00").do(self.post_volume)    # Mid US

        # === Core A/B Format Posts (6 per day) ===
        schedule.every().day.at("02:00").do(self.post_format_tweet)  # Early Asian
        schedule.every().day.at("06:00").do(self.post_format_tweet)  # Mid Asian
        schedule.every().day.at("10:00").do(self.post_format_tweet)  # Early EU
        schedule.every().day.at("14:00").do(self.post_format_tweet)  # Mid EU
        schedule.every().day.at("18:00").do(self.post_format_tweet)  # Early US
        schedule.every().day.at("22:00").do(self.post_format_tweet)  # Late US

        # === Additional Type Post (1 per day) ===
        schedule.every().day.at("12:00").do(self.post_extra_tweet)   # Mid-day personality

    def post_format_tweet(self):
        """Post tweet using next A/B format in rotation"""
        try:
            logger.info("=== Starting A/B Format Post ===")
            format_type, variant = self._get_next_format()
            
            # Try to get market data from volume strategy first
            market_data = self.elion.volume_strategy.analyze()
            if not market_data or ('spikes' not in market_data and 'anomalies' not in market_data):
                # Fallback to trend strategy
                logger.info("No volume data, trying trend strategy")
                market_data = self.elion.trend_strategy.analyze()
                if not market_data or 'trend_tokens' not in market_data:
                    logger.warning("No market data available from either strategy")
                    return
                logger.info("Using trend strategy data")
            else:
                logger.info("Using volume strategy data")
                
            # Generate tweet using format
            tweet = self.elion.format_tweet(format_type, market_data, variant=variant)
            if not tweet:
                logger.warning(f"Failed to format {format_type} tweet")
                # Try a different format as fallback
                fallback_format = 'winners_recap' if format_type != 'winners_recap' else 'volume_alert'
                tweet = self.elion.format_tweet(fallback_format, market_data, variant='A')
                if not tweet:
                    logger.warning("Failed to format fallback tweet")
                    return
                logger.info(f"Using fallback format: {fallback_format}")
                
            # Post tweet
            response = self.api.create_tweet(tweet)
            if response:
                logger.info(f"Posted {format_type} tweet (variant {variant})")
            else:
                logger.error(f"Failed to post {format_type} tweet")
                
        except Exception as e:
            logger.error(f"Error posting format tweet: {e}")

    def post_extra_tweet(self):
        """Post tweet using next additional type in rotation"""
        try:
            logger.info("=== Starting Extra Type Post ===")
            extra_type = self._get_next_extra_type()
            
            # Get market data if needed
            market_data = self.elion.get_market_data() if extra_type in ['alpha', 'volume_alert', 'performance_update'] else None
            
            # Generate tweet using format
            tweet = self.elion.format_tweet(extra_type, market_data)
            if not tweet:
                logger.warning(f"Failed to format {extra_type} tweet")
                return
                
            # Post tweet
            response = self.api.create_tweet(tweet)
            if response:
                logger.info(f"Posted {extra_type} tweet")
            else:
                logger.error(f"Failed to post {extra_type} tweet")
                
        except Exception as e:
            logger.error(f"Error posting extra tweet: {e}")

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
            # Get token performance data
            token_data = self.elion.token_history.get_recent_performance()
            
            # Alternate between token and portfolio updates
            if random.random() < 0.5:  # 50% chance for each type
                # Token performance update
                tweet = self.elion.format_tweet('performance_compare', token_data, variant='A')
            else:
                # Portfolio performance update - use token data as fallback
                tweet = self.elion.format_tweet('performance_compare', token_data, variant='B')
            
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
            
    def post_trend(self):
        """Post trend analysis tweet"""
        try:
            logger.info("=== Starting Trend Analysis Post ===")
            # Get trend analysis
            trend_data = self.elion.trend_strategy.analyze()
            if not trend_data:
                logger.warning("No trend data available")
                return
            
            # Filter out excluded tokens
            trend_tokens = [
                token for token in trend_data.get('trend_tokens', [])
                if self.is_valid_token(token.get('symbol'))
            ]
            
            if not trend_tokens:
                logger.warning("No valid tokens after filtering")
                return
            
            # Format trend tweet using strategy's own formatter
            tweet = self.elion.trend_strategy.format_twitter_output(trend_tokens)
            if not tweet:
                logger.warning("Failed to format trend tweet")
                return
                
            # Post tweet and track tokens
            response = self.api.create_tweet(tweet)
            if response:
                logger.info("Posted trend analysis tweet")
                # Track tokens using TokenMonitor
                self.elion.token_monitor.run_analysis()
            else:
                logger.error("Failed to post trend tweet")
                
        except Exception as e:
            logger.error(f"Error posting trend tweet: {e}")

    def post_volume(self):
        """Post volume analysis tweet"""
        try:
            logger.info("=== Starting Volume Analysis Post ===")
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
            history = self.elion.token_monitor.history_tracker.get_all_token_history()
            tweet = self.elion.tweet_formatters.format_volume_breakout(volume_data, history)
            if not tweet:
                # Try fallback to winners recap
                tweet = self.elion.tweet_formatters.format_winners_recap(history)
            if not tweet:
                logger.warning("Failed to format volume tweet")
                return
                
            # Post tweet and track tokens
            response = self.api.create_tweet(tweet)
            if response:
                logger.info("Posted volume analysis tweet")
                # Track tokens using TokenMonitor
                self.elion.token_monitor.run_analysis()
            else:
                logger.error("Failed to post volume tweet")
                
        except Exception as e:
            logger.error(f"Error posting volume tweet: {e}")

    def run(self):
        """Run the bot"""
        logger.info("=== Starting Bot with Schedule ===")
        logger.info("Trend Posts: 01:00, 05:00, 09:00, 13:00, 17:00, 21:00 UTC")
        logger.info("Volume Posts: 03:00, 11:00, 15:00, 19:00 UTC")
        logger.info("A/B Format Posts: 02:00, 06:00, 10:00, 14:00, 18:00, 22:00 UTC")
        logger.info("Extra Type Post: 12:00 UTC")
        
        while True:
            try:
                schedule.run_pending()
                next_job = schedule.next_run()
                if next_job:
                    minutes_until = int((next_job - datetime.now()).total_seconds() / 60)
                    next_job_time = next_job.strftime("%H:%M UTC")
                    logger.info(f"Next tweet scheduled for {next_job_time} ({minutes_until} minutes from now)")
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
    
    if is_bot_running():
        logger.error("Another instance of the bot is already running!")
        sys.exit(1)
    
    logger.info("Starting Twitter bot...")
    bot = AIGamingBot()
    bot.run()
