"""
Test tweet cycle functionality
"""

import unittest
from datetime import datetime, timedelta
import sys
import os
from unittest.mock import patch, Mock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from elion.elion import Elion

class MockLLM:
    def generate_tweet(self, prompt, min_chars=180, max_chars=280):
        """Mock LLM that returns test data"""
        return "This is a test tweet generated by the mock LLM"
        
    def analyze_project(self, project_data):
        """Mock project analysis"""
        return {
            'score': 85,
            'conviction': 'HIGH',
            'analysis': 'Strong fundamentals, active development'
        }
        
    def analyze_market(self, market_data):
        """Mock market analysis"""
        return {
            'sentiment': 'Bullish',
            'analysis': 'Market showing strong momentum'
        }

class MockDataSources:
    """Mock data sources for testing"""
    def __init__(self):
        pass
        
    def get_market_data(self):
        """Get mock market data"""
        return {
            'price': 50000,
            'volume': 1000000,
            'market_cap': 1000000000,
            'change_24h': 5.5,
            'whale_data': {
                'inflow_24h': 500,
                'outflow_24h': 300
            }
        }
        
    def get_projects(self):
        """Get mock project data"""
        return [
            {
                'name': 'Test Project',
                'symbol': 'TEST',
                'score': 85,
                'analysis': 'Strong fundamentals'
            }
        ]
        
    def get_gem_data(self):
        """Get mock gem data"""
        return {
            'gems': [
                {
                    'symbol': 'GEM',
                    'score': 90,
                    'conviction_level': 'HIGH',
                    'market_data': {
                        'market_cap': 10000000,
                        'price': 1.5
                    },
                    'analysis': 'Promising gem with strong potential'
                }
            ]
        }
        
    def get_market_alpha(self):
        """Get mock market alpha data"""
        return {
            'technical': {
                'trend': 'bullish',
                'momentum': 'strong',
                'support': 48000,
                'resistance': 52000
            },
            'onchain': {
                'network_growth': 'high',
                'whale_confidence': 0.8,
                'retail_sentiment': 'positive'
            }
        }
        
    def get_onchain_metrics(self):
        """Get mock onchain metrics"""
        return {
            'active_addresses': 1000000,
            'transaction_volume': 5000000000,
            'network_growth': 0.15,
            'whale_confidence': 0.8
        }
        
    def get_hot_projects(self):
        """Mock hot projects"""
        return [
            {
                'symbol': 'HOT1',
                'score': 85,
                'market_data': {
                    'market_cap': 10e6,
                    'price': 1.0,
                    'volume': 1e6
                }
            },
            {
                'symbol': 'HOT2',
                'score': 80,
                'market_data': {
                    'market_cap': 5e6,
                    'price': 0.5,
                    'volume': 500e3
                }
            }
        ]
        
    def get_shill_opportunities(self):
        """Mock shill opportunities"""
        return [
            {
                'name': 'Test Token',
                'symbol': 'TEST',
                'score': 85,
                'market_data': {
                    'market_cap': 1e6,
                    'volume': 500e3,
                    'price': 1.0,
                    'price_change': 5.5
                },
                'analysis': 'Strong fundamentals, active development',
                'conviction_level': 'HIGH'
            }
        ]

class MockPortfolio:
    def __init__(self):
        self.positions = []
        self.available_cash = 100000
        
    def calculate_position_size(self, conviction, score=None):
        size_map = {
            'EXTREMELY HIGH': 11250,  # 11.25%
            'HIGH': 7500,            # 7.5%
            'MEDIUM': 3750,          # 3.75%
            'LOW': 2500              # 2.5%
        }
        return size_map.get(conviction, 2500)
        
    def open_position(self, symbol, amount, price, score=None, conviction=None):
        return {
            'success': True,
            'position': {
                'size_usd': amount * price,
                'entry_price': price,
                'amount': amount,
                'score': score,
                'conviction': conviction
            }
        }
        
    def get_portfolio_stats(self):
        return {
            'total_value': 150000,
            'total_roi': 0.5,
            'win_rate': 0.75,
            'available_cash': 50000,
            'positions': [
                {
                    'symbol': 'TEST1',
                    'roi': 0.8,
                    'value': 20000,
                    'entry_time': datetime.now(),
                    'score': 85,
                    'conviction': 'HIGH'
                },
                {
                    'symbol': 'TEST2',
                    'roi': 0.3,
                    'value': 15000,
                    'entry_time': datetime.now(),
                    'score': 75,
                    'conviction': 'MEDIUM'
                }
            ]
        }

class MockPersonality:
    def __init__(self):
        self.current_persona = 'alpha_hunter'
        
    def generate(self, *args, **kwargs):
        """Mock personality generation"""
        return "I am Elion, your friendly AI trading bot! 🤖"
        
    def enhance_with_persona(self, content, persona=None, context=None, user=None):
        """Mock persona enhancement"""
        return f"{content} #ElionAlpha"
        
    def get_random_persona(self):
        """Mock random persona"""
        return 'alpha_hunter'
        
    def enhance_tweet(self, content, persona=None, context=None, user=None):
        """Mock tweet enhancement"""
        return f"{content} 🚀"

class MockContentGenerator:
    """Mock content generator for testing"""
    def generate(self, content_type: str, **kwargs) -> str:
        """Generate mock content"""
        if content_type == 'market_aware':
            return "Market is looking bullish! 🚀"
        elif content_type == 'market_alpha':
            return "Market alpha: BTC showing strength above key levels 📈"
        elif content_type == 'gem_alpha':
            return "Found a promising gem: $GEM"
        elif content_type == 'portfolio_update':
            return "Portfolio update: +5% today 📊"
        elif content_type == 'shill_review':
            return "Shill review: TEST project looks solid"
        else:
            return f"Mock {content_type} tweet"

class MockDateTime:
    """Mock datetime for testing"""
    def __init__(self, hour=0):
        self._hour = hour
        
    def now(self):
        return datetime(2025, 1, 1, self._hour, 0)

class TestTweetCycle(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.llm = MockLLM()
        self.elion = Elion(self.llm)
        self.elion.data_sources = MockDataSources()
        self.elion.portfolio = MockPortfolio()
        self.elion.personality = MockPersonality()
        self.elion.content = MockContentGenerator()
        
    def test_tweet_type_distribution(self):
        """Test tweet type distribution over 24 hours"""
        tweet_types = []
        mock_datetime = MockDateTime()
        self.elion.datetime = mock_datetime
        
        # Simulate 24 hours
        for hour in range(24):
            mock_datetime._hour = hour
            tweet_type = self.elion.get_next_tweet_type()
            tweet_types.append(tweet_type)
                
        # Verify distribution
        type_counts = {
            'portfolio_update': tweet_types.count('portfolio_update'),
            'market_alpha': tweet_types.count('market_alpha'),
            'gem_alpha': tweet_types.count('gem_alpha'),
            'shill_review': tweet_types.count('shill_review'),
            'market_aware': tweet_types.count('market_aware')
        }
        
        # Check portfolio updates (every 4 hours = 6 times)
        self.assertEqual(type_counts['portfolio_update'], 6)
        
        # Check market alpha (twice per day)
        self.assertEqual(type_counts['market_alpha'], 2)
        
        # Check gem alpha (twice per day)
        self.assertEqual(type_counts['gem_alpha'], 2)
        
        # Check shill review (once per day)
        self.assertEqual(type_counts['shill_review'], 1)
        
        # Check market aware (remaining hours)
        self.assertEqual(type_counts['market_aware'], 13)  # 24 - (6 + 2 + 2 + 1)

    def test_tweet_generation(self):
        """Test tweet generation for each type"""
        tweet_types = [
            'portfolio_update',
            'market_alpha',
            'gem_alpha',
            'shill_review',
            'market_aware'
        ]
        
        for tweet_type in tweet_types:
            tweet = None
            if tweet_type == 'portfolio_update':
                tweet = self.elion.get_portfolio_update()
            elif tweet_type == 'market_alpha':
                tweet = self.elion.process_market_alpha()
            elif tweet_type == 'gem_alpha':
                tweet = self.elion.process_gem_alpha()
            elif tweet_type == 'shill_review':
                tweet = self.elion.process_shill_review()
            elif tweet_type == 'market_aware':
                tweet = self.elion.process_market_aware()
                
            self.assertIsNotNone(tweet)
            self.assertIsInstance(tweet, str)
            self.assertTrue(len(tweet) > 0)
            self.assertTrue(len(tweet) <= 280)  # Twitter character limit
            
    def test_tweet_scheduling(self):
        """Test tweet scheduling based on time"""
        test_cases = [
            (0, 'portfolio_update'),   # 12 AM
            (4, 'portfolio_update'),   # 4 AM
            (8, 'portfolio_update'),   # 8 AM
            (9, 'market_alpha'),       # 9 AM
            (11, 'gem_alpha'),         # 11 AM
            (14, 'shill_review'),      # 2 PM
            (16, 'market_alpha'),      # 4 PM
            (18, 'gem_alpha'),         # 6 PM
            (20, 'portfolio_update'),  # 8 PM
            (22, 'market_aware')       # 10 PM
        ]
        
        mock_datetime = MockDateTime()
        self.elion.datetime = mock_datetime
        
        for hour, expected_type in test_cases:
            mock_datetime._hour = hour
            tweet_type = self.elion.get_next_tweet_type()
            self.assertEqual(tweet_type, expected_type)

if __name__ == '__main__':
    unittest.main()
