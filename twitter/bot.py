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
            'trend': {
                'ai': {'target': 3, 'count': 0},
                'gaming': {'target': 2, 'count': 0},
                'meme': {'target': 2, 'count': 0}
            },
            'volume': {
                'leaders': {'target': 2, 'count': 0},
                'spikes': {'target': 2, 'count': 0},
                'anomalies': {'target': 2, 'count': 0}
            },
            'community': {
                'engagement': {'target': 3, 'count': 0}
            }
        }
        
        # Set up tweet schedule
        self._setup_schedule()
    
    def run_cycle(self):
        """Run a single tweet cycle with retries"""
        try:
            # Get next category
            main_cat, sub_cat = self._get_next_category()
            content = None
            
            # Generate content based on category
            try:
                if main_cat == 'trend':
                    content = self.elion.generate_tweet('trend')
                elif main_cat == 'volume':
                    content = self.elion.generate_tweet('volume')
                elif main_cat == 'community':
                    content = self.elion.engage_with_community()
                    
            except Exception as e:
                logger.error(f"Error generating content: {e}")
                # Try community engagement as fallback
                try:
                    content = self.elion.engage_with_community()
                except Exception as e:
                    logger.error(f"Community engagement failed: {e}")
                    return

            if not content:
                logger.warning(f"No content generated for {main_cat}/{sub_cat}")
                return

            # Try to post with retries
            for attempt in range(self.max_retries):
                try:
                    result = self.api.create_tweet(text=content)
                    if result:
                        self.history.add_tweet(result)
                        self.rate_limiter.update_counts()
                        
                        # Update category count
                        self.post_categories[main_cat][sub_cat]['count'] += 1
                        
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

    def _get_next_category(self) -> tuple:
        """Get the next category to post based on targets"""
        hour = datetime.now().hour
        
        # First try market hours schedule (8 AM - 4 PM UTC)
        if 8 <= hour <= 16:
            # Check which market category needs posts
            for main_cat in ['trend', 'volume']:
                for sub_cat, data in self.post_categories[main_cat].items():
                    if data['count'] < data['target']:
                        return main_cat, sub_cat
        
        # Then try community engagement
        if self.post_categories['community']['engagement']['count'] < self.post_categories['community']['engagement']['target']:
            return 'community', 'engagement'
            
        # If all primary targets met, find any category that's below target
        for main_cat in self.post_categories:
            for sub_cat, data in self.post_categories[main_cat].items():
                if data['count'] < data['target']:
                    return main_cat, sub_cat
                    
        # If everything is at target, pick random category to avoid hanging
        main_cats = list(self.post_categories.keys())
        main_cat = random.choice(main_cats)
        sub_cats = list(self.post_categories[main_cat].keys())
        sub_cat = random.choice(sub_cats)
        
        logger.info(f"All targets met, posting additional {main_cat}/{sub_cat}")
        return main_cat, sub_cat

    def _setup_schedule(self):
        """Set up the tweet schedule"""
        # Schedule first tweet in 1 minute
        schedule.every(1).minutes.do(self.run_cycle).tag('tweets')
        logger.info("First tweet scheduled in 1 minute")
        
        # Schedule regular checks
        schedule.every(1).hours.do(self.check_responses)
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
            for main_cat in self.post_categories:
                for sub_cat in self.post_categories[main_cat]:
                    self.post_categories[main_cat][sub_cat]['count'] = 0
            
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
