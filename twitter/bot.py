"""Main Twitter bot class"""

import os
import time
import random
import logging
import schedule
from datetime import datetime, timedelta

from custom_llm import MetaLlamaComponent
from twitter.api_client import TwitterAPI
from twitter.rate_limiter import RateLimiter
from twitter.history_manager import TweetHistory
from elion.elion import Elion

logger = logging.getLogger(__name__)

class AIGamingBot:
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
        model_name = os.getenv('AI_MODEL_NAME', 'meta-llama-3.3-70b-instruct')
        llm = MetaLlamaComponent(
            api_key=os.getenv('AI_ACCESS_TOKEN'),
            api_base=os.getenv('AI_API_URL')
        )
        self.elion = Elion(llm=llm)
        logger.info("Elion initialized")
        
        # Add post categories and their daily targets
        self.post_categories = {
            'trend': {'target': 7, 'count': 0},    # Market trend analysis
            'volume': {'target': 6, 'count': 0},   # Volume analysis
            'personal': {'target': 4, 'count': 0}  # Personality-driven tweets
        }
        
        # Set up tweet schedule
        self._setup_schedule()
    
    def run_cycle(self):
        """Run a single tweet cycle with retries"""
        try:
            # Try each category until we get content
            categories_to_try = ['trend', 'volume', 'personal']
            content = None
            category = None
            
            # First try the next category from scheduler
            next_category = self._get_next_category()
            if next_category in categories_to_try:
                categories_to_try.remove(next_category)
                categories_to_try.insert(0, next_category)
            
            # Try each category until we get content
            for cat in categories_to_try:
                try:
                    content = self.elion.generate_tweet(cat)
                    if content:
                        category = cat
                        break
                except Exception as e:
                    logger.error(f"Error generating {cat} content: {e}")
                    continue

            if not content:
                logger.warning("No content generated for any category")
                return

            # Try to post with retries
            for attempt in range(self.max_retries):
                try:
                    result = self.api.create_tweet(text=content)
                    if result:
                        self.history.add_tweet(result)
                        self.rate_limiter.update_counts()
                        
                        # Update category count
                        self.post_categories[category]['count'] += 1
                        
                        # Reset retry count and schedule next
                        self.retry_count = 0
                        self._schedule_next_tweet()
                        return
                except Exception as e:
                    if "rate limit" in str(e).lower():
                        logger.error("Twitter API rate limit reached")
                        return
                    
                    # For other errors, use shorter backoff
                    wait_time = min(self.base_wait * (1.5 ** attempt), 15)  # Cap at 15 minutes
                    logger.warning(f"Tweet failed, attempt {attempt + 1}/{self.max_retries}. Waiting {wait_time:.1f} minutes...")
                    time.sleep(wait_time * 60)
            
            # All retries failed
            self.retry_count += 1
            if self.retry_count >= self.max_retries:
                logger.error("All tweet retries failed. Entering recovery mode...")
                self._enter_recovery_mode()
            
        except Exception as e:
            logger.error(f"Error in tweet cycle: {e}")
            self.retry_count += 1
            if self.retry_count >= self.max_retries:
                logger.error("Too many errors. Entering recovery mode...")
                self._enter_recovery_mode()

    def _get_next_category(self) -> str:
        """Get the next category to post based on targets"""
        hour = datetime.now().hour
        
        # First try market hours schedule (8 AM - 4 PM UTC)
        if 8 <= hour <= 16:
            # Check which market category needs posts
            for category in ['trend', 'volume']:
                if self.post_categories[category]['count'] < self.post_categories[category]['target']:
                    return category
        
        # Then try personal tweets
        if self.post_categories['personal']['count'] < self.post_categories['personal']['target']:
            return 'personal'
            
        # If all primary targets met, find any category that's below target
        for category, data in self.post_categories.items():
            if data['count'] < data['target']:
                return category
                    
        # If everything is at target, pick random category
        logger.info("All post targets met, picking random category")
        return random.choice(list(self.post_categories.keys()))

    def _setup_schedule(self):
        """Set up the tweet schedule"""
        # Schedule first tweet in 2 minutes to allow for startup
        schedule.every(2).minutes.do(self.run_cycle).tag('tweets')
        logger.info("First tweet scheduled in 2 minutes")
        
        # Schedule daily cleanup only
        schedule.every().day.at("00:00").do(self._cleanup_cache)

    def _enter_recovery_mode(self):
        """Enter recovery mode when too many errors occur"""
        logger.info("Entering recovery mode...")
        
        try:
            # Clear all schedules
            schedule.clear()
            
            # Wait for a longer period
            recovery_wait = 30  # minutes
            logger.info(f"Waiting {recovery_wait} minutes before resuming...")
            time.sleep(recovery_wait * 60)
            
            # Reset retry count
            self.retry_count = 0
            
            # Restart scheduling
            self._setup_schedule()
            logger.info("Recovered successfully!")
            
        except Exception as e:
            logger.error(f"Error in recovery mode: {e}")

    def _schedule_next_tweet(self):
        """Schedule the next tweet"""
        schedule.clear('tweets')
        
        # Default to 17 tweets per day if rate limits not available
        daily_limit = 17
        try:
            daily_limit = self.rate_limiter.rate_limits['post']['daily_limit']
        except (KeyError, AttributeError):
            logger.warning("Could not get daily limit from rate limiter, using default")
            
        # Calculate interval between tweets
        base_interval = (24 * 60) / daily_limit  # minutes
        next_interval = base_interval + random.uniform(-5, 5)
        
        # Schedule next tweet
        schedule.every(next_interval).minutes.do(self.run_cycle).tag('tweets')
        logger.info(f"Next tweet scheduled in {next_interval:.1f} minutes")

    def check_responses(self):
        """Check responses to recent tweets"""
        try:
            recent_tweets = self.history.get_recent_tweets()
            for tweet in recent_tweets:
                metrics = self.api.get_tweet(tweet['id'])
                if metrics and metrics.data:
                    self.history.update_metrics(
                        tweet['id'], 
                        metrics.data.public_metrics
                    )
        except Exception as e:
            logger.error(f"Error checking responses: {e}")

    def _cleanup_cache(self):
        """Clean up old cache data and reset post counts"""
        try:
            # Clean up old tweets from history
            self.history.cleanup_old_tweets()
            
            # Clean up rate limiter cache
            self.rate_limiter.cleanup()
            
            # Reset post category counts
            for category in self.post_categories:
                self.post_categories[category]['count'] = 0
            
        except Exception as e:
            logger.error(f"Error cleaning cache: {e}")

    def run(self):
        """Main bot loop"""
        try:
            logger.info("Starting bot...")
            
            while True:
                schedule.run_pending()
                time.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("\nBot stopped by user")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            raise
