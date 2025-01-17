"""
Portfolio Manager for Elion AI
Manages a $100k portfolio with sophisticated risk management and position sizing
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import os

class PortfolioManager:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.available_cash = initial_capital
        self.positions = {}  # {symbol: {'amount': float, 'entry_price': float, 'entry_time': datetime}}
        self.closed_positions = []  # Track historical trades
        self.portfolio_history = []  # Track daily portfolio value
        
        # Risk management parameters
        self.position_sizes = {
            'EXTREMELY HIGH': 0.1125,  # 11.25% of portfolio
            'HIGH': 0.075,            # 7.5% of portfolio
            'MEDIUM': 0.0375,         # 3.75% of portfolio
            'LOW': 0.025              # 2.5% of portfolio
        }
        self.max_position_size = 0.15  # Max 15% of portfolio per position
        self.stop_loss = 0.30         # 30% stop loss
        self.take_profit = 0.50       # 50% take profit
        
    def calculate_position_size(self, conviction_level: str, score: Optional[float] = None) -> float:
        """Calculate position size based on conviction level and optional score"""
        # Get base size from conviction level
        size_pct = self.position_sizes.get(conviction_level, 0.025)  # Default to LOW
        
        # Adjust size based on score if provided
        if score is not None:
            score_multiplier = min(score / 100, 1.0)  # Score adjustment (0-1)
            size_pct *= score_multiplier
            
        # Calculate size in dollars
        size = min(self.available_cash * size_pct, self.initial_capital * size_pct)
        
        # Ensure we don't exceed max position size
        return min(size, self.initial_capital * self.max_position_size)
        
    def open_position(self, symbol: str, amount: float, price: float, 
                     score: Optional[float] = None, conviction: Optional[str] = None) -> Dict:
        """Open a new position with optional score and conviction level"""
        try:
            # Calculate position value
            position_value = amount * price
            
            # Check risk management rules
            if position_value > self.initial_capital * self.max_position_size:
                return {
                    'success': False,
                    'error': f'Position size exceeds maximum allowed ({self.max_position_size*100}% of portfolio)'
                }
                
            if position_value > self.available_cash:
                return {
                    'success': False,
                    'error': 'Insufficient funds'
                }
                
            # Score check if provided
            if score is not None and conviction == 'EXTREMELY HIGH' and score < 85:
                return {
                    'success': False,
                    'error': 'Score too low for extremely high conviction'
                }
                
            # Open position
            self.positions[symbol] = {
                'amount': amount,
                'entry_price': price,
                'entry_time': datetime.now(),
                'current_price': price,
                'last_update': datetime.now(),
                'score': score,
                'conviction': conviction
            }
            
            self.available_cash -= position_value
            
            return {
                'success': True,
                'position': {
                    'size_usd': position_value,
                    'entry_price': price,
                    'amount': amount,
                    'score': score,
                    'conviction': conviction
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        
    def update_positions(self, market_data: Dict[str, float]) -> List[Dict]:
        """Update positions with latest prices and check take profit/stop loss"""
        updates = []
        
        for symbol, position in list(self.positions.items()):
            if symbol not in market_data:
                continue
                
            current_price = market_data[symbol]
            position['current_price'] = current_price
            position['last_update'] = datetime.now()
            
            # Calculate ROI
            roi = (current_price - position['entry_price']) / position['entry_price']
            
            # Check stop loss
            if roi <= -self.stop_loss:
                self._close_position(symbol, current_price, 'stop_loss')
                updates.append({
                    'symbol': symbol,
                    'type': 'stop_loss',
                    'roi': roi
                })
                continue
                
            # Check take profit
            if roi >= self.take_profit:
                self._close_position(symbol, current_price, 'take_profit')
                updates.append({
                    'symbol': symbol,
                    'type': 'take_profit',
                    'roi': roi
                })
                
        return updates
        
    def _close_position(self, symbol: str, exit_price: float, reason: str):
        """Close a position and record it"""
        position = self.positions[symbol]
        position_value = position['amount'] * exit_price
        roi = (exit_price - position['entry_price']) / position['entry_price']
        
        self.closed_positions.append({
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'amount': position['amount'],
            'roi': roi,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'reason': reason,
            'score': position.get('score'),
            'conviction': position.get('conviction')
        })
        
        self.available_cash += position_value
        del self.positions[symbol]
        
    def get_portfolio_stats(self) -> Dict:
        """Get current portfolio statistics"""
        total_value = self.available_cash
        positions = []
        
        # Calculate current positions value and ROI
        for symbol, pos in self.positions.items():
            current_value = pos['amount'] * pos['current_price']
            roi = (pos['current_price'] - pos['entry_price']) / pos['entry_price']
            total_value += current_value
            
            positions.append({
                'symbol': symbol,
                'roi': roi,
                'value': current_value,
                'entry_time': pos['entry_time'],
                'score': pos.get('score'),
                'conviction': pos.get('conviction')
            })
            
        # Calculate total ROI
        total_roi = (total_value - self.initial_capital) / self.initial_capital
        
        # Calculate win rate from closed positions
        wins = sum(1 for pos in self.closed_positions if pos['roi'] > 0)
        total_trades = len(self.closed_positions)
        win_rate = wins / total_trades if total_trades > 0 else 0.0
        
        return {
            'total_value': total_value,
            'total_roi': total_roi,
            'win_rate': win_rate,
            'available_cash': self.available_cash,
            'positions': positions,
            'closed_positions': self.closed_positions
        }
