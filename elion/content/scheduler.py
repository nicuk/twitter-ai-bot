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
        
        # Regular Scheduled Posts (50% of tweets)
        self.type_distribution = {
            # Regular Scheduled Posts (50%)
            'portfolio_update': 0.1,   # 5 posts
            'market_analysis': 0.05,   # 2-3 posts
            'market_search': 0.05,     # 2-3 posts
            'gem_alpha': 0.1,          # 5 posts
            'shill_review': 0.1,       # 5 posts
            'market_aware': 0.1,       # 5 posts
            
            # Special Event Posts (30%)
            'breaking_alpha': 0.05,    # 2-3 posts
            'whale_alert': 0.05,       # 2-3 posts
            'technical_analysis': 0.05, # 2-3 posts
            'controversial_thread': 0.05, # 2-3 posts
            'giveaway': 0.025,         # 1-2 posts
            'self_aware': 0.025,       # 1-2 posts
            'ai_market_analysis': 0.05, # 2-3 posts
            'self_aware_thought': 0.025, # 1-2 posts
            
            # Reactive Posts (20%)
            'market_response': 0.05,    # 2-3 posts
            'engagement_reply': 0.05,   # 2-3 posts
            'alpha_call': 0.05,        # 2-3 posts
            'technical_alpha': 0.05     # 2-3 posts
        }
        
        self.type_counts = {t: 0 for t in self.type_distribution}
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
            
        # Normalize probabilities
        total_prob = sum(available_types.values())
        normalized_types = {
            t: r/total_prob for t, r in available_types.items()
        }
        
        # Select type based on distribution
        r = random.random()
        cumsum = 0
        for t, p in normalized_types.items():
            cumsum += p
            if r <= cumsum:
                self.type_counts[t] += 1
                self.cycle_count += 1
                return t
                
        # Fallback to first available type
        t = next(iter(available_types))
        self.type_counts[t] += 1
        self.cycle_count += 1
        return t
        
    def boost_working_types(self):
        """Boost probability of working tweet types"""
        if not self.failed_types:
            return
            
        # Calculate boost amount
        failed_total = sum(self.type_distribution[t] for t in self.failed_types)
        working_types = [t for t in self.type_distribution if t not in self.failed_types]
        boost = failed_total / len(working_types)
        
        # Apply boost to working types
        for t in working_types:
            self.type_distribution[t] += boost

    def mark_type_failed(self, tweet_type: str):
        """Mark a tweet type as failed for this cycle"""
        self.failed_types.add(tweet_type)
        # Adjust distribution for remaining types
        remaining_types = {t: r for t, r in self.type_distribution.items() 
                         if t not in self.failed_types}
        if remaining_types:
            # Redistribute failed type's probability
            failed_prob = self.type_distribution[tweet_type]
            boost = failed_prob / len(remaining_types)
            for t in remaining_types:
                self.type_distribution[t] += boost

    def get_cycle_progress(self) -> Dict:
        """Get current cycle progress"""
        return {
            'cycle_count': self.cycle_count,
            'total_cycles': self.total_cycles,
            'type_counts': self.type_counts,
            'failed_types': list(self.failed_types)
        }
