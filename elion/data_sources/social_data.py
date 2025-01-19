"""
Social data source for Elion
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
import tweepy
from .base import BaseDataSource

class SocialDataSource(BaseDataSource):
    """Social data source"""
    
    def __init__(self, twitter_api=None):
        """Initialize social data source"""
        super().__init__()
        self.twitter_api = twitter_api
        
        # Configure cache durations
        self.cache_durations.update({
            'viral_tweets': timedelta(minutes=30),
            'influencer_activity': timedelta(minutes=15),
            'social_sentiment': timedelta(minutes=15)
        })
        
        # Configure key influencers
        self.key_influencers = [
            'VitalikButerin',
            'cz_binance',
            'elonmusk',
            'CryptoCapo_',
            'inversebrah',
            'AltcoinGordon',
            'CryptoCred'
        ]
        
    def _validate_data(self, data: Any) -> bool:
        """Validate social data"""
        if not isinstance(data, (list, dict)):
            return False
        return True
        
    def get_viral_tweets(self, limit: int = 10) -> List[Dict]:
        """Get viral crypto tweets"""
        # Check cache first
        cached = self._get_cached('viral_tweets')
        if cached:
            return cached[:limit]
            
        try:
            tweets = []
            # Search for viral crypto tweets
            query = "(#crypto OR #bitcoin OR #ethereum) min_faves:1000"
            search_results = self.twitter_api.search_tweets(
                q=query,
                lang="en",
                result_type="popular",
                count=limit
            )
            
            for tweet in search_results:
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author': tweet.user.screen_name,
                    'likes': tweet.favorite_count,
                    'retweets': tweet.retweet_count,
                    'created_at': tweet.created_at
                })
                
            # Cache and return
            self._cache_data('viral_tweets', tweets)
            return tweets
            
        except Exception as e:
            print(f"Error getting viral tweets: {e}")
            return []
            
    def get_influencer_activity(self) -> List[Dict]:
        """Get recent activity from key influencers"""
        # Check cache first
        cached = self._get_cached('influencer_activity')
        if cached:
            return cached
            
        try:
            activity = []
            for influencer in self.key_influencers:
                try:
                    tweets = self.twitter_api.user_timeline(
                        screen_name=influencer,
                        count=5,
                        tweet_mode="extended"
                    )
                    
                    for tweet in tweets:
                        if not tweet.retweeted:  # Skip retweets
                            activity.append({
                                'id': tweet.id,
                                'text': tweet.full_text,
                                'author': tweet.user.screen_name,
                                'likes': tweet.favorite_count,
                                'retweets': tweet.retweet_count,
                                'created_at': tweet.created_at
                            })
                            
                except Exception as e:
                    print(f"Error getting tweets for {influencer}: {e}")
                    continue
                    
            # Cache and return
            self._cache_data('influencer_activity', activity)
            return activity
            
        except Exception as e:
            print(f"Error getting influencer activity: {e}")
            return []
            
    def get_social_sentiment(self) -> Dict:
        """Get overall social sentiment"""
        # Check cache first
        cached = self._get_cached('social_sentiment')
        if cached:
            return cached
            
        try:
            # Get recent crypto tweets
            query = "#crypto OR #bitcoin OR #ethereum"
            tweets = self.twitter_api.search_tweets(
                q=query,
                lang="en",
                result_type="recent",
                count=100
            )
            
            # Analyze sentiment
            bullish_count = 0
            bearish_count = 0
            
            bullish_terms = ['moon', 'pump', 'bull', 'long', 'buy', 'bullish', '🚀', '📈']
            bearish_terms = ['dump', 'bear', 'short', 'sell', 'bearish', 'crash', '📉', '🔻']
            
            for tweet in tweets:
                text = tweet.text.lower()
                
                # Count bullish/bearish terms
                if any(term in text for term in bullish_terms):
                    bullish_count += 1
                if any(term in text for term in bearish_terms):
                    bearish_count += 1
                    
            total = bullish_count + bearish_count
            if total == 0:
                sentiment = "Neutral"
                score = 0
            else:
                bull_ratio = bullish_count / total
                if bull_ratio >= 0.7:
                    sentiment = "Very Bullish"
                    score = 1
                elif bull_ratio >= 0.6:
                    sentiment = "Bullish"
                    score = 0.5
                elif bull_ratio <= 0.3:
                    sentiment = "Very Bearish"
                    score = -1
                elif bull_ratio <= 0.4:
                    sentiment = "Bearish"
                    score = -0.5
                else:
                    sentiment = "Neutral"
                    score = 0
                    
            result = {
                'sentiment': sentiment,
                'score': score,
                'bullish_count': bullish_count,
                'bearish_count': bearish_count,
                'total_analyzed': len(tweets)
            }
            
            # Cache and return
            self._cache_data('social_sentiment', result)
            return result
            
        except Exception as e:
            print(f"Error getting social sentiment: {e}")
            return {
                'sentiment': "Neutral",
                'score': 0,
                'bullish_count': 0,
                'bearish_count': 0,
                'total_analyzed': 0
            }
