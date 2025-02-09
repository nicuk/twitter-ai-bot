"""Performance-focused tweet formatters"""

from datetime import datetime, timedelta
from typing import Dict, List
import random
import sys
import os
import logging
from twitter.hashtag_manager import HashtagManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseFormatter:
    """Base class for performance formatters with common utilities."""
    
    def __init__(self):
        self.MAX_TWEET_LENGTH = 280
        self.MIN_TWEET_LENGTH = 210
        self.hashtag_manager = HashtagManager()
    
    def _calculate_gain(self, current: float, previous: float) -> float:
        """Calculate percentage gain safely"""
        if not previous or previous == 0:
            return 0
        return ((current - previous) / previous) * 100
        
    def _get_top_winners(self, history: Dict, limit: int = 3) -> List[Dict]:
        """Get top performing tokens"""
        try:
            # Get today's tokens
            now = datetime.now()
            today = now.date()
            todays_tokens = {k: v for k, v in history.get('tokens', {}).items() 
                           if datetime.fromisoformat(v.get('first_mention_date', '')).date() == today}
            
            # Sort by gain and get top N
            sorted_tokens = sorted([(k, v) for k, v in todays_tokens.items()], 
                                key=lambda x: x[1].get('gain_percentage', 0),
                                reverse=True)[:limit]
            
            # Format token data
            return [{'symbol': k, 'gain_percentage': v.get('gain_percentage', 0)} 
                   for k, v in sorted_tokens]
            
        except Exception:
            return []
        
    def optimize_tweet_length(self, tweet: str, data: Dict, format_type: str) -> str:
        """Optimize tweet length to be between 260-265 characters."""
        # Get similar tokens with fallback
        similar_tokens = data.get('similar_tokens', [])
        if not similar_tokens and format_type != 'performance':
            similar_tokens = ['BTC', 'ETH', 'SOL']  # Fallback to major coins
            
        # Get hashtags from manager
        hashtags, _ = self.hashtag_manager.get_hashtags(format_type)
        
        # Add format-specific padding with relevant token mentions
        if len(tweet) < 260:
            tweet += f"\n\n{' '.join(hashtags)}"
            if len(tweet) < 260 and similar_tokens:
                # Use next set of similar tokens if available
                next_tokens = similar_tokens[3:5] if len(similar_tokens) > 4 else similar_tokens[:2]
                tweet += f"\n${' $'.join(next_tokens)}"
                
        return tweet

class PerformanceCompareFormatter(BaseFormatter):
    """Shows individual token performance"""
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format tweet comparing entry vs current performance"""
        try:
            symbol = token_data.get('symbol', 'UNKNOWN')
            first_price = token_data.get('first_mention_price', 0)
            current_price = token_data.get('current_price', 0)
            volume = token_data.get('volume_24h', 0)
            volume_change = token_data.get('volume_change_24h', 0)
            gain = token_data.get('gain_percentage', 0)
            vmc_ratio = token_data.get('volume_mcap_ratio', 0) * 100  # Convert to percentage
            similar_tokens = token_data.get('similar_tokens', [])  # Get similar tokens
            
            tweet = f"""🤖 Performance: ${symbol}

💰 Price Action:
• Entry: ${first_price:.6f}
• Current: ${current_price:.6f}
• Change: {gain:+.1f}%

📈 Volume:
• 24h: ${volume:,.0f}
• Change: {volume_change:+.1f}%
• V/MC: {vmc_ratio:.1f}%"""

            # Add similar tokens if available (increased to 8)
            if similar_tokens:
                tweet += f"\n\n👥 Special mentions: {' '.join([f'${t}' for t in similar_tokens[:8]])}"

            return self.optimize_tweet_length(tweet, token_data, 'performance')
            
        except Exception as e:
            logger.error(f"Error formatting performance compare tweet: {e}")
            return ""

class SuccessRateFormatter(BaseFormatter):
    """Shows overall success rates"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet showing success rates"""
        try:
            # Get stats
            stats = history_data.get('stats', {})
            
            # Get success rates and gains
            success_rate = stats.get('success_rate_24h', 0)
            avg_gain = stats.get('avg_gain_24h', 0)
            best_gain = stats.get('best_gain_24h', 0)
            
            # Get top performers (increased to 5)
            performers = self._get_top_winners(history_data, 5)
            if not performers:
                return ""
                
            tweet = """📊 Daily Performance Update

🏆 Top Performers:"""

            # Add top performers with special emojis
            emojis = ["1.💎", "2.👑", "3.⭐", "4.💫", "5.✨"]
            for i, token in enumerate(performers):
                symbol = token.get('symbol', '')
                gain = token.get('gain_percentage', 0)
                tweet += f"\n{emojis[i]} ${symbol} (+{gain:.1f}%)"
                
            tweet += f"""

📈 Stats Today:
• Success Rate: {success_rate:.0f}%
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""

            return self.optimize_tweet_length(tweet, {'similar_tokens': [p.get('symbol') for p in performers]}, 'success')
            
        except Exception as e:
            logger.error(f"Error formatting success rate tweet: {e}")
            return ""

class PredictionAccuracyFormatter(BaseFormatter):
    """Shows prediction accuracy stats"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet showing prediction accuracy"""
        try:
            # Get stats
            stats = history_data.get('stats', {})
            
            # Calculate success rates (default to 0 if missing)
            success_rate_24h = stats.get('success_rate_24h', 0)
            success_rate_7d = stats.get('success_rate_7d', 0)
            total_predictions = stats.get('total_predictions', 0)
            
            # Get recent hits (show all 6)
            recent_hits = stats.get('recent_hits', [])[:6]
            
            tweet = f"""🎯 Prediction Accuracy Update

📊 Performance:
• 24h: {success_rate_24h:.0f}%
• 7d: {success_rate_7d:.0f}%
• Total: {total_predictions} predictions

✅ Recent Hits:"""

            # Show all 6 hits
            if recent_hits:
                for hit in recent_hits:
                    symbol = hit.get('symbol', '')
                    target = hit.get('target', 0)
                    actual = hit.get('actual', 0)
                    tweet += f"\n• ${symbol}: +{target:.1f}% → +{actual:.1f}%"

            return self.optimize_tweet_length(tweet, {'similar_tokens': [h.get('symbol') for h in recent_hits]}, 'accuracy')
            
        except Exception as e:
            logger.error(f"Error formatting prediction accuracy tweet: {e}")
            return ""

class WinnersRecapFormatter(BaseFormatter):
    """Shows top performing tokens"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet showing top performers"""
        try:
            # Get today's tokens
            now = datetime.now()
            today = now.date()
            todays_tokens = {k: v for k, v in history_data.get('tokens', {}).items() 
                           if datetime.fromisoformat(v.get('first_mention_date', '')).date() == today}
            
            if not todays_tokens:
                return ""
            
            # Get top performers (increased to 10)
            performers = sorted([(k, v.get('max_gain_percentage_7d', 0)) 
                               for k, v in todays_tokens.items()],
                              key=lambda x: x[1], reverse=True)[:10]  # Get top 10
            
            # Count profitable tokens
            total_tokens = len(todays_tokens)
            profitable = sum(1 for v in todays_tokens.values() if v.get('max_gain_percentage_7d', 0) > 0)
            
            # Format tweet
            tweet = "🏆 Top Performers:"
            
            # Add top 3 with medals
            for i, (symbol, gain) in enumerate(performers[:3]):
                medal = ["🥇", "🥈", "🥉"][i]
                tweet += f"\n{medal} ${symbol}: +{gain:.1f}%"
            
            # Add remaining with numbers
            numbers = ["4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            for i, (symbol, gain) in enumerate(performers[3:]):
                tweet += f"\n{numbers[i]} ${symbol}: +{gain:.1f}%"
            
            tweet += f"\n📊 Overall: {profitable}/{total_tokens} profitable"
            
            return self.optimize_tweet_length(tweet, {'similar_tokens': [p[0] for p in performers]}, 'winners')
            
        except Exception as e:
            logger.error(f"Error formatting winners recap tweet: {e}")
            return ""

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
        'similar_tokens': [
            'TKN1', 'TKN2', 'TKN3', 'TKN4', 'TKN5'
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
