"""
Main ELAI script - Production
"""

import os
import logging
from dotenv import load_dotenv
from twitter.bot import AIGamingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize and run the Twitter bot
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
