"""
Engagement metrics tracking
"""

from datetime import datetime, timedelta
from typing import Dict

class EngagementMetrics:
    """Tracks engagement metrics"""
    
    def __init__(self):
        """Initialize metrics tracking"""
        self.metrics = {
            'viral_tweets': {},      # Track viral tweets
            'topic_performance': {}, # Track by topic
            'time_performance': {},  # Track by time
            'follower_segments': {}  # Track segments
        }
        
        self.viral_thresholds = {
            'likes': 100,
            'retweets': 50,
            'replies': 25
        }
        
    def track_engagement(self, tweet_id: str, metrics: Dict):
        """Track engagement for a tweet"""
        try:
            # Get metrics
            likes = metrics.get('like_count', 0)
            retweets = metrics.get('retweet_count', 0)
            replies = metrics.get('reply_count', 0)
            
            # Check if viral
            is_viral = (
                likes >= self.viral_thresholds['likes'] or
                retweets >= self.viral_thresholds['retweets'] or
                replies >= self.viral_thresholds['replies']
            )
            
            # Store metrics
            self.metrics['viral_tweets'][tweet_id] = {
                'metrics': metrics,
                'is_viral': is_viral,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            print(f"Error tracking metrics: {e}")
            
    def get_performance_stats(self) -> Dict:
        """Get engagement performance stats"""
        try:
            total_tweets = len(self.metrics['viral_tweets'])
            viral_tweets = sum(1 for t in self.metrics['viral_tweets'].values() if t['is_viral'])
            
            return {
                'total_tweets': total_tweets,
                'viral_tweets': viral_tweets,
                'viral_rate': viral_tweets / total_tweets if total_tweets > 0 else 0
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
