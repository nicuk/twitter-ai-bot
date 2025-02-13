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
import tweepy

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

def cleanup_redis_lock():
    """Clean up Redis lock on exit"""
    try:
        if REDIS_AVAILABLE:
            redis_url = os.getenv('REDIS_URL')
            if redis_url:
                redis_client = redis.from_url(redis_url)
                instance_id = os.getenv('RAILWAY_REPLICA_ID', 'local-' + str(os.getpid()))
                # Only remove lock if it belongs to this instance
                current_holder = redis_client.get('twitter_bot_lock')
                if current_holder and current_holder.decode() == instance_id:
                    redis_client.delete('twitter_bot_lock')
                    logger.info(f"Redis lock released by instance {instance_id}")
    except Exception as e:
        logger.error(f"Error cleaning up Redis lock: {e}")

def check_single_instance():
    """Ensure only one instance is running"""
    try:
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available for instance locking")
            return True
            
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            logger.warning("REDIS_URL not set for instance locking")
            return True
            
        redis_client = redis.from_url(redis_url)
        instance_id = os.getenv('RAILWAY_REPLICA_ID', 'local-' + str(os.getpid()))
        
        # Try to get the lock
        lock = redis_client.setnx('twitter_bot_lock', instance_id)
        if lock:
            # We got the lock, set expiry and register cleanup
            redis_client.expire('twitter_bot_lock', 300)  # 5 minute expiry
            atexit.register(cleanup_redis_lock)
            logger.info(f"Instance {instance_id} acquired lock and will start")
            return True
            
        # Check if lock is stale
        ttl = redis_client.ttl('twitter_bot_lock')
        current_holder = redis_client.get('twitter_bot_lock')
        
        if ttl in (-2, -1):  # Key doesn't exist or no expiry
            redis_client.delete('twitter_bot_lock')
            return check_single_instance()  # Try again
            
        # Another instance is running
        logger.error(f"Another bot instance ({current_holder.decode()}) is already running (TTL: {ttl}s). This instance ({instance_id}) will exit.")
        return False
            
    except Exception as e:
        logger.error(f"Error checking instance lock: {e}")
        return True  # Allow running if Redis check fails

def is_bot_running():
    """Check if another instance is running using Redis lock"""
    try:
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, skipping lock check")
            return False
            
        redis_url = os.getenv('REDIS_URL')  # Railway format
        if not redis_url:
            logger.warning("REDIS_URL not set, skipping lock check")
            return False
            
        logger.info("Checking Redis lock...")
        redis_client = redis.from_url(redis_url)
        
        # Generate unique instance ID if not exists
        instance_id = os.getenv('RAILWAY_REPLICA_ID', 'local-' + str(os.getpid()))
        
        # First try to get the lock
        lock = redis_client.setnx('twitter_bot_lock', instance_id)
        if lock:
            # We got the lock
            logger.info(f"Got Redis lock (Instance: {instance_id})")
            redis_client.expire('twitter_bot_lock', 300)  # 5 minute expiry
            return False
            
        # If we didn't get the lock, check if it's stale
        ttl = redis_client.ttl('twitter_bot_lock')
        current_holder = redis_client.get('twitter_bot_lock')
        logger.info(f"Lock exists with TTL: {ttl}s, held by Instance: {current_holder}")
        
        if ttl == -2:  # Key doesn't exist
            logger.info("Lock doesn't exist, clearing")
            redis_client.delete('twitter_bot_lock')
            return False
            
        if ttl == -1:  # No expiry set
            logger.info("Lock has no expiry, clearing stale lock")
            redis_client.delete('twitter_bot_lock')
            return False
            
        # Lock exists and has valid TTL
        sleep_time = 60  # 1 minute
        logger.warning(f"Redis Lock: Another bot instance ({current_holder}) is running (TTL: {ttl}s). This instance ({instance_id}) will sleep for {sleep_time} seconds to avoid conflicts.")
        time.sleep(sleep_time)
        return True
            
    except Exception as e:
        logger.error(f"Error checking Redis lock: {e}")
        return False

from custom_llm import GeminiComponent
from twitter.api_client import TwitterAPI
from twitter.rate_limiter import RateLimiter
from twitter.history_manager import TweetHistory
from elion.elion import Elion
from strategies.volume_strategy import VolumeStrategy

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

    def _get_next_format(self) -> str:
        """Get next format to use based on current hour"""
        from elion.content.tweet_formatters import FORMATTERS
        
        current_hour = datetime.now().hour
        
        # Map hours to specific formats for our 7 daily format posts
        hour_to_format = {
            2: 'performance_compare',   # Early Asian
            4: 'prediction_accuracy',   # Mid Asian
            8: 'success_rate',         # Early EU
            12: 'winners_recap',       # Mid EU
            16: 'performance_compare', # Early US
            20: 'prediction_accuracy', # Mid US
            22: 'success_rate'         # Late US
        }
        
        # Get format for current hour
        format_type = hour_to_format.get(current_hour, 'winners_recap')
        
        # Check if format is available, fallback to winners_recap
        if not FORMATTERS.get(format_type):
            logger.info(f"Format {format_type} not available, falling back to winners_recap")
            format_type = 'winners_recap'
            
        logger.info(f"Using format: {format_type} at hour {current_hour}")
        return format_type

    def _get_next_extra_type(self) -> str:
        """Get next additional type - now just returns AI mystique"""
        return 'ai_mystique'

    def _schedule_tweets(self):
        """Schedule Elion's structured daily tweets"""
        # Clear existing schedule
        schedule.clear()
        logger.info("Cleared existing schedule")
        
        # === Trend Posts (6 per day) ===
        schedule.every().day.at("01:30").do(self.post_trend)     # Early Asian
        schedule.every().day.at("05:00").do(self.post_trend)     # Mid Asian
        schedule.every().day.at("09:00").do(self.post_trend)     # Early EU
        schedule.every().day.at("13:00").do(self.post_trend)     # Mid EU
        schedule.every().day.at("17:30").do(self.post_trend)     # Early US
        schedule.every().day.at("21:00").do(self.post_trend)     # Mid US

        # === Volume Posts (4 per day) ===
        schedule.every().day.at("03:00").do(self.post_volume)    # Asian
        schedule.every().day.at("11:00").do(self.post_volume)    # European
        schedule.every().day.at("15:00").do(self.post_volume)    # Early US
        schedule.every().day.at("19:00").do(self.post_volume)    # Mid US

        # === Core A/B Format Posts (7 per day) ===
        schedule.every().day.at("02:30").do(self.post_format_tweet)  # Early Asian (after trend)
        schedule.every().day.at("04:00").do(self.post_format_tweet)  # Mid Asian
        schedule.every().day.at("08:00").do(self.post_format_tweet)  # Early EU
        schedule.every().day.at("12:00").do(self.post_format_tweet)  # Mid EU
        schedule.every().day.at("16:30").do(self.post_format_tweet)  # Early US
        schedule.every().day.at("20:00").do(self.post_format_tweet)  # Mid US
        schedule.every().day.at("22:00").do(self.post_format_tweet)  # Late US (before trend)

    def _post_tweet(self, tweet):
        """Post a tweet with error handling and backup content"""
        try:
            # Wait for rate limit before posting
            self.rate_limiter.wait()
            
            # Try to post main tweet
            response = self.api.create_tweet(tweet)
            if response:
                logger.info(f"Posted tweet: {tweet}")
                return True
                
        except tweepy.errors.TooManyRequests:
            # Let rate limit errors propagate up
            raise
        except Exception as e:
            # If it's a duplicate content error, don't try backup tweet
            if "duplicate content" in str(e).lower():
                logger.warning("Duplicate tweet detected, skipping backup attempt")
                return False
                
            logger.error(f"Error posting main tweet: {e}")
            
            # Only try backup tweet for non-duplicate errors
            try:
                logger.info("Attempting to post backup tweet...")
                backup_tweet = self.elion.tweet_formatters.get_backup_tweet()
                if backup_tweet:
                    response = self.api.create_tweet(backup_tweet)
                    if response:
                        logger.info(f"Posted backup tweet: {backup_tweet}")
                        return True
                    
            except Exception as e:
                logger.error(f"Error posting backup tweet: {e}")
            
        return False

    def post_format_tweet(self):
        """Post tweet using format based on current hour"""
        try:
            logger.info("=== Starting Format Post ===")
            format_type = self._get_next_format()
            logger.info(f"Formatting tweet type: {format_type}")
            
            # Get token history data from token monitor
            history_data = self.elion.token_monitor.history_tracker.get_recent_performance()
            if not history_data:
                logger.warning("No token history data available")
                return self._post_fallback_tweet()
                
            # For performance_compare, also get current market data
            market_data = None
            if format_type == 'performance_compare':
                market_data = self.elion.get_market_data()
                if not market_data:
                    logger.warning("No market data available for performance compare")
                    return self._post_fallback_tweet()
            
            # Format tweet using appropriate data
            tweet = None
            if format_type == 'performance_compare':
                tweet = self.elion.format_tweet(format_type, market_data)
            else:
                # Convert history data to the format expected by formatters
                formatted_data = {
                    'tokens': [
                        {
                            'symbol': symbol,
                            'gain_percentage': data.get('gain_percentage', 0),
                            'first_mention_date': data.get('first_mention_date'),
                            'volume_24h': data.get('current_volume', 0),
                            'current_mcap': data.get('current_mcap', 0)
                        }
                        for symbol, data in history_data.items()
                    ]
                }
                tweet = self.elion.format_tweet(format_type, formatted_data)
                
            if not tweet:
                logger.warning(f"Failed to format {format_type} tweet")
                return self._post_fallback_tweet()
                
            # Post the tweet
            return self._post_tweet(tweet)
            
        except Exception as e:
            logger.error(f"Error posting format tweet: {e}")
            return self._post_fallback_tweet()

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
            self._post_tweet(content)
            
        except Exception as e:
            logger.error(f"Error posting AI mystique tweet: {e}")
            
    def post_performance(self):
        """Post performance update for tokens"""
        try:
            # Get token performance data
            token_data = self.elion.token_history.get_recent_performance()
            
            # Format performance tweet
            tweet = self.elion.format_tweet('performance_compare', token_data)
            
            # Post tweet with rate limiting
            self.rate_limiter.wait()
            self._post_tweet(tweet)
            
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
            self._post_tweet(content)
            
        except Exception as e:
            logger.error(f"Error posting summary tweet: {e}")
            
    def post_trend(self):
        """Post trend analysis tweet"""
        try:
            logger.info("=== Starting Trend Analysis Post ===")
            
            # Get fresh trend analysis
            trend_data = self.elion.trend_strategy.analyze()
            if not trend_data:
                logger.warning("No trend data available")
                return self._post_fallback_tweet()
            
            # Filter out excluded tokens
            trend_tokens = [
                token for token in trend_data.get('trend_tokens', [])
                if self.is_valid_token(token.get('symbol'))
            ]
            
            if not trend_tokens:
                logger.warning("No valid tokens after filtering")
                return self._post_fallback_tweet()
            
            # Format trend tweet using strategy's own formatter
            tweet = self.elion.trend_strategy.format_twitter_output(trend_tokens)
            if not tweet:
                logger.warning("Failed to format trend tweet")
                return self._post_fallback_tweet()
                
            # Post tweet and track tokens
            try:
                if self._post_tweet(tweet):
                    # Only track tokens if tweet was successful
                    for token in trend_tokens:
                        self.history.track_token(token['symbol'])
                    return True
                return False
            except tweepy.errors.TooManyRequests:
                # If we hit rate limit, don't use fallback
                raise
            except Exception as e:
                logger.error(f"Error posting trend tweet: {e}")
                return self._post_fallback_tweet()
                
        except Exception as e:
            logger.error(f"Error in trend analysis: {e}")
            return self._post_fallback_tweet()

    def post_volume(self):
        """Post volume analysis tweet"""
        try:
            # Get volume data from strategy
            volume_data = self.elion.volume_strategy.analyze()
            
            if not volume_data:
                logger.warning("No volume data available")
                return self._post_fallback_tweet()
            
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
                return self._post_fallback_tweet()
            
            # Format volume tweet using filtered data
            history = self.elion.token_monitor.history_tracker.get_recent_performance()
            
            # Get the highest V/MC ratio token from spikes and anomalies
            all_tokens = []
            if volume_data.get('spikes'):
                all_tokens.extend(volume_data['spikes'])
            if volume_data.get('anomalies'):
                all_tokens.extend(volume_data['anomalies'])
                
            if not all_tokens:
                logger.warning("No tokens to process")
                return self._post_fallback_tweet()
                
            # Get token with highest score
            score, token = max(all_tokens, key=lambda x: x[0])
            
            # Format tweet
            tweet = self.elion.volume_strategy.format_twitter_output(
                volume_data.get('spikes', []),
                volume_data.get('anomalies', []),
                history=history  # Pass history data to the formatter
            )
            
            if not tweet:
                logger.warning("Failed to format volume tweet")
                return self._post_fallback_tweet()
                
            # Post tweet and track tokens
            self._post_tweet(tweet)
            # Track tokens using TokenMonitor
            self.elion.token_monitor.run_analysis()
                
        except Exception as e:
            logger.error(f"Error posting volume tweet: {e}")
            logger.exception("Full traceback:")  # Add full traceback for debugging
            return self._post_fallback_tweet()

    def _post_fallback_tweet(self):
        """Post a fallback tweet when main tweet generation fails"""
        try:
            logger.info("Attempting to post fallback tweet...")
            backup_tweet = self.elion.tweet_formatters.get_backup_tweet()
            if backup_tweet:
                return self._post_tweet(backup_tweet)
            else:
                logger.error("No backup tweet available")
                return False
        except Exception as e:
            logger.error(f"Error posting fallback tweet: {e}")
            return False

    def is_valid_token(self, symbol: str) -> bool:
        """Check if token should be included in analysis"""
        if not symbol:
            return False
        return symbol.upper() not in self.EXCLUDED_TOKENS

    def run(self):
        """Run the bot"""
        try:
            # Clear any pending jobs from schedule
            schedule.clear()
            
            # Set up fresh schedule starting from next occurrence
            self._schedule_tweets()
            
            # Track last post time
            last_post_time = 0
            min_post_delay = 300  # 5 minutes between posts
            
            # Run continuously
            while True:
                try:
                    current_time = time.time()
                    
                    # Only process a job if enough time has passed since last post
                    if current_time - last_post_time >= min_post_delay:
                        # Get all pending jobs
                        pending_jobs = [job for job in schedule.get_jobs() if job.should_run]
                        
                        if pending_jobs:
                            # Sort jobs by their next run time
                            pending_jobs.sort(key=lambda job: job.next_run)
                            
                            # Only run the earliest job
                            try:
                                job = pending_jobs[0]
                                logger.info(f"Running scheduled job: {job.job_func.__name__}")
                                job.run()
                                last_post_time = current_time
                                
                            except tweepy.errors.TooManyRequests:
                                # Handle rate limit with proper cooldown
                                self.rate_limiter.handle_rate_limit()
                            except Exception as e:
                                logger.error(f"Error running scheduled job: {e}")
                    
                    time.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(60)  # Wait before retrying
                
        except Exception as e:
            logger.error(f"Error in bot run loop: {e}")
            raise

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Only start if we're the single instance
    if check_single_instance():
        bot = AIGamingBot()
        bot.run()
    else:
        logger.error("Exiting: Another instance is already running")
        sys.exit(1)
