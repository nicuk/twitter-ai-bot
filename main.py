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
    
    # Load API key
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    if not api_key:
        logger.error("CRYPTORANK_API_KEY not found")
        return
    
    # Test trend strategy
    logger.info("\nTesting Trend Strategy:")
    from strategies.trend_strategy import TrendStrategy
    trend = TrendStrategy(api_key)
    trend_result = trend.analyze()
    print("\nTrend Analysis Result:")
    print(json.dumps(trend_result, indent=2))
    
    # Format trend tweet
    from strategies.trend_strategy import format_twitter_output
    if trend_result.get('trend_tokens'):
        trend_tokens = [(1, {'symbol': t.split()[0][1:], 
                           'price': 0.0,
                           'price_change': float(t.split()[1].rstrip('%')),
                           'volume': 1e6}) for t in trend_result['trend_tokens']]
        trend_tweet = format_twitter_output(trend_tokens)
        print("\nTrend Tweet:")
        print("-" * 40)
        print(trend_tweet)
        print("-" * 40)
        print(f"Character count: {len(trend_tweet)}")
    else:
        print("\nNo trend tokens found")
    
    # Test volume strategy
    logger.info("\nTesting Volume Strategy:")
    from strategies.volume_strategy import test_volume_strategy
    volume_result = test_volume_strategy()
    print("\nVolume Analysis Result:")
    print(volume_result)
    
    logger.info("Market tests completed")

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ELAI Twitter Bot')
    parser.add_argument('--test', action='store_true', help='Run tests only')
    parser.add_argument('--test-type', choices=['personal', 'market'], help='Type of test to run')
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
            else:
                # Run both by default
                test_personal_tweets(MetaLlamaComponent(
                    api_key=os.getenv('AI_ACCESS_TOKEN'),
                    api_base=os.getenv('AI_API_URL')
                ))
                test_market_tweets()
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
