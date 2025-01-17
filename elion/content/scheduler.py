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
            'market_analysis': 0.1,   # 5 posts
            'market_search': 0.1,     # 5 posts
            'gem_alpha': 0.2,         # 10 posts
            'shill_review': 0.2,      # 10 posts
            'market_aware': 0.2       # 10 posts
        }
        self.type_counts = {
            'portfolio_update': 0,
            'market_analysis': 0,
            'market_search': 0,
            'gem_alpha': 0,
            'shill_review': 0,
            'market_aware': 0
        }
        self.failed_types = set()  # Track failed tweet types
        
    def _reset_cycle(self):
        """Reset cycle counts"""
        self.cycle_count = 0
        self.type_counts = {k: 0 for k in self.type_counts}
        self.failed_types.clear()
        
    def get_next_tweet_type(self) -> str:
        """Get the next tweet type based on timing and distribution rules"""
        current_hour = self.datetime.now().hour
        
        # Reset cycle if completed
        if self.cycle_count >= self.total_cycles:
            self._reset_cycle()
        
        # Don't try failed types again in same cycle
        available_types = {
            t: r for t, r in self.type_distribution.items()
            if t not in self.failed_types
        }
        
        if not available_types:
            self._reset_cycle()
            available_types = self.type_distribution
        
        # Adjust for time of day
        if 0 <= current_hour < 6:  # Night hours
            available_types = {
                t: r * 0.5 for t, r in available_types.items()
                if t not in ['market_analysis', 'portfolio_update']
            }
        elif 14 <= current_hour < 20:  # Peak hours
            available_types = {
                t: r * 1.5 for t, r in available_types.items()
                if t in ['market_analysis', 'gem_alpha']
            }
        
        # Calculate remaining posts
        remaining = {
            t: int(self.total_cycles * r) - self.type_counts[t]
            for t, r in available_types.items()
        }
        
        # Filter out completed types
        remaining = {t: r for t, r in remaining.items() if r > 0}
        
        if not remaining:
            return None
        
        # Select type weighted by remaining posts
        total = sum(remaining.values())
        weights = [r/total for r in remaining.values()]
        tweet_type = random.choices(list(remaining.keys()), weights=weights)[0]
        
        # Update counts
        self.type_counts[tweet_type] += 1
        self.cycle_count += 1
        
        return tweet_type
        
    def handle_failed_tweet(self, tweet_type: str):
        """Handle a failed tweet attempt"""
        self.failed_types.add(tweet_type)
        
        # If too many failures, adjust distribution
        if len(self.failed_types) > len(self.type_distribution) / 2:
            self._adjust_distribution()

    def _adjust_distribution(self):
        """Adjust type distribution based on failures"""
        working_types = set(self.type_distribution.keys()) - self.failed_types
        if not working_types:
            return
        
        # Redistribute failed type percentages
        failed_total = sum(self.type_distribution[t] for t in self.failed_types)
        boost = failed_total / len(working_types)
        
        for t in working_types:
            self.type_distribution[t] += boost

    def get_cycle_progress(self) -> Dict:
        """Get current cycle progress"""
        return {
            'cycle_count': self.cycle_count,
            'total_cycles': self.total_cycles,
            'type_counts': self.type_counts,
            'remaining_posts': {
                tweet_type: int(self.total_cycles * ratio) - self.type_counts[tweet_type]
                for tweet_type, ratio in self.type_distribution.items()
            },
            'failed_types': list(self.failed_types)
        }
