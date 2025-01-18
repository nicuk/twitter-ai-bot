import tweepy
import schedule
import time
from datetime import datetime, timedelta
import requests
import os
import json
import logging
from dotenv import load_dotenv
from typing import Dict, List, Optional
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import sys
import random

from elion.elion import Elion
from elion.data_sources import DataSources
from tweet_history_manager import TweetHistoryManager
from custom_llm import MetaLlamaComponent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
logger.info("Loading environment variables...")
load_dotenv('.env.test')  # Load test environment first
load_dotenv('.env', override=True)  # Then override with production env
logger.info("Environment variables loaded")

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def start_healthcheck(port=8080):
    """Start health check server"""
    try:
        server = HTTPServer(('', port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        logger.info(f"Health check server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start health check server: {e}")
        # Don't fail the whole bot if health check fails
        pass

class AIGamingBot:
    def __init__(self):
        """Initialize the Twitter bot"""
        logger.info("\nInitializing Twitter bot...")
        
        # Initialize retry settings
        self.max_retries = 3
        self.base_wait = 5  # Base wait time in minutes
        self.retry_count = 0
        
        # Cache file paths
        self.cache_file = 'rate_limits.json'
        self.response_cache_file = 'response_cache.json'
        
        # Map tweet types to categories
        self.tweet_categories = {
            'market_analysis': 'analysis',
            'gem_alpha': 'alpha',
            'shill_review': 'review',
            'market_aware': 'analysis',
            'technical_analysis': 'analysis',
            'self_aware': 'thoughts',
            'ai_market_analysis': 'analysis',
            'self_aware_thought': 'thoughts',
            'controversial_thread': 'discussion',
            'giveaway': 'community',
            'whale_alert': 'alert'
        }
        
        # Track rate limits
        self.rate_limits = {
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'daily_limit': 17,  # Keep 1 buffer from 18 limit
                'monthly_limit': 100  # Twitter's monthly post cap
            },
            'search': {
                'daily_searches': 0,
                'monthly_posts_pulled': 0,
                'monthly_post_limit': 500000,  # Twitter's monthly post pull limit
                'last_search': None
            }
        }
        
        # Check required Twitter and AI credentials
        required_vars = {
            'TWITTER_CLIENT_ID': 'Twitter API Key',
            'TWITTER_CLIENT_SECRET': 'Twitter API Secret',
            'TWITTER_ACCESS_TOKEN': 'Twitter Access Token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'Twitter Access Token Secret',
            'TWITTER_BEARER_TOKEN': 'Twitter Bearer Token',
            'AI_ACCESS_TOKEN': 'AI API Access Token',
            'AI_API_URL': 'AI API Base URL',
            'AI_MODEL_NAME': 'AI Model Name'
        }
        
        missing_vars = []
        for var, desc in required_vars.items():
            if not os.getenv(var):
                missing_vars.append(f"{desc} ({var})")
        
        if missing_vars:
            error_msg = "Missing required environment variables:\n"
            error_msg += "\n".join(f"- {var}" for var in missing_vars)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Initialize Twitter API clients
        logger.info("Initializing Twitter client...")
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=True
        )
        logger.info("Twitter client initialized")
        
        # Initialize Elion
        logger.info("Initializing Elion...")
        model_name = os.getenv('AI_MODEL_NAME', 'meta-llama-3.3-70b-instruct')
        llm = MetaLlamaComponent(
            api_key=os.getenv('AI_ACCESS_TOKEN'),
            api_base=os.getenv('AI_API_URL')
        )
        
        # Check for optional CryptoRank API key
        cryptorank_api_key = os.getenv('CRYPTORANK_API_KEY')
        if not cryptorank_api_key:
            logger.warning("CryptoRank API not available - Operating in Community Focus Mode")
            logger.info("Elion will prioritize:")
            logger.info("- Self-aware thoughts and discussions")
            logger.info("- Community engagement and giveaways")
            logger.info("- Controversial topics and AI insights")
        
        self.elion = Elion(llm=llm, cryptorank_api_key=cryptorank_api_key)
        logger.info("Elion initialized")
        
        # Initialize tweet history manager
        self.tweet_history = TweetHistoryManager()
        
        # Set up tweet schedule
        self._setup_schedule()
        
        # Load cached data if exists
        self._load_cache()
        
        # Initialize response tracking
        self.response_cache = self._load_response_cache()
    
    def _setup_schedule(self):
        """Set up the tweet schedule"""
        # Calculate intervals
        daily_limit = self.rate_limits['post']['daily_limit']
        hours_in_day = 24
        
        # Calculate base interval in minutes
        base_interval = (hours_in_day * 60) / daily_limit
        
        # Add some randomness to avoid exact patterns
        def random_interval():
            return base_interval + random.uniform(-5, 5)
        
        # Track countdown messages
        countdown_messages = 0
        
        # Schedule next tweet
        def schedule_next():
            nonlocal countdown_messages
            interval = random_interval()
            schedule.every(interval).minutes.do(self.run_cycle)
            
            # Only show first two countdown messages
            if countdown_messages < 2:
                logger.info(f"Next tweet scheduled in {int(interval)} minutes")
                countdown_messages += 1
            
        # Initial schedule
        schedule_next()
        
        # After each tweet, schedule the next one
        def run_and_reschedule():
            self.run_cycle()
            # Clear the old schedule
            schedule.clear()
            # Schedule the next tweet
            schedule_next()
            # Reschedule response checking and cache cleanup
            schedule.every(1).hours.do(self.check_responses)
            schedule.every().day.at("00:00").do(self._cleanup_cache)
            
        # Response checking (every hour)
        schedule.every(1).hours.do(self.check_responses)
        
        # Cache cleanup (daily)
        schedule.every().day.at("00:00").do(self._cleanup_cache)
    
    def _can_post_tweet(self) -> bool:
        """Check if we can post a tweet based on rate limits"""
        current_time = datetime.utcnow()
        
        # Reset daily count if needed
        if current_time - self.rate_limits['post']['last_reset'] > timedelta(days=1):
            self.rate_limits['post']['daily_count'] = 0
            self.rate_limits['post']['last_reset'] = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Reset monthly count if needed
        if current_time - self.rate_limits['post']['monthly_reset'] > timedelta(days=30):
            self.rate_limits['post']['monthly_count'] = 0
            self.rate_limits['post']['monthly_reset'] = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Check limits
        if self.rate_limits['post']['daily_count'] >= self.rate_limits['post']['daily_limit']:
            next_reset = self.rate_limits['post']['last_reset'] + timedelta(days=1)
            time_until = next_reset - current_time
            hours = int(time_until.total_seconds() / 3600)
            minutes = int((time_until.total_seconds() % 3600) / 60)
            logger.info(f"Daily tweet limit reached ({self.rate_limits['post']['daily_count']}/{self.rate_limits['post']['daily_limit']}). Reset in {hours}h {minutes}m")
            return False
            
        if self.rate_limits['post']['monthly_count'] >= self.rate_limits['post']['monthly_limit']:
            next_reset = self.rate_limits['post']['monthly_reset'] + timedelta(days=30)
            time_until = next_reset - current_time
            days = time_until.days
            hours = int((time_until.total_seconds() % (24 * 3600)) / 3600)
            logger.info(f"Monthly tweet limit reached ({self.rate_limits['post']['monthly_count']}/{self.rate_limits['post']['monthly_limit']}). Reset in {days}d {hours}h")
            return False
            
        return True
    
    def _update_post_counts(self):
        """Update tweet count after successful post"""
        self.rate_limits['post']['daily_count'] += 1
        self.rate_limits['post']['monthly_count'] += 1
        self._save_cache()
    
    def _load_cache(self):
        """Load cached data"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                    # Convert ISO format strings back to datetime objects
                    self.rate_limits['post']['last_reset'] = datetime.fromisoformat(cache['rate_limits']['post']['last_reset'])
                    self.rate_limits['post']['monthly_reset'] = datetime.fromisoformat(cache['rate_limits']['post']['monthly_reset'])
                    self.rate_limits['post']['daily_count'] = cache['rate_limits']['post']['daily_count']
                    self.rate_limits['post']['monthly_count'] = cache['rate_limits']['post']['monthly_count']
                    self.rate_limits['post']['daily_limit'] = cache['rate_limits']['post']['daily_limit']
                    self.rate_limits['post']['monthly_limit'] = cache['rate_limits']['post']['monthly_limit']
                    
                    self.rate_limits['search']['daily_searches'] = cache['rate_limits']['search']['daily_searches']
                    self.rate_limits['search']['monthly_posts_pulled'] = cache['rate_limits']['search']['monthly_posts_pulled']
                    self.rate_limits['search']['monthly_post_limit'] = cache['rate_limits']['search']['monthly_post_limit']
                    self.rate_limits['search']['last_search'] = datetime.fromisoformat(cache['rate_limits']['search']['last_search']) if cache['rate_limits']['search']['last_search'] else None
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
    
    def _save_cache(self):
        """Save cache data"""
        try:
            # Convert datetime objects to ISO format strings
            cache = {
                'rate_limits': {
                    'post': {
                        'daily_count': self.rate_limits['post']['daily_count'],
                        'monthly_count': self.rate_limits['post']['monthly_count'],
                        'last_reset': self.rate_limits['post']['last_reset'].isoformat(),
                        'monthly_reset': self.rate_limits['post']['monthly_reset'].isoformat(),
                        'daily_limit': self.rate_limits['post']['daily_limit'],
                        'monthly_limit': self.rate_limits['post']['monthly_limit']
                    },
                    'search': {
                        'daily_searches': self.rate_limits['search']['daily_searches'],
                        'monthly_posts_pulled': self.rate_limits['search']['monthly_posts_pulled'],
                        'monthly_post_limit': self.rate_limits['search']['monthly_post_limit'],
                        'last_search': self.rate_limits['search']['last_search'].isoformat() if self.rate_limits['search']['last_search'] else None
                    }
                }
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def _load_response_cache(self):
        """Load response cache from JSON"""
        try:
            if os.path.exists(self.response_cache_file):
                with open(self.response_cache_file, 'r') as f:
                    return json.load(f)
            return {'questions': {}}
        except Exception as e:
            logger.error(f"Error loading response cache: {e}")
            return {'questions': {}}
    
    def _save_response_cache(self):
        """Save response cache to JSON"""
        try:
            # Convert datetime objects to ISO format strings
            cache = {
                'questions': {}
            }
            for tweet_id, data in self.response_cache['questions'].items():
                cache['questions'][tweet_id] = {
                    'text': data['text'],
                    'time': data['time'],  # Already ISO format
                    'responses_checked': data['responses_checked'],
                    'used': data.get('used', False),
                    'responses': {}
                }
                # Store only high-engagement responses to save space
                for rid, rdata in data.get('responses', {}).items():
                    if rdata.get('engagement_score', 0) >= 5:  # Only store responses with good engagement
                        cache['questions'][tweet_id]['responses'][rid] = {
                            'text': rdata['text'],
                            'user': rdata['user'],
                            'engagement_score': rdata['engagement_score']
                        }
            
            with open(self.response_cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Error saving response cache: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache data"""
        try:
            self._load_cache()  # Ensure we have latest data
            current_time = datetime.utcnow()
            
            # Reset counts if needed
            if current_time - self.rate_limits['post']['last_reset'] > timedelta(days=1):
                self.rate_limits['post']['daily_count'] = 0
                self.rate_limits['post']['last_reset'] = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_time - self.rate_limits['post']['monthly_reset'] > timedelta(days=30):
                self.rate_limits['post']['monthly_count'] = 0
                self.rate_limits['post']['monthly_reset'] = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Clean up old responses
            if self.response_cache:
                for cache_type in ['questions']:
                    old_items = []
                    for tweet_id, data in self.response_cache[cache_type].items():
                        if current_time - datetime.fromisoformat(data['time']) > timedelta(days=7):
                            old_items.append(tweet_id)
                    for tweet_id in old_items:
                        del self.response_cache[cache_type][tweet_id]
                
                self._save_response_cache()
            
            self._save_cache()
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")
    
    def check_responses(self):
        """Check responses to recent tweets"""
        try:
            # Clean old entries first
            current_time = datetime.utcnow()
            for tweet_id in list(self.response_cache['questions'].keys()):
                data = self.response_cache['questions'][tweet_id]
                tweet_time = datetime.fromisoformat(data['time'])
                
                # Remove entries older than 7 days
                if (current_time - tweet_time).days > 7:
                    del self.response_cache['questions'][tweet_id]
                    continue
                
                # Skip if already checked
                if data['responses_checked']:
                    continue
                
                try:
                    # Get replies
                    replies = self.api.get_tweet_replies(tweet_id)
                    
                    # Store only high-engagement responses
                    for reply in replies:
                        engagement_score = reply.public_metrics['like_count'] + reply.public_metrics['retweet_count'] * 2
                        if engagement_score >= 5:  # Only store responses with good engagement
                            data['responses'][str(reply.id)] = {
                                'text': reply.text,
                                'user': reply.author_id,
                                'engagement_score': engagement_score
                            }
                    
                    data['responses_checked'] = True
                    
                except Exception as e:
                    logger.error(f"Error getting replies for {tweet_id}: {e}")
                    continue
            
            self._save_response_cache()
            
        except Exception as e:
            logger.error(f"Error checking responses: {e}")
    
    def run_cycle(self):
        """Run a single tweet cycle"""
        try:
            if not self._can_post_tweet():
                logger.info("Skipping tweet cycle - rate limit reached")
                return
                
            # Get next tweet type
            tweet_type = self.elion.get_next_tweet_type()
            if not tweet_type:
                logger.warning("No valid tweet type available")
                return
                
            logger.info(f"Generating {tweet_type} tweet...")
            
            # Try to generate tweet
            tweet = self.elion.generate_tweet(tweet_type)
            if not tweet:
                logger.warning(f"Failed to generate {tweet_type} tweet, will try again later")
                return
                
            # Validate tweet before posting
            if not self.elion._validate_tweet(tweet):
                logger.warning(f"Generated tweet failed validation: {tweet}")
                return
                
            # Post tweet
            logger.info("Posting tweet...")
            try:
                response = self.api.create_tweet(text=tweet)
                
                if response and hasattr(response, 'data'):
                    tweet_id = response.data['id']
                    logger.info(f"Tweet posted successfully! ID: {tweet_id}")
                    
                    # Get category from tweet type
                    category = self.tweet_categories.get(tweet_type, 'other')
                    
                    # Update tracking
                    self._update_post_counts()
                    self.tweet_history.add_tweet(tweet, "default", category)
                    
                    # Save cache
                    self._save_cache()
                    
                    # Schedule next tweet
                    schedule.clear()
                    daily_limit = self.rate_limits['post']['daily_limit']
                    base_interval = (24 * 60) / daily_limit
                    next_interval = base_interval + random.uniform(-5, 5)
                    schedule.every(next_interval).minutes.do(self.run_cycle)
                    schedule.every(1).hours.do(self.check_responses)
                    schedule.every().day.at("00:00").do(self._cleanup_cache)
                    
                    logger.info(f"Next tweet scheduled in {int(next_interval)} minutes")
                else:
                    logger.error("Failed to post tweet - invalid response")
                    return
                    
            except tweepy.errors.Unauthorized as e:
                logger.error(f"Twitter API authentication failed: {e}")
                logger.error("Please check your Twitter API credentials in the .env file")
                return
            except tweepy.errors.Forbidden as e:
                logger.error(f"Twitter API request forbidden: {e}")
                return
            except tweepy.errors.TweepyException as e:
                logger.error(f"Twitter API error: {e}")
                return
                
        except Exception as e:
            logger.error(f"Error in tweet cycle: {e}")
            return
    
    def engagement_cycle(self):
        """Run engagement cycle"""
        try:
            # Check if we can post
            if not self._can_post_tweet():
                return
            
            # Try to feature a response first
            featured = False
            for tweet_id, data in self.response_cache['questions'].items():
                if not data.get('used', False):
                    # Get responses with high engagement
                    for response_id, response_data in data.get('responses', {}).items():
                        if response_data.get('engagement_score', 0) > 10:  # Threshold for featuring
                            try:
                                # Generate response using Elion
                                tweet = self.elion.engage_with_community({
                                    'type': 'feature_response',
                                    'user': response_data['user'],
                                    'content': response_data['text']
                                })
                                
                                # Post response
                                self.api.create_tweet(
                                    text=tweet,
                                    in_reply_to_tweet_id=tweet_id
                                )
                                logger.info(f"Featured response: {tweet}")
                                
                                # Mark as used
                                data['used'] = True
                                self._save_response_cache()
                                
                                featured = True
                                break
                            except Exception as e:
                                logger.error(f"Error featuring response: {e}")
                                continue
            
            # If no feature, do regular engagement
            if not featured:
                engagement = self.elion.engage_with_community({
                    'type': 'regular_engagement',
                    'content': None
                })
                if engagement:
                    self.api.create_tweet(
                        text=engagement,
                        in_reply_to_tweet_id=None
                    )
                    logger.info(f"Engagement tweet posted: {engagement}")
            
            self._update_post_counts()
            
        except Exception as e:
            logger.error(f"Error in engagement cycle: {e}")
    
    def run(self):
        """Main bot loop - runs continuously"""
        try:
            logger.info("Starting bot...")
            
            # Run initial cycles
            self.run_cycle()
            self.engagement_cycle()
            
            # Main loop
            while True:
                # Get next scheduled jobs
                next_jobs = sorted(schedule.jobs, key=lambda x: x.next_run)
                if next_jobs:
                    next_job = next_jobs[0]
                    time_until = next_job.next_run - datetime.now()
                    minutes = int(time_until.total_seconds() / 60)
                    logger.info(f"Next tweet scheduled in {minutes} minutes")
                
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")
        except tweepy.errors.TooManyRequests:
            # Let Tweepy handle rate limits
            pass
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            if self.retry_count < self.max_retries:
                self.retry_count += 1
                wait_time = self.base_wait * (2 ** self.retry_count)
                logger.info(f"Retrying in {wait_time} minutes...")
                time.sleep(wait_time * 60)
                self.run()
            else:
                logger.info("Max retries reached. Exiting...")
                sys.exit(1)

def main():
    """Main function to run the Twitter AI Bot"""
    logger.info("\nInitializing Twitter AI Bot...")
    
    try:
        logger.info("Starting healthcheck server...")
        # Start healthcheck server for Railway
        start_healthcheck()
        
        logger.info("Creating bot instance...")
        # Start bot
        bot = AIGamingBot()
        logger.info("Starting bot...")
        bot.run()
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
