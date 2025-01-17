"""
Market data source for Elion
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from .base import BaseDataSource
from .cryptorank_api import CryptoRankAPI

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
        
    def _validate_data(self, data: Any) -> bool:
        """Validate market data"""
        if not isinstance(data, (list, dict)):
            return False
        return True
        
    def get_market_data(self) -> List[Dict]:
        """Get current market data"""
        # Check cache first
        cached = self._get_cached('market_data')
        if cached:
            return cached
            
        # Get fresh data
        data = self.cryptorank_api.get_currencies()
        if not data:
            return []
            
        # Cache and return
        self._cache_data('market_data', data)
        return data
        
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
