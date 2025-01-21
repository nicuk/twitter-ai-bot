"""
Main ELAI script
"""

import os
import logging
import argparse
from dotenv import load_dotenv
from custom_llm import MetaLlamaComponent
from elion.elion import Elion
from twitter.bot import AIGamingBot
from elion.content.generator import ContentGenerator
from elion.personality import PersonalityManager

def test_personal_tweets(llm):
    """Test ELAI's personal tweet generation"""
    logger = logging.getLogger(__name__)
    logger.info("Testing personal tweet generation...")
    
    # Initialize components
    personality = PersonalityManager()
    generator = ContentGenerator(personality, llm)
    
    # Open file for writing test results
    with open('tweet_test_results.txt', 'w', encoding='utf-8') as f:
        # Generate 5 test tweets
        for i in range(5):
            tweet = generator.generate('self_aware')
            
            # Split and analyze tweet parts
            parts = tweet.split('\n\n')
            content = parts[0]
            hashtags = parts[1] if len(parts) > 1 else ''
            
            # Write to file with clear formatting
            f.write(f"\n{'='*80}\n")
            f.write(f"Test Tweet {i+1}:\n")
            f.write(f"{'-'*40}\n\n")
            
            f.write("Content:\n")
            f.write("-" * 20 + "\n")
            f.write(content + "\n")
            f.write(f"[Length: {len(content)} chars]\n\n")
            
            f.write("Hashtags:\n")
            f.write("-" * 20 + "\n")
            f.write(hashtags + "\n")
            f.write(f"[Length: {len(hashtags)} chars]\n\n")
            
            f.write(f"Total Length: {len(tweet)} chars\n\n")
            
    logger.info("Test results written to tweet_test_results.txt")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ELAI Twitter Bot')
    parser.add_argument('--test', action='store_true', help='Run tests only')
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ELAI...")
    
    # Load environment variables
    load_dotenv()
    
    # Initialize LLM
    api_url = os.getenv('AI_API_URL')
    access_token = os.getenv('AI_ACCESS_TOKEN')
    
    logger.info(f"API URL: {'Set' if api_url else 'Missing'}")
    logger.info(f"Access Token: {'Set' if access_token else 'Missing'}")
    
    try:
        # Initialize LLM
        llm = MetaLlamaComponent(
            api_key=access_token,
            api_base=api_url
        )
        
        if args.test:
            # Run only tests
            test_personal_tweets(llm)
        else:
            # Initialize Elion and run bot
            elai = Elion(llm)
            logger.info("Initializing Twitter bot...")
            bot = AIGamingBot()
            bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
