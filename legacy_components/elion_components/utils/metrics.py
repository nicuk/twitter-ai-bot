"""
Performance metrics tracking for Elion
"""

from typing import Dict, List
from datetime import datetime, timedelta

class MetricsTracker:
    """Tracks and analyzes performance metrics"""
    
    def __init__(self):
        """Initialize metrics tracker"""
        self.metrics = {
            'tweets': [],
            'engagement': {},
            'viral_hits': [],
            'performance': {
                'engagement_rate': 0.0,
                'viral_rate': 0.0,
                'alpha_accuracy': 0.0
            }
        }
        
        # Viral thresholds
        self.viral_thresholds = {
            'likes': 100,
            'retweets': 50,
            'replies': 20
        }

    def track_content(self, content_type: str, content: str, confidence: float) -> None:
        """Track new content"""
        try:
            if not content:
                return
                
            self.metrics['tweets'].append({
                'content_type': content_type,
                'content': content,
                'confidence': confidence,
                'timestamp': datetime.now(),
                'performance': None  # To be updated later
            })
            
        except Exception as e:
            print(f"Error tracking content: {e}")

    def analyze_tweet(self, tweet_data: Dict) -> Dict:
        """Analyze tweet performance"""
        try:
            # Get engagement metrics
            likes = tweet_data.get('likes', 0)
            retweets = tweet_data.get('retweets', 0)
            replies = tweet_data.get('replies', 0)
            
            # Calculate engagement rate
            total_engagement = likes + retweets + replies
            followers = tweet_data.get('followers', 1)  # Avoid div by 0
            engagement_rate = total_engagement / followers
            
            # Check if viral
            is_viral = (
                likes >= self.viral_thresholds['likes'] or
                retweets >= self.viral_thresholds['retweets'] or
                replies >= self.viral_thresholds['replies']
            )
            
            # Update metrics
            if is_viral:
                self.metrics['viral_hits'].append(tweet_data)
            
            # Calculate performance
            performance = {
                'engagement_rate': engagement_rate,
                'is_viral': is_viral,
                'metrics': {
                    'likes': likes,
                    'retweets': retweets,
                    'replies': replies
                }
            }
            
            # Update tweet record
            tweet_id = tweet_data.get('id')
            if tweet_id:
                self.metrics['engagement'][tweet_id] = performance
            
            return performance
            
        except Exception as e:
            print(f"Error analyzing tweet: {e}")
            return {}

    def get_performance_stats(self) -> Dict:
        """Get overall performance statistics"""
        try:
            # Get recent tweets (last 7 days)
            cutoff = datetime.now() - timedelta(days=7)
            recent_tweets = [
                t for t in self.metrics['tweets']
                if t['timestamp'] > cutoff
            ]
            
            if not recent_tweets:
                return self.metrics['performance']
            
            # Calculate metrics
            engagement_rates = [
                t['performance']['engagement_rate']
                for t in recent_tweets
                if t['performance']
            ]
            
            viral_hits = [
                t for t in recent_tweets
                if t['performance'] and t['performance']['is_viral']
            ]
            
            # Update performance metrics
            self.metrics['performance'].update({
                'engagement_rate': sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0.0,
                'viral_rate': len(viral_hits) / len(recent_tweets) if recent_tweets else 0.0
            })
            
            return self.metrics['performance']
            
        except Exception as e:
            print(f"Error getting performance stats: {e}")
            return self.metrics['performance']
