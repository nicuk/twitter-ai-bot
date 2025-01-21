"""
Twitter Bot powered by ELAI (Enhanced Learning AI)
"""

import os
import sys
import time
import logging
import argparse
import schedule
from datetime import datetime
from dotenv import load_dotenv

import tweepy
from elion.core.elion import Elion
from custom_llm import MetaLlamaComponent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterBot:
    """Twitter Bot powered by ELAI"""
    
    def __init__(self):
        """Initialize the Twitter bot"""
        logger.info("\nInitializing Twitter bot...")
        
        # Load environment variables
        load_dotenv()
        
        # Initialize Twitter client
        self._init_twitter()
        
        # Initialize ELAI
        self._init_elai()
        
        # Set up tweet schedule
        self._setup_schedule()
    
    def _init_twitter(self):
        """Initialize Twitter API client"""
        required_vars = {
            'TWITTER_CLIENT_ID': 'Twitter API Key',
            'TWITTER_CLIENT_SECRET': 'Twitter API Secret',
            'TWITTER_ACCESS_TOKEN': 'Twitter Access Token',
            'TWITTER_ACCESS_TOKEN_SECRET': 'Twitter Access Token Secret',
            'TWITTER_BEARER_TOKEN': 'Twitter Bearer Token'
        }
        
        # Validate Twitter credentials
        missing = [f"{desc} ({var})" for var, desc in required_vars.items() 
                  if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing Twitter credentials:\n" + "\n".join(f"- {m}" for m in missing))
        
        # Initialize client
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
    
    def _init_elai(self):
        """Initialize ELAI"""
        required_vars = {
            'AI_ACCESS_TOKEN': 'AI API Access Token',
            'AI_API_URL': 'AI API Base URL',
            'AI_MODEL_NAME': 'AI Model Name',
            'CRYPTORANK_API_KEY': 'CryptoRank API Key'
        }
        
        # Validate AI credentials
        missing = [f"{desc} ({var})" for var, desc in required_vars.items() 
                  if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing AI credentials:\n" + "\n".join(f"- {m}" for m in missing))
        
        # Initialize ELAI
        logger.info("Initializing ELAI...")
        llm = MetaLlamaComponent(
            api_key=os.getenv('AI_ACCESS_TOKEN'),
            api_base=os.getenv('AI_API_URL')
        )
        
        self.elai = Elion(
            api_key=os.getenv('CRYPTORANK_API_KEY'),
            llm=llm
        )
        logger.info("ELAI initialized")
    
    def _setup_schedule(self):
        """Set up tweet schedule"""
        # Market updates: 4 times a day
        schedule.every().day.at("00:00").do(self.post_market_update)
        schedule.every().day.at("06:00").do(self.post_market_update)
        schedule.every().day.at("12:00").do(self.post_market_update)
        schedule.every().day.at("18:00").do(self.post_market_update)
        
        # Self-aware thoughts: Every 3 hours
        for hour in range(0, 24, 3):
            schedule.every().day.at(f"{hour:02d}:30").do(self.post_thought)
        
        # Engagement check: Every hour
        schedule.every().hour.do(self.check_engagement)
        
        logger.info("Tweet schedule initialized")
    
    def post_market_update(self):
        """Post market update"""
        try:
            content = self.elai.analyze('tweet')
            if content:
                self.api.create_tweet(text=content)
                logger.info("Posted market update")
            else:
                logger.warning("No market update content generated")
        except Exception as e:
            logger.error(f"Failed to post market update: {e}")
    
    def post_thought(self):
        """Post self-aware thought"""
        try:
            content = self.elai.analyze('self_aware_thought')
            if content:
                self.api.create_tweet(text=content)
                logger.info("Posted self-aware thought")
            else:
                logger.warning("No thought content generated")
        except Exception as e:
            logger.error(f"Failed to post thought: {e}")
    
    def check_engagement(self):
        """Check and respond to engagement"""
        try:
            # Get recent mentions
            mentions = self.api.get_users_mentions(
                id=self.api.get_me()[0].id,
                max_results=100
            )
            
            # Process each mention
            for mention in mentions.data or []:
                response = self.elai.analyze('engagement_reply', {'tweet': mention.text})
                if response:
                    self.api.create_tweet(
                        text=response,
                        in_reply_to_tweet_id=mention.id
                    )
            
            logger.info("Checked engagement")
        except Exception as e:
            logger.error(f"Failed to check engagement: {e}")
    
    def test_tweet(self):
        """Generate a test tweet without posting"""
        try:
            logger.info("\nGenerating test tweet...")
            content = self.elai.analyze('tweet')
            if content:
                logger.info("\nGenerated tweet content:")
                logger.info("-" * 40)
                logger.info(content)
                logger.info("-" * 40)
            else:
                logger.warning("No tweet content generated")
        except Exception as e:
            logger.error(f"Failed to generate test tweet: {e}")
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Twitter bot...")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Twitter Bot powered by ELAI')
    parser.add_argument('--test-tweet', action='store_true', help='Generate a test tweet without posting')
    args = parser.parse_args()
    
    bot = TwitterBot()
    
    if args.test_tweet:
        bot.test_tweet()
    else:
        bot.run()

if __name__ == "__main__":
    main()
