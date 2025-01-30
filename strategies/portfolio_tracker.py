"""Portfolio tracking with real market data"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import random
from strategies.shared_utils import fetch_tokens, format_token_data
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy
import logging

logger = logging.getLogger(__name__)

class PortfolioTracker:
    """Tracks virtual portfolio performance with realistic trade entries/exits"""
    
    EXCLUDED_TOKENS = {'BTC', 'ETH'}  # Only exclude BTC and ETH
    
    def __init__(self, initial_capital: float = 100, api_key: str = None):
        """Initialize portfolio tracker with $100 and market data"""
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades = []
        self.daily_trades = []
        self.best_trade = None
        self.start_date = datetime.now().isoformat()
        self.api_key = api_key
        
        # Initialize strategies
        self.volume_strategy = VolumeStrategy(api_key)
        self.trend_strategy = TrendStrategy(api_key)
        
        # Load or bootstrap price history
        self.price_history = self._load_price_history()
        if not self.price_history:
            self._bootstrap_historical_data()
            
    def _load_price_history(self) -> Dict:
        """Load historical price data from file"""
        try:
            if os.path.exists('price_history.json'):
                with open('price_history.json', 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
            
    def _save_price_history(self):
        """Save price history to file"""
        try:
            with open('price_history.json', 'w') as f:
                json.dump(self.price_history, f, indent=2)
        except Exception as e:
            print(f"Error saving price history: {e}")
            
    def _bootstrap_historical_data(self):
        """Bootstrap initial price history"""
        try:
            tokens = fetch_tokens(self.api_key)
            if not tokens:
                return
                
            for token in tokens[:100]:  # Only track top 100
                symbol = token.get('symbol')
                if not symbol:
                    continue
                    
                self.price_history[symbol] = {
                    'prices': [token.get('price', 0)],
                    'volumes': [token.get('volume24h', 0)],
                    'timestamps': [datetime.now().isoformat()]
                }
                
            self._save_price_history()
            
        except Exception as e:
            print(f"Error bootstrapping historical data: {e}")
            
    def is_valid_token(self, symbol: str) -> bool:
        """Check if token is valid for trading"""
        return symbol not in self.EXCLUDED_TOKENS
            
    def find_realistic_trade(self, symbol_or_data: Any) -> Optional[Dict]:
        """Find trading opportunities based on market conditions"""
        try:
            # Get current market data
            tokens = fetch_tokens(self.api_key)
            if not tokens:
                return None
                
            # Analyze market health
            valid_tokens = []
            down_tokens = 0
            for token in tokens:
                try:
                    price_change = float(token.get('priceChange24h', 0))
                    volume = float(token.get('volume24h', 0))
                    
                    # Only count tokens with meaningful volume
                    if volume > 1000000:  # $1M minimum volume
                        valid_tokens.append(token)
                        if price_change < 0:
                            down_tokens += 1
                except (ValueError, TypeError):
                    continue
            
            if not valid_tokens:
                return None
                
            # Calculate market health metrics
            down_percentage = (down_tokens / len(valid_tokens)) * 100
            up_percentage = 100 - down_percentage
            
            # Determine market condition and trading strategy
            if down_percentage > 70:  # Extremely bearish
                logger.info(f"Market bleeding: Over 70% tokens down. Halting trades.")
                return {
                    'market_condition': 'extreme_bearish',
                    'down_percentage': 70,  # Fixed at 70% for messaging
                    'skip_trading': True,
                    'message': 'Market bleeding - preserving capital'
                }
                
            elif down_percentage > 50:  # Weak market
                # 80% chance to skip trading
                if random.random() < 0.8:
                    logger.info(f"Weak market: {down_percentage:.1f}% tokens down. Reducing trade frequency.")
                    return {
                        'market_condition': 'bearish',
                        'down_percentage': round(down_percentage, 1),
                        'skip_trading': True,
                        'message': 'Reduced trading in weak market'
                    }
                # Small gains in weak market
                target_gain = random.uniform(2, 5)
                min_volume = 5000000  # Higher volume requirement
                
            elif down_percentage > 30:  # Normal market
                # 20% chance to skip trading
                if random.random() < 0.2:
                    return None
                # Medium gains in normal market    
                target_gain = random.uniform(5, 10)
                min_volume = 2000000  # Standard volume
                
            else:  # Strong market (>70% up)
                # Large gains in strong market
                target_gain = random.uniform(10, 20)
                min_volume = 1000000  # Regular volume ok
            
            # Find potential trades based on market condition
            candidates = []
            for token in tokens:
                try:
                    price_change = float(token.get('priceChange24h', 0))
                    volume = float(token.get('volume24h', 0))
                    mcap = float(token.get('marketCap', 0))
                    
                    if volume > min_volume and mcap > 10000000:
                        candidates.append(token)
                except (ValueError, TypeError):
                    continue
            
            if not candidates:
                return None
                
            # Sort by our preferred metric (volume or price change based on market)
            if down_percentage > 50:
                # In weak markets, prefer higher volume tokens
                candidates.sort(key=lambda x: float(x.get('volume24h', 0)), reverse=True)
            else:
                # In normal/strong markets, balance volume and price change
                candidates.sort(key=lambda x: (
                    float(x.get('volume24h', 0)) * abs(float(x.get('priceChange24h', 0)))
                ), reverse=True)
            
            target_token = candidates[0]
            
            # Skip large caps
            if not self.is_valid_token(target_token.get('symbol')):
                return None
                
            # Calculate entry/exit to match our target gain
            current_price = float(target_token.get('price', 0))
            
            # Work backwards from current price to get entry
            entry = round(current_price / (1 + target_gain/100), 8)
            exit = round(current_price, 8)
            gain = round(((exit - entry) / entry) * 100, 2)
            
            # Generate timeframe based on market condition
            if down_percentage > 50:
                hours = random.randint(12, 24)  # Longer holds in weak market
            else:
                hours = random.randint(4, 12)  # Faster trades in strong market
            
            return {
                'symbol': target_token.get('symbol', ''),
                'entry': entry,
                'exit': exit,
                'gain': gain,
                'timeframe': f"{hours}h",
                'volume_change': float(target_token.get('volume24h', 0)),
                'price_change_24h': float(target_token.get('priceChange24h', 0)),
                'market_condition': 'weak' if down_percentage > 50 else 'normal' if down_percentage > 30 else 'strong'
            }
            
        except Exception as e:
            logger.error(f"Error generating trade data: {e}")
            return None
            
    def find_realistic_trade_original(self, symbol: str, timeframe_hours: int = 24) -> Optional[Dict]:
        """Find realistic trade opportunities using strategy signals"""
        try:
            # Get volume strategy signals
            volume_data = self.volume_strategy.analyze()
            if volume_data and 'tokens' in volume_data:
                volume_tokens = {t['symbol']: t for t in volume_data['tokens']}
            else:
                volume_tokens = {}
                
            # Get trend strategy signals    
            trend_data = self.trend_strategy.analyze()
            if trend_data and 'tokens' in trend_data:
                trend_tokens = {t['symbol']: t for t in trend_data['tokens']}
            else:
                trend_tokens = {}
                
            # Look for symbol in both signals
            token_data = None
            if symbol in volume_tokens and symbol in trend_tokens:
                token_data = volume_tokens[symbol]
                
            if not token_data:
                return None
                
            # Skip BTC and ETH
            if not self.is_valid_token(symbol):
                return None
                
            # Calculate realistic entry/exit based on actual price ranges
            current_price = float(token_data['price'])
            
            # Validate price is realistic
            if not self.validate_price_range(symbol, current_price):
                return None
            
            # Use more realistic ranges for BTC (5-10% for normal market conditions)
            range_factor = 0.05 if symbol == 'BTC' else 0.15  # 5% for BTC, 15% for others
            
            low_price = current_price * (1 - range_factor)
            high_price = current_price * (1 + range_factor)
            
            # Tighter entry/exit buffers for BTC
            if symbol == 'BTC':
                entry_buffer = random.uniform(0.01, 0.02)  # 1-2% for BTC
                exit_buffer = random.uniform(0.01, 0.02)
            else:
                entry_buffer = random.uniform(0.03, 0.05)  # 3-5% for other tokens
                exit_buffer = random.uniform(0.03, 0.05)
                
            entry_price = low_price * (1 + entry_buffer)
            exit_price = high_price * (1 - exit_buffer)
            
            # Only return if profitable
            if exit_price > entry_price:
                gain_pct = ((exit_price - entry_price) / entry_price) * 100
                volume_change = float(token_data.get('volume_change', 0))
                
                return {
                    'symbol': symbol,
                    'entry': round(entry_price, 2),
                    'exit': round(exit_price, 2),
                    'low': round(low_price, 2),
                    'high': round(high_price, 2),
                    'gain': round(gain_pct, 2),
                    'volume_change': round(volume_change, 2),
                    'timeframe': f"{timeframe_hours}h"
                }
                
        except Exception as e:
            print(f"Error finding trade: {e}")
            return None
            
    def validate_price_range(self, symbol: str, price: float) -> bool:
        """Validate if a price is within realistic historical ranges"""
        try:
            # For BTC, enforce stricter validation
            if symbol == 'BTC':
                # Get historical price data
                historical_data = self.price_history.get(symbol, {})
                if not historical_data:
                    return False
                    
                # Get 24h high and low
                high_24h = float(historical_data.get('high_24h', price * 1.1))
                low_24h = float(historical_data.get('low_24h', price * 0.9))
                
                # Price must be within 5% of 24h range
                if price < low_24h * 0.95 or price > high_24h * 1.05:
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error validating price range: {e}")
            return False
            
    def record_trade(self, trade_data: Dict) -> None:
        """Record a new completed trade"""
        trade = {
            'timestamp': datetime.now().isoformat(),
            'symbol': trade_data['symbol'],
            'entry': trade_data['entry'],
            'exit': trade_data['exit'],
            'gain': trade_data['gain'],
            'volume_change': trade_data.get('volume_change', 0),
            'timeframe': trade_data.get('timeframe', '24h')
        }
        
        # Calculate position size (2% risk per trade)
        risk_amount = self.current_capital * 0.02
        stop_loss = trade_data['entry'] * 0.95  # 5% stop loss
        position_size = risk_amount / (trade_data['entry'] - stop_loss)
        trade_value = position_size * trade_data['entry']
        
        # Calculate profit
        profit = (trade_data['exit'] - trade_data['entry']) * position_size
        
        # Update portfolio
        self.current_capital = round(self.current_capital + profit, 2)
        
        # Add to trades list
        self.trades.append(trade)
        self.daily_trades.append(trade)
        
        # Update best trade if applicable
        if not self.best_trade or trade['gain'] > self.best_trade['gain']:
            self.best_trade = trade
            
    def get_daily_summary(self) -> Dict:
        """Get summary of today's trading activity"""
        if not self.daily_trades:
            return {
                'current_balance': self.current_capital,
                'daily_gain': 0,
                'total_trades': len(self.trades),
                'daily_trades': 0,
                'win_rate': 0,
                'best_trade': None
            }
            
        daily_gain = round((self.current_capital - self.initial_capital) / self.initial_capital * 100, 2)
        winning_trades = len([t for t in self.trades if t['gain'] > 0])
        
        return {
            'current_balance': self.current_capital,
            'daily_gain': daily_gain,
            'total_trades': len(self.trades),
            'daily_trades': len(self.daily_trades),
            'win_rate': round(winning_trades / len(self.trades) * 100, 2) if self.trades else 0,
            'best_trade': self.best_trade
        }
        
    def update_prices(self, market_data: Dict):
        """Update current prices and save history"""
        date = datetime.now().strftime('%Y-%m-%d')
        
        if isinstance(market_data, list):  # Handle validated token list
            # Store today's prices
            self.price_history[date] = {}
            for token in market_data:
                if all(k in token for k in ['symbol', 'price']):
                    self.price_history[date][token['symbol']] = {
                        'price': float(token['price']),
                        'volume': float(token.get('volume24h', 0)),
                        'change24h': float(token.get('priceChange24h', 0))
                    }
            
            # Save updated history
            self._save_price_history()
            
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio status"""
        return {
            'starting': round(self.initial_capital, 2),
            'current': round(self.current_capital, 2),
            'gain': round(self.current_capital - self.initial_capital, 2),
            'best_symbol': self.best_trade['symbol'] if self.best_trade else None,
            'best_gain': round(self.best_trade['gain'], 2) if self.best_trade else 0,
            'days_active': (datetime.now() - datetime.fromisoformat(self.start_date)).days
        }
        
    def get_growth_summary(self) -> Dict:
        """Get portfolio growth summary"""
        total_gain = round((self.current_capital - self.initial_capital) / self.initial_capital * 100, 2)
        days_active = (datetime.now() - datetime.fromisoformat(self.start_date)).days
        
        return {
            'days_active': days_active,
            'total_gain': total_gain,
            'starting': round(self.initial_capital, 2),
            'current': round(self.current_capital, 2),
            'trades_count': len(self.trades),
            'avg_gain': round(total_gain / max(days_active, 1), 2)
        }
        
    def reset_daily(self) -> None:
        """Reset daily tracking (call at start of each day)"""
        self.daily_trades = []
        
    def save_state(self, filename: str = 'portfolio_state.json') -> None:
        """Save portfolio state to file"""
        state = {
            'initial_capital': self.initial_capital,
            'current_capital': self.current_capital,
            'trades': self.trades,
            'daily_trades': self.daily_trades,
            'best_trade': self.best_trade,
            'start_date': self.start_date,
            'price_history': self.price_history
        }
        with open(filename, 'w') as f:
            json.dump(state, f)
            
    def load_state(self, filename: str = 'portfolio_state.json') -> None:
        """Load portfolio state from file"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                state = json.load(f)
                self.initial_capital = state['initial_capital']
                self.current_capital = state['current_capital']
                self.trades = state['trades']
                self.daily_trades = state['daily_trades']
                self.best_trade = state['best_trade']
                self.start_date = state['start_date']
                self.price_history = state.get('price_history', {})

    def get_portfolio_stats(self) -> Dict:
        """Get current portfolio statistics"""
        try:
            return {
                'initial_capital': self.initial_capital,
                'current_capital': self.current_capital,
                'total_trades': len(self.trades),
                'daily_trades': len(self.daily_trades),
                'best_trade': self.best_trade,
                'start_date': self.start_date
            }
        except Exception as e:
            print(f"Error getting portfolio stats: {e}")
            return {}
