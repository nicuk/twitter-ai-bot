"""
Portfolio management for Elion
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta

class PortfolioManager:
    """Manages portfolio tracking and updates"""
    
    def __init__(self):
        """Initialize portfolio manager"""
        self.initial_capital = 100_000  # Starting with $100k
        self.holdings = {}  # Current holdings
        self.cash = self.initial_capital  # Available cash
        self.trades = []  # Trade history
        
        # Investment criteria
        self.investment_criteria = {
            'min_market_cap': 10_000_000,  # $10M minimum
            'min_volume_24h': 1_000_000,   # $1M daily volume
            'max_allocation': 0.20,         # Max 20% in one asset
            'min_allocation': 0.05,         # Min 5% position size
            'required_metrics': [
                'market_cap',
                'volume_24h',
                'price_change_24h',
                'price_change_7d',
                'total_supply'
            ],
            'risk_factors': [
                'liquidity',
                'volatility',
                'team_background',
                'development_activity',
                'community_growth'
            ]
        }
        
    def get_portfolio_state(self) -> Dict:
        """Get current portfolio state"""
        if not self.holdings:
            return {
                'status': 'seeking_investments',
                'available_capital': self.initial_capital,
                'investment_criteria': self.investment_criteria
            }
            
        total_value = self.cash
        for symbol, data in self.holdings.items():
            total_value += data['value']
            
        return {
            'holdings': self.holdings,
            'total_value': total_value,
            'cash': self.cash,
            'performance': self._calculate_performance(),
            'stats': self._calculate_stats()
        }
        
    def evaluate_investment(self, project_data: Dict) -> Dict:
        """Evaluate a potential investment against criteria"""
        try:
            # Check required metrics
            missing_metrics = [
                metric for metric in self.investment_criteria['required_metrics']
                if metric not in project_data
            ]
            if missing_metrics:
                return {
                    'approved': False,
                    'reason': f"Missing required metrics: {', '.join(missing_metrics)}"
                }
                
            # Check minimum requirements
            if project_data['market_cap'] < self.investment_criteria['min_market_cap']:
                return {
                    'approved': False,
                    'reason': "Market cap too low"
                }
                
            if project_data['volume_24h'] < self.investment_criteria['min_volume_24h']:
                return {
                    'approved': False,
                    'reason': "Volume too low"
                }
                
            # Calculate potential position size
            suggested_size = min(
                self.cash * self.investment_criteria['max_allocation'],
                project_data['market_cap'] * 0.01  # Max 1% of market cap
            )
            
            if suggested_size / self.initial_capital < self.investment_criteria['min_allocation']:
                return {
                    'approved': False,
                    'reason': "Position size too small"
                }
                
            return {
                'approved': True,
                'suggested_size': suggested_size,
                'risk_score': self._calculate_risk_score(project_data),
                'metrics_analysis': self._analyze_metrics(project_data)
            }
            
        except Exception as e:
            return {
                'approved': False,
                'reason': f"Error evaluating investment: {str(e)}"
            }
            
    def _calculate_risk_score(self, project_data: Dict) -> float:
        """Calculate risk score (0-100, lower is better)"""
        score = 50  # Start at neutral
        
        # Market cap factor (0-20)
        mcap = project_data['market_cap']
        if mcap > 1_000_000_000:  # >$1B
            score -= 20
        elif mcap > 100_000_000:  # >$100M
            score -= 15
        elif mcap > 50_000_000:   # >$50M
            score -= 10
            
        # Volume factor (0-20)
        volume = project_data['volume_24h']
        if volume > 10_000_000:  # >$10M
            score -= 20
        elif volume > 5_000_000:  # >$5M
            score -= 15
        elif volume > 1_000_000:  # >$1M
            score -= 10
            
        # Volatility factor (0-20)
        volatility = abs(project_data.get('price_change_24h', 0))
        if volatility > 20:
            score += 20
        elif volatility > 10:
            score += 10
            
        # Development activity (0-20)
        if project_data.get('development_score', 0) > 80:
            score -= 20
        elif project_data.get('development_score', 0) > 60:
            score -= 10
            
        # Community factor (0-20)
        if project_data.get('community_score', 0) > 80:
            score -= 20
        elif project_data.get('community_score', 0) > 60:
            score -= 10
            
        return max(0, min(100, score))
        
    def _analyze_metrics(self, project_data: Dict) -> Dict:
        """Analyze project metrics"""
        return {
            'market_metrics': {
                'market_cap_rating': 'high' if project_data['market_cap'] > 100_000_000 else 'medium',
                'volume_rating': 'high' if project_data['volume_24h'] > 5_000_000 else 'medium',
                'liquidity': project_data['volume_24h'] / project_data['market_cap']
            },
            'technical_metrics': {
                'volatility': abs(project_data.get('price_change_24h', 0)),
                'trend': 'up' if project_data.get('price_change_7d', 0) > 0 else 'down',
                'momentum': project_data.get('price_change_24h', 0)
            },
            'project_metrics': {
                'development': project_data.get('development_score', 0),
                'community': project_data.get('community_score', 0),
                'risk_level': self._calculate_risk_score(project_data)
            }
        }
        
    def _calculate_performance(self) -> Dict:
        """Calculate portfolio performance metrics"""
        if not self.holdings:
            return {
                'change_24h': 0,
                'return_30d': 0,
                'total_return': 0
            }
            
        total_value = self.cash
        for symbol, data in self.holdings.items():
            total_value += data['value']
            
        return {
            'change_24h': 0,  # TODO: Calculate from price history
            'return_30d': 0,  # TODO: Calculate from price history
            'total_return': ((total_value / self.initial_capital) - 1) * 100
        }
        
    def _calculate_stats(self) -> Dict:
        """Calculate trading statistics"""
        if not self.trades:
            return {
                'win_rate': 0,
                'best_trade': None,
                'avg_hold_time': 0
            }
            
        winning_trades = [t for t in self.trades if t['pnl'] > 0]
        
        return {
            'win_rate': (len(winning_trades) / len(self.trades)) * 100,
            'best_trade': max(self.trades, key=lambda x: x['pnl'])['symbol'] if self.trades else None,
            'avg_hold_time': sum(t['hold_time'].days for t in self.trades) / len(self.trades)
        }
