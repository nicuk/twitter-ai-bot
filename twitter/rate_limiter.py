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
        # Default rate limits
        self.default_limits = {
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'daily_limit': 17,  # Keep 1 buffer from 18 limit
                'monthly_limit': 100,  # Twitter's monthly post cap
                'last_rate_limit': None,  # Track when we last hit a rate limit
                'rate_limit_cooldown': 901,  # Twitter's rate limit cooldown in seconds
                'last_post_time': 0  # Track when we last successfully posted
            }
        }
        self.rate_limits = self.default_limits.copy()
        self.cache_file = 'rate_limits.json'
        self._load_cache()
    
    @property
    def last_post_time(self) -> float:
        """Get the last successful post time"""
        return self.rate_limits['post']['last_post_time']
    
    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        if self.rate_limits['post']['last_rate_limit']:
            time_since_limit = (datetime.utcnow() - self.rate_limits['post']['last_rate_limit']).total_seconds()
            return time_since_limit < self.rate_limits['post']['rate_limit_cooldown']
        return False
    
    def update_post_time(self) -> None:
        """Update the last successful post time"""
        self.rate_limits['post']['last_post_time'] = time.time()
        self._save_cache()
    
    def can_post(self) -> bool:
        """Check if we can post based on rate limits"""
        self._check_resets()
        
        # Check if we're in rate limit cooldown
        if self.rate_limits['post']['last_rate_limit']:
            time_since_limit = (datetime.utcnow() - self.rate_limits['post']['last_rate_limit']).total_seconds()
            if time_since_limit < self.rate_limits['post']['rate_limit_cooldown']:
                logger.warning(f"In rate limit cooldown for {self.rate_limits['post']['rate_limit_cooldown'] - time_since_limit:.0f} more seconds")
                return False
            else:
                # Reset rate limit after cooldown
                self.rate_limits['post']['last_rate_limit'] = None
                self._save_cache()
        
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
                    if 'last_rate_limit' in data['post']:
                        data['post']['last_rate_limit'] = datetime.fromisoformat(data['post']['last_rate_limit'])
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
                    'monthly_reset': self.rate_limits['post']['monthly_reset'].isoformat(),
                    'last_rate_limit': self.rate_limits['post']['last_rate_limit'].isoformat() if self.rate_limits['post']['last_rate_limit'] else None
                }
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            logger.error(f"Error saving rate limits: {e}")

    def handle_rate_limit(self) -> None:
        """Handle a rate limit error"""
        self.rate_limits['post']['last_rate_limit'] = datetime.utcnow()
        self._save_cache()
        logger.warning(f"Rate limit exceeded. Sleeping for {self.rate_limits['post']['rate_limit_cooldown']} seconds.")
        time.sleep(self.rate_limits['post']['rate_limit_cooldown'])

    def wait(self) -> None:
        """Wait until we can post again"""
        while not self.can_post():
            logger.info("Rate limit reached, waiting 60 seconds...")
            time.sleep(60)  # Wait a minute before checking again
            self._check_resets()

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
