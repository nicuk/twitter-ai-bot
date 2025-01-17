"""
Unit tests for the MarketAnalyzer component
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from elion.market_analyzer import MarketAnalyzer

class TestMarketAnalyzer(unittest.TestCase):
    """Test suite for MarketAnalyzer class"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that can be reused across tests"""
        cls.sample_prices = [100, 105, 95, 110, 115, 105, 100, 120, 125, 130]
        cls.sample_volumes = [1000, 1200, 800, 1500, 1800, 2000, 1900]
        cls.sample_whale_movements = [
            {'type': 'buy', 'volume': 1000000},
            {'type': 'sell', 'volume': 500000},
            {'type': 'buy', 'volume': 800000}
        ]

    def setUp(self):
        """Set up test fixtures before each test"""
        self.mock_data_sources = Mock()
        self.analyzer = MarketAnalyzer(self.mock_data_sources)
        
        # Set up common mock returns
        self.mock_data_sources.get_market_data.return_value = {
            'price_history': self.sample_prices,
            'volume_history': self.sample_volumes,
            'market_sentiment': 'bullish',
            'whale_movements': self.sample_whale_movements
        }
        
        self.mock_data_sources.get_onchain_metrics.return_value = {
            'network_growth': 0.15,
            'whale_confidence': 0.8,
            'active_addresses': 1000,
            'transaction_volume': 5000000
        }

    def test_analyze_market_conditions_returns_valid_structure(self):
        """Market analysis should return dictionary with required fields"""
        result = self.analyzer.analyze_market_conditions()
        
        # Check structure
        self.assertIsInstance(result, dict)
        self.assertIn('onchain', result)
        self.assertIn('sentiment', result)
        self.assertIn('whale_activity', result)
        self.assertIn('timestamp', result)
        
        # Check timestamp is recent
        self.assertIsInstance(result['timestamp'], datetime)
        self.assertLess(
            datetime.utcnow() - result['timestamp'],
            timedelta(seconds=1)
        )

    def test_analyze_onchain_metrics_bullish_case(self):
        """Should return bullish sentiment when metrics are strong"""
        result = self.analyzer._analyze_onchain_metrics()
        
        self.assertEqual(result['sentiment'], 'bullish')
        self.assertGreater(result['confidence'], 0.7)
        self.assertEqual(
            result['metrics']['network_growth'],
            self.mock_data_sources.get_onchain_metrics()['network_growth']
        )

    def test_analyze_onchain_metrics_bearish_case(self):
        """Should return bearish sentiment when metrics are weak"""
        self.mock_data_sources.get_onchain_metrics.return_value.update({
            'network_growth': -0.15,
            'whale_confidence': 0.2
        })
        
        result = self.analyzer._analyze_onchain_metrics()
        
        self.assertEqual(result['sentiment'], 'bearish')
        self.assertGreater(result['confidence'], 0.6)

    def test_analyze_market_sentiment_bullish_case(self):
        """Should detect bullish sentiment from market data"""
        market_data = {
            'market_sentiment': 'bullish',
            'total_mcap': '1000000000',
            'total_volume': '100000000'
        }
        
        result = self.analyzer._analyze_market_sentiment(market_data)
        
        self.assertGreater(result['sentiment'], 0.6)
        self.assertGreater(result['confidence'], 0.1)
        self.assertIn('bullish_sentiment', result['signals'])

    def test_analyze_moving_averages_crossover_detection(self):
        """Should detect golden and death crosses"""
        # Test golden cross
        # Create prices where short MA starts lower but crosses above long MA
        prices = ([10] * 51) + ([20] * 20)  # Need extra data point for previous calculation
        result = self.analyzer._analyze_moving_averages(
            prices, 
            short_period=20,
            long_period=50
        )
        
        self.assertEqual(result['trend'], 'bullish')
        self.assertGreater(result['confidence'], 0.5)
        self.assertEqual(result['crossover'], 'golden_cross')
        
        # Test death cross
        # Create prices where short MA starts higher but crosses below long MA
        prices = ([20] * 51) + ([10] * 20)  # Need extra data point for previous calculation
        result = self.analyzer._analyze_moving_averages(
            prices,
            short_period=20,
            long_period=50
        )
        
        self.assertEqual(result['trend'], 'bearish')
        self.assertGreater(result['confidence'], 0.5)
        self.assertEqual(result['crossover'], 'death_cross')

    def test_analyze_volume_patterns_high_volume(self):
        """Should detect high volume patterns"""
        market_data = {
            'volumes': [1000] * 7 + [2000] * 3  # Recent volume 2x higher
        }
        
        result = self.analyzer._analyze_volume_patterns(market_data)
        
        self.assertEqual(result['pattern'], 'high_volume')
        self.assertGreater(result['confidence'], 0.7)
        self.assertGreater(result['metrics']['volume_change'], 0.5)

    def test_analyze_whale_movements_net_buyer(self):
        """Should detect net buying pressure from whales"""
        market_data = {
            'whale_movements': [
                {'type': 'buy', 'volume': 1000000},
                {'type': 'buy', 'volume': 800000},
                {'type': 'sell', 'volume': 500000}
            ]
        }
        
        result = self.analyzer._analyze_whale_movements(market_data)
        
        self.assertEqual(result['impact'], 'bullish')
        self.assertGreater(result['confidence'], 0.7)
        self.assertGreater(result['metrics']['net_volume'], 0)

    def test_find_support_resistance_levels(self):
        """Should identify key support and resistance levels"""
        # Create a price series with clear local minima and maxima
        prices = [
            100, 95, 90, 95, 100,  # Local minimum at 90
            105, 110, 115, 110, 105,  # Local maximum at 115
            100, 95, 90, 95, 100,  # Local minimum at 90
            105, 110, 120, 110, 105,  # Local maximum at 120
            100, 95, 85, 95, 100,  # Local minimum at 85
            105, 110, 125, 110, 105  # Local maximum at 125
        ]
        
        result = self.analyzer._find_support_resistance(prices, num_levels=3)
        
        # Test structure
        self.assertIn('support', result)
        self.assertIn('resistance', result)
        self.assertIn('confidence', result)
        
        # Test values
        self.assertGreater(len(result['support']), 0)
        self.assertGreater(len(result['resistance']), 0)
        
        # Test levels are sorted correctly
        if len(result['support']) > 1:
            self.assertGreater(result['support'][0], result['support'][-1])
        if len(result['resistance']) > 1:
            self.assertGreater(result['resistance'][0], result['resistance'][-1])

    def test_calculate_momentum_strong_trend(self):
        """Should detect strong momentum in price trends"""
        # Strong upward momentum
        prices = [100, 110, 120, 130, 140]
        
        result = self.analyzer._calculate_momentum(prices, period=3)
        
        self.assertGreater(result['momentum'], 0)
        self.assertGreater(result['confidence'], 0.7)
        self.assertGreater(result['metrics']['consistency'], 0.8)

    def test_error_handling_missing_data(self):
        """Should handle missing or invalid data gracefully"""
        # Test with None data
        self.mock_data_sources.get_market_data.return_value = None
        result = self.analyzer.analyze_market_conditions()
        
        self.assertIsInstance(result, dict)
        self.assertIn('onchain', result)
        self.assertIn('sentiment', result)
        
        # Test with empty data
        self.mock_data_sources.get_market_data.return_value = {}
        result = self.analyzer.analyze_market_conditions()
        
        self.assertIsInstance(result, dict)
        self.assertIn('onchain', result)
        self.assertIn('sentiment', result)

if __name__ == '__main__':
    unittest.main()
