"""Test script for token tracking system"""

import os
import logging
import threading
from dotenv import load_dotenv
from strategies.token_monitor import TokenMonitor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_token_data_extraction():
    """Test specifically token data extraction with sample data"""
    print("\nTesting token data extraction...")
    
    # Create sample tokens data matching the format we see in logs
    sample_tokens = [
        {
            'symbol': 'GRIFFAIN',
            'price': 0.161787912002,
            'volume24h': 57353103.64324295,
            'marketCap': 161768643.7088322,
            'priceChange24h': -13.129074256162362
        },
        {
            'symbol': 'MLG',
            'price': 0.123151750035,
            'volume24h': 8467615.34345487,
            'marketCap': 122848719.51376663,
            'priceChange24h': 11.981336861289016
        },
        {
            'symbol': 'FLAY',
            'price': 0.118723577872,
            'volume24h': 1975968.2860313312,
            'marketCap': 80904319.14788327,
            'priceChange24h': -11.725763418351436
        }
    ]
    
    # Initialize TokenMonitor without API key since we're testing with sample data
    monitor = TokenMonitor(api_key=None)
    
    def update_token(token):
        """Helper function to update a token in a thread"""
        print(f"\nTracking {token['symbol']}...")
        monitor.track_token(token)
    
    # Create threads to update tokens concurrently
    threads = []
    for token in sample_tokens:
        thread = threading.Thread(target=update_token, args=(token,))
        threads.append(thread)
    
    # Start all threads
    print("\nStarting concurrent token updates...")
    for thread in threads:
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Verify the tracked token data
    print("\nVerifying tracked token data...")
    for token in sample_tokens:
        symbol = token['symbol']
        history = monitor.history_tracker.get_token_history(symbol)
        if history:
            print(f"\nTracked data for {symbol}:")
            print(f"Current price: {history.current_price} (Expected: {token['price']})")
            print(f"Current volume: {history.current_volume} (Expected: {token['volume24h']})")
            print(f"Current mcap: {history.current_mcap} (Expected: {token['marketCap']})")
            
            # Verify values match
            assert abs(history.current_price - token['price']) < 1e-10, f"Price mismatch for {symbol}"
            assert abs(history.current_volume - token['volume24h']) < 1e-10, f"Volume mismatch for {symbol}"
            assert abs(history.current_mcap - token['marketCap']) < 1e-10, f"Market cap mismatch for {symbol}"
        else:
            print(f"\nError: Token {symbol} not found in history")
    
if __name__ == "__main__":
    test_token_data_extraction()
