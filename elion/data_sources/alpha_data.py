"""
Alpha data source for Elion
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from .base import BaseDataSource
from .cryptorank_api import CryptoRankAPI

class AlphaDataSource(BaseDataSource):
    """Handles alpha opportunities from CryptoRank API"""
    
    def __init__(self, cryptorank_api: CryptoRankAPI):
        """Initialize alpha data source"""
        super().__init__()
        self.cryptorank_api = cryptorank_api
        
        # Configure cache durations
        self.cache_durations.update({
            'alpha_opportunities': timedelta(minutes=30),
            'undervalued_gems': timedelta(hours=1),
            'gem_alpha': timedelta(minutes=30)
        })
        
    def _validate_data(self, data: Any) -> bool:
        """Validate alpha data"""
        if not isinstance(data, (list, dict)):
            return False
        return True
        
    def get_alpha_opportunities(self) -> List[Dict]:
        """Get potential alpha opportunities"""
        # Check cache first
        cached = self._get_cached('alpha_opportunities')
        if cached:
            return cached
            
        try:
            # Get market data
            market_data = self.cryptorank_api.get_currencies()
            if not market_data:
                return []
                
            # Filter for potential opportunities
            opportunities = []
            for coin in market_data:
                # Skip stablecoins and high mcap coins
                if self._is_stablecoin(coin):
                    continue
                    
                mcap = coin.get('market_cap', 0)
                if mcap > 1e9:  # Skip coins with mcap > $1B
                    continue
                    
                # Look for strong momentum
                price_change = coin.get('price_change_24h', 0)
                volume_change = coin.get('volume_change_24h', 0)
                
                if price_change > 10 and volume_change > 50:
                    opportunities.append({
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'price': coin['price'],
                        'market_cap': mcap,
                        'price_change_24h': price_change,
                        'volume_change_24h': volume_change,
                        'opportunity_type': 'momentum_play'
                    })
                    
            # Cache and return
            self._cache_data('alpha_opportunities', opportunities)
            return opportunities
            
        except Exception as e:
            print(f"Error getting alpha opportunities: {e}")
            return []
            
    def get_undervalued_gems(self) -> List[Dict]:
        """Get undervalued gems based on market data"""
        # Check cache first
        cached = self._get_cached('undervalued_gems')
        if cached:
            return cached
            
        try:
            # Get market data
            market_data = self.cryptorank_api.get_currencies()
            if not market_data:
                return []
                
            # Filter for potential gems
            gems = []
            for coin in market_data:
                # Skip stablecoins and high mcap coins
                if self._is_stablecoin(coin):
                    continue
                    
                mcap = coin.get('market_cap', 0)
                if mcap > 100e6:  # Skip coins with mcap > $100M
                    continue
                    
                # Look for oversold conditions
                price_change_7d = coin.get('price_change_7d', 0)
                price_change_24h = coin.get('price_change_24h', 0)
                
                if price_change_7d < -30 and price_change_24h > 0:
                    gems.append({
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'price': coin['price'],
                        'market_cap': mcap,
                        'price_change_24h': price_change_24h,
                        'price_change_7d': price_change_7d,
                        'opportunity_type': 'oversold_gem'
                    })
                    
            # Cache and return
            self._cache_data('undervalued_gems', gems)
            return gems
            
        except Exception as e:
            print(f"Error getting undervalued gems: {e}")
            return []
            
    def _is_stablecoin(self, coin: Dict) -> bool:
        """Check if a coin is likely a stablecoin"""
        symbol = coin.get('symbol', '').upper()
        price = coin.get('price', 0)
        price_change_24h = coin.get('price_change_24h', 0)
        
        # Check for common stablecoin symbols
        if symbol in ['USDT', 'USDC', 'DAI', 'BUSD', 'UST']:
            return True
            
        # Check for stable price
        if 0.95 <= price <= 1.05 and abs(price_change_24h) < 1:
            return True
            
        return False
