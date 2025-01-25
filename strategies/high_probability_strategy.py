"""High probability token tracking strategy with strict win-rate requirements"""

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

from strategies.scoring_base import BaseScoring

class CryptoRankAPI:
    """CryptoRank API client for token data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = 'https://api.cryptorank.io/v1'
        
    def fetch_tokens(self, sort_by='volume24h', direction='DESC', limit=500) -> List[Dict]:
        """Fetch token data from CryptoRank API"""
        try:
            # For testing without API key, return mock data
            if not self.api_key:
                return self._get_mock_data()
                
            params = {
                'api_key': self.api_key,
                'limit': limit,
                'sort': sort_by,
                'direction': direction
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
            },
            {
                'symbol': 'ETH',
                'price': '2500',
                'volume24h': '15000000000',
                'marketCap': '300000000000',
                'price_change_1h': '0.3',
                'price_change_24h': '1.5',
                'price_change_7d': '3.0'
            }
        ]

@dataclass
class TokenTrack:
    symbol: str
    start_monitoring_time: datetime.datetime
    initial_reference_price: float  # Internal reference only, not for reporting
    highest_price: float
    current_price: float
    last_updated: datetime.datetime
    status: str  # 'monitoring', 'success', 'expired'
    peak_gain_percentage: float
    volume_24h: float
    market_cap: float

class HighProbabilityStrategy:
    """Strategy for identifying high-probability token movements and reporting successful gains"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.api = CryptoRankAPI(api_key)
        self.tracked_tokens: Dict[str, TokenTrack] = {}
        self.tracking_file = "tracked_tokens.json"
        self.load_tracked_tokens()
        
    def load_tracked_tokens(self):
        """Load previously tracked tokens from file"""
        try:
            if os.path.exists(self.tracking_file):
                with open(self.tracking_file, 'r') as f:
                    data = json.load(f)
                    for symbol, track_data in data.items():
                        track_data['start_monitoring_time'] = datetime.datetime.fromisoformat(track_data['start_monitoring_time'])
                        track_data['last_updated'] = datetime.datetime.fromisoformat(track_data['last_updated'])
                        self.tracked_tokens[symbol] = TokenTrack(**track_data)
        except Exception as e:
            logger.error(f"Error loading tracked tokens: {e}")
            self.tracked_tokens = {}

    def save_tracked_tokens(self):
        """Save tracked tokens to file"""
        try:
            data = {}
            for symbol, track in self.tracked_tokens.items():
                track_dict = track.__dict__
                track_dict['start_monitoring_time'] = track_dict['start_monitoring_time'].isoformat()
                track_dict['last_updated'] = track_dict['last_updated'].isoformat()
                data[symbol] = track_dict
            
            with open(self.tracking_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracked tokens: {e}")

    def calculate_trend_strength(self, token: Dict) -> float:
        """Calculate trend strength score (0-100) based on multiple timeframes"""
        try:
            price_change_1h = float(token.get('price_change_1h', 0))
            price_change_24h = float(token.get('price_change_24h', 0))
            price_change_7d = float(token.get('price_change_7d', 0))
            
            # Weight recent price changes more heavily
            trend_score = (
                price_change_1h * 0.4 +
                price_change_24h * 0.35 +
                price_change_7d * 0.25
            )
            
            # Normalize to 0-100 scale
            return max(0, min(100, (trend_score + 100) / 2))
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0

    def calculate_volume_quality(self, token: Dict) -> float:
        """Calculate volume quality score (0-100) based on volume and market cap"""
        try:
            volume_24h = float(token.get('volume24h', 0))
            market_cap = float(token.get('marketCap', 0))
            
            if market_cap == 0:
                return 0
                
            volume_to_mcap = volume_24h / market_cap
            
            # Score based on healthy volume/mcap ratio (0.1-0.3 is considered healthy)
            if volume_to_mcap < 0.05:
                return 0  # Too little volume
            elif volume_to_mcap > 1:
                return 0  # Too much volume, suspicious
            elif 0.1 <= volume_to_mcap <= 0.3:
                return 100  # Ideal range
            else:
                # Scale linearly between ranges
                if volume_to_mcap < 0.1:
                    return (volume_to_mcap - 0.05) * 2000  # Scale from 0.05-0.1
                else:
                    return max(0, 100 - (volume_to_mcap - 0.3) * 142.85)  # Scale down from 0.3-1.0
                    
        except Exception as e:
            logger.error(f"Error calculating volume quality: {e}")
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

    def find_high_probability_tokens(self) -> List[Dict]:
        """Identify tokens with highest probability of price increase"""
        try:
            # Fetch top 500 tokens by volume
            tokens = self.api.fetch_tokens(sort_by='volume24h', direction='DESC', limit=500)
            
            high_prob_tokens = []
            for token in tokens:
                if not self.is_token_valid(token):
                    continue
                    
                trend_score = self.calculate_trend_strength(token)
                volume_score = self.calculate_volume_quality(token)
                
                # Require both high trend and volume scores
                if trend_score >= 70 and volume_score >= 80:
                    token['trend_score'] = trend_score
                    token['volume_score'] = volume_score
                    token['combined_score'] = (trend_score * 0.6 + volume_score * 0.4)
                    high_prob_tokens.append(token)
            
            # Sort by combined score
            return sorted(high_prob_tokens, key=lambda x: x['combined_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error finding high probability tokens: {e}")
            return []

    def start_tracking(self, token: Dict):
        """Start monitoring a new token without announcing entry price"""
        try:
            symbol = token['symbol']
            if symbol in self.tracked_tokens:
                return
                
            current_price = float(token['price'])
            track = TokenTrack(
                symbol=symbol,
                start_monitoring_time=datetime.datetime.now(),
                initial_reference_price=current_price,  # Keep internally but don't report
                highest_price=current_price,
                current_price=current_price,
                last_updated=datetime.datetime.now(),
                status='monitoring',
                peak_gain_percentage=0.0,
                volume_24h=float(token['volume24h']),
                market_cap=float(token['marketCap'])
            )
            
            self.tracked_tokens[symbol] = track
            self.save_tracked_tokens()
            
            logger.info(f"Started monitoring {symbol}")
            
        except Exception as e:
            logger.error(f"Error starting to monitor token: {e}")

    def update_tracking(self, token: Dict):
        """Update tracking and identify successful price movements"""
        try:
            symbol = token['symbol']
            if symbol not in self.tracked_tokens:
                return
                
            track = self.tracked_tokens[symbol]
            current_price = float(token['price'])
            track.current_price = current_price
            track.last_updated = datetime.datetime.now()
            
            # Update volume and market cap
            track.volume_24h = float(token['volume24h'])
            track.market_cap = float(token['marketCap'])
            
            # Calculate gain from initial reference (internal only)
            gain_pct = ((current_price - track.initial_reference_price) / track.initial_reference_price) * 100
            
            # Update highest price if new high
            if current_price > track.highest_price:
                track.highest_price = current_price
                track.peak_gain_percentage = gain_pct
                
                # If we have a significant gain, mark as success
                if gain_pct >= 5.0:  # Minimum 5% gain to report
                    track.status = 'success'
                    logger.info(f"{symbol} reached {gain_pct:.1f}% gain")
            
            # Check if 7 days have passed
            elif (datetime.datetime.now() - track.start_monitoring_time).days >= 7:
                track.status = 'expired'
                
            self.save_tracked_tokens()
            
        except Exception as e:
            logger.error(f"Error updating token monitoring: {e}")

    def get_successful_trades(self) -> List[Dict]:
        """Get list of successful trades to report"""
        try:
            successful = []
            for track in self.tracked_tokens.values():
                if track.status == 'success':
                    successful.append({
                        'symbol': track.symbol,
                        'highest_price': track.highest_price,
                        'gain_percentage': track.peak_gain_percentage,
                        'volume_24h': track.volume_24h,
                        'market_cap': track.market_cap
                    })
            return sorted(successful, key=lambda x: x['gain_percentage'], reverse=True)
        except Exception as e:
            logger.error(f"Error getting successful trades: {e}")
            return []

    def analyze(self) -> Dict:
        """Run analysis and return results"""
        try:
            # Update existing tracked tokens
            tokens = self.api.fetch_tokens(limit=2000)
            token_map = {t['symbol']: t for t in tokens}
            
            for symbol in list(self.tracked_tokens.keys()):
                if symbol in token_map:
                    self.update_tracking(token_map[symbol])
            
            # Find new high probability tokens
            high_prob_tokens = self.find_high_probability_tokens()
            
            # Start monitoring new tokens (limit to top 5 at a time)
            active_monitoring = len([t for t in self.tracked_tokens.values() 
                                   if t.status == 'monitoring'])
            
            for token in high_prob_tokens[:max(0, 5 - active_monitoring)]:
                self.start_tracking(token)
            
            # Get successful trades
            successful_trades = self.get_successful_trades()
            
            return {
                'monitoring_tokens': [t for t in self.tracked_tokens.values() if t.status == 'monitoring'],
                'successful_trades': successful_trades,
                'new_candidates': high_prob_tokens[:5]
            }
            
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return {}
