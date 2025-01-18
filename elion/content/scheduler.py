"""
Tweet scheduler for different content types
"""

from typing import List, Dict
from datetime import datetime, timedelta
import random

class TweetScheduler:
    """Schedules different types of tweets"""
    
    def __init__(self, limited_mode: bool = False):
        """Initialize scheduler"""
        self.limited_mode = limited_mode
        self.last_tweet_time = {}
        
        # Define tweet types and their frequencies (in hours)
        self.tweet_frequencies = {
            # Regular tweets
            'market_analysis': 4,
            'portfolio_update': 12,
            'gem_alpha': 6,
            'shill_review': 8,
            # Special tweets
            'self_aware_thought': 3,
            'controversial_thread': 6,
            'giveaway': 24,
            'technical_analysis': 8,
            'breaking_alpha': 12,
            'whale_alert': 4
        }
        
        # Define priorities for limited mode
        self.limited_mode_priorities = [
            'self_aware_thought',
            'controversial_thread',
            'giveaway'
        ]
        
    def get_next_tweet_type(self) -> str:
        """Get the next tweet type to post"""
        current_time = datetime.utcnow()
        
        # Get eligible tweet types
        eligible_types = []
        
        # In limited mode, only consider priority tweet types
        tweet_types = (
            self.limited_mode_priorities if self.limited_mode 
            else self.tweet_frequencies.keys()
        )
        
        for tweet_type in tweet_types:
            last_time = self.last_tweet_time.get(tweet_type, datetime.min)
            frequency = self.tweet_frequencies[tweet_type]
            if current_time - last_time > timedelta(hours=frequency):
                eligible_types.append(tweet_type)
                
        if not eligible_types:
            return 'self_aware_thought'  # Default to self-aware if nothing else
            
        # Prioritize self-aware thoughts and engagement
        if self.limited_mode:
            priorities = {
                'self_aware_thought': 0.5,
                'controversial_thread': 0.3,
                'giveaway': 0.2
            }
            
            # Use weighted random selection
            total = sum(priorities.get(t, 0) for t in eligible_types)
            r = random.random() * total
            
            for tweet_type in eligible_types:
                r -= priorities.get(tweet_type, 0)
                if r <= 0:
                    return tweet_type
                    
            return eligible_types[0]  # Fallback
            
        # Normal mode - random selection
        return random.choice(eligible_types)
        
    def update_last_tweet_time(self, tweet_type: str):
        """Update the last tweet time for a type"""
        self.last_tweet_time[tweet_type] = datetime.utcnow()
        
    def get_tweet_schedule(self) -> List[Dict]:
        """Get the current tweet schedule"""
        current_time = datetime.utcnow()
        schedule = []
        
        tweet_types = (
            self.limited_mode_priorities if self.limited_mode 
            else self.tweet_frequencies.keys()
        )
        
        for tweet_type in tweet_types:
            last_time = self.last_tweet_time.get(tweet_type, datetime.min)
            frequency = self.tweet_frequencies[tweet_type]
            next_time = last_time + timedelta(hours=frequency)
            
            schedule.append({
                'type': tweet_type,
                'last_posted': last_time,
                'next_scheduled': next_time,
                'frequency': frequency
            })
            
        return sorted(schedule, key=lambda x: x['next_scheduled'])
