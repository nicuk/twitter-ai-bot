"""
Tweet scheduling functionality for Elion
"""

from datetime import datetime
from typing import Dict
import random

class TweetScheduler:
    """Handles tweet scheduling and timing"""
    
    def __init__(self):
        """Initialize tweet scheduler"""
        self.datetime = datetime
        self.cycle_count = 0
        self.total_cycles = 50
        self.type_distribution = {
            'portfolio_update': 0.2,  # 10 posts
            'market_alpha': 0.2,      # 10 posts
            'gem_alpha': 0.2,         # 10 posts
            'shill_review': 0.2,      # 10 posts
            'market_aware': 0.2       # 10 posts
        }
        self.type_counts = {
            'portfolio_update': 0,
            'market_alpha': 0,
            'gem_alpha': 0,
            'shill_review': 0,
            'market_aware': 0
        }
        
    def _reset_cycle(self):
        """Reset cycle counts"""
        self.cycle_count = 0
        self.type_counts = {k: 0 for k in self.type_counts}
        
    def get_next_tweet_type(self) -> str:
        """Get the next tweet type based on timing and distribution rules"""
        current_hour = self.datetime.now().hour
        
        # Reset cycle if completed
        if self.cycle_count >= self.total_cycles:
            self._reset_cycle()
            
        # Calculate remaining posts needed for each type
        remaining_posts = {
            tweet_type: int(self.total_cycles * ratio) - self.type_counts[tweet_type]
            for tweet_type, ratio in self.type_distribution.items()
        }
        
        # Filter out completed types
        available_types = [t for t, r in remaining_posts.items() if r > 0]
        
        if not available_types:
            self._reset_cycle()
            return self.get_next_tweet_type()
            
        # Prioritize based on time of day if possible
        priority_type = None
        
        # Portfolio updates every 4 hours
        if current_hour % 4 == 0 and 'portfolio_update' in available_types:
            priority_type = 'portfolio_update'
            
        # Market alpha at 9 AM and 4 PM
        elif current_hour in [9, 16] and 'market_alpha' in available_types:
            priority_type = 'market_alpha'
            
        # Gem alpha at 11 AM and 6 PM
        elif current_hour in [11, 18] and 'gem_alpha' in available_types:
            priority_type = 'gem_alpha'
            
        # Shill review at 2 PM
        elif current_hour == 14 and 'shill_review' in available_types:
            priority_type = 'shill_review'
            
        # Use priority type if available and timing is right
        if priority_type and priority_type in available_types:
            tweet_type = priority_type
        else:
            # Otherwise, randomly select from available types
            # Weight by remaining posts needed
            weights = [remaining_posts[t] for t in available_types]
            tweet_type = random.choices(available_types, weights=weights, k=1)[0]
            
        # Update counts
        self.type_counts[tweet_type] += 1
        self.cycle_count += 1
        
        return tweet_type
        
    def get_cycle_progress(self) -> Dict:
        """Get current cycle progress"""
        return {
            'cycle_count': self.cycle_count,
            'total_cycles': self.total_cycles,
            'type_counts': self.type_counts,
            'remaining_posts': {
                tweet_type: int(self.total_cycles * ratio) - self.type_counts[tweet_type]
                for tweet_type, ratio in self.type_distribution.items()
            }
        }
