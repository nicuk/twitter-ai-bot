"""
Tweet scheduling functionality for Elion
"""

from datetime import datetime
from typing import Dict

class TweetScheduler:
    """Handles tweet scheduling and timing"""
    
    def __init__(self):
        """Initialize tweet scheduler"""
        self.datetime = datetime
        
    def get_next_tweet_type(self) -> str:
        """Get the next tweet type based on timing and distribution rules"""
        current_hour = self.datetime.now().hour
        
        # Portfolio updates every 4 hours (6 times per day)
        if current_hour % 4 == 0:
            return 'portfolio_update'
            
        # Market alpha twice per day (9 AM and 4 PM)
        if current_hour in [9, 16]:
            return 'market_alpha'
            
        # Gem alpha twice per day (11 AM and 6 PM)
        if current_hour in [11, 18]:
            return 'gem_alpha'
            
        # Shill review once per day (2 PM)
        if current_hour == 14:
            return 'shill_review'
            
        # Default to market awareness for other hours
        return 'market_aware'
