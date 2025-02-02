"""Track historical data for tokens that pass filters"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class TokenHistoricalData:
    # Initial data
    symbol: str
    first_mention_date: datetime
    first_mention_price: float
    first_mention_volume_24h: float
    first_mention_mcap: float
    first_mention_volume_mcap_ratio: float
    current_price: float
    current_volume: float
    current_mcap: float
    last_updated: datetime
    
    # Performance metrics after first mention (with defaults)
    price_24h_after: float = 0
    price_48h_after: float = 0
    price_7d_after: float = 0
    max_price_7d: float = 0
    max_price_7d_date: Optional[datetime] = None
    max_gain_percentage_7d: float = 0
    
    volume_24h_after: float = 0
    volume_48h_after: float = 0
    volume_7d_after: float = 0
    max_volume_7d: float = 0
    max_volume_7d_date: Optional[datetime] = None
    max_volume_increase_7d: float = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        data = {
            'symbol': self.symbol,
            'first_mention_date': self.first_mention_date.isoformat(),
            'first_mention_price': self.first_mention_price,
            'first_mention_volume_24h': self.first_mention_volume_24h,
            'first_mention_mcap': self.first_mention_mcap,
            'first_mention_volume_mcap_ratio': self.first_mention_volume_mcap_ratio,
            'price_24h_after': self.price_24h_after,
            'price_48h_after': self.price_48h_after,
            'price_7d_after': self.price_7d_after,
            'max_price_7d': self.max_price_7d,
            'max_gain_percentage_7d': self.max_gain_percentage_7d,
            'volume_24h_after': self.volume_24h_after,
            'volume_48h_after': self.volume_48h_after,
            'volume_7d_after': self.volume_7d_after,
            'max_volume_7d': self.max_volume_7d,
            'max_volume_increase_7d': self.max_volume_increase_7d,
            'current_price': self.current_price,
            'current_volume': self.current_volume,
            'current_mcap': self.current_mcap,
            'last_updated': self.last_updated.isoformat()
        }
        
        if self.max_price_7d_date:
            data['max_price_7d_date'] = self.max_price_7d_date.isoformat()
        if self.max_volume_7d_date:
            data['max_volume_7d_date'] = self.max_volume_7d_date.isoformat()
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TokenHistoricalData':
        """Create instance from dictionary"""
        kwargs = {
            'symbol': data['symbol'],
            'first_mention_date': datetime.fromisoformat(data['first_mention_date']),
            'first_mention_price': data['first_mention_price'],
            'first_mention_volume_24h': data['first_mention_volume_24h'],
            'first_mention_mcap': data['first_mention_mcap'],
            'first_mention_volume_mcap_ratio': data['first_mention_volume_mcap_ratio'],
            'price_24h_after': data.get('price_24h_after', 0),
            'price_48h_after': data.get('price_48h_after', 0),
            'price_7d_after': data.get('price_7d_after', 0),
            'max_price_7d': data.get('max_price_7d', 0),
            'max_gain_percentage_7d': data.get('max_gain_percentage_7d', 0),
            'volume_24h_after': data.get('volume_24h_after', 0),
            'volume_48h_after': data.get('volume_48h_after', 0),
            'volume_7d_after': data.get('volume_7d_after', 0),
            'max_volume_7d': data.get('max_volume_7d', 0),
            'max_volume_increase_7d': data.get('max_volume_increase_7d', 0),
            'current_price': data['current_price'],
            'current_volume': data['current_volume'],
            'current_mcap': data['current_mcap'],
            'last_updated': datetime.fromisoformat(data['last_updated'])
        }
        
        if 'max_price_7d_date' in data:
            kwargs['max_price_7d_date'] = datetime.fromisoformat(data['max_price_7d_date'])
        if 'max_volume_7d_date' in data:
            kwargs['max_volume_7d_date'] = datetime.fromisoformat(data['max_volume_7d_date'])
            
        return cls(**kwargs)

class TokenHistoryTracker:
    """Tracks historical data for tokens that pass filters"""
    
    _instance = None
    
    def __new__(cls):
        """Create singleton instance"""
        if cls._instance is None:
            cls._instance = super(TokenHistoryTracker, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize tracker with Railway's persistent storage"""
        # Only initialize once
        if self._initialized:
            return
            
        self._initialized = True
        
        # Use Railway's persistent storage directory
        self.data_dir = '/data'
        logger.info(f"Initializing TokenHistoryTracker with data directory: {self.data_dir}")
        
        # If /data doesn't exist, try creating it
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            logger.info(f"Data directory exists: {os.path.exists(self.data_dir)}")
            logger.info(f"Data directory writable: {os.access(self.data_dir, os.W_OK)}")
            logger.info(f"Data directory absolute path: {os.path.abspath(self.data_dir)}")
            
            # List contents of /data to verify
            if os.path.exists(self.data_dir):
                logger.info(f"Contents of {self.data_dir}:")
                for item in os.listdir(self.data_dir):
                    logger.info(f"  - {item}")
                    
        except Exception as e:
            logger.error(f"Error with /data directory: {e}")
            raise  # Let it fail in Railway if we can't access persistent storage
            
        self.history_file = os.path.join(self.data_dir, 'token_history.json')
        logger.info(f"Using token history file: {self.history_file}")
        logger.info(f"History file absolute path: {os.path.abspath(self.history_file)}")
        
        # Initialize empty history if file doesn't exist
        if not os.path.exists(self.history_file):
            logger.info("Creating new token history file")
            try:
                with open(self.history_file, 'w') as f:
                    json.dump({}, f)
            except Exception as e:
                logger.error(f"Failed to create token history file: {e}")
                raise
                
        self.token_history: Dict[str, TokenHistoricalData] = {}
        self.load_history()
    
    def load_history(self):
        """Load token history from file"""
        try:
            if os.path.exists(self.history_file):
                logger.info(f"Loading token history from {self.history_file}")
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.token_history = {
                        symbol: TokenHistoricalData.from_dict(token_data)
                        for symbol, token_data in data.items()
                    }
                logger.info(f"Loaded {len(self.token_history)} tokens from history")
                for symbol in self.token_history:
                    logger.debug(f"Loaded token: {symbol}")
            else:
                logger.warning(f"No history file found at {self.history_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding token history JSON: {e}")
            self.token_history = {}
        except Exception as e:
            logger.error(f"Error loading token history: {e}")
            logger.exception("Full traceback:")
            self.token_history = {}
    
    def save_history(self):
        """Save token history to file"""
        try:
            logger.info(f"Saving {len(self.token_history)} tokens to {self.history_file}")
            
            # Ensure data directory exists
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Write to temporary file first
            temp_file = f"{self.history_file}.tmp"
            with open(temp_file, 'w') as f:
                json.dump(
                    {symbol: data.to_dict() for symbol, data in self.token_history.items()},
                    f,
                    indent=2
                )
            
            # Atomically rename temp file to actual file
            os.replace(temp_file, self.history_file)
            
            logger.info(f"Successfully saved token history")
            logger.info(f"Current tokens: {', '.join(self.token_history.keys())}")
            
        except Exception as e:
            logger.error(f"Error saving token history: {e}")
            logger.exception("Full traceback:")
            # Try to recover the file if it exists
            if os.path.exists(self.history_file):
                logger.info("Attempting to reload from existing file")
                self.load_history()
    
    def update_token(self, token: Dict):
        """Update token data in history"""
        try:
            # Extract token data using correct keys from CryptoRank API
            symbol = token.get('symbol', '').upper()
            if not symbol:
                return
                
            # Try different key formats (CryptoRank API vs Strategy format)
            price = float(token.get('current_price', 
                token.get('price', 
                token.get('lastPrice', 0))))
                
            volume = float(token.get('24h_volume',
                token.get('volume24h',
                token.get('volume', 0))))
                
            mcap = float(token.get('market_cap',
                token.get('marketCap',
                token.get('mcap', 0))))
                
            volume_mcap_ratio = (volume / mcap * 100) if mcap > 0 else 0
            current_time = datetime.now()
            
            # Add debug logging
            logger.debug(f"Updating token {symbol}:")
            logger.debug(f"Price: {price}")
            logger.debug(f"Volume: {volume}")
            logger.debug(f"Market Cap: {mcap}")
            
            if symbol not in self.token_history:
                # First mention of token
                self.token_history[symbol] = TokenHistoricalData(
                    symbol=symbol,
                    first_mention_date=current_time,
                    first_mention_price=price,
                    first_mention_volume_24h=volume,
                    first_mention_mcap=mcap,
                    first_mention_volume_mcap_ratio=volume_mcap_ratio,
                    current_price=price,
                    current_volume=volume,
                    current_mcap=mcap,
                    last_updated=current_time
                )
                logger.info(f"Added new token {symbol} to history")
            else:
                # Update existing token data
                token_data = self.token_history[symbol]
                time_since_mention = current_time - token_data.first_mention_date
                
                # Update performance metrics within first 7 days
                if time_since_mention <= timedelta(days=7):
                    # Always update current metrics
                    token_data.current_price = price
                    token_data.current_volume = volume
                    token_data.current_mcap = mcap
                    token_data.last_updated = current_time
                    
                    # Update 24h metrics if enough time has passed
                    if time_since_mention >= timedelta(hours=24):
                        token_data.price_24h_after = price
                        token_data.volume_24h_after = volume
                    
                    # Update 48h metrics if enough time has passed
                    if time_since_mention >= timedelta(hours=48):
                        token_data.price_48h_after = price
                        token_data.volume_48h_after = volume
                    
                    # Update 7d metrics if enough time has passed
                    if time_since_mention >= timedelta(days=7):
                        token_data.price_7d_after = price
                        token_data.volume_7d_after = volume
                    
                    # Update max price and volume within 7d
                    if price > token_data.max_price_7d:
                        token_data.max_price_7d = price
                        token_data.max_price_7d_date = current_time
                        token_data.max_gain_percentage_7d = ((price - token_data.first_mention_price) / token_data.first_mention_price) * 100
                        
                    if volume > token_data.max_volume_7d:
                        token_data.max_volume_7d = volume
                        token_data.max_volume_7d_date = current_time
                        token_data.max_volume_increase_7d = ((volume - token_data.first_mention_volume_24h) / token_data.first_mention_volume_24h) * 100 if token_data.first_mention_volume_24h > 0 else 0
                        
                    logger.debug(f"Updated existing token {symbol}")
                    
            # Save after each update
            self.save_history()
            
        except Exception as e:
            logger.error(f"Error updating token {symbol}: {str(e)}")
    
    def get_token_history(self, symbol: str) -> Optional[TokenHistoricalData]:
        """Get historical data for a specific token"""
        return self.token_history.get(symbol)
    
    def get_all_token_history(self) -> Dict[str, TokenHistoricalData]:
        """Get historical data for all tracked tokens"""
        return self.token_history
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics for all tracked tokens"""
        stats = {
            'total_tokens': len(self.token_history),
            'tokens_24h_gain': 0,
            'tokens_48h_gain': 0,
            'tokens_7d_gain': 0,
            'avg_24h_gain': 0.0,
            'avg_48h_gain': 0.0,
            'avg_7d_gain': 0.0,
            'max_24h_gain': 0.0,
            'max_48h_gain': 0.0,
            'max_7d_gain': 0.0,
            'best_performers': []
        }
        
        for token in self.token_history.values():
            # 24h performance
            if token.price_24h_after > 0:
                gain_24h = ((token.price_24h_after - token.first_mention_price) / token.first_mention_price) * 100
                if gain_24h > 0:
                    stats['tokens_24h_gain'] += 1
                stats['avg_24h_gain'] += gain_24h
                stats['max_24h_gain'] = max(stats['max_24h_gain'], gain_24h)
            
            # 48h performance
            if token.price_48h_after > 0:
                gain_48h = ((token.price_48h_after - token.first_mention_price) / token.first_mention_price) * 100
                if gain_48h > 0:
                    stats['tokens_48h_gain'] += 1
                stats['avg_48h_gain'] += gain_48h
                stats['max_48h_gain'] = max(stats['max_48h_gain'], gain_48h)
            
            # 7d performance
            if token.price_7d_after > 0:
                gain_7d = ((token.price_7d_after - token.first_mention_price) / token.first_mention_price) * 100
                if gain_7d > 0:
                    stats['tokens_7d_gain'] += 1
                stats['avg_7d_gain'] += gain_7d
                stats['max_7d_gain'] = max(stats['max_7d_gain'], gain_7d)
            
            # Track best performers (tokens with >20% gain in any timeframe)
            max_gain = token.max_gain_percentage_7d
            if max_gain >= 20:
                stats['best_performers'].append({
                    'symbol': token.symbol,
                    'first_mention_date': token.first_mention_date.isoformat(),
                    'max_gain': max_gain,
                    'max_gain_date': token.max_price_7d_date.isoformat() if token.max_price_7d_date else None,
                    'initial_volume_mcap_ratio': token.first_mention_volume_mcap_ratio
                })
        
        # Calculate averages
        total = stats['total_tokens']
        if total > 0:
            stats['avg_24h_gain'] /= total
            stats['avg_48h_gain'] /= total
            stats['avg_7d_gain'] /= total
            
        # Sort best performers by gain
        stats['best_performers'].sort(key=lambda x: x['max_gain'], reverse=True)
        
        return stats
    
    def get_recent_opportunities(self, days_back: int = 30) -> List[Dict]:
        """Get tokens that showed significant gains recently"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(days=days_back)
        
        opportunities = []
        for token in self.token_history.values():
            if token.first_mention_date >= cutoff_time and token.max_gain_percentage_7d >= 10:
                opportunities.append({
                    'symbol': token.symbol,
                    'mention_date': token.first_mention_date.isoformat(),
                    'initial_price': token.first_mention_price,
                    'max_price': token.max_price_7d,
                    'max_gain': token.max_gain_percentage_7d,
                    'time_to_max': (token.max_price_7d_date - token.first_mention_date).total_seconds() / 3600 if token.max_price_7d_date else 0,
                    'volume_mcap_ratio': token.first_mention_volume_mcap_ratio
                })
        
        # Sort by gain percentage
        opportunities.sort(key=lambda x: x['max_gain'], reverse=True)
        return opportunities
    
    def find_success_patterns(self) -> Dict:
        """Analyze patterns in successful tokens (>20% gain)"""
        patterns = {
            'avg_volume_mcap_ratio': 0.0,
            'avg_time_to_peak': 0.0,
            'best_timeframe': {'24h': 0, '48h': 0, '7d': 0},
            'total_successful': 0
        }
        
        for token in self.token_history.values():
            if token.max_gain_percentage_7d >= 20:
                patterns['total_successful'] += 1
                patterns['avg_volume_mcap_ratio'] += token.first_mention_volume_mcap_ratio
                
                if token.max_price_7d_date:
                    time_to_peak = (token.max_price_7d_date - token.first_mention_date).total_seconds() / 3600
                    patterns['avg_time_to_peak'] += time_to_peak
                
                # Determine best timeframe
                gain_24h = ((token.price_24h_after - token.first_mention_price) / token.first_mention_price * 100) if token.price_24h_after > 0 else 0
                gain_48h = ((token.price_48h_after - token.first_mention_price) / token.first_mention_price * 100) if token.price_48h_after > 0 else 0
                gain_7d = ((token.price_7d_after - token.first_mention_price) / token.first_mention_price * 100) if token.price_7d_after > 0 else 0
                
                max_gain = max(gain_24h, gain_48h, gain_7d)
                if max_gain == gain_24h:
                    patterns['best_timeframe']['24h'] += 1
                elif max_gain == gain_48h:
                    patterns['best_timeframe']['48h'] += 1
                else:
                    patterns['best_timeframe']['7d'] += 1
        
        if patterns['total_successful'] > 0:
            patterns['avg_volume_mcap_ratio'] /= patterns['total_successful']
            patterns['avg_time_to_peak'] /= patterns['total_successful']
            
        return patterns
