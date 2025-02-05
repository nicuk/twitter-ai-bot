"""Performance-focused tweet formatters"""

from datetime import datetime
from typing import Dict, List
import random
import sys
import os

# Add parent directory to path so we can import elion modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from elion.content.tweet_formatters import TweetFormatters

class BasePerformanceFormatter(TweetFormatters):
    """Base class for performance formatters with common utilities."""
    
    def __init__(self):
        self.MAX_TWEET_LENGTH = 280
        self.MIN_TWEET_LENGTH = 210
    
    def _calculate_gain(self, current: float, previous: float) -> float:
        """Calculate percentage gain safely"""
        if not previous or previous == 0:
            return 0
        return ((current - previous) / previous) * 100
        
    def _get_top_winners(self, history: Dict, limit: int = 2) -> List[Dict]:
        """Get top performing tokens"""
        winners = []
        for symbol, data in history.items():
            if data.get('first_mention_price', 0) > 0:
                gain = self._calculate_gain(data.get('current_price', 0), data.get('first_mention_price', 0))
                winners.append({
                    'symbol': symbol,
                    'gain_percentage': gain,
                    'max_gain_percentage_7d': data.get('max_gain_percentage_7d', 0)
                })
        return sorted(winners, key=lambda x: x.get('max_gain_percentage_7d', 0), reverse=True)[:limit]
        
    def optimize_tweet_length(self, tweet: str, data: Dict, format_type: str) -> str:
        """Optimize tweet length to be between 210-280 characters.
        
        Args:
            tweet: Base tweet to optimize
            data: Data dictionary used to generate the tweet
            format_type: Type of tweet format
            
        Returns:
            Optimized tweet with length between 210-280 characters
        """
        # If tweet is already in range, return as is
        if self.MIN_TWEET_LENGTH <= len(tweet) <= self.MAX_TWEET_LENGTH:
            return tweet
            
        # If tweet is too long, truncate it
        if len(tweet) > self.MAX_TWEET_LENGTH:
            return tweet[:self.MAX_TWEET_LENGTH-3] + "..."
            
        # If tweet is too short, add relevant insight
        insights = {
            'performance_compare': [
                "\n\n💡 Strong momentum with increasing volume",
                "\n\n💡 Pattern suggests potential continuation",
                "\n\n💡 Technical indicators remain bullish",
                "\n\n💡 Similar setups had positive outcomes"
            ],
            'success_rate': [
                "\n\n💡 Consistent performance across cycles",
                "\n\n💡 Strategy shows improving accuracy",
                "\n\n💡 Risk management remains key focus",
                "\n\n💡 Data-driven approach yields results"
            ],
            'prediction_accuracy': [
                "\n\n💡 Pattern recognition improving",
                "\n\n💡 Models show high confidence",
                "\n\n💡 Historical accuracy validates approach",
                "\n\n💡 Continuous model refinement"
            ],
            'winners_recap': [
                "\n\n💡 Winners show strong fundamentals",
                "\n\n💡 Volume profile remains healthy",
                "\n\n💡 Technical setup looks promising",
                "\n\n💡 Market sentiment stays positive"
            ]
        }
        
        if format_type in insights:
            # Get random insight for this type
            available_insights = insights[format_type]
            insight = random.choice(available_insights)
            
            # Add insight if it fits
            if len(tweet) + len(insight) <= self.MAX_TWEET_LENGTH:
                return tweet + insight
                
        return tweet

class PerformanceCompareFormatter(BasePerformanceFormatter):
    """Formats tweets comparing token performance"""
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format a performance comparison tweet"""
        # Safely calculate percentage changes
        price_change = ((token_data.get('current_price', 0) - token_data.get('first_mention_price', 0)) / 
                       token_data.get('first_mention_price', 1) * 100) if token_data.get('first_mention_price', 0) > 0 else 0
                       
        volume_change = ((token_data.get('volume_24h', 0) - token_data.get('first_mention_volume_24h', 0)) / 
                        token_data.get('first_mention_volume_24h', 1) * 100) if token_data.get('first_mention_volume_24h', 0) > 0 else 0
        
        # Base tweet
        tweet = f"""🤖 Performance: ${token_data.get('symbol', 'UNKNOWN')}

💰 Price Action:
• Entry: ${token_data.get('first_mention_price', 0):.4f}
• Current: ${token_data.get('current_price', 0):.4f}
• Change: {price_change:+.1f}%

📈 Volume:
• 24h: {token_data.get('volume_24h', 0):,.0f}
• Change: {volume_change:+.1f}%
• V/MC: {token_data.get('volume_mcap_ratio', 0) * 100:.1f}%"""

        # Add similar V/MC tokens if available
        similar_tokens = token_data.get('similar_vmc_tokens', [])
        if similar_tokens:
            # Sort by closest V/MC ratio to our token
            target_vmc = token_data.get('volume_mcap_ratio', 0)
            similar_tokens.sort(key=lambda x: abs(x['volume_mcap_ratio'] - target_vmc))
            
            # Add tokens while staying under limit
            MAX_LENGTH = 265  # 280 - 15 buffer
            token_tags = []
            for token in similar_tokens:
                next_tag = f"${token['symbol']}"
                if len(tweet) + len(" " + next_tag) <= MAX_LENGTH:
                    token_tags.append(next_tag)
                else:
                    break
            
            if token_tags:
                tweet += "\n\n" + " ".join(token_tags)

        return tweet

class SuccessRateFormatter(BasePerformanceFormatter):
    """Shows overall performance metrics."""
    
    def _get_rank_emoji(self, rank: int) -> str:
        """Get emoji for rank"""
        if rank == 1:
            return "1.💎"  # Diamond for 1st
        elif rank == 2:
            return "2.👑"  # Crown for 2nd
        elif rank == 3:
            return "3.⭐"  # Star for 3rd
        elif rank <= 5:
            return f"{rank}.🔥"  # Fire for 4th-5th
        else:
            return f"{rank}.⚡"  # Lightning for others
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format a success rate tweet"""
        tweet = f"""📊 Daily Performance Update

🏆 Top Performers:"""
        
        # Add ranked performers
        MAX_LENGTH = 260  # 280 - 20 buffer
        top_performers = token_data.get('top_performers', [])
        if top_performers:
            # Sort by gain descending
            top_performers.sort(key=lambda x: x['gain'], reverse=True)
            
            # Add performers while staying under limit
            for i, token in enumerate(top_performers, 1):
                rank_emoji = self._get_rank_emoji(i)
                next_line = f"\n{rank_emoji} ${token['symbol']} (+{token['gain']:.1f}%)"
                if len(tweet) + len(next_line) <= MAX_LENGTH:
                    tweet += next_line
                else:
                    break

        # Add daily stats
        tweet += f"""

📈 Stats Today:
• Success Rate: {token_data.get('success_rate', 0)}%
• Avg Gain: +{token_data.get('avg_gain', 0)}%
• Best: +{token_data.get('best_gain', 0):.1f}%"""

        return tweet

class PredictionAccuracyFormatter(BasePerformanceFormatter):
    """Shows prediction accuracy with pattern matches."""
    
    def _is_positive_success(self, pred: Dict) -> bool:
        """Check if prediction was successful and both predicted/actual were positive"""
        try:
            # Remove '%' and '+' signs and convert to float
            predicted = float(pred['predicted'].replace('%', '').replace('+', ''))
            actual = float(pred['actual'].replace('%', '').replace('+', ''))
            # Only count as success if both predicted and actual were positive
            return pred['success'] and predicted > 0 and actual > 0
        except (ValueError, KeyError):
            return False
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format a prediction accuracy tweet"""
        # Get successful predictions with positive gains
        successful_predictions = [
            pred for pred in token_data.get('recent_predictions', [])
            if self._is_positive_success(pred)
        ]
        
        # If less than 2 successful predictions, return None
        if len(successful_predictions) < 2:
            return None
            
        tweet = f"""🎯 Prediction Accuracy Update

📊 Performance:
• 24h: {token_data.get('accuracy_24h', 0)}%
• 7d: {token_data.get('accuracy_7d', 0)}%
• Total: {token_data.get('total_predictions', 0)} predictions"""

        # Add up to 6 successful predictions
        if successful_predictions:
            tweet += "\n\n✅ Recent Hits:"
            for pred in successful_predictions[:6]:  # Limit to 6 successful predictions
                next_line = f"\n• ${pred['symbol']}: {pred['predicted']} → {pred['actual']}"
                if len(tweet) + len(next_line) <= 260:  # 280 - 20 buffer
                    tweet += next_line
                else:
                    break

        return tweet

class WinnersRecapFormatter(BasePerformanceFormatter):
    """Shows weekly winners with key stats."""
    
    def format_tweet(self, history_data: Dict) -> str:
        """Format winners recap tweet"""
        winners = self._get_top_winners(history_data)
        if not winners:
            return None
            
        tweet = f"""🏆 Weekly Winners Report

1. ${winners[0]['symbol']}
• Gain: +{winners[0].get('gain_percentage', 0):.1f}%
• Peak: +{winners[0].get('max_gain_percentage_7d', 0):.1f}%"""

        if len(winners) > 1:
            tweet += f"""

2. ${winners[1]['symbol']}
• Gain: +{winners[1].get('gain_percentage', 0):.1f}%
• Peak: +{winners[1].get('max_gain_percentage_7d', 0):.1f}%"""

        return self.optimize_tweet_length(tweet, {'history': history_data}, 'winners_recap')

def get_mock_data():
    """Get mock data for testing"""
    return {
        'symbol': 'TEST',
        'first_mention_price': 1.0,
        'current_price': 1.25,
        'first_mention_volume_24h': 1000000,
        'volume_24h': 1500000,
        'volume_mcap_ratio': 0.75,
        'first_mention_date': '2024-01-01',
        'similar_vmc_tokens': [
            {'symbol': 'TKN1', 'volume_mcap_ratio': 0.72, 'price_change_24h': 15.5},
            {'symbol': 'TKN2', 'volume_mcap_ratio': 0.78, 'price_change_24h': 8.2},
            {'symbol': 'TKN3', 'volume_mcap_ratio': 0.71, 'price_change_24h': 12.3},
            {'symbol': 'TKN4', 'volume_mcap_ratio': 0.76, 'price_change_24h': -5.1},
            {'symbol': 'TKN5', 'volume_mcap_ratio': 0.79, 'price_change_24h': 3.2}
        ]
    }

def get_mock_history():
    """Get mock history data for testing"""
    return {
        'success_rate': 78,
        'avg_gain': 35,
        'best_gain': 45,
        'top_performers': [
            {'symbol': 'TKN1', 'gain': 35.0},
            {'symbol': 'TKN2', 'gain': 32.5},
            {'symbol': 'TKN3', 'gain': 28.7},
            {'symbol': 'TKN4', 'gain': 25.3},
            {'symbol': 'TKN5', 'gain': 22.1},
            {'symbol': 'TKN6', 'gain': 18.9},
            {'symbol': 'TKN7', 'gain': 15.4}
        ]
    }

def get_mock_prediction_data():
    """Get mock prediction data for testing"""
    return {
        'accuracy_24h': 82,
        'accuracy_7d': 75,
        'total_predictions': 50,
        'recent_predictions': [
            {'symbol': 'TKN1', 'predicted': '+15%', 'actual': '+18.5%', 'success': True},
            {'symbol': 'TKN2', 'predicted': '+10%', 'actual': '+12.3%', 'success': True},
            {'symbol': 'TKN3', 'predicted': '+20%', 'actual': '-8.7%', 'success': False},  # Negative, will be filtered
            {'symbol': 'TKN4', 'predicted': '+25%', 'actual': '+27.1%', 'success': True},
            {'symbol': 'TKN5', 'predicted': '+30%', 'actual': '+32.5%', 'success': True},
            {'symbol': 'TKN6', 'predicted': '+18%', 'actual': '+21.2%', 'success': True},
            {'symbol': 'TKN7', 'predicted': '+22%', 'actual': '-19.1%', 'success': False},  # Negative, will be filtered
            {'symbol': 'TKN8', 'predicted': '+28%', 'actual': '+30.8%', 'success': True},
            {'symbol': 'TKN9', 'predicted': '+15%', 'actual': '+17.3%', 'success': True}
        ]
    }

def get_mock_prediction_data_few_success():
    """Get mock prediction data with few successes for testing"""
    return {
        'accuracy_24h': 40,
        'accuracy_7d': 35,
        'total_predictions': 20,
        'recent_predictions': [
            {'symbol': 'TKN1', 'predicted': '+15%', 'actual': '+18.5%', 'success': True},
            {'symbol': 'TKN2', 'predicted': '+20%', 'actual': '-8.7%', 'success': False},
            {'symbol': 'TKN3', 'predicted': '+25%', 'actual': '+27.1%', 'success': True},
            {'symbol': 'TKN4', 'predicted': '+30%', 'actual': '-22.5%', 'success': False}
        ]
    }

def test_performance_compare():
    """Test performance compare formatter"""
    print("\n=== Testing PerformanceCompareFormatter ===")
    formatter = PerformanceCompareFormatter()
    tweet = formatter.format_tweet(get_mock_data())
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}")

def test_success_rate():
    """Test success rate formatter"""
    print("\n=== Testing SuccessRateFormatter ===")
    formatter = SuccessRateFormatter()
    tweet = formatter.format_tweet(get_mock_history())
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}")

def test_prediction_accuracy():
    """Test prediction accuracy formatter"""
    print("\n=== Testing PredictionAccuracyFormatter ===\n")
    formatter = PredictionAccuracyFormatter()
    
    print("Test with many successful predictions:")
    mock_data = get_mock_prediction_data()
    tweet = formatter.format_tweet(mock_data)
    if tweet:
        print(f"Tweet ({len(tweet)} chars):")
        print(tweet)
    else:
        print("Not enough successful predictions")
    
    print("\nTest with few successful predictions:")
    mock_data = get_mock_prediction_data_few_success()
    tweet = formatter.format_tweet(mock_data)
    if tweet:
        print(f"Tweet ({len(tweet)} chars):")
        print(tweet)
    else:
        print("Not enough successful predictions")

def test_winners_recap():
    """Test winners recap formatter"""
    print("\n=== Testing WinnersRecapFormatter ===")
    formatter = WinnersRecapFormatter()
    tweet = formatter.format_tweet(get_mock_history())
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}")

if __name__ == "__main__":
    # Run tests one by one
    test_performance_compare()
    test_success_rate()
    test_prediction_accuracy()
    test_winners_recap()
