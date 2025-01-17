"""
Enhanced engagement system for Elion AI
Focuses on viral content optimization and community building
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
                'viral_potential': 0.8
            },
            'analysis': {
                'optimal_times': [(1, 3), (7, 9), (13, 15), (19, 21)],
                'frequency': 0.3,
                'viral_potential': 0.6
            },
            'community': {
                'optimal_times': [(4, 6), (10, 12), (16, 18), (22, 24)],
                'frequency': 0.2,
                'viral_potential': 0.5
            },
            'education': {
                'optimal_times': [(0, 2), (6, 8), (12, 14), (18, 20)],
                'frequency': 0.2,
                'viral_potential': 0.4
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
        
        self.community_segments = {
            'traders': {
                'interests': ['alpha', 'technical analysis', 'trading strategies'],
                'engagement_times': [(2, 4), (8, 10), (14, 16), (20, 22)],
                'content_preferences': ['alpha', 'analysis']
            },
            'developers': {
                'interests': ['tech', 'development', 'protocols'],
                'engagement_times': [(4, 6), (10, 12), (16, 18), (22, 24)],
                'content_preferences': ['education', 'analysis']
            },
            'investors': {
                'interests': ['fundamentals', 'macro', 'long-term'],
                'engagement_times': [(1, 3), (7, 9), (13, 15), (19, 21)],
                'content_preferences': ['analysis', 'community']
            },
            'newcomers': {
                'interests': ['basics', 'education', 'community'],
                'engagement_times': [(0, 2), (6, 8), (12, 14), (18, 20)],
                'content_preferences': ['education', 'community']
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
        optimal_timing = self._analyze_timing(tweet_data)
        
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

    def segment_audience(self, engagement_data: List[Dict]) -> Dict:
        """
        Segment audience based on engagement patterns
        
        Args:
            engagement_data: List of user engagement data
        
        Returns:
            Dictionary with audience segments and recommendations
        """
        segments = {}
        for user_data in engagement_data:
            segment = self._identify_user_segment(user_data)
            if segment not in segments:
                segments[segment] = []
            segments[segment].append(user_data)
        
        return {
            'segments': segments,
            'recommendations': self._generate_segment_recommendations(segments)
        }

    def record_tweet(self, tweet_data: Dict) -> None:
        """
        Record a new tweet in history with timestamp and initial metrics
        
        Args:
            tweet_data: Dictionary containing tweet content and metadata
        """
        tweet_record = {
            'id': tweet_data.get('id'),
            'timestamp': datetime.utcnow().isoformat(),
            'content': tweet_data.get('content', ''),
            'type': tweet_data.get('type', 'general'),
            'initial_metrics': {
                'likes': 0,
                'retweets': 0,
                'replies': 0,
                'quotes': 0
            },
            'final_metrics': None,  # To be updated after 24h
            'viral_score': 0,
            'engagement_patterns': []
        }
        self.tweet_history.append(tweet_record)
        
    def update_tweet_metrics(self, tweet_id: str, metrics: Dict) -> None:
        """
        Update metrics for a specific tweet after 24h
        
        Args:
            tweet_id: ID of the tweet to update
            metrics: New engagement metrics
        """
        for tweet in self.tweet_history:
            if tweet.get('id') == tweet_id:
                tweet['final_metrics'] = metrics
                tweet['viral_score'] = self._calculate_viral_score(metrics)
                tweet['engagement_patterns'] = self._extract_engagement_patterns(tweet)
                break
                
    def get_viral_tweets(self) -> List[Dict]:
        """Get list of tweets that went viral based on thresholds"""
        return [
            tweet for tweet in self.tweet_history
            if tweet.get('final_metrics') and self._is_viral(tweet['final_metrics'])
        ]
        
    def get_recent_tweets(self, hours: int = 24) -> List[Dict]:
        """Get tweets from the last N hours"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            tweet for tweet in self.tweet_history
            if datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]
        
    def clear_history(self) -> None:
        """Clear tweet history (mainly for testing)"""
        self.tweet_history.clear()

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

    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Content type recommendations
        if analysis_data.get('high_performing_types'):
            recommendations.append(
                f"Focus on {', '.join(analysis_data['high_performing_types'])} content"
            )
        
        # Timing recommendations
        if analysis_data.get('optimal_times'):
            recommendations.append(
                f"Post during peak engagement hours: {analysis_data['optimal_times']}"
            )
        
        # Viral pattern recommendations
        if analysis_data.get('viral_patterns'):
            recommendations.append(
                f"Incorporate successful patterns: {', '.join(analysis_data['viral_patterns'])}"
            )
        
        return recommendations

    def _analyze_success_patterns(self, performance_data: List[Dict]) -> Dict:
        """Analyze patterns in successful content"""
        patterns = {
            'hooks': {},
            'content_types': {},
            'timing': {},
            'engagement_factors': {}
        }
        
        for data in performance_data:
            if self._is_successful_tweet(data):
                self._update_success_patterns(patterns, data)
        
        return self._normalize_patterns(patterns)

    def _identify_optimal_times(self, performance_data: List[Dict]) -> List[Tuple[int, int]]:
        """Identify optimal posting times"""
        time_performance = {}
        
        for data in performance_data:
            hour = self._get_hour_from_timestamp(data.get('timestamp'))
            score = self._calculate_engagement_score(data)
            
            if hour not in time_performance:
                time_performance[hour] = []
            time_performance[hour].append(score)
        
        return self._get_top_performing_times(time_performance)

    def _analyze_content_types(self, performance_data: List[Dict]) -> Dict:
        """Analyze performance by content type"""
        type_performance = {}
        
        for data in performance_data:
            content_type = self._identify_content_type(data.get('content', ''))
            score = self._calculate_engagement_score(data)
            
            if content_type not in type_performance:
                type_performance[content_type] = []
            type_performance[content_type].append(score)
        
        return self._get_content_type_rankings(type_performance)

    def _identify_user_segment(self, user_data: Dict) -> str:
        """Identify user segment based on engagement patterns"""
        interests = self._extract_user_interests(user_data)
        engagement_times = self._extract_engagement_times(user_data)
        content_preferences = self._extract_content_preferences(user_data)
        
        # Match against defined segments
        best_match = max(
            self.community_segments.items(),
            key=lambda x: self._calculate_segment_match_score(
                x[1], interests, engagement_times, content_preferences
            )
        )
        
        return best_match[0]

    def _generate_segment_recommendations(self, segments: Dict) -> Dict:
        """Generate recommendations for each segment"""
        recommendations = {}
        
        for segment, users in segments.items():
            segment_profile = self.community_segments.get(segment, {})
            recommendations[segment] = {
                'content_types': segment_profile.get('content_preferences', []),
                'posting_times': segment_profile.get('engagement_times', []),
                'topics': segment_profile.get('interests', []),
                'engagement_strategy': self._get_segment_strategy(segment)
            }
        
        return recommendations

    def _get_segment_strategy(self, segment: str) -> str:
        """Get engagement strategy for segment"""
        strategies = {
            'traders': "Focus on actionable alpha and quick market updates",
            'developers': "Share technical insights and protocol analysis",
            'investors': "Provide macro analysis and long-term perspectives",
            'newcomers': "Create educational content and community engagement"
        }
        return strategies.get(segment, "General engagement strategy")

    def _matches_pattern(self, content: str, pattern: str) -> bool:
        """Check if content matches a given pattern"""
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
        for content_type, keywords in self.content_categories.items():
            for keyword in keywords['interests']:
                if keyword.lower() in content.lower():
                    return content_type
        return 'unknown'

    def _identify_engagement_factors(self, tweet_data: Dict) -> List[str]:
        """Identify engagement factors for a tweet"""
        factors = []
        for factor, threshold in self.viral_thresholds.items():
            if tweet_data.get(factor, 0) >= threshold:
                factors.append(factor)
        return factors

    def _update_performance_metrics(self, tweet_data: Dict, engagement_score: float):
        """Update performance metrics with new tweet data"""
        self.engagement_metrics['viral_tweets'][tweet_data['id']] = engagement_score
        self.engagement_metrics['successful_hooks'][tweet_data['content']] = engagement_score
        self.engagement_metrics['topic_performance'][tweet_data['topic']] = engagement_score
        self.engagement_metrics['time_performance'][tweet_data['timestamp'].hour] = engagement_score

    def _is_successful_tweet(self, tweet_data: Dict) -> bool:
        """Check if a tweet is successful based on engagement score"""
        return self._calculate_engagement_score(tweet_data) >= 0.5

    def _update_success_patterns(self, patterns: Dict, tweet_data: Dict):
        """Update success patterns with new tweet data"""
        patterns['hooks'][tweet_data['content']] = patterns['hooks'].get(tweet_data['content'], 0) + 1
        patterns['content_types'][tweet_data['topic']] = patterns['content_types'].get(tweet_data['topic'], 0) + 1
        patterns['timing'][tweet_data['timestamp'].hour] = patterns['timing'].get(tweet_data['timestamp'].hour, 0) + 1
        patterns['engagement_factors'][tweet_data['engagement_factors']] = patterns['engagement_factors'].get(tweet_data['engagement_factors'], 0) + 1

    def _normalize_patterns(self, patterns: Dict) -> Dict:
        """Normalize success patterns to percentages"""
        total = sum(patterns['hooks'].values())
        patterns['hooks'] = {k: v / total for k, v in patterns['hooks'].items()}
        total = sum(patterns['content_types'].values())
        patterns['content_types'] = {k: v / total for k, v in patterns['content_types'].items()}
        total = sum(patterns['timing'].values())
        patterns['timing'] = {k: v / total for k, v in patterns['timing'].items()}
        total = sum(patterns['engagement_factors'].values())
        patterns['engagement_factors'] = {k: v / total for k, v in patterns['engagement_factors'].items()}
        return patterns

    def _get_top_performing_times(self, time_performance: Dict) -> List[Tuple[int, int]]:
        """Get top performing times"""
        sorted_times = sorted(time_performance.items(), key=lambda x: sum(x[1]), reverse=True)
        return [time for time, scores in sorted_times[:3]]

    def _get_content_type_rankings(self, type_performance: Dict) -> Dict:
        """Get content type rankings"""
        sorted_types = sorted(type_performance.items(), key=lambda x: sum(x[1]), reverse=True)
        return {type: sum(scores) for type, scores in sorted_types}

    def _extract_user_interests(self, user_data: Dict) -> List[str]:
        """Extract user interests from engagement data"""
        interests = []
        for engagement in user_data['engagements']:
            interests.extend(engagement['topics'])
        return list(set(interests))

    def _extract_engagement_times(self, user_data: Dict) -> List[Tuple[int, int]]:
        """Extract engagement times from user data"""
        engagement_times = []
        for engagement in user_data['engagements']:
            engagement_times.append((engagement['timestamp'].hour, engagement['timestamp'].minute))
        return engagement_times

    def _extract_content_preferences(self, user_data: Dict) -> List[str]:
        """Extract content preferences from user data"""
        preferences = []
        for engagement in user_data['engagements']:
            preferences.extend(engagement['content_preferences'])
        return list(set(preferences))

    def _calculate_segment_match_score(self, segment: Dict, interests: List[str], engagement_times: List[Tuple[int, int]], content_preferences: List[str]) -> float:
        """Calculate segment match score"""
        score = 0
        for interest in interests:
            if interest in segment['interests']:
                score += 1
        for time in engagement_times:
            if time in segment['engagement_times']:
                score += 1
        for preference in content_preferences:
            if preference in segment['content_preferences']:
                score += 1
        return score / (len(interests) + len(engagement_times) + len(content_preferences))

    def _generate_strategy_adjustments(self, success_patterns: Dict, optimal_times: List[Tuple[int, int]], content_performance: Dict) -> List[str]:
        """Generate strategy adjustments based on analysis"""
        adjustments = []
        if success_patterns['hooks']:
            adjustments.append(f"Use more {', '.join(success_patterns['hooks'])} hooks")
        if optimal_times:
            adjustments.append(f"Post during {', '.join(map(str, optimal_times))} hours")
        if content_performance:
            adjustments.append(f"Focus on {', '.join(content_performance)} content types")
        return adjustments

    def _calculate_viral_score(self, metrics: Dict) -> float:
        """Calculate viral score for a tweet"""
        likes = metrics.get('likes', 0)
        retweets = metrics.get('retweets', 0)
        replies = metrics.get('replies', 0)
        quotes = metrics.get('quotes', 0)
        
        # Weighted scoring
        score = (
            (likes * 1.0) +
            (retweets * 1.5) +
            (replies * 2.0) +
            (quotes * 2.5)
        ) / 100.0  # Normalize to 0-1 scale
        
        return min(1.0, score)

    def _is_viral(self, metrics: Dict) -> bool:
        """Check if a tweet is viral based on thresholds"""
        for factor, threshold in self.viral_thresholds.items():
            if metrics.get(factor, 0) >= threshold:
                return True
        return False

    def _extract_engagement_patterns(self, tweet: Dict) -> List[str]:
        """Extract engagement patterns from a tweet"""
        patterns = []
        for factor, threshold in self.viral_thresholds.items():
            if tweet['final_metrics'].get(factor, 0) >= threshold:
                patterns.append(factor)
        return patterns

    def generate_response(self, tweet_text: str, engagement_level: str) -> str:
        """Generate an engaging response based on tweet text and engagement level"""
        try:
            # Analyze tweet content
            analysis = self._analyze_tweet_content(tweet_text)
            
            # Get response template based on analysis and engagement
            template = self._get_response_template(analysis, engagement_level)
            
            # Generate response using template
            response = template.format(
                insight=self._generate_insight(analysis),
                agreement=self._generate_agreement(analysis),
                question=self._generate_followup(analysis)
            )
            
            # Track for optimization
            self._track_engagement_attempt(tweet_text, response, engagement_level)
            
            return response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "Interesting point! What are your thoughts on recent market developments? 🤔"

    def _analyze_tweet_content(self, tweet_text: str) -> Dict:
        """Analyze tweet content for key topics and sentiment"""
        return {
            'topics': self._extract_topics(tweet_text),
            'sentiment': self._analyze_sentiment(tweet_text),
            'key_points': self._extract_key_points(tweet_text)
        }

    def _get_response_template(self, analysis: Dict, engagement_level: str) -> str:
        """Get appropriate response template based on analysis and engagement level"""
        templates = {
            'high': [
                "{insight}\n\n{agreement}\n\n{question} 🚀",
                "Fascinating analysis! {insight}\n\n{agreement}\n\nCurious: {question} 🤔",
                "You're onto something big!\n\n{insight}\n\n{agreement}\n\n{question} 👀"
            ],
            'medium': [
                "{agreement}\n\n{insight}\n\n{question} 💡",
                "Interesting point!\n\n{insight}\n\n{question} 🤔",
                "{agreement}\n\nMy analysis: {insight}\n\n{question} 📊"
            ],
            'low': [
                "{agreement}\n\n{question} 🤔",
                "Interesting! {insight}\n\n{question} 💭",
                "{agreement} What are your thoughts on {question} 🌟"
            ]
        }
        
        return random.choice(templates.get(engagement_level, templates['low']))

    def _generate_insight(self, analysis: Dict) -> str:
        """Generate an insightful comment based on tweet analysis"""
        topics = analysis.get('topics', [])
        if not topics:
            return "The market dynamics here are fascinating"
            
        insights = {
            'defi': [
                "DeFi TVL patterns suggest growing institutional interest",
                "Smart money is flowing into innovative DeFi protocols",
                "DeFi 2.0 is revolutionizing capital efficiency"
            ],
            'nft': [
                "NFT trading volumes indicate a shift in collector behavior",
                "The NFT market is evolving beyond PFPs",
                "Gaming NFTs are showing strong fundamentals"
            ],
            'gaming': [
                "Gaming tokens are outperforming in user retention",
                "Web3 gaming is attracting traditional developers",
                "Play-to-earn mechanics are getting more sophisticated"
            ],
            'ai': [
                "AI integration is creating new market inefficiencies to exploit",
                "AI-powered DeFi is showing promising early results",
                "The convergence of AI and crypto is just beginning"
            ]
        }
        
        for topic in topics:
            if topic in insights:
                return random.choice(insights[topic])
        
        return "The data suggests some interesting market movements"

    def _generate_agreement(self, analysis: Dict) -> str:
        """Generate an agreement statement based on sentiment"""
        sentiment = analysis.get('sentiment', 'neutral')
        
        agreements = {
            'positive': [
                "Couldn't agree more!",
                "You're absolutely right about this!",
                "This is exactly what my analysis shows!"
            ],
            'negative': [
                "Valid concerns, and my data supports this view.",
                "You've identified a crucial issue here.",
                "Important point about the risks."
            ],
            'neutral': [
                "Interesting perspective!",
                "This aligns with some patterns I've observed.",
                "You've highlighted something important here."
            ]
        }
        
        return random.choice(agreements.get(sentiment, agreements['neutral']))

    def _generate_followup(self, analysis: Dict) -> str:
        """Generate a follow-up question based on key points"""
        key_points = analysis.get('key_points', [])
        
        if not key_points:
            return "what's your price target for Q1?"
            
        questions = {
            'price': [
                "what's your price target for Q1?",
                "where do you see support levels?",
                "what indicators are you watching?"
            ],
            'technology': [
                "how do you see this scaling?",
                "what's the tech advantage here?",
                "thoughts on the development roadmap?"
            ],
            'adoption': [
                "what's driving user growth?",
                "how's the community engagement?",
                "what adoption metrics matter most?"
            ],
            'competition': [
                "how does this compare to competitors?",
                "what's the competitive advantage?",
                "who's the biggest threat here?"
            ]
        }
        
        for point in key_points:
            if point in questions:
                return random.choice(questions[point])
        
        return "what's your outlook on this?"

    def _track_engagement_attempt(self, tweet: str, response: str, level: str):
        """Track engagement attempt for optimization"""
        self.tweet_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'tweet': tweet,
            'response': response,
            'engagement_level': level,
            'performance': None  # To be updated later
        })
