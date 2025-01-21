"""Rate limiting for Twitter API"""

from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        """Initialize rate limiter"""
        self.rate_limits = {
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'daily_limit': 17,  # Keep 1 buffer from 18 limit
                'monthly_limit': 100  # Twitter's monthly post cap
            }
        }
        self.cache_file = 'rate_limits.json'
        self._load_cache()
    
    def can_post(self) -> bool:
        """Check if we can post based on rate limits"""
        self._check_resets()
        return (self.rate_limits['post']['daily_count'] < self.rate_limits['post']['daily_limit'] and
                self.rate_limits['post']['monthly_count'] < self.rate_limits['post']['monthly_limit'])
    
    def update_counts(self) -> None:
        """Update post counts after successful post"""
        self.rate_limits['post']['daily_count'] += 1
        self.rate_limits['post']['monthly_count'] += 1
        self._save_cache()
    
    def _check_resets(self) -> None:
        """Check and handle daily/monthly resets"""
        now = datetime.utcnow()
        
        # Check daily reset
        if now.date() > self.rate_limits['post']['last_reset'].date():
            self.rate_limits['post']['daily_count'] = 0
            self.rate_limits['post']['last_reset'] = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
        # Check monthly reset
        if now.replace(day=1) > self.rate_limits['post']['monthly_reset']:
            self.rate_limits['post']['monthly_count'] = 0
            self.rate_limits['post']['monthly_reset'] = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def _load_cache(self) -> None:
        """Load cached rate limits"""
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                self.rate_limits = data
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    
    def _save_cache(self) -> None:
        """Save current rate limits to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.rate_limits, f)
        except Exception as e:
            logger.error(f"Error saving rate limits: {e}")
