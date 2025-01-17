"""
Test suite for Elion's core functionality
"""

import unittest
from unittest.mock import Mock, patch
from elion.elion import Elion
from elion.data_sources import DataSources
from elion.portfolio import Portfolio

class TestElion(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_data_sources = Mock(spec=DataSources)
        self.mock_portfolio = Mock(spec=Portfolio)
        
        # Create Elion instance
        self.elion = Elion()
        
        # Inject mocked dependencies
        self.elion.data_sources = self.mock_data_sources
        self.elion.portfolio = self.mock_portfolio

    def test_shill_review_live_token(self):
        """Test shill review for a live token"""
        # Mock a live token with good metrics
        mock_project = {
            'name': 'Test Token',
            'symbol': 'TEST',
            'score': 85,
            'market_data': {
                'market_cap': 1000000,
                'volume': 500000,
                'price': 1.0,
                'price_change': 5.5
            },
            'analysis': 'Strong fundamentals, active development',
            'conviction_level': 'HIGH'
        }
        
        self.mock_data_sources.get_shill_opportunities.return_value = [mock_project]
        
        # Mock portfolio calculation
        self.mock_portfolio.calculate_position_size.return_value = 10000
        self.mock_portfolio.open_position.return_value = {
            'success': True,
            'position': {
                'size_usd': 10000,
                'size_pct': 10,
                'entry_price': 1.0
            }
        }

        response = self.elion._format_shill_review([mock_project])
        
        # Verify response format and content
        self.assertIn('TEST', response)
        self.assertIn('85/100', response)
        self.assertIn('HIGH CONVICTION', response)
        self.assertIn('$10,000', response)

    def test_shill_review_unlaunched_token(self):
        """Test shill review for an unlaunched token"""
        mock_project = {
            'name': 'Unlaunched Token',
            'symbol': 'UNL',
            'score': 0,
            'analysis': 'Token not live yet',
            'conviction_level': 'REJECTED'
        }
        
        self.mock_data_sources.get_shill_opportunities.return_value = [mock_project]
        
        response = self.elion._format_shill_review([mock_project])
        
        self.assertIn('not convinced', response.lower())
        self.assertNotIn('Investment Decision', response)

    def test_portfolio_update(self):
        """Test portfolio update formatting"""
        mock_stats = {
            'total_value': 150000,
            'total_roi': 0.5,  # 50% ROI
            'win_rate': 0.75,  # 75% win rate
            'positions': [
                {
                    'symbol': 'TEST1',
                    'roi': 0.8,
                    'value': 20000
                },
                {
                    'symbol': 'TEST2',
                    'roi': 0.3,
                    'value': 15000
                }
            ],
            'closed_positions': [
                {
                    'symbol': 'TEST3',
                    'roi': 0.6,
                    'exit_time': '2025-01-16T20:00:00Z'
                }
            ],
            'available_cash': 50000
        }
        
        self.mock_portfolio.get_portfolio_stats.return_value = mock_stats
        
        response = self.elion.get_portfolio_update()
        
        # Verify portfolio update format
        self.assertIn('$150,000', response)  # Total value
        self.assertIn('50.0%', response)     # ROI
        self.assertIn('75.0%', response)     # Win rate
        self.assertIn('TEST1: 80.0%', response)  # Position ROI
        self.assertIn('$50,000', response)   # Available cash

    def test_market_response(self):
        """Test market alpha response"""
        mock_market_data = {
            'sentiment': 'bullish',
            'btc_dominance': 45.5,
            'market_cap': 2100000000000,
            'volume_24h': 98000000000,
            'trending_coins': ['BTC', 'ETH', 'SOL'],
            'fear_greed_index': 75
        }
        
        self.mock_data_sources.get_market_alpha.return_value = mock_market_data
        
        response = self.elion._format_market_response(mock_market_data)
        
        # Verify market response format
        self.assertIn('bullish', response.lower())
        self.assertIn('45.5%', response)
        self.assertIn('BTC', response)
        self.assertIn('ETH', response)
        self.assertIn('SOL', response)

    def test_gem_alpha(self):
        """Test gem alpha call"""
        mock_gem = {
            'name': 'Gem Token',
            'symbol': 'GEM',
            'score': 90,
            'market_data': {
                'market_cap': 500000,
                'volume': 250000,
                'price': 0.1
            },
            'analysis': 'Promising low cap gem',
            'conviction_level': 'EXTREMELY HIGH'
        }
        
        self.mock_data_sources.get_market_alpha.return_value = {'gems': [mock_gem]}
        
        response = self.elion._format_gem_alpha({'gems': [mock_gem]})
        
        # Verify gem alpha format
        self.assertIn('GEM', response)
        self.assertIn('90/100', response)
        self.assertIn('EXTREMELY HIGH', response)
        self.assertIn('$500,000', response)  # Market cap
        self.assertIn('$0.1', response)      # Price
