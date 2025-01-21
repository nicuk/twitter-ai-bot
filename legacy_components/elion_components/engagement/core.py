"""
Core engagement functionality
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
import json
import random

class EngagementManager:
    def __init__(self):
        self.engagement_metrics = {
            'viral_tweets': {},      # Track viral tweets and their patterns
            'successful_hooks': {},   # Track which hooks perform best
            'topic_performance': {},  # Track performance by topic
            'time_performance': {},   # Track performance by time of day
            'follower_segments': {}   # Track different follower segments
        }
        
        self.tweet_history = []      # Track all tweets and their performance
        
        self.viral_thresholds = {
            'likes': 100,
            'retweets': 50,
            'replies': 25,
            'quotes': 10
        }
        
        self.content_categories = {
            'alpha': {
                'optimal_times': [(2, 4), (8, 10), (14, 16), (20, 22)],  # UTC
                'frequency': 0.3,  # 30% of content
                'viral_potential': 0.8,
                'interests': ['alpha', 'technical analysis', 'trading strategies']
            },
            'analysis': {
                'optimal_times': [(1, 3), (7, 9), (13, 15), (19, 21)],
                'frequency': 0.3,
                'viral_potential': 0.6,
                'interests': ['fundamentals', 'macro', 'long-term']
            },
            'community': {
                'optimal_times': [(4, 6), (10, 12), (16, 18), (22, 24)],
                'frequency': 0.2,
                'viral_potential': 0.5,
                'interests': ['community', 'events', 'networking']
            },
            'education': {
                'optimal_times': [(0, 2), (6, 8), (12, 14), (18, 20)],
                'frequency': 0.2,
                'viral_potential': 0.4,
                'interests': ['basics', 'education', 'tutorials']
            }
        }
        
        self.viral_patterns = {
            'hooks': {
                'controversy': "Present a contrarian but well-supported view",
                'prediction': "Make a bold but calculated prediction",
                'insight': "Share unique perspective on common topic",
                'alpha': "Provide actionable trading insight",
                'thread': "Start an engaging thread with clear value",
                'poll': "Ask engaging community question"
            },
            'triggers': {
                'market_movement': 0.8,    # High chance of viral during big moves
                'trending_topic': 0.7,     # Good chance with trending topics
                'breaking_news': 0.9,      # Excellent for breaking news
                'community_event': 0.6     # Decent for community events
            }
        }

    def analyze_tweet_performance(self, tweet_data: Dict) -> Dict:
        """
        Analyze tweet performance and extract viral patterns
        
        Args:
            tweet_data: Dictionary containing tweet metrics and content
        
        Returns:
            Dictionary with analysis results and recommendations
        """
        engagement_score = self._calculate_engagement_score(tweet_data)
        viral_patterns = self._extract_viral_patterns(tweet_data)
        optimal_timing = self._analyze_post_timing(datetime.utcnow())  # For demo, using current time
        
        # Update metrics
        self._update_performance_metrics(tweet_data, engagement_score)
        
        return {
            'engagement_score': engagement_score,
            'viral_patterns': viral_patterns,
            'optimal_timing': optimal_timing,
            'recommendations': self._generate_recommendations(tweet_data)
        }

    def optimize_content_strategy(self, recent_performance: List[Dict]) -> Dict:
        """
        Optimize content strategy based on recent performance
        
        Args:
            recent_performance: List of recent tweet performance data
        
        Returns:
            Dictionary with optimized strategy recommendations
        """
        # Analyze patterns in successful content
        success_patterns = self._analyze_success_patterns(recent_performance)
        
        # Identify optimal posting times
        optimal_times = self._identify_optimal_times(recent_performance)
        
        # Determine best performing content types
        content_performance = self._analyze_content_types(recent_performance)
        
        return {
            'recommended_patterns': success_patterns,
            'optimal_posting_times': optimal_times,
            'content_type_priority': content_performance,
            'strategy_adjustments': self._generate_strategy_adjustments(
                success_patterns, optimal_times, content_performance
            )
        }

    def _calculate_engagement_score(self, tweet_data: Dict) -> float:
        """Calculate engagement score for a tweet"""
        likes = tweet_data.get('likes', 0)
        retweets = tweet_data.get('retweets', 0)
        replies = tweet_data.get('replies', 0)
        quotes = tweet_data.get('quotes', 0)
        
        # Weighted scoring
        score = (
            (likes * 1.0) +
            (retweets * 1.5) +
            (replies * 2.0) +
            (quotes * 2.5)
        ) / 100.0  # Normalize to 0-1 scale
        
        return min(1.0, score)

    def _extract_viral_patterns(self, tweet_data: Dict) -> Dict:
        """Extract viral patterns from successful tweet"""
        patterns = {
            'hooks': [],
            'timing': None,
            'content_type': None,
            'engagement_factors': []
        }
        
        # Analyze hooks used
        content = tweet_data.get('content', '')
        for hook_type, pattern in self.viral_patterns['hooks'].items():
            if self._matches_pattern(content, pattern):
                patterns['hooks'].append(hook_type)
        
        # Analyze timing
        timestamp = tweet_data.get('timestamp')
        if timestamp:
            patterns['timing'] = self._analyze_post_timing(timestamp)
        
        # Analyze content type
        patterns['content_type'] = self._identify_content_type(content)
        
        # Identify engagement factors
        patterns['engagement_factors'] = self._identify_engagement_factors(tweet_data)
        
        return patterns

    def _matches_pattern(self, content: str, pattern: str) -> bool:
        """Check if content matches a given pattern"""
        # Check for thread pattern specifically
        if pattern == "Start an engaging thread with clear value":
            return '🧵' in content or 'thread' in content.lower()
        
        # For other patterns, do a simple substring match
        return pattern.lower() in content.lower()

    def _analyze_post_timing(self, timestamp: datetime) -> Tuple[int, int]:
        """Analyze post timing and return optimal time range"""
        hour = timestamp.hour
        for time_range in self.content_categories['alpha']['optimal_times']:
            if time_range[0] <= hour <= time_range[1]:
                return time_range
        return (0, 0)

    def _identify_content_type(self, content: str) -> str:
        """Identify content type based on keywords"""
        for content_type, info in self.content_categories.items():
            for keyword in info.get('interests', []):
                if keyword.lower() in content.lower():
                    return content_type
        return 'unknown'

    def _identify_engagement_factors(self, tweet_data: Dict) -> List[str]:
        """Identify engagement factors for a tweet"""
        factors = []
        
        # Check metrics against thresholds
        for metric, value in tweet_data.items():
            if metric in self.viral_thresholds and value >= self.viral_thresholds[metric]:
                factors.append(f'high_{metric}')
        
        # Check content factors
        content = tweet_data.get('content', '').lower()
        if '🧵' in content or 'thread' in content:
            factors.append('thread')
        if 'breaking' in content:
            factors.append('breaking_news')
        if 'alpha' in content:
            factors.append('alpha_content')
        
        return factors

    def _update_performance_metrics(self, tweet_data: Dict, engagement_score: float) -> None:
        """Update performance metrics with new tweet data"""
        # Update viral tweets if applicable
        if engagement_score > 0.7:  # High engagement threshold
            tweet_id = tweet_data.get('id')
            if tweet_id:
                self.engagement_metrics['viral_tweets'][tweet_id] = {
                    'score': engagement_score,
                    'patterns': self._extract_viral_patterns(tweet_data)
                }
        
        # Update hook performance
        content = tweet_data.get('content', '')
        for hook_type, pattern in self.viral_patterns['hooks'].items():
            if self._matches_pattern(content, pattern):
                if hook_type not in self.engagement_metrics['successful_hooks']:
                    self.engagement_metrics['successful_hooks'][hook_type] = []
                self.engagement_metrics['successful_hooks'][hook_type].append(engagement_score)

    def _analyze_success_patterns(self, performance_data: List[Dict]) -> Dict:
        """Analyze patterns in successful content"""
        patterns = {
            'hooks': {},
            'content_types': {},
            'timing': {},
            'engagement_factors': {}
        }
        
        for data in performance_data:
            if self._calculate_engagement_score(data) > 0.5:  # Successful threshold
                extracted = self._extract_viral_patterns(data)
                
                # Track hooks
                for hook in extracted.get('hooks', []):
                    patterns['hooks'][hook] = patterns['hooks'].get(hook, 0) + 1
                
                # Track content type
                content_type = extracted.get('content_type')
                if content_type:
                    patterns['content_types'][content_type] = patterns['content_types'].get(content_type, 0) + 1
                
                # Track timing
                timing = extracted.get('timing')
                if timing:
                    patterns['timing'][timing] = patterns['timing'].get(timing, 0) + 1
                
                # Track engagement factors
                for factor in extracted.get('engagement_factors', []):
                    patterns['engagement_factors'][factor] = patterns['engagement_factors'].get(factor, 0) + 1
        
        return patterns

    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Content type recommendations
        content_type = analysis_data.get('content_type')
        if content_type in self.content_categories:
            optimal_times = self.content_categories[content_type]['optimal_times']
            recommendations.append(f"Post {content_type} content during optimal hours: {optimal_times}")
        
        # Hook recommendations
        hooks = analysis_data.get('hooks', [])
        if hooks:
            recommendations.append(f"Continue using effective hooks: {', '.join(hooks)}")
        else:
            recommendations.append("Try incorporating viral hooks like threads or alpha insights")
        
        # Engagement recommendations
        engagement_score = analysis_data.get('engagement_score', 0)
        if engagement_score < 0.3:
            recommendations.append("Boost engagement by asking questions and encouraging discussion")
        elif engagement_score < 0.6:
            recommendations.append("Good engagement - try adding more actionable insights")
        else:
            recommendations.append("Strong engagement - maintain this content quality")
        
        return recommendations

    def _identify_optimal_times(self, performance_data: List[Dict]) -> List[Tuple[int, int]]:
        """Identify optimal posting times based on performance data"""
        time_scores = {}
        
        # Analyze performance by hour
        for data in performance_data:
            timestamp = data.get('timestamp')
            if timestamp:
                hour = timestamp.hour
                score = self._calculate_engagement_score(data)
                if hour not in time_scores:
                    time_scores[hour] = []
                time_scores[hour].append(score)
        
        # Find best performing hours
        avg_scores = {}
        for hour, scores in time_scores.items():
            avg_scores[hour] = sum(scores) / len(scores)
        
        # Get top 3 time ranges
        sorted_hours = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        return [(hour, (hour + 2) % 24) for hour, _ in sorted_hours]

    def _analyze_content_types(self, performance_data: List[Dict]) -> Dict:
        """Analyze performance by content type"""
        type_scores = {}
        
        # Calculate scores by type
        for data in performance_data:
            content = data.get('content', '')
            content_type = self._identify_content_type(content)
            score = self._calculate_engagement_score(data)
            
            if content_type not in type_scores:
                type_scores[content_type] = []
            type_scores[content_type].append(score)
        
        # Calculate average scores
        return {
            content_type: sum(scores) / len(scores)
            for content_type, scores in type_scores.items()
        }

    def _generate_strategy_adjustments(self, success_patterns: Dict, optimal_times: List[Tuple[int, int]], content_performance: Dict) -> List[str]:
        """Generate strategy adjustments based on analysis"""
        adjustments = []
        
        # Pattern-based adjustments
        if success_patterns.get('hooks'):
            top_hooks = sorted(success_patterns['hooks'].items(), key=lambda x: x[1], reverse=True)[:2]
            adjustments.append(f"Focus on top hooks: {', '.join(h[0] for h in top_hooks)}")
        
        # Timing adjustments
        if optimal_times:
            times_str = ', '.join([f"{t[0]:02d}:00-{t[1]:02d}:00" for t in optimal_times[:2]])
            adjustments.append(f"Prioritize posting during: {times_str}")
        
        # Content adjustments
        if content_performance:
            top_types = sorted(content_performance.items(), key=lambda x: x[1], reverse=True)[:2]
            adjustments.append(f"Increase {', '.join(t[0] for t in top_types)} content")
        
        return adjustments

    def generate_reply(self, tweet_data: Dict) -> str:
        """Generate a reply to a tweet based on engagement patterns"""
        # Identify content type and sentiment
        content_type = self._identify_content_type(tweet_data.get('content', ''))
        
        # Get relevant interests for this content type
        interests = self.content_categories.get(content_type, {}).get('interests', [])
        
        # Select appropriate reply style based on engagement factors
        engagement_factors = self._identify_engagement_factors(tweet_data)
        
        # Build reply template based on factors
        if 'high_likes' in engagement_factors or 'high_retweets' in engagement_factors:
            template = "Thanks for the engagement! {insight}"
        elif 'thread' in engagement_factors:
            template = "Great thread! Here's another perspective: {insight}"
        elif 'alpha_content' in engagement_factors:
            template = "Interesting alpha! Have you considered {insight}"
        else:
            template = "Thanks for sharing! {insight}"
        
        # Generate insight based on content type
        if content_type == 'alpha':
            insight = "Let's keep tracking this signal."
        elif content_type == 'analysis':
            insight = "Your analysis aligns with recent market patterns."
        elif content_type == 'community':
            insight = "The community's input is valuable here."
        else:
            insight = "Looking forward to more updates."
        
        return template.format(insight=insight)
