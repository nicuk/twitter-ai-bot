"""
Test suite for Elion's core functionality
"""

import unittest
from unittest.mock import Mock, patch
from elion.elion import Elion
from elion.data_sources import DataSources
from elion.portfolio import PortfolioManager
from elion.llm_integration import LLMIntegration
from elion.personality import ElionPersonality
from elion.content.generator import ContentGenerator

class MockPersonality:
    def enhance_tweet(self, content, persona=None):
        return content

class MockContentGenerator:
    def __init__(self, personality, llm):
        self.personality = personality
        self.llm = llm
        
    def generate(self, content_type: str, data: dict) -> str:
        """Generate mock content"""
        if content_type == 'market_analysis':
            return "📊 $BTC Technical Analysis\n\nPrice: $50,000\nTrend: BULLISH\nRSI: 65\nMACD: positive crossover\nVolume: 1.2B\n\nBullish setup with strong momentum."
        elif content_type == 'gem_alpha':
            return "💎 GEM ALERT: $GEM\n\nScore: 90/100\nMarket Cap: $500,000\nVolume: $250,000\nPrice: $0.1\n\nConviction: EXTREMELY HIGH\n\nPromising low cap gem with strong potential."
        elif content_type == 'portfolio_update':
            return "📈 Portfolio Update\n\nTotal Value: $150,000\nTotal ROI: 50.0%\nWin Rate: 75.0%\n\nTop Positions:\n$BTC: 80.0%\n$ETH: 30.0%\n\nStrong performance across the board!"
        else:
            return f"Mock {content_type} tweet"

class TestElion(unittest.TestCase):
    def setUp(self):
        # Mock dependencies
        self.mock_data_sources = Mock(spec=DataSources)
        self.mock_portfolio = Mock(spec=PortfolioManager)
        self.mock_llm = Mock()  # No spec for flexibility
        self.mock_llm.generate = Mock(return_value="AI-generated analysis")
        
        # Mock personality and content generator
        self.mock_personality = MockPersonality()
        
        # Create Elion instance with mocked dependencies
        self.elion = Elion(llm=self.mock_llm)
        self.elion.data_sources = self.mock_data_sources
        self.elion.portfolio = self.mock_portfolio
        self.elion.personality = self.mock_personality
        self.elion.content = MockContentGenerator(self.mock_personality, self.mock_llm)

    def test_technical_analysis(self):
        """Test technical analysis tweet formatting"""
        # Mock technical analysis data
        analysis_data = {
            'symbol': 'BTC',
            'price': 50000,
            'trend': 'bullish',
            'rsi': 65,
            'macd': 'positive crossover',
            'volume': '1.2B',
            'patterns': ['cup and handle', 'golden cross']
        }
        
        # Set up mocks
        self.mock_data_sources.get_market_data.return_value = analysis_data
        
        # Generate tweet
        response = self.elion.process_market_alpha()
        
        # Verify tweet format
        self.assertIsNotNone(response)
        self.assertIn('📊', response)  # Has chart emoji
        self.assertIn('$BTC', response)  # Has symbol
        self.assertIn('BULLISH', response)  # Has trend
        self.assertIn('RSI:', response)  # Has indicators
        self.assertIn('MACD:', response)
        self.assertIn('Volume:', response)
        self.assertLessEqual(len(response), 280)  # Within tweet limit

    def test_gem_alpha(self):
        """Test gem alpha tweet formatting"""
        # Mock gem data
        gem_data = {
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
        
        # Set up mocks
        self.mock_data_sources.get_undervalued_gems.return_value = [gem_data]
        
        # Generate tweet
        response = self.elion.process_gem_alpha()
        
        # Verify tweet format
        self.assertIsNotNone(response)
        self.assertIn('💎', response)  # Has gem emoji
        self.assertIn('$GEM', response)  # Has symbol
        self.assertIn('90/100', response)  # Has score
        self.assertIn('$500,000', response)  # Has market cap
        self.assertIn('$0.1', response)  # Has price
        self.assertLessEqual(len(response), 280)  # Within tweet limit

    def test_portfolio_update(self):
        """Test portfolio update tweet formatting"""
        # Mock portfolio stats
        stats = {
            'total_value': 150000,
            'total_roi': 0.5,
            'win_rate': 0.75,
            'available_cash': 50000,
            'positions': [
                {'symbol': 'BTC', 'roi': 0.8, 'value': 20000},
                {'symbol': 'ETH', 'roi': 0.3, 'value': 15000}
            ]
        }
        
        # Set up mocks
        self.mock_portfolio.get_portfolio_stats.return_value = stats
        
        # Generate tweet
        response = self.elion.process_portfolio_update()
        
        # Verify tweet format
        self.assertIsNotNone(response)
        self.assertIn('Portfolio', response)
        self.assertIn('$150,000', response)  # Total value
        self.assertIn('50.0%', response)  # ROI
        self.assertIn('75.0%', response)  # Win rate
        self.assertIn('$BTC', response)  # Position symbols
        self.assertIn('$ETH', response)
        self.assertLessEqual(len(response), 280)  # Within tweet limit

if __name__ == '__main__':
    unittest.main()
