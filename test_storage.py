"""Test token storage persistence"""
import os
from dotenv import load_dotenv
from twitter.bot import AIGamingBot
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_token_storage():
    """Test that tokens are properly stored and persisted"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize bot
        bot = AIGamingBot()
        
        # Get initial token count
        initial_tokens = len(bot.elion.token_monitor.history_tracker.get_all_token_history())
        logger.info(f"Initial token count: {initial_tokens}")
        
        # Run volume analysis (this should find and store tokens)
        logger.info("Running volume analysis...")
        volume_data = bot.elion.volume_strategy.analyze()
        
        if not volume_data:
            logger.error("No volume data found")
            return
            
        # Filter tokens
        valid_tokens = []
        if 'spikes' in volume_data:
            valid_tokens.extend([
                data for _, data in volume_data['spikes']
                if data.get('symbol') not in bot.EXCLUDED_TOKENS
            ])
            
        if 'anomalies' in volume_data:
            valid_tokens.extend([
                data for _, data in volume_data['anomalies']
                if data.get('symbol') not in bot.EXCLUDED_TOKENS
            ])
            
        if not valid_tokens:
            logger.error("No valid tokens found")
            return
            
        # Process each token
        for token in valid_tokens:
            bot.elion.token_monitor.history_tracker.update_token(token)
            logger.info(f"Processed token: {token.get('symbol')}")
            
        # Check final token count
        final_tokens = len(bot.elion.token_monitor.history_tracker.get_all_token_history())
        logger.info(f"Final token count: {final_tokens}")
        
        # Show all tokens
        all_tokens = bot.elion.token_monitor.history_tracker.get_all_token_history()
        logger.info("Current tokens in history:")
        for symbol, data in all_tokens.items():
            logger.info(f"- {symbol}: First seen at {data.first_mention_price}, Current price: {data.current_price}")
            
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    test_token_storage()
