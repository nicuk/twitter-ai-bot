"""Tweet history management"""

from datetime import datetime, timedelta, date

import json
import logging

logger = logging.getLogger(__name__)

class TweetHistory:
    def __init__(self):
        """Initialize tweet history manager"""
        self.tweets = []
        self.max_history = 100  # Keep last 100 tweets
        self.history = {}  # Initialize history dictionary
    
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
                
    def cleanup_old_tweets(self, days: int = 7) -> None:
        """Remove tweets older than specified days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        self.tweets = [
            tweet for tweet in self.tweets
            if datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]

    def track_token(self, symbol: str, price_data: dict = None) -> None:
        """Track a token that was mentioned in a tweet
        
        Args:
            symbol: Token symbol
            price_data: Optional dict containing price info:
                - current_price: Current token price
                - entry_price: Entry price if available
                - gain_percentage: Current gain/loss percentage
        """
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Initialize history for new tokens
            if symbol not in self.history:
                self.history[symbol] = {
                    'symbol': symbol,
                    'first_mention_date': current_time,
                    'last_mention_date': current_time,
                    'mention_count': 1,
                    'entry_price': price_data.get('entry_price', 0) if price_data else 0,
                    'current_price': price_data.get('current_price', 0) if price_data else 0,
                    'gain_percentage': price_data.get('gain_percentage', 0) if price_data else 0
                }
            else:
                # Update existing token history
                self.history[symbol].update({
                    'last_mention_date': current_time,
                    'mention_count': self.history[symbol]['mention_count'] + 1
                })
                
                # Update price data if provided
                if price_data:
                    self.history[symbol].update({
                        'current_price': price_data.get('current_price', self.history[symbol].get('current_price', 0)),
                        'entry_price': price_data.get('entry_price', self.history[symbol].get('entry_price', 0)),
                        'gain_percentage': price_data.get('gain_percentage', self.history[symbol].get('gain_percentage', 0))
                    })
            
            # Save updated history
            self._save_history()
            
        except Exception as e:
            logger.error(f"Error tracking token {symbol}: {e}")

    def _save_history(self) -> None:
        # TO DO: implement saving history to a file or database
        pass
