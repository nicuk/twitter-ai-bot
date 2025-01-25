"""Rate limiting for Twitter API"""

from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        """Initialize rate limiter"""
        # Default rate limits
        self.default_limits = {
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'daily_limit': 17,  # Keep 1 buffer from 18 limit
                'monthly_limit': 100  # Twitter's monthly post cap
            }
        }
        self.rate_limits = self.default_limits.copy()
        self.cache_file = 'rate_limits.json'
        self._load_cache()
        self.rate_limits = self.default_limits.copy()  # Always reset to default limits
        
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
                # Ensure all required keys exist
                if 'post' in data and all(k in data['post'] for k in self.default_limits['post']):
                    # Convert date strings back to datetime
                    data['post']['last_reset'] = datetime.fromisoformat(data['post']['last_reset'])
                    data['post']['monthly_reset'] = datetime.fromisoformat(data['post']['monthly_reset'])
                    self.rate_limits = data
                else:
                    logger.warning("Invalid cache format, using default limits")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No valid cache found, using default limits")
            
    def _save_cache(self) -> None:
        """Save current rate limits to cache"""
        try:
            # Convert datetime to string for JSON serialization
            cache_data = {
                'post': {
                    **self.rate_limits['post'],
                    'last_reset': self.rate_limits['post']['last_reset'].isoformat(),
                    'monthly_reset': self.rate_limits['post']['monthly_reset'].isoformat()
                }
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.error(f"Error saving rate limits: {e}")

    def cleanup(self) -> None:
        """Clean up old rate limit data"""
        try:
            # Reset to default limits
            self.rate_limits = self.default_limits.copy()
            
            # Check if cache file exists and delete it
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                logger.info("Rate limiter cache cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up rate limiter: {e}")
