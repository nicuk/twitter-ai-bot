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
    
    print("\nTesting Personal Tweets:\n")
    
    # Generate 5 test tweets
    for i in range(5):
        tweet = generator.generate('self_aware')
        print(f"\nTweet {i+1}:\n{tweet}")
        print(f"Length: {len(tweet)} chars\n")
        
    # Open file for writing test results
    with open('tweet_test_results.txt', 'w', encoding='utf-8') as f:
        # Generate 5 test tweets
        for i in range(5):
            tweet = generator.generate('self_aware')
            
            # Write to file with clear formatting
            header = f"\n{'='*80}\nTest Tweet {i+1}:\n{'-'*40}\n\n"
            content_section = f"Content:\n{'-'*20}\n{tweet}\n[Length: {len(tweet)} chars]\n\n"
            
            # Write to file
            f.write(header)
            f.write(content_section)
            
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
    
    # Initialize ELAI
    elion = Elion(llm=llm)
    
    # Write results to file in real-time
    with open('market_tweet_results.txt', 'w', encoding='utf-8') as f:
        f.write("Market Tweet Test Results\n")
        f.write("=" * 80 + "\n\n")
        
        # Test trend tweets
        logger.info("\nTesting Trend Tweets:")
        f.write("Trend Tweets:\n")
        f.write("-" * 50 + "\n")
        
        for i in range(2):
            f.write(f"\nTrend Tweet Test {i+1}:\n")
            tweet = elion.generate_tweet('trend')
            if tweet:
                f.write(tweet + "\n")
                f.write(f"Length: {len(tweet)} chars\n")
            else:
                f.write("No trend tweet generated\n")
            f.write("-" * 50 + "\n")
            f.flush()  # Force write to disk
        
        # Test volume tweets
        logger.info("\nTesting Volume Tweets:")
        f.write("\nVolume Tweets:\n")
        f.write("-" * 50 + "\n")
        
        for i in range(2):
            f.write(f"\nVolume Tweet Test {i+1}:\n")
            tweet = elion.generate_tweet('volume')
            if tweet:
                f.write(tweet + "\n")
                f.write(f"Length: {len(tweet)} chars\n")
            else:
                f.write("No volume tweet generated\n")
            f.write("-" * 50 + "\n")
            f.flush()  # Force write to disk
        
        # Test automatic rotation
        logger.info("\nTesting Tweet Rotation:")
        f.write("\nRotation Tweets:\n")
        f.write("-" * 50 + "\n")
        
        for i in range(3):
            f.write(f"\nRotation Test {i+1}:\n")
            tweet = elion.generate_tweet()  # Let it choose type
            if tweet:
                f.write(f"Strategy: {elion.state['last_strategy']}\n")
                f.write(tweet + "\n")
                f.write(f"Length: {len(tweet)} chars\n")
            else:
                f.write("No tweet generated\n")
            f.write("-" * 50 + "\n")
            f.flush()  # Force write to disk
                
    logger.info("Market tests completed. Results written to market_tweet_results.txt")
    
    # Display results from file
    with open('market_tweet_results.txt', 'r', encoding='utf-8') as f:
        print("\nTest Results:")
        print("=" * 80)
        print(f.read())

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

def test_market_data_integration():
    """Test market data storage, trend/volume strategies, and LLM integration"""
    logger = logging.getLogger(__name__)
    logger.info("Testing market data integration...")
    
    try:
        # Initialize components
        load_dotenv()
        from elion.data_storage import DataStorage
        from strategies.trend_strategy import TrendStrategy
        from strategies.volume_strategy import VolumeStrategy
        from elion.llm_integration import LLMIntegration
        
        storage = DataStorage()
        trend_strategy = TrendStrategy(os.getenv('CRYPTORANK_API_KEY'))
        volume_strategy = VolumeStrategy(os.getenv('CRYPTORANK_API_KEY'))
        llm = LLMIntegration()
        
        # Step 1: Test trend strategy and market data storage
        logger.info("\nStep 1: Testing trend strategy and market data storage...")
        trend_data = trend_strategy.analyze()
        if trend_data:
            logger.info("✓ Trend strategy successfully fetched and analyzed data")
            
            # Check if data was stored
            latest_market_data = storage.get_latest_market_data()
            if latest_market_data:
                logger.info("✓ Market data successfully stored in database")
                btc_data = next((coin for coin in latest_market_data.get('coins', []) 
                               if coin.get('symbol') == 'BTC'), None)
                if btc_data:
                    logger.info(f"✓ Current BTC Price: ${float(btc_data['price']):,.2f}")
            else:
                logger.error("✗ Failed to retrieve market data from storage")
        else:
            logger.error("✗ Trend strategy failed to fetch data")
            
        # Step 2: Test volume strategy
        logger.info("\nStep 2: Testing volume strategy...")
        volume_data = volume_strategy.analyze()
        if volume_data:
            logger.info("✓ Volume strategy successfully fetched and analyzed data")
            if volume_data.get('spikes'):
                logger.info(f"✓ Found {len(volume_data['spikes'])} volume spikes")
        else:
            logger.error("✗ Volume strategy failed to fetch data")
            
        # Step 3: Test LLM integration with market data
        logger.info("\nStep 3: Testing LLM integration with market data...")
        test_prompt = "What's the current Bitcoin price and market sentiment?"
        response = llm.generate_response(
            test_prompt,
            context={'type': 'market_analysis'},
            market_state={'state': 'analyzing'}
        )
        if response:
            logger.info("✓ LLM successfully generated response with market data:")
            logger.info(f"Prompt: {test_prompt}")
            logger.info(f"Response: {response}")
        else:
            logger.error("✗ LLM failed to generate response")
            
        logger.info("\nMarket data integration test complete!")
        return True
        
    except Exception as e:
        logger.error(f"Market data integration test failed: {e}", exc_info=True)
        return False

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='ELAI Twitter Bot')
    parser.add_argument('--test', action='store_true', help='Run tests only')
    parser.add_argument('--test-type', type=str, 
                       choices=['personal', 'market', 'llm', 'market-data'], 
                       help='Type of test to run')
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
            elif args.test_type == 'market-data':
                test_market_data_integration()
            else:
                # Run all tests by default
                test_personal_tweets(MetaLlamaComponent(
                    api_key=os.getenv('AI_ACCESS_TOKEN'),
                    api_base=os.getenv('AI_API_URL')
                ))
                test_market_tweets()
                test_llm()
                test_market_data_integration()
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
