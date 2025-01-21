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
        self.initial_tweets_count = 0  # Track number of initial tweets
        self.initial_tweets_max = 5    # Number of initial self-aware tweets
        
        # Tweet type distribution
        self.type_distribution = {
            # Alpha Generation (75%)
            'gem_alpha': 0.40,         # 20 posts - Main focus on finding gems
            'breaking_alpha': 0.25,    # 12-13 posts - AI project alerts & big market moves
            'shill_review': 0.10,      # 5 posts - Only strong quantitative signals
            
            # Portfolio & Performance (15%)
            'portfolio_update': 0.15,  # 7-8 posts - Show our success
            
            # Basic Engagement (10%)
            'self_aware': 0.10,        # 5 posts - Personality tweets
        }
        
        # Define non-market-data tweet types
        self.non_market_types = {
            'self_aware': 0.3,
            'self_aware_thought': 0.3,
            'controversial_thread': 0.2,
            'giveaway': 0.2
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
        
        # For the first few tweets, prioritize non-market-data tweets
        if self.initial_tweets_count < self.initial_tweets_max:
            self.initial_tweets_count += 1
            # Use non-market distribution for initial tweets
            r = random.random()
            cumsum = 0
            for t, p in self.non_market_types.items():
                cumsum += p
                if r <= cumsum:
                    self.type_counts[t] += 1
                    self.cycle_count += 1
                    return t
            # Fallback to first non-market type
            t = next(iter(self.non_market_types))
            self.type_counts[t] += 1
            self.cycle_count += 1
            return t
        
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
