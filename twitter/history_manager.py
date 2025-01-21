"""Tweet history management"""

from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class TweetHistory:
    def __init__(self):
        """Initialize tweet history manager"""
        self.tweets = []
        self.max_history = 100  # Keep last 100 tweets
    
    def add_tweet(self, tweet_data: dict) -> None:
        """Add new tweet to history"""
        tweet_data['timestamp'] = datetime.utcnow().isoformat()
        self.tweets.append(tweet_data)
        
        # Keep only last N tweets
        if len(self.tweets) > self.max_history:
            self.tweets = self.tweets[-self.max_history:]
    
    def get_recent_tweets(self, hours: int = 24) -> list:
        """Get tweets from last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            tweet for tweet in self.tweets
            if datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]
    
    def update_metrics(self, tweet_id: str, metrics: dict) -> None:
        """Update metrics for a tweet"""
        for tweet in self.tweets:
            if tweet.get('id') == tweet_id:
                tweet['metrics'] = metrics
                break
