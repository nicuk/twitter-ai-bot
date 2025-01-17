"""
Test suite for Elion's project analysis system
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from elion.project_analysis import ProjectAnalyzer
from elion.data_sources import DataSources

class TestProjectAnalyzer(unittest.TestCase):
    def setUp(self):
        self.mock_data_sources = Mock(spec=DataSources)
        self.mock_llm = Mock()
        self.analyzer = ProjectAnalyzer(self.mock_data_sources, self.mock_llm)

    def test_early_shill_bonus(self):
        """Test early shill bonus calculations"""
        self.assertEqual(self.analyzer._calculate_early_bonus(1), 100)  # First shill
        self.assertEqual(self.analyzer._calculate_early_bonus(2), 60)   # Second shill
        self.assertEqual(self.analyzer._calculate_early_bonus(3), 30)   # Third shill
        self.assertEqual(self.analyzer._calculate_early_bonus(4), 0)    # Too late

    def test_token_liveness_check(self):
        """Test token liveness validation"""
        # Mock live token
        live_token = {
            'values': {
                'USD': {
                    'price': 1.0,
                    'volume24h': 1000000,
                    'liquidity': 500000
                }
            },
            'contract_verified': True
        }
        self.assertTrue(self.analyzer._is_token_live(live_token))

        # Mock unlaunched token
        unlaunched_token = {
            'values': {
                'USD': {
                    'price': 0,
                    'volume24h': 0,
                    'liquidity': 0
                }
            },
            'contract_verified': False
        }
        self.assertFalse(self.analyzer._is_token_live(unlaunched_token))

    def test_llm_analysis(self):
        """Test LLM-based project analysis"""
        # Mock project data
        mock_project_data = {
            'name': 'Test Token',
            'symbol': 'TEST',
            'values': {
                'USD': {
                    'price': 1.0,
                    'volume24h': 1000000,
                    'liquidity': 500000,
                }
            },
            'contract_verified': True,
            'market_cap': 10000000,
            'holder_count': 1000,
            'twitter_engagement': 0.8,
            'telegram_growth': 0.7,
            'sentiment_score': 0.9,
            'github_commits_week': 15,
            'security_score': 0.9,
            'unique_value_prop': 0.8
        }

        # Mock LLM response
        mock_llm_response = {
            'scores': {
                'fundamentals': 85,
                'tokenomics': 80,
                'market_metrics': 75,
                'social_signals': 90
            },
            'analysis': 'Detailed analysis of the project...'
        }

        self.mock_data_sources.get_coin_details.return_value = mock_project_data
        self.mock_llm.analyze.return_value = mock_llm_response

        result = self.analyzer.analyze_project('test_id', 1)  # First shill position

        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Test Token')
        self.assertEqual(result['symbol'], 'TEST')
        self.assertTrue(65 <= result['score'] <= 100)  # Score should be in valid range
        self.assertIn(result['conviction_level'], 
                     ['EXTREMELY HIGH', 'HIGH', 'MODERATE', 'LOW', 'REJECTED'])

        # Verify LLM was called with correct prompt
        self.mock_llm.analyze.assert_called_once()
        prompt = self.mock_llm.analyze.call_args[0][0]
        self.assertIn('Test Token', prompt)
        self.assertIn('$TEST', prompt)

    def test_unlaunched_token(self):
        """Test rejection of unlaunched tokens"""
        mock_project_data = {
            'name': 'Unlaunched Token',
            'symbol': 'UNL',
            'values': {
                'USD': {
                    'price': 0,
                    'volume24h': 0,
                    'liquidity': 0
                }
            },
            'contract_verified': False
        }

        self.mock_data_sources.get_coin_details.return_value = mock_project_data
        result = self.analyzer.analyze_project('unl_id', 1)

        self.assertIn('Token not live', result['analysis'])
        self.assertEqual(result['conviction_level'], 'REJECTED')
