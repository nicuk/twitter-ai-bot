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
        
        # Map hours to specific formats
        hour_to_format = {
            2: 'first_hour',            # Early Asian
            6: 'breakout',              # Mid Asian
            10: 'prediction_accuracy',   # Early EU
            14: 'success_rate',         # Mid EU
            18: 'performance_compare',   # Early US
            22: 'winners_recap'         # Late US
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
        
        # === Trend Posts (7 per day) ===
        schedule.every().day.at("00:00").do(self.post_trend)     # Midnight
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

    def _post_tweet(self, tweet):
        """Post a tweet with error handling and backup content"""
        try:
            # Try to post main tweet
            response = self.api.create_tweet(tweet)
            if response:
                logger.info(f"Posted tweet: {tweet}")
                return True
                
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
            
            # Get market data
            market_data = self.elion.get_market_data()
            if not market_data:
                logger.warning("No market data available")
                return self._post_fallback_tweet()
            
            # Generate tweet using format
            tweet = self.elion.format_tweet(format_type, market_data)
            if not tweet:
                logger.warning(f"Failed to format {format_type} tweet")
                return self._post_fallback_tweet()
            
            # Post tweet
            self._post_tweet(tweet)
                
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
        """Post performance update for latest token"""
        try:
            logger.info("\n=== Starting Performance Post ===")
            logger.info(f"Current time: {datetime.utcnow()}")
            
            # Get token performance data
            logger.info("Fetching latest token data...")
            token_data = self.elion.token_monitor.get_latest_token()
            if not token_data:
                logger.warning("No token data available for performance update")
                return False
                
            logger.info(f"Latest token data: {token_data}")
                
            # Format performance tweet
            logger.info("Formatting performance tweet...")
            tweet = self.elion.format_tweet('performance_compare', {'token': token_data}, variant='A')
            
            if not tweet:
                logger.warning("Failed to generate performance tweet")
                return False
            
            logger.info(f"Generated tweet: {tweet[:100]}...")
            
            # Post tweet with rate limiting
            self.rate_limiter.wait()
            self._post_tweet(tweet)
            
            logger.info(f"Posted performance update: {tweet[:100]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error posting performance update: {str(e)}")
            logger.exception("Full traceback:")
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
            logger.info("\n=== Starting Trend Analysis Post ===")
            logger.info(f"Current time: {datetime.utcnow()}")
            
            # Get trend analysis
            logger.info("Fetching trend data from Elion...")
            trend_data = self.elion.trend_strategy.analyze()
            if not trend_data:
                logger.warning("No trend data available")
                return self._post_fallback_tweet()
                
            logger.info(f"Raw trend data: {trend_data}")
            
            # Filter out excluded tokens
            trend_tokens = [
                token for token in trend_data.get('trend_tokens', [])
                if self.is_valid_token(token.get('symbol'))
            ]
            
            logger.info(f"Found {len(trend_tokens)} valid tokens after filtering")
            if not trend_tokens:
                logger.warning("No valid tokens after filtering")
                return self._post_fallback_tweet()
            
            # Format trend tweet using strategy's own formatter
            logger.info("Formatting trend tweet...")
            tweet = self.elion.trend_strategy.format_twitter_output(trend_tokens)
            if not tweet:
                logger.warning("Failed to format trend tweet")
                return self._post_fallback_tweet()
                
            logger.info(f"Generated tweet: {tweet[:100]}...")
                
            # Post tweet
            self._post_tweet(tweet)
            return True
                
        except Exception as e:
            logger.error(f"Error posting trend tweet: {e}")
            logger.exception("Full traceback:")
            return self._post_fallback_tweet()

    def post_volume(self):
        """Post volume analysis tweet"""
        try:
            logger.info("\n=== Starting Volume Analysis Post ===")
            logger.info(f"Current time: {datetime.utcnow()}")
            
            # Get volume data
            logger.info("Fetching volume data from Elion...")
            volume_data = self.elion.volume_strategy.analyze()
            if not volume_data:
                logger.warning("No volume data available")
                return self._post_fallback_tweet()
                
            logger.info(f"Raw volume data: {volume_data}")
            
            # Format volume tweet
            logger.info("Formatting volume tweet...")
            tweet = self.elion.volume_strategy.format_twitter_output(volume_data)
            if not tweet:
                logger.warning("Failed to format volume tweet")
                return self._post_fallback_tweet()
                
            logger.info(f"Generated tweet: {tweet[:100]}...")
            
            # Post tweet
            self._post_tweet(tweet)
            return True
            
        except Exception as e:
            logger.error(f"Error posting volume tweet: {e}")
            logger.exception("Full traceback:")
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

    def force_post(self, post_type: str, bypass_lock: bool = True):
        """Force an immediate post without waiting for schedule
        
        Args:
            post_type: Type of post to force ('trend', 'volume', 'performance', 'format', 'ai_mystique')
            bypass_lock: If True, bypasses the Redis lock check (use carefully!)
        """
        logger.info(f"\n=== Forcing immediate {post_type} post ===")
        
        # Check if another instance is running (unless bypassing)
        if not bypass_lock:
            is_running = is_bot_running()
            if is_running:
                logger.warning("Another bot instance is running. Skipping force post.")
                return False
        else:
            logger.warning("Bypassing Redis lock for testing!")
            
        try:
            # Map post types to methods
            post_methods = {
                'trend': self.post_trend,
                'volume': self.post_volume,
                'performance': self.post_performance,
                'format': self.post_format_tweet,
                'ai_mystique': self.post_ai_mystique
            }
            
            # Get the post method
            post_method = post_methods.get(post_type)
            if not post_method:
                logger.error(f"Invalid post type: {post_type}")
                return False
                
            # Execute the post
            logger.info(f"Executing {post_type} post...")
            return post_method()
            
        except Exception as e:
            logger.error(f"Error forcing {post_type} post: {str(e)}")
            logger.exception("Full traceback:")
            return False

    def run(self):
        """Run the bot"""
        try:
            # Check if another instance is running
            if is_bot_running():
                logger.error("Another bot instance is already running")
                return
                
            logger.info("=== Bot Status ===")
            logger.info("✓ Redis connection: Active")
            logger.info("✓ Twitter API: Initialized")
            logger.info("✓ Schedule: Set up")
            
            # Log all scheduled jobs
            logger.info("\n=== Scheduled Tasks ===")
            all_jobs = schedule.get_jobs()
            
            # Group jobs by function name and find earliest run time for each
            job_groups = {}
            for job in all_jobs:
                func_name = job.job_func.__name__
                next_run = job.next_run
                if next_run:
                    mins_to_next = int((next_run - datetime.now()).total_seconds() / 60)
                    if func_name not in job_groups or mins_to_next < job_groups[func_name]:
                        job_groups[func_name] = mins_to_next
            
            # Display next occurrence of each task type
            for func_name, mins in sorted(job_groups.items(), key=lambda x: x[1]):
                hours = mins // 60
                remaining_mins = mins % 60
                if hours > 0:
                    logger.info(f"• {func_name}: Next run in {hours}h {remaining_mins}m")
                else:
                    logger.info(f"• {func_name}: Next run in {mins}m")
            
            # Get and log next job
            next_run = schedule.next_run()
            if next_run:
                # Find the next job(s)
                next_jobs = [
                    job for job in schedule.get_jobs()
                    if job.next_run == next_run
                ]
                
                mins_to_next = int((next_run - datetime.now()).total_seconds() / 60)
                hours = mins_to_next // 60
                remaining_mins = mins_to_next % 60
                
                logger.info(f"\n=== Next Tweet ===")
                # Map function names to friendly names
                tweet_types = {
                    'post_trend': 'Trend Analysis',
                    'post_volume': 'Volume Alert',
                    'post_format_tweet': 'ELAI Update',
                    'post_extra_tweet': 'Market Insight',
                    '_post_fallback_tweet': 'Fallback Tweet'
                }
                
                for job in next_jobs:
                    tweet_type = tweet_types.get(job.job_func.__name__, 'Fallback Tweet')
                    if hours > 0:
                        logger.info(f"{tweet_type}: {hours}h {remaining_mins}m")
                    else:
                        logger.info(f"{tweet_type}: {mins_to_next}m")
            
            # Run pending tasks immediately
            schedule.run_pending()
            
            # Main loop
            last_log_time = datetime.now()
            last_health_check = datetime.now()
            
            logger.info("\n=== Bot Running ===")
            logger.info("Monitoring for scheduled tasks...")
            
            while True:
                schedule.run_pending()
                now = datetime.now()
                
                # Log next scheduled tweet (every minute)
                if (now - last_log_time).total_seconds() >= 60:
                    next_run = schedule.next_run()
                    if next_run:
                        # Find the next job(s)
                        next_jobs = [
                            job for job in schedule.get_jobs()
                            if job.next_run == next_run
                        ]
                        
                        mins_to_next = int((next_run - now).total_seconds() / 60)
                        hours = mins_to_next // 60
                        remaining_mins = mins_to_next % 60
                        
                        # Map function names to friendly names
                        tweet_types = {
                            'post_trend': 'Trend Analysis',
                            'post_volume': 'Volume Alert',
                            'post_format_tweet': 'ELAI Update',
                            'post_extra_tweet': 'Market Insight',
                            '_post_fallback_tweet': 'Fallback Tweet'
                        }
                        
                        for job in next_jobs:
                            tweet_type = tweet_types.get(job.job_func.__name__, 'Fallback Tweet')
                            if hours > 0:
                                logger.info(f"Next tweet: {tweet_type} in {hours}h {remaining_mins}m")
                            else:
                                logger.info(f"Next tweet: {tweet_type} in {mins_to_next}m")
                    last_log_time = now
                
                # Health check (every hour)
                if (now - last_health_check).total_seconds() >= 3600:
                    logger.info("\n=== Health Check ===")
                    try:
                        # Check Redis
                        redis_url = os.getenv('REDIS_URL')
                        if redis_url:
                            redis_client = redis.from_url(redis_url)
                            redis_client.ping()
                            logger.info("✓ Redis: Connected")
                        
                        # Check scheduled jobs
                        if len(schedule.get_jobs()) > 0:
                            logger.info("✓ Scheduler: Active")
                            
                        logger.info("All systems operational")
                    except Exception as e:
                        logger.error(f"Health check failed: {e}")
                    
                    last_health_check = now
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            logger.exception("Full traceback:")  # Add full traceback
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
