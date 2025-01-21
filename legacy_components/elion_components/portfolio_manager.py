"""
Virtual Portfolio Manager for Elion AI
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
        self.max_position_size = 0.15  # Max 15% of portfolio per position
        self.stop_loss = 0.30         # 30% stop loss
        self.take_profit = {          # Take profit levels
            'tier1': {'target': 0.5, 'size': 0.3},    # Sell 30% at 50% profit
            'tier2': {'target': 1.0, 'size': 0.3},    # Sell 30% at 100% profit
            'tier3': {'target': 2.0, 'size': 0.2},    # Sell 20% at 200% profit
            'tier4': {'target': 5.0, 'size': 0.2}     # Hold 20% for moonshot
        }
        
        # Position sizing based on conviction
        self.conviction_sizing = {
            'EXTREMELY HIGH': 0.15,  # 15% of portfolio
            'HIGH': 0.10,           # 10% of portfolio
            'MODERATE': 0.05        # 5% of portfolio
        }
        
        # Load historical data if exists
        self._load_portfolio()

    def calculate_position_size(self, score: float, conviction: str, current_price: float) -> Optional[float]:
        """Calculate position size based on conviction and available capital"""
        if conviction not in self.conviction_sizing:
            return None
            
        # Base size on conviction
        size_pct = self.conviction_sizing[conviction]
        
        # Adjust based on score (85-100 gets full size, below that reduces linearly)
        score_multiplier = min(1.0, max(0, (score - 65) / 20))
        adjusted_size = size_pct * score_multiplier
        
        # Calculate actual position size
        position_value = self.initial_capital * adjusted_size
        
        # Check if we have enough available cash
        if position_value > self.available_cash:
            position_value = self.available_cash
            
        return position_value / current_price

    def open_position(self, symbol: str, amount: float, price: float, score: float, conviction: str) -> Dict:
        """Open a new position"""
        if symbol in self.positions:
            return {'success': False, 'message': f'Already holding {symbol}'}
            
        position_value = amount * price
        if position_value > self.available_cash:
            return {'success': False, 'message': 'Insufficient funds'}
            
        self.positions[symbol] = {
            'amount': amount,
            'entry_price': price,
            'entry_time': datetime.now().isoformat(),
            'score': score,
            'conviction': conviction,
            'take_profit_hits': [],
            'current_price': price,
            'last_update': datetime.now().isoformat()
        }
        
        self.available_cash -= position_value
        self._save_portfolio()
        
        return {
            'success': True,
            'message': f'Opened position in {symbol}',
            'position': {
                'size_usd': position_value,
                'size_pct': (position_value / self.initial_capital) * 100,
                'entry_price': price
            }
        }

    def update_positions(self, market_data: Dict[str, Dict]) -> List[Dict]:
        """Update all positions with new market data and execute take-profit/stop-loss"""
        updates = []
        
        for symbol, position in list(self.positions.items()):
            if symbol not in market_data:
                continue
                
            current_price = market_data[symbol]['price']
            position['current_price'] = current_price
            position['last_update'] = datetime.now().isoformat()
            
            entry_price = position['entry_price']
            roi = (current_price - entry_price) / entry_price
            
            # Check stop loss
            if roi <= -self.stop_loss:
                close_info = self.close_position(symbol, current_price, 'Stop loss hit')
                updates.append({
                    'symbol': symbol,
                    'type': 'stop_loss',
                    'roi': roi,
                    'close_info': close_info
                })
                continue
                
            # Check take profit levels
            for tier, tp in self.take_profit.items():
                if roi >= tp['target'] and tier not in position['take_profit_hits']:
                    # Calculate amount to sell
                    sell_amount = position['amount'] * tp['size']
                    if sell_amount > 0:
                        close_info = self.close_position(
                            symbol, 
                            current_price, 
                            f'Take profit {tier}',
                            partial_amount=sell_amount
                        )
                        position['take_profit_hits'].append(tier)
                        updates.append({
                            'symbol': symbol,
                            'type': 'take_profit',
                            'tier': tier,
                            'roi': roi,
                            'close_info': close_info
                        })
        
        self._save_portfolio()
        return updates

    def close_position(self, symbol: str, price: float, reason: str, partial_amount: Optional[float] = None) -> Dict:
        """Close a position (partially or fully)"""
        if symbol not in self.positions:
            return {'success': False, 'message': f'No position in {symbol}'}
            
        position = self.positions[symbol]
        amount = partial_amount if partial_amount else position['amount']
        
        if amount > position['amount']:
            return {'success': False, 'message': 'Invalid amount'}
            
        value = amount * price
        roi = (price - position['entry_price']) / position['entry_price']
        profit = value - (amount * position['entry_price'])
        
        self.available_cash += value
        
        # Update or remove position
        if partial_amount:
            position['amount'] -= partial_amount
        else:
            del self.positions[symbol]
            
        # Record closed trade
        self.closed_positions.append({
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': price,
            'amount': amount,
            'roi': roi,
            'profit': profit,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now().isoformat(),
            'reason': reason,
            'score': position['score'],
            'conviction': position['conviction']
        })
        
        self._save_portfolio()
        
        return {
            'success': True,
            'message': f'{"Partially " if partial_amount else ""}Closed {symbol} position',
            'roi': roi,
            'profit': profit
        }

    def get_portfolio_stats(self) -> Dict:
        """Get current portfolio statistics"""
        total_value = self.available_cash
        positions_value = 0
        positions_summary = []
        
        for symbol, pos in self.positions.items():
            current_value = pos['amount'] * pos['current_price']
            positions_value += current_value
            roi = (pos['current_price'] - pos['entry_price']) / pos['entry_price']
            
            positions_summary.append({
                'symbol': symbol,
                'value': current_value,
                'roi': roi,
                'score': pos['score'],
                'conviction': pos['conviction'],
                'entry_time': pos['entry_time']
            })
            
        total_value += positions_value
        
        # Calculate historical performance
        closed_profit = sum(trade['profit'] for trade in self.closed_positions)
        win_rate = len([t for t in self.closed_positions if t['profit'] > 0]) / len(self.closed_positions) if self.closed_positions else 0
        
        return {
            'total_value': total_value,
            'available_cash': self.available_cash,
            'positions_value': positions_value,
            'total_roi': (total_value - self.initial_capital) / self.initial_capital,
            'positions': positions_summary,
            'closed_profit': closed_profit,
            'win_rate': win_rate,
            'n_trades': len(self.closed_positions)
        }

    def _save_portfolio(self):
        """Save portfolio state to file"""
        portfolio_data = {
            'available_cash': self.available_cash,
            'positions': self.positions,
            'closed_positions': self.closed_positions,
            'portfolio_history': self.portfolio_history
        }
        
        with open('elion_portfolio.json', 'w') as f:
            json.dump(portfolio_data, f, indent=4)

    def _load_portfolio(self):
        """Load portfolio state from file"""
        try:
            if os.path.exists('elion_portfolio.json'):
                with open('elion_portfolio.json', 'r') as f:
                    data = json.load(f)
                    self.available_cash = data['available_cash']
                    self.positions = data['positions']
                    self.closed_positions = data['closed_positions']
                    self.portfolio_history = data['portfolio_history']
        except Exception as e:
            print(f"Error loading portfolio: {e}")
