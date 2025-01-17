"""
Portfolio tracking functionality for Elion with live CryptoRank data
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import os
import requests

class PortfolioManager:
    """Manages portfolio tracking and performance stats using live CryptoRank data"""
    
    def __init__(self):
        """Initialize portfolio manager"""
        self.portfolio_file = 'virtual_portfolio.json'
        self.cryptorank_base_url = 'https://api.cryptorank.io/v1'  # Using v1 API consistently
        self.cryptorank_api_key = os.getenv('CRYPTORANK_API_KEY')
        if self.cryptorank_api_key:
            self.headers = {
                'X-Api-Key': self.cryptorank_api_key
            }
        
        # Load or initialize portfolio
        self.portfolio = self._load_portfolio()
        
    def _load_portfolio(self) -> Dict:
        """Load portfolio from file or create new one"""
        try:
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            
        # Return default portfolio if file doesn't exist or error
        return {
            'holdings': {},  # {symbol: {'amount': float, 'entry_price': float, 'entry_date': str}}
            'cash': 100000,  # Start with $100,000 virtual USD
            'performance': {
                'daily': 0,
                'weekly': 0,
                'monthly': 0,
                'total': 0
            },
            'stats': {
                'win_rate': 0,
                'avg_profit': 0,
                'best_trade': None,
                'worst_trade': None,
                'total_trades': 0,
                'winning_trades': 0
            },
            'trade_history': [],  # [{symbol, entry_price, exit_price, profit, date}]
            'last_update': datetime.utcnow().isoformat()
        }
    
    def _save_portfolio(self):
        """Save portfolio to file"""
        try:
            with open(self.portfolio_file, 'w') as f:
                json.dump(self.portfolio, f, indent=2)
        except Exception as e:
            print(f"Error saving portfolio: {e}")
    
    def _get_live_prices(self, symbols=None) -> Dict:
        """Get live prices from CryptoRank API"""
        if not self.cryptorank_api_key:
            return {}
            
        try:
            response = requests.get(
                f"{self.cryptorank_base_url}/currencies", 
                headers=self.headers
            )
            
            if response.status_code != 200:
                print(f"Error fetching prices: {response.status_code}")
                return {}
                
            data = response.json()
            return {coin['symbol']: coin['price'] for coin in data.get('data', [])}
            
        except Exception as e:
            print(f"Error fetching prices: {e}")
            return {}
    
    def update_portfolio_value(self):
        """Update portfolio value with live prices"""
        if not self.portfolio['holdings']:
            return
            
        live_prices = self._get_live_prices(list(self.portfolio['holdings'].keys()))
        total_value = self.portfolio['cash']
        
        for symbol, holding in self.portfolio['holdings'].items():
            if symbol in live_prices:
                current_price = live_prices[symbol]
                value = holding['amount'] * current_price
                total_value += value
                
                # Update holding with current data
                holding['current_price'] = current_price
                holding['current_value'] = value
                holding['profit_loss'] = ((current_price - holding['entry_price']) / holding['entry_price']) * 100
        
        self.portfolio['total_value'] = total_value
        self.portfolio['last_update'] = datetime.utcnow().isoformat()
        self._save_portfolio()
    
    def add_position(self, symbol: str, amount: float, price: float) -> bool:
        """Add new position to portfolio"""
        try:
            cost = amount * price
            if cost > self.portfolio['cash']:
                print(f"Insufficient funds: {cost} needed, {self.portfolio['cash']} available")
                return False
            
            self.portfolio['holdings'][symbol] = {
                'amount': amount,
                'entry_price': price,
                'entry_date': datetime.utcnow().isoformat()
            }
            self.portfolio['cash'] -= cost
            self._save_portfolio()
            return True
        except Exception as e:
            print(f"Error adding position: {e}")
            return False
    
    def close_position(self, symbol: str) -> bool:
        """Close an existing position"""
        try:
            if symbol not in self.portfolio['holdings']:
                return False
                
            live_prices = self._get_live_prices([symbol])
            if not live_prices or symbol not in live_prices:
                return False
                
            holding = self.portfolio['holdings'][symbol]
            exit_price = live_prices[symbol]
            profit = ((exit_price - holding['entry_price']) / holding['entry_price']) * 100
            
            # Add to cash balance
            self.portfolio['cash'] += holding['amount'] * exit_price
            
            # Add to trade history
            self.portfolio['trade_history'].append({
                'symbol': symbol,
                'entry_price': holding['entry_price'],
                'exit_price': exit_price,
                'profit': profit,
                'date': datetime.utcnow().isoformat()
            })
            
            # Update stats
            self.portfolio['stats']['total_trades'] += 1
            if profit > 0:
                self.portfolio['stats']['winning_trades'] += 1
            self.portfolio['stats']['win_rate'] = (self.portfolio['stats']['winning_trades'] / self.portfolio['stats']['total_trades']) * 100
            
            # Update best/worst trades
            if (self.portfolio['stats']['best_trade'] is None or 
                profit > self.portfolio['trade_history'][self.portfolio['stats']['best_trade']]['profit']):
                self.portfolio['stats']['best_trade'] = len(self.portfolio['trade_history']) - 1
                
            if (self.portfolio['stats']['worst_trade'] is None or 
                profit < self.portfolio['trade_history'][self.portfolio['stats']['worst_trade']]['profit']):
                self.portfolio['stats']['worst_trade'] = len(self.portfolio['trade_history']) - 1
            
            # Remove position
            del self.portfolio['holdings'][symbol]
            self._save_portfolio()
            return True
        except Exception as e:
            print(f"Error closing position: {e}")
            return False
    
    def get_portfolio_stats(self) -> Optional[Dict]:
        """Get current portfolio stats with live data"""
        try:
            self.update_portfolio_value()
            
            # Calculate performance
            total_value = self.portfolio['total_value']
            initial_value = 100000  # Our starting amount
            
            stats = {
                'performance': {
                    'total': ((total_value - initial_value) / initial_value) * 100
                },
                'holdings': [],
                'stats': {
                    'win_rate': self.portfolio['stats']['win_rate'],
                    'total_trades': self.portfolio['stats']['total_trades'],
                    'cash': self.portfolio['cash']
                }
            }
            
            # Add current holdings with live data
            for symbol, holding in self.portfolio['holdings'].items():
                stats['holdings'].append({
                    'symbol': symbol,
                    'amount': holding['amount'],
                    'entry_price': holding['entry_price'],
                    'current_price': holding.get('current_price'),
                    'profit_loss': holding.get('profit_loss'),
                    'value': holding.get('current_value')
                })
            
            # Add best and worst trades if they exist
            if self.portfolio['trade_history']:
                if self.portfolio['stats']['best_trade'] is not None:
                    best = self.portfolio['trade_history'][self.portfolio['stats']['best_trade']]
                    stats['stats']['best_trade'] = f"{best['symbol']} ({best['profit']:.1f}%)"
                    
                if self.portfolio['stats']['worst_trade'] is not None:
                    worst = self.portfolio['trade_history'][self.portfolio['stats']['worst_trade']]
                    stats['stats']['worst_trade'] = f"{worst['symbol']} ({worst['profit']:.1f}%)"
            
            return stats
        except Exception as e:
            print(f"Error getting portfolio stats: {e}")
            return None
    
    def get_portfolio_update(self) -> Optional[Dict]:
        """Get portfolio update for tweet generation"""
        stats = self.get_portfolio_stats()
        if not stats:
            return None
            
        # Format data for tweet generation
        return {
            'total_value': self.portfolio['total_value'],
            'cash': stats['stats']['cash'],
            'total_return': stats['performance']['total'],
            'holdings': stats['holdings'],
            'win_rate': stats['stats']['win_rate'],
            'best_trade': stats['stats'].get('best_trade'),
            'worst_trade': stats['stats'].get('worst_trade')
        }
