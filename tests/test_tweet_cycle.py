"""
Test suite for Elion's tweet cycle and portfolio updates
"""

import unittest
from unittest.mock import Mock, patch
from elion.tweet_history_manager import TweetHistoryManager

class TestTweetCycle(unittest.TestCase):
    def setUp(self):
        self.history_manager = TweetHistoryManager()

    def test_portfolio_update_cycle(self):
        """Test portfolio update scheduling"""
        # Test regular posts (not portfolio update)
        for i in range(199):
            tweet_type = self.history_manager.get_tweet_type_for_next_post()
            self.assertNotEqual(tweet_type, 'portfolio_update')
            self.history_manager.history['metadata']['total_tweets'] += 1

        # Test 200th post (should be portfolio update)
        tweet_type = self.history_manager.get_tweet_type_for_next_post()
        self.assertEqual(tweet_type, 'portfolio_update')

    def test_tweet_type_distribution(self):
        """Test distribution of tweet types in cycle"""
        type_counts = {
            'gem_alpha': 0,
            'shill_review': 0,
            'ai_aware': 0,
            'controversial': 0,
            'giveaway': 0,
            'regular': 0,
            'portfolio_update': 0
        }

        # Simulate 1000 tweets
        for i in range(1000):
            tweet_type = self.history_manager.get_tweet_type_for_next_post()
            type_counts[tweet_type] += 1
            self.history_manager.history['metadata']['total_tweets'] += 1

        # Verify portfolio updates
        self.assertEqual(type_counts['portfolio_update'], 1000 // 200)

        # Verify other tweet type ratios
        cycle_length = 50
        expected_cycles = 1000 // cycle_length
        self.assertGreaterEqual(type_counts['gem_alpha'], expected_cycles * 5)
        self.assertGreaterEqual(type_counts['shill_review'], expected_cycles * 5)
        self.assertGreaterEqual(type_counts['ai_aware'], expected_cycles * 2)
        self.assertGreaterEqual(type_counts['controversial'], expected_cycles * 2)
        self.assertGreaterEqual(type_counts['giveaway'], expected_cycles)

    def test_hot_projects_update(self):
        """Test hot projects update integration"""
        self.history_manager.add_hot_project('TEST', 50.0)  # 50% ROI
        
        # Simulate tweets until we get a gem update
        max_attempts = 100
        found_gem_update = False
        
        for _ in range(max_attempts):
            tweet_type = self.history_manager.get_tweet_type_for_next_post()
            if tweet_type == 'gem_update':
                found_gem_update = True
                break
            self.history_manager.history['metadata']['total_tweets'] += 1
            
        self.assertTrue(found_gem_update)

    def test_metadata_tracking(self):
        """Test tweet metadata tracking"""
        initial_tweets = self.history_manager.history['metadata']['total_tweets']
        
        # Simulate 500 tweets
        for _ in range(500):
            self.history_manager.get_tweet_type_for_next_post()
            self.history_manager.history['metadata']['total_tweets'] += 1
            
        final_tweets = self.history_manager.history['metadata']['total_tweets']
        self.assertEqual(final_tweets - initial_tweets, 500)
