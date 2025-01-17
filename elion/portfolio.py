"""
Portfolio management system for Elion
"""

from typing import Dict, List
from datetime import datetime

class Portfolio:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.available_cash = initial_capital
        self.positions = {}  # {symbol: position_data}
        self.closed_positions = []
        self.trade_history = []

    def calculate_position_size(self, score: float, conviction_level: str, current_price: float) -> float:
        """Calculate position size based on conviction and score"""
        if conviction_level == 'EXTREMELY HIGH' and score >= 85:
            return min(self.available_cash * 0.15, 15000)  # Max 15% of portfolio
        elif conviction_level == 'HIGH' and score >= 75:
            return min(self.available_cash * 0.10, 10000)  # Max 10% of portfolio
        elif conviction_level == 'MODERATE' and score >= 65:
            return min(self.available_cash * 0.05, 5000)   # Max 5% of portfolio
        return 0

    def open_position(self, symbol: str, amount: float, price: float, score: float, conviction_level: str) -> Dict:
        """Open a new position"""
        if amount > self.available_cash:
            return {'success': False, 'error': 'Insufficient funds'}

        position_size = amount / price
        position = {
            'size': position_size,
            'size_usd': amount,
            'entry_price': price,
            'current_price': price,
            'score': score,
            'conviction_level': conviction_level,
            'entry_time': datetime.utcnow().isoformat(),
            'size_pct': (amount / self.initial_capital) * 100,
            'roi': 0.0,
            'take_profit_hits': []
        }

        self.positions[symbol] = position
        self.available_cash -= amount
        self.trade_history.append({
            'type': 'open',
            'symbol': symbol,
            'amount': amount,
            'price': price,
            'time': position['entry_time']
        })

        return {'success': True, 'position': position}

    def update_positions(self, market_data: Dict) -> List[Dict]:
        """Update positions with current market data and execute take profits/stop losses"""
        updates = []
        
        for symbol, position in list(self.positions.items()):
            if symbol not in market_data:
                continue

            current_price = market_data[symbol]['price']
            position['current_price'] = current_price
            position['roi'] = (current_price / position['entry_price']) - 1

            # Check stop loss (-30%)
            if position['roi'] <= -0.3:
                self._close_position(symbol, current_price, 'stop_loss')
                updates.append({
                    'symbol': symbol,
                    'type': 'stop_loss',
                    'roi': position['roi']
                })
                continue

            # Check take profit levels
            roi = position['roi']
            if roi >= 5.0 and 'tier4' not in position['take_profit_hits']:
                self._take_profit(symbol, current_price, 0.2, 'tier4')  # 20% at 500%
                updates.append({
                    'symbol': symbol,
                    'type': 'take_profit',
                    'tier': 'tier4',
                    'amount': 0.2
                })
            elif roi >= 2.0 and 'tier3' not in position['take_profit_hits']:
                self._take_profit(symbol, current_price, 0.2, 'tier3')  # 20% at 200%
                updates.append({
                    'symbol': symbol,
                    'type': 'take_profit',
                    'tier': 'tier3',
                    'amount': 0.2
                })
            elif roi >= 1.0 and 'tier2' not in position['take_profit_hits']:
                self._take_profit(symbol, current_price, 0.3, 'tier2')  # 30% at 100%
                updates.append({
                    'symbol': symbol,
                    'type': 'take_profit',
                    'tier': 'tier2',
                    'amount': 0.3
                })
            elif roi >= 0.5 and 'tier1' not in position['take_profit_hits']:
                self._take_profit(symbol, current_price, 0.3, 'tier1')  # 30% at 50%
                updates.append({
                    'symbol': symbol,
                    'type': 'take_profit',
                    'tier': 'tier1',
                    'amount': 0.3
                })

        return updates

    def _take_profit(self, symbol: str, current_price: float, percentage: float, tier: str):
        """Execute a take profit order"""
        position = self.positions[symbol]
        amount_to_sell = position['size'] * percentage
        value = amount_to_sell * current_price
        
        position['size'] -= amount_to_sell
        position['take_profit_hits'].append(tier)
        self.available_cash += value
        
        self.trade_history.append({
            'type': 'take_profit',
            'symbol': symbol,
            'amount': value,
            'price': current_price,
            'time': datetime.utcnow().isoformat(),
            'tier': tier
        })

    def _close_position(self, symbol: str, current_price: float, reason: str):
        """Close an entire position"""
        position = self.positions[symbol]
        value = position['size'] * current_price
        roi = (current_price / position['entry_price']) - 1
        
        self.available_cash += value
        self.closed_positions.append({
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': current_price,
            'roi': roi,
            'size_usd': position['size_usd'],
            'exit_time': datetime.utcnow().isoformat(),
            'reason': reason
        })
        
        self.trade_history.append({
            'type': 'close',
            'symbol': symbol,
            'amount': value,
            'price': current_price,
            'time': datetime.utcnow().isoformat(),
            'reason': reason
        })
        
        del self.positions[symbol]

    def get_portfolio_stats(self) -> Dict:
        """Get comprehensive portfolio statistics"""
        total_value = self.available_cash
        for symbol, pos in self.positions.items():
            total_value += pos['size'] * pos['current_price']

        # Calculate win rate
        closed_trades = len(self.closed_positions)
        winning_trades = len([p for p in self.closed_positions if p['roi'] > 0])
        win_rate = winning_trades / closed_trades if closed_trades > 0 else 0

        return {
            'total_value': total_value,
            'available_cash': self.available_cash,
            'total_roi': (total_value / self.initial_capital) - 1,
            'win_rate': win_rate,
            'n_trades': len(self.trade_history),
            'positions': [
                {
                    'symbol': symbol,
                    'roi': pos['roi'],
                    'value': pos['size'] * pos['current_price']
                }
                for symbol, pos in self.positions.items()
            ],
            'closed_positions': self.closed_positions
        }
