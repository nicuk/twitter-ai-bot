"""Strategy for maximizing follower engagement through high-accuracy trade predictions"""

import os
import sys
from pathlib import Path
import datetime
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
import requests

# Set up logging
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

@dataclass
class TradeRecord:
    symbol: str
    detection_time: datetime.datetime
    initial_price: float  # Internal only, not for display
    current_price: float
    highest_price: float
    volume_24h: float
    market_cap: float
    trend_score: float
    volume_score: float
    status: str  # 'monitoring', 'success', 'expired'
    peak_gain: float
    engagement_score: float
    last_updated: datetime.datetime
    announcement_made: bool  # Whether we've announced this as a success

class EngagementStrategy:
    """Strategy for maximizing social engagement through high-accuracy predictions"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = 'https://api.cryptorank.io/v1'
        self.monitored_tokens: Dict[str, TradeRecord] = {}
        self.track_record_file = "track_record.json"
        self.success_threshold = 5.0  # Minimum gain % to count as success
        self.monitoring_days = 7
        self.load_track_record()

    def load_track_record(self):
        """Load existing track record"""
        try:
            if os.path.exists(self.track_record_file):
                with open(self.track_record_file, 'r') as f:
                    data = json.load(f)
                    for symbol, record in data.items():
                        record['detection_time'] = datetime.datetime.fromisoformat(record['detection_time'])
                        record['last_updated'] = datetime.datetime.fromisoformat(record['last_updated'])
                        self.monitored_tokens[symbol] = TradeRecord(**record)
        except Exception as e:
            logger.error(f"Error loading track record: {e}")
            self.monitored_tokens = {}

    def save_track_record(self):
        """Save track record to file"""
        try:
            data = {}
            for symbol, record in self.monitored_tokens.items():
                record_dict = record.__dict__
                record_dict['detection_time'] = record_dict['detection_time'].isoformat()
                record_dict['last_updated'] = record_dict['last_updated'].isoformat()
                data[symbol] = record_dict
            
            with open(self.track_record_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving track record: {e}")

    def calculate_engagement_score(self, token: Dict) -> float:
        """Calculate how engaging a token might be for followers"""
        try:
            market_cap = float(token.get('marketCap', 0))
            volume_24h = float(token.get('volume24h', 0))
            price_change_24h = abs(float(token.get('price_change_24h', 0)))
            
            # Factors that make a token interesting to followers:
            # 1. Large enough to be credible (market cap)
            # 2. Active enough to be tradeable (volume)
            # 3. Volatile enough to be exciting (price change)
            
            market_cap_score = min(market_cap / 1e9, 1.0)  # Cap at 1B market cap
            volume_score = min(volume_24h / market_cap, 1.0) if market_cap > 0 else 0
            volatility_score = min(price_change_24h / 10, 1.0)  # Cap at 10% change
            
            # Weight the scores (adjust weights based on what drives more engagement)
            return (market_cap_score * 0.3 + 
                   volume_score * 0.4 + 
                   volatility_score * 0.3) * 100
                   
        except Exception as e:
            logger.error(f"Error calculating engagement score: {e}")
            return 0

    def get_token_data(self, limit: int = 500) -> List[Dict]:
        """Fetch token data from API"""
        try:
            if not self.api_key:
                return self._get_mock_data()
                
            params = {
                'api_key': self.api_key,
                'limit': limit,
                'sort': 'volume24h',
                'direction': 'DESC'
            }
            
            response = requests.get(f"{self.base_url}/currencies", params=params)
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                return self._get_mock_data()
                
            data = response.json()
            return data.get('data', [])
            
        except Exception as e:
            logger.error(f"Error fetching tokens: {e}")
            return self._get_mock_data()

    def _get_mock_data(self) -> List[Dict]:
        """Return mock data for testing"""
        return [
            {
                'symbol': 'BTC',
                'price': '40000',
                'volume24h': '20000000000',
                'marketCap': '800000000000',
                'price_change_1h': '0.5',
                'price_change_24h': '2.5',
                'price_change_7d': '5.0'
            }
        ]

    def calculate_trend_score(self, token: Dict) -> float:
        """Calculate trend strength score (0-100)"""
        try:
            price_change_1h = float(token.get('price_change_1h', 0))
            price_change_24h = float(token.get('price_change_24h', 0))
            price_change_7d = float(token.get('price_change_7d', 0))
            
            # Weight recent changes more heavily
            weighted_change = (
                price_change_1h * 0.4 +
                price_change_24h * 0.35 +
                price_change_7d * 0.25
            )
            
            # Normalize to 0-100 scale
            return max(0, min(100, (weighted_change + 10) * 5))
            
        except Exception as e:
            logger.error(f"Error calculating trend score: {e}")
            return 0

    def calculate_volume_score(self, token: Dict) -> float:
        """Calculate volume quality score (0-100)"""
        try:
            volume_24h = float(token.get('volume24h', 0))
            market_cap = float(token.get('marketCap', 0))
            
            if market_cap == 0:
                return 0
                
            volume_ratio = volume_24h / market_cap
            
            # Score based on volume/mcap ratio
            if volume_ratio < 0.05:
                return 0  # Too little volume
            elif volume_ratio > 1:
                return 0  # Too much volume (suspicious)
            elif 0.1 <= volume_ratio <= 0.3:
                return 100  # Ideal range
            else:
                # Scale linearly between ranges
                if volume_ratio < 0.1:
                    return (volume_ratio - 0.05) * 2000
                else:
                    return max(0, 100 - (volume_ratio - 0.3) * 142.85)
                    
        except Exception as e:
            logger.error(f"Error calculating volume score: {e}")
            return 0

    def is_token_valid(self, token: Dict) -> bool:
        """Check if token meets basic validity criteria"""
        try:
            # Must have minimum market cap of $10M
            if float(token.get('marketCap', 0)) < 10_000_000:
                return False
                
            # Must have minimum 24h volume of $1M
            if float(token.get('volume24h', 0)) < 1_000_000:
                return False
                
            # Exclude stablecoins and wrapped tokens
            symbol = token.get('symbol', '').upper()
            if any(x in symbol for x in ['USD', 'USDT', 'USDC', 'DAI', 'BUSD', 'W']):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking token validity: {e}")
            return False

    def start_monitoring(self, token: Dict):
        """Start monitoring a new token without announcing entry"""
        try:
            symbol = token['symbol']
            if symbol in self.monitored_tokens:
                return
                
            current_price = float(token['price'])
            trend_score = self.calculate_trend_score(token)
            volume_score = self.calculate_volume_score(token)
            engagement_score = self.calculate_engagement_score(token)
            
            record = TradeRecord(
                symbol=symbol,
                detection_time=datetime.datetime.now(),
                initial_price=current_price,
                current_price=current_price,
                highest_price=current_price,
                volume_24h=float(token['volume24h']),
                market_cap=float(token['marketCap']),
                trend_score=trend_score,
                volume_score=volume_score,
                status='monitoring',
                peak_gain=0.0,
                engagement_score=engagement_score,
                last_updated=datetime.datetime.now(),
                announcement_made=False
            )
            
            self.monitored_tokens[symbol] = record
            self.save_track_record()
            
            logger.info(f"Started monitoring {symbol} (Engagement Score: {engagement_score:.1f})")
            
        except Exception as e:
            logger.error(f"Error starting to monitor token: {e}")

    def update_monitoring(self, token: Dict) -> Optional[Dict]:
        """Update monitoring and return announcement data if needed"""
        try:
            symbol = token['symbol']
            if symbol not in self.monitored_tokens:
                return None
                
            record = self.monitored_tokens[symbol]
            current_price = float(token['price'])
            record.current_price = current_price
            record.volume_24h = float(token['volume24h'])
            record.market_cap = float(token['marketCap'])
            record.last_updated = datetime.datetime.now()
            
            # Calculate gain from initial price
            gain_pct = ((current_price - record.initial_price) / record.initial_price) * 100
            
            # Update highest price and peak gain
            if current_price > record.highest_price:
                record.highest_price = current_price
                record.peak_gain = gain_pct
                
                # Check if we should announce success
                if gain_pct >= self.success_threshold and not record.announcement_made:
                    record.status = 'success'
                    record.announcement_made = True
                    self.save_track_record()
                    return {
                        'type': 'success',
                        'symbol': symbol,
                        'gain': gain_pct,
                        'trend_score': record.trend_score,
                        'volume_score': record.volume_score,
                        'price': current_price
                    }
            
            # Check if monitoring period expired
            if (datetime.datetime.now() - record.detection_time).days >= self.monitoring_days:
                record.status = 'expired'
                self.save_track_record()
                
            return None
            
        except Exception as e:
            logger.error(f"Error updating monitoring: {e}")
            return None

    def get_performance_stats(self) -> Dict:
        """Get strategy performance statistics"""
        try:
            completed = [r for r in self.monitored_tokens.values() 
                        if r.status in ['success', 'expired']]
            
            if not completed:
                return {
                    'total_predictions': 0,
                    'success_rate': 0,
                    'avg_gain': 0,
                    'best_gain': 0
                }
            
            successes = [r for r in completed if r.status == 'success']
            
            return {
                'total_predictions': len(completed),
                'success_rate': (len(successes) / len(completed)) * 100,
                'avg_gain': sum(r.peak_gain for r in successes) / len(successes) if successes else 0,
                'best_gain': max((r.peak_gain for r in successes), default=0)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance stats: {e}")
            return {}

    def analyze(self) -> Dict:
        """Run analysis and return results"""
        try:
            announcements = []
            
            # Update existing monitored tokens
            tokens = self.get_token_data(limit=2000)
            token_map = {t['symbol']: t for t in tokens}
            
            for symbol in list(self.monitored_tokens.keys()):
                if symbol in token_map:
                    announcement = self.update_monitoring(token_map[symbol])
                    if announcement:
                        announcements.append(announcement)
            
            # Find new potential tokens
            candidates = []
            for token in tokens:
                if not self.is_token_valid(token):
                    continue
                    
                trend_score = self.calculate_trend_score(token)
                volume_score = self.calculate_volume_score(token)
                engagement_score = self.calculate_engagement_score(token)
                
                if trend_score >= 70 and volume_score >= 80:
                    token['trend_score'] = trend_score
                    token['volume_score'] = volume_score
                    token['engagement_score'] = engagement_score
                    candidates.append(token)
            
            # Sort candidates by engagement potential
            candidates.sort(key=lambda x: x['engagement_score'], reverse=True)
            
            # Start monitoring top candidates (limit to 5 active)
            active_monitoring = len([r for r in self.monitored_tokens.values() 
                                   if r.status == 'monitoring'])
            
            for token in candidates[:max(0, 5 - active_monitoring)]:
                self.start_monitoring(token)
            
            return {
                'announcements': announcements,
                'monitoring': [r for r in self.monitored_tokens.values() 
                             if r.status == 'monitoring'],
                'candidates': candidates[:5],
                'stats': self.get_performance_stats()
            }
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return {}
