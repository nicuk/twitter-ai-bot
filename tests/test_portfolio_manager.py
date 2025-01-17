"""
Test suite for Elion's portfolio management system
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from elion.portfolio_manager import PortfolioManager

class TestPortfolioManager(unittest.TestCase):
    def setUp(self):
        self.portfolio = PortfolioManager(initial_capital=100000.0)

    def test_position_sizing(self):
        """Test position sizing based on conviction"""
        # Test EXTREMELY HIGH conviction
        size = self.portfolio.calculate_position_size(
            score=90,
            conviction='EXTREMELY HIGH',
            current_price=1.0
        )
        self.assertAlmostEqual(size * 1.0, 15000.0)  # Should be 15% of portfolio

        # Test HIGH conviction
        size = self.portfolio.calculate_position_size(
            score=80,
            conviction='HIGH',
            current_price=1.0
        )
        self.assertAlmostEqual(size * 1.0, 10000.0)  # Should be 10% of portfolio

        # Test MODERATE conviction
        size = self.portfolio.calculate_position_size(
            score=70,
            conviction='MODERATE',
            current_price=1.0
        )
        self.assertAlmostEqual(size * 1.0, 5000.0)  # Should be 5% of portfolio

    def test_position_management(self):
        """Test opening and managing positions"""
        # Open a position
        result = self.portfolio.open_position(
            symbol='TEST',
            amount=10000,
            price=1.0,
            score=90,
            conviction='EXTREMELY HIGH'
        )
        self.assertTrue(result['success'])
        self.assertEqual(self.portfolio.available_cash, 90000.0)

        # Test take profit
        market_data = {'TEST': {'price': 1.5}}  # 50% up
        updates = self.portfolio.update_positions(market_data)
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]['type'], 'take_profit')
        self.assertEqual(updates[0]['tier'], 'tier1')

        # Test stop loss
        market_data = {'TEST': {'price': 0.6}}  # 40% down
        updates = self.portfolio.update_positions(market_data)
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0]['type'], 'stop_loss')

    def test_portfolio_stats(self):
        """Test portfolio statistics calculation"""
        # Open some positions
        self.portfolio.open_position(
            symbol='TEST1',
            amount=10000,
            price=1.0,
            score=90,
            conviction='EXTREMELY HIGH'
        )
        self.portfolio.open_position(
            symbol='TEST2',
            amount=5000,
            price=2.0,
            score=80,
            conviction='HIGH'
        )

        # Update prices
        market_data = {
            'TEST1': {'price': 1.5},  # 50% up
            'TEST2': {'price': 2.4}   # 20% up
        }
        self.portfolio.update_positions(market_data)

        # Get stats
        stats = self.portfolio.get_portfolio_stats()
        
        self.assertGreater(stats['total_value'], 100000.0)  # Should be in profit
        self.assertGreater(stats['total_roi'], 0)
        self.assertEqual(len(stats['positions']), 2)

    def test_risk_management(self):
        """Test risk management rules"""
        # Try to open oversized position
        result = self.portfolio.open_position(
            symbol='TEST',
            amount=20000,  # 20% of portfolio (above max 15%)
            price=1.0,
            score=90,
            conviction='EXTREMELY HIGH'
        )
        self.assertFalse(result['success'])

        # Test position limits
        positions = []
        for i in range(10):
            result = self.portfolio.open_position(
                symbol=f'TEST{i}',
                amount=1000,
                price=1.0,
                score=90,
                conviction='EXTREMELY HIGH'
            )
            positions.append(result['success'])

        self.assertTrue(all(positions))  # All positions should open successfully
        self.assertGreater(self.portfolio.available_cash, 0)  # Should still have cash

    def test_take_profit_strategy(self):
        """Test take profit execution"""
        # Open position
        self.portfolio.open_position(
            symbol='TEST',
            amount=10000,
            price=1.0,
            score=90,
            conviction='EXTREMELY HIGH'
        )

        # Test each take profit tier
        price_levels = [1.5, 2.0, 3.0, 6.0]  # 50%, 100%, 200%, 500%
        for i, price in enumerate(price_levels, 1):
            market_data = {'TEST': {'price': price}}
            updates = self.portfolio.update_positions(market_data)
            self.assertEqual(updates[0]['type'], 'take_profit')
            self.assertEqual(updates[0]['tier'], f'tier{i}')
