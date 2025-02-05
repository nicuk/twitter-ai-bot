"""
Startup script to initialize token history before starting the main application
"""
import os
import sys
import logging
from strategies.token_monitor import TokenMonitor
from main import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_token_history():
    """Initialize token history with current market data"""
    api_key = os.getenv('CRYPTORANK_API_KEY')
    if not api_key:
        logger.error("No API key found. Please set CRYPTORANK_API_KEY environment variable")
        return False
        
    logger.info("Initializing token history...")
    monitor = TokenMonitor(api_key)
    
    # Run analysis once to get current market data
    analysis = monitor.run_analysis()
    
    # Track tokens from volume strategy
    volume_data = analysis.get('volume_data', {})
    trend_data = analysis.get('trend_data', {})
    
    tokens_tracked = 0
    
    # Track volume spikes
    if 'spikes' in volume_data:
        for score, token in volume_data['spikes']:
            logger.info(f"Tracking volume spike: ${token['symbol']}")
            monitor.track_token(token)
            tokens_tracked += 1
            
    # Track volume anomalies
    if 'anomalies' in volume_data:
        for score, token in volume_data['anomalies']:
            logger.info(f"Tracking volume anomaly: ${token['symbol']}")
            monitor.track_token(token)
            tokens_tracked += 1
            
    # Track trend tokens
    if 'trend_tokens' in trend_data:
        for token in trend_data['trend_tokens']:
            logger.info(f"Tracking trend token: ${token['symbol']}")
            monitor.track_token(token)
            tokens_tracked += 1
            
    logger.info(f"Successfully tracked {tokens_tracked} tokens")
    return True

if __name__ == "__main__":
    # Initialize token history first
    success = initialize_token_history()
    if not success:
        logger.error("Failed to initialize token history")
        sys.exit(1)
        
    # Start the main application
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
