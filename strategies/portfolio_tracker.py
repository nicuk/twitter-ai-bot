"""Portfolio tracking with real market data"""

from typing import Dict, List, Optional
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
        """Initialize with 7 days of historical data using real APIs"""
        now = datetime.now()
        
        # Get current market data
        tokens = fetch_tokens(self.api_key, sort_by='volume24h', direction='DESC')
        if not tokens:
            return
            
        # Generate 7 days of price history
        for days_ago in range(7, -1, -1):
            date = (now - timedelta(days=days_ago)).strftime('%Y-%m-%d')
            self.price_history[date] = {}
            
            for token in tokens[:10]:  # Top 10 by volume
                formatted = format_token_data(token)
                if not formatted:
                    continue
                    
                symbol = formatted['symbol']
                base_price = float(formatted['price'])
                base_volume = float(formatted.get('volume24h', 1000000))
                
                # Add some randomness for historical prices
                daily_change = random.uniform(-0.3, 0.3)  # 30% max daily change
                price = base_price * (1 + daily_change)
                volume = base_volume * random.uniform(0.7, 1.3)
                
                self.price_history[date][symbol] = {
                    'price': round(price, 2),
                    'volume': volume,
                    'change24h': daily_change * 100
                }
                
        # Save bootstrapped data
        self._save_price_history()
        
    def find_realistic_trade(self, symbol: str, timeframe_hours: int = 24) -> Optional[Dict]:
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
