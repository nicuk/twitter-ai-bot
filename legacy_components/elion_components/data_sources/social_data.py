"""
Social data source for Elion
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from .base import BaseDataSource
from twitter_api_bot import TwitterBot

class SocialDataSource(BaseDataSource):
    """Social data source that connects to Twitter API Bot"""
    
    def __init__(self, credentials: Dict[str, str] = None):
        """Initialize social data source"""
        super().__init__()
        self.twitter = TwitterBot()
        
        # Configure cache durations
        self.cache_durations.update({
            'viral_tweets': timedelta(minutes=30),
            'tweet_metrics': timedelta(minutes=15)
        })
    
    def _validate_data(self, data: Any) -> bool:
        """Validate social data"""
        if not isinstance(data, (list, dict)):
            return False
        return True
    
    def get_viral_tweets(self, limit: int = 10) -> List[Dict]:
        """Get viral crypto tweets"""
        cache_key = f'viral_tweets_{limit}'
        cached = self.get_cached(cache_key)
        if cached:
            return cached
            
        tweets = self.twitter.get_viral_tweets(limit)
        self.cache_data(cache_key, tweets)
        return tweets
        
    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """Get metrics for a specific tweet"""
        cache_key = f'tweet_metrics_{tweet_id}'
        cached = self.get_cached(cache_key)
        if cached:
            return cached
            
        metrics = self.twitter.get_tweet_metrics(tweet_id)
        self.cache_data(cache_key, metrics)
        return metrics
        
    def post_tweet(self, content: str) -> Dict:
        """Post a new tweet"""
        return self.twitter.post_tweet(content)
        
    def schedule_tweet(self, content: str, timestamp: str) -> Dict:
        """Schedule a tweet for later"""
        return self.twitter.schedule_tweet(content, timestamp)
