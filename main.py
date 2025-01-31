"""
Main entry point for the Twitter bot
"""

import os
import logging
import asyncio
import threading
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI
from twitter.bot import AIGamingBot
from api.endpoints import setup_routes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_bot():
    """Run the Twitter bot in a separate thread"""
    try:
        # Initialize and run the Twitter bot
        logger.info("Initializing Twitter bot...")
        bot = AIGamingBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        raise

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Initialize FastAPI app
    app = FastAPI()
    setup_routes(app)
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run FastAPI server
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
