"""Token monitoring and tracking functionality"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class TokenMonitor:
    """Monitors and tracks token performance over time"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize token monitor"""
        self.api_key = api_key
        self.tracked_tokens = {}  # symbol -> {first_seen, last_price, etc}
        self.tracking_window = timedelta(days=7)  # Track tokens for 7 days
        
    def track_token(self, symbol: str, price: Optional[float] = None, volume: Optional[float] = None) -> None:
        """Track a new token or update existing token data
        
        Args:
            symbol: Token symbol
            price: Current price (optional)
            volume: Current volume (optional)
        """
        now = datetime.now()
        
        # Initialize token data if not exists
        if symbol not in self.tracked_tokens:
            self.tracked_tokens[symbol] = {
                'first_seen': now,
                'last_seen': now,
                'first_price': price,
                'last_price': price,
                'highest_price': price if price else 0,
                'lowest_price': price if price else float('inf'),
                'highest_volume': volume if volume else 0,
                'volume_history': [],
                'price_history': []
            }
            
        # Update existing token data
        token_data = self.tracked_tokens[symbol]
        token_data['last_seen'] = now
        
        if price is not None:
            token_data['last_price'] = price
            token_data['price_history'].append((now, price))
            
            # Update price extremes
            if price > token_data['highest_price']:
                token_data['highest_price'] = price
            if price < token_data['lowest_price']:
                token_data['lowest_price'] = price
                
        if volume is not None:
            token_data['volume_history'].append((now, volume))
            if volume > token_data['highest_volume']:
                token_data['highest_volume'] = volume
                
        # Cleanup old data
        self._cleanup_old_tokens()
        
    def _cleanup_old_tokens(self) -> None:
        """Remove tokens that haven't been seen in tracking window"""
        now = datetime.now()
        cutoff = now - self.tracking_window
        
        self.tracked_tokens = {
            symbol: data 
            for symbol, data in self.tracked_tokens.items()
            if data['last_seen'] > cutoff
        }
        
    def get_token_stats(self, symbol: str) -> Optional[Dict]:
        """Get tracking stats for a token"""
        if symbol not in self.tracked_tokens:
            return None
            
        data = self.tracked_tokens[symbol]
        first_price = data.get('first_price')
        last_price = data.get('last_price')
        
        if first_price and last_price:
            price_change = ((last_price - first_price) / first_price) * 100
        else:
            price_change = 0
            
        return {
            'symbol': symbol,
            'days_tracked': (data['last_seen'] - data['first_seen']).days,
            'price_change': price_change,
            'highest_price': data.get('highest_price'),
            'lowest_price': data.get('lowest_price'),
            'highest_volume': data.get('highest_volume')
        }
