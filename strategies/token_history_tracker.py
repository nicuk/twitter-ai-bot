"""Track historical data for tokens that pass filters"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
import os
import logging
import redis

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
    _initialized = False
    
    def __new__(cls):
        """Create singleton instance"""
        if cls._instance is None:
            cls._instance = super(TokenHistoryTracker, cls).__new__(cls)
        return cls._instance
        
    def __init__(self):
        """Initialize tracker with Redis storage if available, fallback to file"""
        if TokenHistoryTracker._initialized:
            return
            
        TokenHistoryTracker._initialized = True
        
        # Initialize storage
        self.token_history: Dict[str, TokenHistoricalData] = {}
        self.using_redis = False
        
        # Try Redis first - use Railway's variable reference
        redis_url = os.getenv('REDIS_URL')  # Railway format
        logger.info(f"Redis URL found: {redis_url is not None}")
        if redis_url:
            try:
                logger.info("Attempting to connect to Redis...")
                self.redis = redis.from_url(redis_url)
                # Test connection
                self.redis.ping()
                self.using_redis = True
                logger.info("Connected to Redis successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                logger.info("Falling back to file storage")
                self.setup_file_storage()
        else:
            logger.info("No REDIS_URL found, using file storage")
            self.setup_file_storage()
            
        self.load_history()
        
    def setup_file_storage(self):
        """Set up file-based storage"""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        self.history_file = os.path.join(self.data_dir, 'token_history.json')
        logger.info(f"Using file storage at: {self.history_file}")
        
    def load_history(self):
        """Load token history from storage"""
        try:
            if self.using_redis:
                data = self.redis.get('token_history')
                if data:
                    json_data = json.loads(data)
                    # Filter out tokens with invalid (0) first mention values
                    valid_tokens = {
                        symbol: TokenHistoricalData.from_dict(token_data)
                        for symbol, token_data in json_data.items()
                        if token_data.get('first_mention_price', 0) > 0 
                        and token_data.get('first_mention_volume_24h', 0) > 0
                        and token_data.get('first_mention_mcap', 0) > 0
                    }
                    self.token_history = valid_tokens
                    logger.info(f"Loaded {len(self.token_history)} valid tokens from Redis")
                    if len(valid_tokens) < len(json_data):
                        logger.info(f"Removed {len(json_data) - len(valid_tokens)} invalid tokens with 0 values")
            else:
                if os.path.exists(self.history_file):
                    with open(self.history_file, 'r') as f:
                        data = json.load(f)
                        if data:
                            # Filter out tokens with invalid (0) first mention values
                            valid_tokens = {
                                symbol: TokenHistoricalData.from_dict(token_data)
                                for symbol, token_data in data.items()
                                if token_data.get('first_mention_price', 0) > 0 
                                and token_data.get('first_mention_volume_24h', 0) > 0
                                and token_data.get('first_mention_mcap', 0) > 0
                            }
                            self.token_history = valid_tokens
                            logger.info(f"Loaded {len(self.token_history)} valid tokens from file")
                            if len(valid_tokens) < len(data):
                                logger.info(f"Removed {len(data) - len(valid_tokens)} invalid tokens with 0 values")
                        
        except Exception as e:
            logger.error(f"Error loading token history: {e}")
    
    def save_history(self):
        """Save token history to storage"""
        try:
            data = {
                symbol: token.to_dict() 
                for symbol, token in self.token_history.items()
            }
            
            if self.using_redis:
                self.redis.set('token_history', json.dumps(data))
                logger.info(f"Saved {len(self.token_history)} tokens to Redis")
            else:
                with open(self.history_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Saved {len(self.token_history)} tokens to file")
                
        except Exception as e:
            logger.error(f"Error saving token history: {e}")
    
    def update_token(self, token: Dict):
        """Update token data in history"""
        try:
            # Extract token data using correct keys from CryptoRank API
            symbol = token.get('symbol', '').upper()
            if not symbol:
                logger.warning("No symbol found in token data")
                return
                
            # Extract values from passed token data
            price = float(token.get('current_price', 0))
            volume = float(token.get('current_volume', 0))
            mcap = float(token.get('current_mcap', 0))
            volume_mcap_ratio = (volume / mcap * 100) if mcap > 0 else 0
            current_time = datetime.now()
            
            # Validate current_time is not in the future
            if current_time > datetime.now() + timedelta(minutes=5):
                logger.error(f"Invalid future timestamp detected for {symbol}: {current_time}")
                return
            
            # Add detailed debug logging
            logger.info(f"Updating token {symbol}:")
            logger.info(f"Raw token data: {token}")
            logger.info(f"Extracted values:")
            logger.info(f"  Price: {price}")
            logger.info(f"  Volume: {volume}")
            logger.info(f"  Market Cap: {mcap}")
            logger.info(f"  V/MC Ratio: {volume_mcap_ratio}")
            
            if symbol not in self.token_history:
                # First mention of token
                logger.info(f"First mention of token {symbol}")
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
            else:
                # Update existing token data
                logger.info(f"Updating existing token {symbol}")
                token_data = self.token_history[symbol]
                
                # Validate first_mention_date is not in the future
                if token_data.first_mention_date > datetime.now():
                    logger.error(f"Invalid future first_mention_date detected for {symbol}: {token_data.first_mention_date}")
                    del self.token_history[symbol]
                    return
                
                # Update current values
                token_data.current_price = price
                token_data.current_volume = volume
                token_data.current_mcap = mcap
                token_data.last_updated = current_time
                
                # Calculate time since first mention
                time_diff = current_time - token_data.first_mention_date
                logger.info(f"Time since first mention: {time_diff}")
                
                # Update time-based metrics if enough time has passed
                # Continue updating these values even after the time period
                if time_diff >= timedelta(hours=24):
                    logger.info(f"Updating 24h metrics for {symbol}")
                    token_data.price_24h_after = price
                    token_data.volume_24h_after = volume
                
                if time_diff >= timedelta(hours=48):
                    logger.info(f"Updating 48h metrics for {symbol}")
                    token_data.price_48h_after = price
                    token_data.volume_48h_after = volume
                
                if time_diff >= timedelta(days=7):
                    logger.info(f"Updating 7d metrics for {symbol}")
                    token_data.price_7d_after = price
                    token_data.volume_7d_after = volume
                
                # Update max values (now tracked beyond 7 days)
                if price > token_data.max_price_7d:
                    logger.info(f"New max price for {symbol}: {price}")
                    token_data.max_price_7d = price
                    token_data.max_price_7d_date = current_time
                    # Avoid division by zero for price gain calculation
                    if token_data.first_mention_price > 0:
                        token_data.max_gain_percentage_7d = ((price - token_data.first_mention_price) / token_data.first_mention_price) * 100
                    else:
                        token_data.max_gain_percentage_7d = 0
                        logger.warning(f"First mention price is 0 for {symbol}, cannot calculate gain percentage")
                
                if volume > token_data.max_volume_7d:
                    logger.info(f"New max volume for {symbol}: {volume}")
                    token_data.max_volume_7d = volume
                    token_data.max_volume_7d_date = current_time
                    # Avoid division by zero for volume increase calculation
                    if token_data.first_mention_volume_24h > 0:
                        token_data.max_volume_increase_7d = ((volume - token_data.first_mention_volume_24h) / token_data.first_mention_volume_24h) * 100
                    else:
                        token_data.max_volume_increase_7d = 0
                        logger.warning(f"First mention volume is 0 for {symbol}, cannot calculate volume increase")
            
            # Save changes to storage
            self.save_history()
            
        except Exception as e:
            logger.error(f"Error updating token {symbol}: {e}")
    
    def get_token_history(self, symbol: str) -> Optional[TokenHistoricalData]:
        """Get historical data for a specific token"""
        return self.token_history.get(symbol.upper())

    def calculate_price_change(self, symbol: str) -> float:
        """Calculate price change percentage since first mention"""
        token = self.token_history.get(symbol)
        if not token:
            return 0.0
        if token.first_mention_price == 0:
            return 0.0
        return ((token.current_price - token.first_mention_price) / token.first_mention_price) * 100

    def calculate_volume_change(self, symbol: str) -> float:
        """Calculate volume change percentage since first mention"""
        token = self.get_token_history(symbol)
        if not token:
            return 0.0
        if token.first_mention_volume_24h == 0:
            return 0.0
        return ((token.current_volume - token.first_mention_volume_24h) / token.first_mention_volume_24h) * 100

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
