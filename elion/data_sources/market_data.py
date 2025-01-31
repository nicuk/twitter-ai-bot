"""
Market data source for Elion
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from .base import BaseDataSource
from .cryptorank_api import CryptoRankAPI
import logging

logger = logging.getLogger(__name__)

class MarketDataSource(BaseDataSource):
    """Handles market data from CryptoRank API"""
    
    def __init__(self, cryptorank_api: CryptoRankAPI):
        """Initialize market data source"""
        super().__init__()
        self.cryptorank_api = cryptorank_api
        
        # Configure cache durations
        self.cache_durations.update({
            'market_data': timedelta(minutes=5),
            'market_sentiment': timedelta(minutes=15),
            'market_condition': timedelta(minutes=15)
        })
        
        # Configure price limits and excluded tokens
        self.max_prices = {
            'default': 1000  # Default max for other tokens
        }
        
        # List of excluded tokens (top market cap coins)
        self.excluded_tokens = {'BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'SOL', 'ADA', 'DOGE', 'AVAX'}
        
    def _validate_data(self, data: Any) -> List[Dict]:
        """Validate market data"""
        if not isinstance(data, (list, dict)):
            return []
            
        # If it's a list of tokens, validate each token
        if isinstance(data, list):
            valid_tokens = []
            for token in data:
                if self._validate_token(token):
                    valid_tokens.append(token)
            return valid_tokens
            
        return []
        
    def _validate_token(self, token: Dict) -> bool:
        """Validate individual token data"""
        try:
            # Required fields
            if not all(k in token for k in ['symbol', 'price']):
                return False
                
            symbol = token['symbol']
            
            # Exclude top tokens
            if symbol in self.excluded_tokens:
                return False
                
            # Basic data validation - just ensure numbers are valid
            try:
                price = float(token['price'])
                volume = float(token.get('volume24h', 0))
                if price <= 0:  # Only check if price is positive
                    logger.warning(f"Invalid price for {symbol}: ${price}")
                    return False
            except (ValueError, TypeError):
                logger.warning(f"Invalid numeric data for {symbol}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error validating token {token.get('symbol', 'unknown')}: {e}")
            return False
            
    def get_market_data(self) -> List[Dict]:
        """Get current market data"""
        # Check cache first
        cached = self._get_cached('market_data')
        if cached:
            return cached
            
        # Fetch fresh data
        tokens = self.cryptorank_api.fetch_tokens()
        if not tokens:
            return []
            
        # Validate tokens
        valid_tokens = self._validate_data(tokens)
        if valid_tokens:
            self._set_cached('market_data', valid_tokens)
            return valid_tokens
            
        return []
        
    def get_market_sentiment(self, btc_data: Dict) -> str:
        """Determine market sentiment based on BTC performance"""
        try:
            change_24h = btc_data.get('price_change_24h', 0)
            
            if change_24h >= 5:
                return "Strongly Bullish 🚀"
            elif change_24h >= 2:
                return "Bullish 📈"
            elif change_24h <= -5:
                return "Strongly Bearish 📉"
            elif change_24h <= -2:
                return "Bearish 🔻"
            else:
                return "Neutral ⚖️"
                
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            return "Neutral ⚖️"
            
    def get_market_condition(self, market_data: List[Dict]) -> str:
        """Determine overall market condition"""
        try:
            # Calculate percentage of coins with positive 24h change
            total_coins = len(market_data)
            if total_coins == 0:
                return "Uncertain"
                
            positive_coins = sum(1 for coin in market_data 
                               if coin.get('price_change_24h', 0) > 0)
            positive_ratio = positive_coins / total_coins
            
            if positive_ratio >= 0.7:
                return "Strong Uptrend 🌙"
            elif positive_ratio >= 0.6:
                return "Uptrend 📈"
            elif positive_ratio <= 0.3:
                return "Strong Downtrend 🔻"
            elif positive_ratio <= 0.4:
                return "Downtrend 📉"
            else:
                return "Consolidation ⚖️"
                
        except Exception as e:
            print(f"Error getting market condition: {e}")
            return "Uncertain"
