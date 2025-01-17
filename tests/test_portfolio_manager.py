"""
Test portfolio management functionality
"""

import unittest
from datetime import datetime, timedelta
from elion.portfolio import PortfolioManager

class TestPortfolioManager(unittest.TestCase):
    def setUp(self):
        self.portfolio = PortfolioManager()
        
    def test_position_sizing(self):
        """Test position sizing based on conviction"""
        # Test different conviction levels
        size = self.portfolio.calculate_position_size('EXTREMELY HIGH')
        self.assertAlmostEqual(size, 15000.0)  # 15% of initial capital
        
        size = self.portfolio.calculate_position_size('HIGH')
        self.assertAlmostEqual(size, 10000.0)  # 10% of initial capital
        
        size = self.portfolio.calculate_position_size('MEDIUM')
        self.assertAlmostEqual(size, 5000.0)   # 5% of initial capital
        
        size = self.portfolio.calculate_position_size('LOW')
        self.assertAlmostEqual(size, 2500.0)   # 2.5% of initial capital
        
    def test_position_management(self):
        """Test opening and managing positions"""
        # Open a position
        result = self.portfolio.open_position(
            symbol='TEST',
            amount=1000,
            price=10.0
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(self.portfolio.available_cash, 90000.0)
        
        # Try to open position with insufficient funds
        result = self.portfolio.open_position(
            symbol='TEST2',
            amount=10000,
            price=10.0
        )
        
        self.assertFalse(result['success'])
        
    def test_portfolio_stats(self):
        """Test portfolio statistics calculation"""
        # Open two positions
        self.portfolio.open_position(
            symbol='TEST1',
            amount=1000,
            price=10.0
        )
        
        self.portfolio.open_position(
            symbol='TEST2',
            amount=500,
            price=20.0
        )
        
        # Update with current prices
        self.portfolio.update_positions({
            'TEST1': 15.0,  # 50% gain
            'TEST2': 25.0   # 25% gain
        })
        
        stats = self.portfolio.get_portfolio_stats()
        
        # Verify stats
        self.assertEqual(len(stats['positions']), 2)
        self.assertGreater(stats['total_value'], self.portfolio.initial_capital)
        self.assertGreater(stats['total_roi'], 0)
        
    def test_risk_management(self):
        """Test risk management rules"""
        # Try to open oversized position
        result = self.portfolio.open_position(
            symbol='TEST',
            amount=2000,
            price=10.0  # Would be 20% of portfolio
        )
        
        self.assertFalse(result['success'])
        self.assertIn('exceeds maximum allowed', result['error'])
        
    def test_take_profit_strategy(self):
        """Test take profit execution"""
        # Open position
        self.portfolio.open_position(
            symbol='TEST',
            amount=1000,
            price=10.0
        )
        
        # Update with 50% gain (take profit level)
        updates = self.portfolio.update_positions({
            'TEST': 15.0
        })
        
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]['type'], 'take_profit')
        self.assertEqual(updates[0]['symbol'], 'TEST')
        self.assertGreater(updates[0]['roi'], 0.5)
