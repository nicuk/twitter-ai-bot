"""
Test suite for market analysis functionality
"""

import unittest
from unittest.mock import Mock, patch
from elion.analysis.market import MarketAnalyzer

class TestMarketAnalysis(unittest.TestCase):
    def setUp(self):
        self.analyzer = MarketAnalyzer()
    
    def test_get_current_data(self):
        """Test getting current market data"""
        data = self.analyzer.get_current_data()
        self.assertIsNotNone(data)
    
    def test_analyze_trend(self):
        """Test trend analysis"""
        market_data = {
            'prices': [100, 105, 103, 107],
            'volumes': [1000, 1200, 900, 1100]
        }
        trend = self.analyzer._analyze_trend(market_data)
        self.assertIn('direction', trend)
    
    def test_analyze_sentiment(self):
        """Test sentiment analysis"""
        market_data = {
            'price_change': 5.0,
            'volume_change': 20.0
        }
        sentiment = self.analyzer._analyze_sentiment(market_data)
        self.assertIn('sentiment', sentiment)

if __name__ == '__main__':
    unittest.main()
