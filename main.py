"""
Main ELAI script
"""

import os
import logging
from dotenv import load_dotenv
from custom_llm import MetaLlamaComponent
from elion.elion import Elion
from twitter.bot import AIGamingBot

def main():
    """Main entry point"""
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
        
        # Initialize Elion (only needs LLM)
        elai = Elion(llm)
        
        # Initialize and run Twitter bot
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
