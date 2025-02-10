"""Debug script to test different post types with detailed logging"""

import os
import sys
import logging
from datetime import datetime
import time
import requests
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twitter.bot import AIGamingBot
from elion.data_sources.cryptorank_api import CryptoRankAPI

# Load environment variables
load_dotenv()

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG for maximum detail
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('debug_posts.log')
    ]
)

# Get loggers for different components
bot_logger = logging.getLogger('twitter.bot')
api_logger = logging.getLogger('twitter.api_client')
elion_logger = logging.getLogger('elion')
crypto_logger = logging.getLogger('elion.data_sources.cryptorank_api')

def test_railway_endpoints():
    """Test Railway API endpoints directly"""
    api_logger.info("\n=== Testing Railway Endpoints ===")
    
    # Test endpoints
    endpoints = {
        'Main Bot': 'https://twitter-ai-bot-production.up.railway.app',
        'ELAI Bot': 'https://elai-production.up.railway.app'
    }
    
    for name, base_url in endpoints.items():
        api_logger.info(f"\nTesting {name} endpoints:")
        
        # Test each endpoint
        test_paths = [
            '/token-history',
            '/analysis/current',
            '/analysis/performance'
        ]
        
        for path in test_paths:
            url = f"{base_url}{path}"
            api_logger.info(f"\nTesting {url}")
            
            try:
                start_time = time.time()
                response = requests.get(url)
                duration = time.time() - start_time
                
                api_logger.info(f"Status: {response.status_code}")
                api_logger.info(f"Response time: {duration:.2f}s")
                api_logger.info(f"Headers: {dict(response.headers)}")
                
                if response.status_code == 200:
                    data = response.json()
                    api_logger.info(f"Response size: {len(str(data))} chars")
                else:
                    api_logger.error(f"Error response: {response.text}")
                    
            except Exception as e:
                api_logger.error(f"Error testing {url}: {str(e)}")
            
            time.sleep(1)  # Small delay between requests

def test_post_type(bot: AIGamingBot, post_type: str):
    """Test a specific post type with detailed logging"""
    start_time = datetime.now()
    api_logger.info(f"\n=== Testing {post_type} post ===")
    api_logger.info(f"Start time: {start_time}")
    
    try:
        # Get the post function
        post_func = getattr(bot, f"post_{post_type}")
        if not post_func:
            api_logger.error(f"Post type {post_type} not found")
            return
            
        # Log pre-post state
        api_logger.info("Checking Twitter API status...")
        api_status = bot.api.verify_credentials()
        api_logger.info(f"Twitter API status: {'OK' if api_status else 'Failed'}")
        
        # Try to post
        api_logger.info(f"Attempting to post {post_type}...")
        result = post_func()
        
        # Log result
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        api_logger.info(f"Post attempt completed in {duration:.2f} seconds")
        api_logger.info(f"Result: {'Success' if result else 'Failed'}")
        
    except Exception as e:
        api_logger.error(f"Error testing {post_type}: {str(e)}", exc_info=True)

def main():
    """Run tests for all post types"""
    try:
        # First test Railway endpoints
        test_railway_endpoints()
        
        # Initialize bot
        bot_logger.info("\nInitializing bot for testing...")
        bot = AIGamingBot()
        
        # Test CryptoRank API directly
        crypto_logger.info("\nTesting CryptoRank API directly...")
        api = CryptoRankAPI(os.getenv('CRYPTORANK_API_KEY'))
        currencies = api.get_currencies(limit=5)
        crypto_logger.info(f"Got {len(currencies)} currencies from CryptoRank")
        
        # Test each post type
        post_types = ['trend', 'volume', 'performance', 'ai_mystique']
        for post_type in post_types:
            test_post_type(bot, post_type)
            time.sleep(5)  # Wait between posts
            
    except Exception as e:
        bot_logger.error(f"Error in main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
