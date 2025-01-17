"""
Viral patterns and content optimization
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ViralPatterns:
    """Analyzes and optimizes for viral patterns"""
    
    def __init__(self):
        """Initialize viral patterns"""
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
        
        self.viral_hooks = {
            'controversy': "Present a contrarian but well-supported view",
            'prediction': "Make a bold but calculated prediction",
            'insight': "Share unique perspective on common topic",
            'alpha': "Provide actionable trading insight",
            'thread': "Start an engaging thread with clear value",
            'poll': "Ask engaging community question"
        }
        
        self.viral_triggers = {
            'market_movement': 0.8,    # High chance during big moves
            'trending_topic': 0.7,     # Good with trending topics
            'breaking_news': 0.9,      # Excellent for breaking news
            'community_event': 0.6     # Good for community events
        }
        
    def analyze_patterns(self, tweet_data: Dict) -> Dict:
        """Analyze viral patterns in tweet"""
        try:
            tweet_text = tweet_data.get('text', '').lower()
            metrics = tweet_data.get('public_metrics', {})
            
            # Identify content category
            category = self.get_optimal_category(tweet_text)
            
            # Check for viral hooks
            hooks_used = self._identify_hooks(tweet_text)
            
            # Check for viral triggers
            triggers_present = self._identify_triggers(tweet_text)
            
            # Calculate viral potential
            viral_potential = self._calculate_viral_potential(
                category,
                hooks_used,
                triggers_present,
                metrics
            )
            
            return {
                'category': category,
                'hooks_used': hooks_used,
                'triggers_present': triggers_present,
                'viral_potential': viral_potential
            }
            
        except Exception as e:
            print(f"Error analyzing patterns: {e}")
            return {}
            
    def get_optimal_category(self, text: str) -> str:
        """Get optimal content category for text"""
        text = text.lower()
        
        if any(word in text for word in ['alpha', 'gem', 'opportunity']):
            return 'alpha'
        elif any(word in text for word in ['analysis', 'chart', 'pattern']):
            return 'analysis'
        elif any(word in text for word in ['learn', 'guide', 'how to']):
            return 'education'
        else:
            return 'community'
            
    def _identify_hooks(self, text: str) -> List[str]:
        """Identify viral hooks used in text"""
        hooks = []
        text = text.lower()
        
        if 'but' in text or 'however' in text:
            hooks.append('controversy')
        if 'will' in text or 'predict' in text:
            hooks.append('prediction')
        if 'thread' in text or '🧵' in text:
            hooks.append('thread')
        if 'poll' in text:
            hooks.append('poll')
            
        return hooks
        
    def _identify_triggers(self, text: str) -> List[str]:
        """Identify viral triggers in text"""
        triggers = []
        text = text.lower()
        
        if any(word in text for word in ['crash', 'pump', 'dump']):
            triggers.append('market_movement')
        if any(word in text for word in ['breaking', 'alert', 'just in']):
            triggers.append('breaking_news')
        if any(word in text for word in ['trending', 'viral']):
            triggers.append('trending_topic')
            
        return triggers
        
    def _calculate_viral_potential(
        self,
        category: str,
        hooks: List[str],
        triggers: List[str],
        metrics: Dict
    ) -> float:
        """Calculate viral potential score"""
        score = self.content_categories[category]['viral_potential']
        
        # Add hook bonuses
        score += len(hooks) * 0.1
        
        # Add trigger bonuses
        for trigger in triggers:
            score += self.viral_triggers.get(trigger, 0)
            
        # Cap at 1.0
        return min(score, 1.0)
