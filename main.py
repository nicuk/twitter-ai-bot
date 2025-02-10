import os
import logging
import threading
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from api.endpoints import setup_routes
from twitter.bot import AIGamingBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_bot():
    """Run the Twitter bot"""
    try:
        logger.info("Initializing Twitter bot...")
        bot = AIGamingBot()
        
        # Check Redis connection through bot's instance check
        redis_url = os.getenv('REDIS_URL')
        redis_status = "Active" if redis_url else "Not configured"
        logger.info("=== Bot Status ===")
        logger.info(f"✓ Redis connection: {redis_status}")
        logger.info("=================")
        
        bot.run()
    except Exception as e:
        logger.error(f"Error running bot: {e}")

def main():
    """Main entry point"""
    # Load environment variables
    load_dotenv()
    
    # Initialize FastAPI app
    app = FastAPI()
    setup_routes(app)
    
    # Start bot in a background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run FastAPI server (single process)
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
