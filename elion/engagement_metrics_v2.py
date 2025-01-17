"""
Engagement metrics tracking system
"""

from datetime import datetime, timedelta
from typing import Dict, List

class EngagementMetrics:
    """Tracks all engagement metrics"""
    
    def __init__(self):
        """Initialize metrics tracking"""
        self.metrics = {
            'viral_tweets': {},      # Track viral tweets and patterns
            'successful_hooks': {},   # Track successful hooks
            'topic_performance': {},  # Track by topic
            'time_performance': {},   # Track by time
            'follower_segments': {}   # Track segments
        }
        
        self.viral_thresholds = {
            'likes': 100,
            'retweets': 50,
            'replies': 25,
            'quotes': 10
        }
        
    def track_engagement(self, tweet_data: Dict):
        """Track engagement metrics for a tweet"""
        try:
            tweet_id = tweet_data.get('id')
            if not tweet_id:
                return
                
            # Extract metrics
            metrics = tweet_data.get('public_metrics', {})
            timestamp = tweet_data.get('created_at', datetime.utcnow())
            
            # Check viral status
            is_viral = self._check_viral_status(metrics)
            
            # Store tweet metrics
            self.metrics['viral_tweets'][tweet_id] = {
                'metrics': metrics,
                'is_viral': is_viral,
                'timestamp': timestamp,
                'content': tweet_data.get('text', '')
            }
            
            # Update time performance
            hour = datetime.fromisoformat(timestamp).hour
            self._update_time_metrics(hour, is_viral)
            
            # Update topic performance
            topics = self._extract_topics(tweet_data.get('text', ''))
            self._update_topic_metrics(topics, is_viral)
            
        except Exception as e:
            print(f"Error tracking metrics: {e}")
            
    def _check_viral_status(self, metrics: Dict) -> bool:
        """Check if tweet meets viral thresholds"""
        return any([
            metrics.get('like_count', 0) >= self.viral_thresholds['likes'],
            metrics.get('retweet_count', 0) >= self.viral_thresholds['retweets'],
            metrics.get('reply_count', 0) >= self.viral_thresholds['replies'],
            metrics.get('quote_count', 0) >= self.viral_thresholds['quotes']
        ])
        
    def _update_time_metrics(self, hour: int, is_viral: bool):
        """Update performance metrics by time"""
        if hour not in self.metrics['time_performance']:
            self.metrics['time_performance'][hour] = {
                'total': 0,
                'viral': 0
            }
            
        self.metrics['time_performance'][hour]['total'] += 1
        if is_viral:
            self.metrics['time_performance'][hour]['viral'] += 1
            
    def _update_topic_metrics(self, topics: List[str], is_viral: bool):
        """Update performance metrics by topic"""
        for topic in topics:
            if topic not in self.metrics['topic_performance']:
                self.metrics['topic_performance'][topic] = {
                    'total': 0,
                    'viral': 0
                }
                
            self.metrics['topic_performance'][topic]['total'] += 1
            if is_viral:
                self.metrics['topic_performance'][topic]['viral'] += 1
                
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from tweet text"""
        # Simple topic extraction - can be enhanced
        topics = []
        if 'market' in text.lower():
            topics.append('market')
        if 'alpha' in text.lower():
            topics.append('alpha')
        if 'analysis' in text.lower():
            topics.append('analysis')
        return topics
        
    def get_performance_stats(self) -> Dict:
        """Get overall performance statistics"""
        try:
            total_tweets = len(self.metrics['viral_tweets'])
            viral_tweets = sum(1 for t in self.metrics['viral_tweets'].values() if t['is_viral'])
            
            # Get best performing times
            time_stats = sorted(
                self.metrics['time_performance'].items(),
                key=lambda x: x[1]['viral'] / x[1]['total'] if x[1]['total'] > 0 else 0,
                reverse=True
            )[:3]
            
            # Get best performing topics
            topic_stats = sorted(
                self.metrics['topic_performance'].items(),
                key=lambda x: x[1]['viral'] / x[1]['total'] if x[1]['total'] > 0 else 0,
                reverse=True
            )[:3]
            
            return {
                'total_tweets': total_tweets,
                'viral_tweets': viral_tweets,
                'viral_rate': viral_tweets / total_tweets if total_tweets > 0 else 0,
                'best_times': time_stats,
                'best_topics': topic_stats
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
