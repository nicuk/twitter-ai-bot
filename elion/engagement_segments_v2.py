"""
Community segmentation and targeting
"""

from datetime import datetime
from typing import Dict, List, Optional

class CommunitySegments:
    """Manages community segments and targeting"""
    
    def __init__(self):
        """Initialize community segments"""
        self.segments = {
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
        
        self.user_segments = {}  # Track user segment data
        
    def update_segments(self, tweet_data: Dict) -> Dict:
        """Update segment data based on tweet"""
        try:
            user_id = tweet_data.get('author_id')
            if not user_id:
                return {}
                
            tweet_text = tweet_data.get('text', '').lower()
            
            # Identify likely segment
            segment = self._identify_segment(tweet_text)
            
            # Update user segment data
            if user_id not in self.user_segments:
                self.user_segments[user_id] = {
                    'segment': segment,
                    'confidence': 0.6,  # Initial confidence
                    'interests': [],
                    'engagement_times': []
                }
            else:
                # Update confidence if same segment
                if self.user_segments[user_id]['segment'] == segment:
                    self.user_segments[user_id]['confidence'] = min(
                        self.user_segments[user_id]['confidence'] + 0.1,
                        1.0
                    )
                else:
                    # Decrease confidence if different segment
                    self.user_segments[user_id]['confidence'] *= 0.9
                    
                    # Switch segment if confidence low
                    if self.user_segments[user_id]['confidence'] < 0.4:
                        self.user_segments[user_id]['segment'] = segment
                        self.user_segments[user_id]['confidence'] = 0.6
            
            # Update engagement time
            if tweet_data.get('created_at'):
                hour = datetime.fromisoformat(tweet_data['created_at']).hour
                self.user_segments[user_id]['engagement_times'].append(hour)
                # Keep only last 10 times
                self.user_segments[user_id]['engagement_times'] = self.user_segments[user_id]['engagement_times'][-10:]
            
            return self.user_segments[user_id]
            
        except Exception as e:
            print(f"Error updating segments: {e}")
            return {}
            
    def get_user_segment(self, context: Dict) -> Optional[str]:
        """Get user's segment from context"""
        try:
            user_id = context.get('author_id')
            if not user_id or user_id not in self.user_segments:
                # Try to identify from tweet text
                tweet_text = context.get('tweet_text', '')
                return self._identify_segment(tweet_text)
                
            return self.user_segments[user_id]['segment']
            
        except Exception as e:
            print(f"Error getting user segment: {e}")
            return None
            
    def _identify_segment(self, text: str) -> str:
        """Identify likely segment from text"""
        text = text.lower()
        
        # Count matches for each segment
        matches = {
            segment: sum(1 for interest in info['interests'] if interest in text)
            for segment, info in self.segments.items()
        }
        
        # Return segment with most matches
        return max(matches.items(), key=lambda x: x[1])[0]
        
    def get_segment_preferences(self, segment: str) -> Dict:
        """Get content preferences for segment"""
        return self.segments.get(segment, self.segments['newcomers'])
