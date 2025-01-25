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

from custom_llm import MetaLlamaComponent
from twitter.api_client import TwitterAPI
from twitter.rate_limiter import RateLimiter
from twitter.history_manager import TweetHistory
from elion.elion import Elion

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
        self.elion = Elion(model_name)
        
        # Schedule tweets
        self._schedule_tweets()
        
    def _schedule_tweets(self):
        """Schedule Elion's structured daily tweets"""
        # 2 AI Mystique Posts
        schedule.every().day.at("02:00").do(self.post_ai_mystique)  # Early market
        schedule.every().day.at("10:00").do(self.post_ai_mystique)  # Mid-market
        
        # 3 Performance Posts
        schedule.every().day.at("06:00").do(self.post_performance)  # Early performance
        schedule.every().day.at("14:00").do(self.post_performance)  # Mid performance
        schedule.every().day.at("18:00").do(self.post_performance)  # Late performance
        
        # 2 Summary Posts
        schedule.every().day.at("20:00").do(self.post_summary)  # Evening summary
        schedule.every().day.at("22:00").do(self.post_summary)  # Final summary
        
    def post_ai_mystique(self):
        """Post AI mystique tweet"""
        try:
            # Get market data
            market_data = self.elion.get_market_data()
            
            # Generate mystique tweet
            content = self.elion.content.generate_ai_mystique(market_data)
            if not content:
                logger.warning("Failed to generate AI mystique tweet")
                return
                
            # Post tweet
            self.api.post_tweet(content)
            logger.info("Posted AI mystique tweet")
            
        except Exception as e:
            logger.error(f"Error posting AI mystique tweet: {e}")
            
    def post_performance(self):
        """Post performance tweet"""
        try:
            # Get trade data
            trade_data = self.elion.get_latest_trade()
            if not trade_data:
                logger.warning("No trade data available")
                return
                
            # Generate performance tweet
            content = self.elion.content.generate_performance_post(trade_data)
            if not content:
                logger.warning("Failed to generate performance tweet")
                return
                
            # Post tweet
            self.api.post_tweet(content)
            logger.info("Posted performance tweet")
            
        except Exception as e:
            logger.error(f"Error posting performance tweet: {e}")
            
    def post_summary(self):
        """Post summary tweet"""
        try:
            # Generate summary tweet
            content = self.elion.content.generate_summary_post()
            if not content:
                logger.warning("Failed to generate summary tweet")
                return
                
            # Post tweet
            self.api.post_tweet(content)
            logger.info("Posted summary tweet")
            
        except Exception as e:
            logger.error(f"Error posting summary tweet: {e}")
            
    def run(self):
        """Run the bot"""
        logger.info("Starting bot...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                self.retry_count += 1
                
                if self.retry_count > self.max_retries:
                    logger.error("Max retries exceeded. Stopping bot.")
                    break
                    
                wait_time = self.base_wait * (2 ** self.retry_count)
                logger.info(f"Waiting {wait_time} minutes before retry...")
                time.sleep(wait_time * 60)
                
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    bot = AIGamingBot()
    bot.run()
