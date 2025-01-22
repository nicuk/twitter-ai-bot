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
import json
import sys
from datetime import datetime

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

def test_market_tweets():
    """Test market-based tweet generation"""
    logger = logging.getLogger(__name__)
    logger.info("Testing market tweet generation...")
    
    # Load API key and initialize LLM
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    if not api_key:
        logger.error("CRYPTORANK_API_KEY not found")
        return
        
    llm = MetaLlamaComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    
    # Initialize ELAI and bot
    elion = Elion(llm=llm)
    bot = AIGamingBot()
    
    # Test scheduling logic
    logger.info("\nTesting Tweet Scheduling:")
    print("-" * 50)
    
    # Current time is in Asian market hours
    current_hour = datetime.now().hour
    print(f"\nCurrent time: {current_hour}:00 UTC")
    
    # Get next category 5 times to see distribution
    print("\nTesting next 5 tweet categories:")
    for i in range(5):
        category = bot._get_next_category()
        print(f"Tweet {i+1}: {category}")
    
    # Test trend tweets
    logger.info("\nTesting Trend Tweets:")
    print("-" * 50)
    
    # Get market data once
    market_data = elion.get_market_data()
    
    for i in range(3):
        tweet = elion.format_tweet('trend', market_data)
        if tweet:
            print(f"\nTrend Tweet {i+1}:")
            print(tweet)
            print(f"Length: {len(tweet)} chars")
            print("-" * 50)
        else:
            print(f"\nNo trend tweet generated (attempt {i+1})")
            
    # Test volume tweets
    logger.info("\nTesting Volume Tweets:")
    print("-" * 50)
    
    # Reuse market data
    for i in range(3):
        tweet = elion.format_tweet('volume', market_data)
        if tweet:
            print(f"\nVolume Tweet {i+1}:")
            print(tweet)
            print(f"Length: {len(tweet)} chars")
            print("-" * 50)
        else:
            print(f"\nNo volume tweet generated (attempt {i+1})")
            
    # Write results to file
    with open('market_tweet_results.txt', 'w', encoding='utf-8') as f:
        f.write("Market Tweet Test Results\n")
        f.write("=" * 50 + "\n\n")
        
        # Test trend tweets
        f.write("Trend Tweets:\n")
        f.write("-" * 30 + "\n")
        for i in range(3):
            tweet = elion.format_tweet('trend', market_data)
            if tweet:
                f.write(f"\nTweet {i+1}:\n")
                f.write(tweet + "\n")
                f.write(f"Length: {len(tweet)} chars\n")
                f.write("-" * 30 + "\n")
            else:
                f.write(f"\nNo trend tweet generated (attempt {i+1})\n")
                
        # Test volume tweets
        f.write("\nVolume Tweets:\n")
        f.write("-" * 30 + "\n")
        for i in range(3):
            tweet = elion.format_tweet('volume', market_data)
            if tweet:
                f.write(f"\nTweet {i+1}:\n")
                f.write(tweet + "\n")
                f.write(f"Length: {len(tweet)} chars\n")
                f.write("-" * 30 + "\n")
            else:
                f.write(f"\nNo volume tweet generated (attempt {i+1})\n")
                
    logger.info("Market tests completed. Results written to market_tweet_results.txt")

def test_llm():
    """Test LLM functionality"""
    logger = logging.getLogger(__name__)
    logger.info("Testing LLM...")
    
    # Initialize LLM
    llm = MetaLlamaComponent(
        api_key=os.getenv('AI_ACCESS_TOKEN'),
        api_base=os.getenv('AI_API_URL')
    )
    
    # Simple test prompt
    test_prompt = "What's your analysis of the current crypto market? Keep it under 100 characters."
    
    try:
        response = llm.generate(test_prompt)
        logger.info(f"\nLLM Test Response:\n{response}\n")
        return True
    except Exception as e:
        logger.error(f"LLM test failed: {e}")
        return False

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ELAI Twitter Bot')
    parser.add_argument('--test', action='store_true', help='Run tests only')
    parser.add_argument('--test-type', type=str, choices=['personal', 'market', 'llm'], help='Type of test to run')
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    logger.info("Starting ELAI...")
    
    try:
        if args.test:
            # Run tests based on type
            if args.test_type == 'personal':
                test_personal_tweets(MetaLlamaComponent(
                    api_key=os.getenv('AI_ACCESS_TOKEN'),
                    api_base=os.getenv('AI_API_URL')
                ))
            elif args.test_type == 'market':
                test_market_tweets()
            elif args.test_type == 'llm':
                test_llm()
            else:
                # Run both by default
                test_personal_tweets(MetaLlamaComponent(
                    api_key=os.getenv('AI_ACCESS_TOKEN'),
                    api_base=os.getenv('AI_API_URL')
                ))
                test_market_tweets()
                test_llm()
        else:
            # Initialize Elion and run bot
            elai = Elion(MetaLlamaComponent(
                api_key=os.getenv('AI_ACCESS_TOKEN'),
                api_base=os.getenv('AI_API_URL')
            ))
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
