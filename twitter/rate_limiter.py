"""Rate limiting for Twitter API"""

from datetime import datetime
import json
import logging
import os
import time

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        """Initialize rate limiter"""
        # Just track counts without limits
        self.default_limits = {
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            }
        }
        self.rate_limits = self.default_limits.copy()
        self.cache_file = 'rate_limits.json'
        self._load_cache()
    
    def can_post(self) -> bool:
        """Check if we can post"""
        self._check_resets()
        return True  # Always allow posting, Tweepy handles limits
    
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
        """Load cached post counts"""
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
                    logger.warning("Invalid cache format, using default values")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No valid cache found, using default values")
            
    def _save_cache(self) -> None:
        """Save current post counts to cache"""
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
            logger.error(f"Error saving post counts: {e}")

    def wait(self) -> None:
        """No waiting needed as Tweepy handles rate limits"""
        return

    def cleanup(self) -> None:
        """Clean up old post count data"""
        try:
            # Reset to default values
            self.rate_limits = self.default_limits.copy()
            
            # Check if cache file exists and delete it
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                logger.info("Cleaned up post count cache")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
