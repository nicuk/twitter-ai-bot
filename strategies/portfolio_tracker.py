"""Portfolio tracking with real market data"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import random
from strategies.shared_utils import fetch_tokens, format_token_data
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy

class PortfolioTracker:
    """Tracks virtual portfolio performance with realistic trade entries/exits"""
    
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
            
    def find_realistic_trade(self, symbol_or_data: Any) -> Optional[Dict]:
        """Generate realistic trade data using raw API data"""
        try:
            # Get current market data
            tokens = fetch_tokens(self.api_key)
            if not tokens:
                return None
                
            # Find a token with significant price movement
            significant_movers = []
            for token in tokens:
                try:
                    price_change = float(token.get('priceChange24h', 0))
                    volume = float(token.get('volume24h', 0))
                    mcap = float(token.get('marketCap', 0))
                    
                    # Look for tokens with >5% price change and decent volume
                    if abs(price_change) > 5 and volume > 1000000:  # $1M min volume
                        significant_movers.append(token)
                except (ValueError, TypeError):
                    continue
            
            # Sort by absolute price change
            significant_movers.sort(key=lambda x: abs(float(x.get('priceChange24h', 0))), reverse=True)
            
            # Pick a token - either the requested one or a random significant mover
            target_token = None
            if isinstance(symbol_or_data, str):
                # If specific symbol requested, try to find it
                target_token = next((t for t in tokens if t.get('symbol') == symbol_or_data), None)
            elif isinstance(symbol_or_data, dict):
                # If token data provided, use its symbol
                symbol = symbol_or_data.get('symbol')
                target_token = next((t for t in tokens if t.get('symbol') == symbol), None)
            
            # If no specific token found/requested, pick a random significant mover
            if not target_token and significant_movers:
                target_token = random.choice(significant_movers[:5])  # Pick from top 5 movers
                
            if not target_token:
                return None
                
            # Generate realistic trade data
            current_price = float(target_token.get('price', 0))
            high_24h = float(target_token.get('high24h', current_price * 1.05))
            low_24h = float(target_token.get('low24h', current_price * 0.95))
            volume_24h = float(target_token.get('volume24h', 0))
            price_change = float(target_token.get('priceChange24h', 0))
            
            # Generate entry/exit based on actual price movement
            if price_change > 0:
                # For upward movement, we bought low and sold high
                entry = round(random.uniform(low_24h, current_price * 0.99), 2)  # Entry below current
                exit = current_price
            else:
                # For downward movement, we shorted high and covered low
                entry = round(random.uniform(current_price * 1.01, high_24h), 2)  # Entry above current
                exit = current_price
                
            gain = round(((exit - entry) / entry) * 100, 2)
            
            # Generate realistic timeframe (2-8 hours ago)
            hours_ago = random.randint(2, 8)
            timeframe = f"{hours_ago}h"
            
            # Calculate volume change from historical data
            symbol = target_token.get('symbol', '')
            hist_volume = self.price_history.get(symbol, {}).get('volumes', [0])[0]
            volume_change = round(((volume_24h - hist_volume) / max(volume_24h, 1)) * 100, 2)
            
            return {
                'symbol': symbol,
                'entry': entry,
                'exit': exit,
                'gain': gain,
                'timeframe': timeframe,
                'volume_change': volume_change,
                'price_change_24h': price_change
            }
            
        except Exception as e:
            print(f"Error generating trade data: {e}")
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
                
            # Calculate realistic entry/exit
            current_price = float(token_data['price'])
            low_price = current_price * 0.7  # Assume 30% range
            high_price = current_price * 1.3
            
            # 3-5% above low for entry
            entry_buffer = random.uniform(0.03, 0.05)
            entry_price = low_price * (1 + entry_buffer)
            
            # 3-5% below high for exit
            exit_buffer = random.uniform(0.03, 0.05)
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
        
        if 'coins' in market_data:
            # Store today's prices
            self.price_history[date] = {
                coin['symbol']: {
                    'price': coin['price'],
                    'volume': coin.get('volume24h', 0),
                    'change24h': coin.get('priceChange24h', 0)
                }
                for coin in market_data['coins']
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
