"""
Base classes for data sources
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

class BaseDataSource(ABC):
    """Base class for all data sources"""
    
    def __init__(self):
        """Initialize base data source"""
        self.cache = {}
        self.cache_durations = {}
        
    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if available and not expired"""
        if key not in self.cache:
            return None
            
        cache_data = self.cache[key]
        if not cache_data or 'timestamp' not in cache_data:
            return None
            
        # Check if cache has expired
        duration = self.cache_durations.get(key, timedelta(minutes=5))
        if datetime.now() - cache_data['timestamp'] > duration:
            return None
            
        return cache_data.get('data')
        
    def _cache_data(self, key: str, data: Any):
        """Cache data with timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
    @abstractmethod
    def _validate_data(self, data: Any) -> bool:
        """Validate data before caching"""
        pass
