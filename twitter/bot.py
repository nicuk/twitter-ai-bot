"""Main Twitter bot class"""

import os
import time
import random
import schedule
import logging
from datetime import datetime, timedelta

# Import core strategy components
from strategies.scoring_base import BaseScoring
from strategies.shared_utils import (
    calculate_activity_score,
    format_token_info,
    filter_tokens_by_volume,
    filter_tokens_by_trend,
    fetch_tokens,
    get_movement_description
)
from strategies.cryptorank_client import CryptoRankAPI
from strategies.trend_strategy import (
    analyze_ai_tokens,
    analyze_gaming_tokens,
    analyze_meme_tokens,
    format_twitter_output as format_trend_output,
    get_trend_insight
)
from strategies.volume_strategy import (
    analyze_volume_leaders,
    find_volume_spikes,
    format_twitter_output as format_volume_output,
    get_elai_insight
)
from elion.core.elion import Elion
from custom_llm import MetaLlamaComponent
from .api_client import TwitterAPI
from .rate_limiter import RateLimiter
from .history_manager import TweetHistory

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
        self.scoring = BaseScoring()
        self.cryptorank = CryptoRankAPI(os.getenv('CRYPTORANK_API_KEY'))
        
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
            if not self.rate_limiter.can_post():
                return

            # Get next category to post
            main_cat, sub_cat = self._get_next_category()
            if not main_cat:
                logger.info("All post targets met for today")
                return

            content = None
            
            # For market analysis, fetch and prepare data first
            if main_cat in ['trend', 'volume']:
                try:
                    # Get tokens using CryptoRank client
                    tokens = self.cryptorank.get_tokens()
                    if not tokens:
                        logger.error("Failed to fetch tokens")
                        # If market analysis fails, try community engagement as fallback
                        main_cat, sub_cat = 'community', 'engagement'
                        
                    else:
                        # Format tokens consistently
                        formatted_tokens = [
                            token for token in (format_token_info(t) for t in tokens)
                            if token is not None
                        ]
                        
                        if main_cat == 'trend':
                            if sub_cat == 'ai':
                                ai_tokens = analyze_ai_tokens(formatted_tokens)
                                content = self._format_trend_tweet(ai_tokens)
                            elif sub_cat == 'gaming':
                                gaming_tokens = analyze_gaming_tokens(formatted_tokens)
                                content = self._format_trend_tweet(gaming_tokens)
                            elif sub_cat == 'meme':
                                meme_tokens = analyze_meme_tokens(formatted_tokens)
                                content = self._format_trend_tweet(meme_tokens)
                                
                        elif main_cat == 'volume':
                            if sub_cat == 'leaders':
                                leaders = analyze_volume_leaders(formatted_tokens)
                                content = self._format_volume_tweet(leaders)
                            elif sub_cat == 'spikes':
                                spikes = find_volume_spikes(formatted_tokens)
                                content = self._format_volume_tweet(spikes)
                            elif sub_cat == 'anomalies':
                                anomalies = find_volume_anomalies(formatted_tokens)
                                content = self._format_volume_tweet(anomalies)
                                
                        # Calculate confidence and apply penalties for market posts
                        if content and formatted_tokens:
                            token = formatted_tokens[0]
                            activity_score = calculate_activity_score(
                                volume=token['volume'],
                                mcap=token['mcap'],
                                price_change=token['price_change']
                            )
                            stability_score = self.scoring.get_stability_score(token)
                            
                            # Apply volatility penalty if needed
                            final_score = self.scoring.apply_volatility_penalty(
                                score=activity_score + stability_score,
                                price_change=token['price_change']
                            )
                            
                            # Get confidence label
                            label, emoji = self.scoring.get_confidence_label(final_score)
                            content = f"{content}\n\n{label} {emoji}"
                        
                except Exception as e:
                    logger.error(f"Error in market analysis: {e}")
                    # If market analysis fails, try community engagement as fallback
                    main_cat, sub_cat = 'community', 'engagement'
            
            # Try community engagement if no market content or as fallback
            if not content and main_cat == 'community':
                try:
                    content = self.elion.engage_with_community()
                except Exception as e:
                    logger.error(f"Community engagement failed: {e}")
                    # If community engagement fails, schedule next attempt
                    self._schedule_next_tweet()
                    return

            if not content:
                logger.warning(f"No content generated for {main_cat}/{sub_cat}")
                # Schedule next attempt even if no content was generated
                self._schedule_next_tweet()
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
                        # Mark community engagement as maxed if that's what failed
                        if main_cat == 'community':
                            self.post_categories['community']['engagement']['count'] = self.post_categories['community']['engagement']['target']
                        # Schedule next attempt
                        self._schedule_next_tweet()
                        return
                    
                    logger.error(f"Error posting tweet (attempt {attempt + 1}/{self.max_retries}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.base_wait * 60)  # Wait before retry
            
            # If all retries failed, schedule next attempt
            self._schedule_next_tweet()
            
        except Exception as e:
            logger.error(f"Error in tweet cycle: {e}")
            # Always schedule next attempt, even if there's an error
            self._schedule_next_tweet()

    def _get_next_category(self) -> tuple:
        """Get the next category to post based on targets"""
        hour = datetime.now().hour
        market_score = self.scoring.get_market_hours_score()
        
        # First try market hours schedule (8 AM - 4 PM UTC)
        if 8 <= hour <= 16 and market_score > 5:
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
        # Schedule initial tweet
        self.run_cycle()
        
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
        daily_limit = self.rate_limiter.rate_limits['post']['daily_limit']
        base_interval = (24 * 60) / daily_limit
        next_interval = base_interval + random.uniform(-5, 5)
        schedule.every(next_interval).minutes.do(self.run_cycle).tag('tweets')

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

    def _format_trend_tweet(self, tokens: list) -> str:
        """Format trend analysis tweet"""
        try:
            # Get trend analysis
            ai_tokens = analyze_ai_tokens(tokens)
            gaming_tokens = analyze_gaming_tokens(tokens)
            meme_tokens = analyze_meme_tokens(tokens)
            
            # Get insight and format
            insight = get_trend_insight(ai_tokens + gaming_tokens + meme_tokens)
            return format_trend_output(insight)
        except Exception as e:
            logger.error(f"Error formatting trend tweet: {e}")
            return None

    def _format_volume_tweet(self, tokens: list) -> str:
        """Format volume analysis tweet"""
        try:
            # Get volume analysis
            spikes = find_volume_spikes(tokens)
            leaders = analyze_volume_leaders(tokens)
            
            # Get insight and format
            insight = get_elai_insight(spikes + leaders)
            return format_volume_output(insight)
        except Exception as e:
            logger.error(f"Error formatting volume tweet: {e}")
            return None

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

def main():
    """Main entry point for the Twitter bot"""
    try:
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize and run bot
        bot = AIGamingBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
