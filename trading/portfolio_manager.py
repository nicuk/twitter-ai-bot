"""Portfolio management for Elion"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from database.trade_db import TradeDatabase

class PortfolioManager:
    """Manages Elion's trading portfolio"""
    
    def __init__(self):
        """Initialize portfolio manager"""
        self.db = TradeDatabase()
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.max_position_size = 0.20  # 20% max position size
        
    def calculate_position_size(self, entry: float, stop: float) -> Dict:
        """Calculate position size based on risk management"""
        try:
            # Get current portfolio value
            stats = self.db.get_portfolio_stats()
            if not stats:
                return None
                
            portfolio_value = stats['current_balance']
            
            # Calculate risk amount (2% of portfolio)
            risk_amount = portfolio_value * self.risk_per_trade
            
            # Calculate position size
            risk_per_unit = abs(entry - stop)
            position_size = risk_amount / risk_per_unit
            
            # Calculate total position value
            position_value = position_size * entry
            
            # Limit position size to 20% of portfolio
            if position_value > portfolio_value * self.max_position_size:
                position_size = (portfolio_value * self.max_position_size) / entry
                position_value = position_size * entry
            
            return {
                'size': position_size,
                'value': position_value,
                'risk_amount': risk_amount,
                'risk_percentage': self.risk_per_trade * 100
            }
            
        except Exception as e:
            print(f"Error calculating position size: {e}")
            return None
            
    def execute_trade(self, trade_data: Dict) -> bool:
        """Execute a trade and update portfolio"""
        try:
            # Calculate PNL
            entry_value = trade_data['entry_price'] * trade_data['quantity']
            exit_value = trade_data['exit_price'] * trade_data['quantity']
            pnl = exit_value - entry_value
            pnl_percentage = (pnl / entry_value) * 100
            
            # Prepare trade record
            trade_record = {
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'symbol': trade_data['symbol'],
                'entry_price': trade_data['entry_price'],
                'exit_price': trade_data['exit_price'],
                'quantity': trade_data['quantity'],
                'pnl': pnl,
                'pnl_percentage': pnl_percentage,
                'trade_type': trade_data.get('type', 'long'),
                'duration': trade_data.get('duration', 'unknown'),
                'status': 'closed'
            }
            
            # Add trade to database
            return self.db.add_trade(trade_record)
            
        except Exception as e:
            print(f"Error executing trade: {e}")
            return False
            
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio summary"""
        try:
            stats = self.db.get_portfolio_stats()
            if not stats:
                return None
                
            return {
                'current_balance': stats['current_balance'],
                'total_gain': ((stats['current_balance'] - 100) / 100) * 100,
                'daily_pnl': stats['daily_pnl'],
                'total_trades': stats['total_trades'],
                'win_rate': (stats['winning_trades'] / stats['total_trades'] * 100) if stats['total_trades'] > 0 else 0,
                'best_trade': stats['best_trade']
            }
            
        except Exception as e:
            print(f"Error getting portfolio summary: {e}")
            return None
    
    def reset_daily_stats(self):
        """Reset daily statistics"""
        return self.db.reset_daily_stats()
