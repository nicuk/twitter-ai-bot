"""
Parameter validation utilities for CryptoRank API V2
"""

from typing import Any, Dict, Optional, List

def validate_api_key(api_key: Optional[str]) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    return len(api_key) > 0

def validate_currency_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and sanitize currency request parameters"""
    validated = {}
    
    # Handle limit parameter
    if 'limit' in params:
        limit = int(params['limit'])
        validated['limit'] = min(max(1, limit), 1000)  # Ensure between 1-1000
        
    # Handle sorting parameters
    if 'sortBy' in params:
        valid_sort_fields = [
            'marketCap', 'volume24h', 'price', 'percentChange24h', 
            'percentChange7d', 'rank'
        ]
        sort_by = str(params['sortBy'])
        validated['sortBy'] = sort_by if sort_by in valid_sort_fields else 'marketCap'
        
    if 'sortDirection' in params:
        valid_directions = ['ASC', 'DESC']
        direction = str(params['sortDirection']).upper()
        validated['sortDirection'] = direction if direction in valid_directions else 'DESC'
        
    # Handle include parameter
    if 'include' in params:
        valid_includes = ['percentChange', 'links', 'supply']
        includes = params['include']
        if isinstance(includes, str):
            includes = [includes]
        validated['include'] = [inc for inc in includes if inc in valid_includes]
        
    # Handle market cap filters
    if 'marketCap[from]' in params:
        validated['marketCap[from]'] = max(0, float(params['marketCap[from]']))
    if 'marketCap[to]' in params:
        validated['marketCap[to]'] = max(0, float(params['marketCap[to]']))
        
    # Handle volume filters
    if 'volume24h[from]' in params:
        validated['volume24h[from]'] = max(0, float(params['volume24h[from]']))
    if 'volume24h[to]' in params:
        validated['volume24h[to]'] = max(0, float(params['volume24h[to]']))
        
    # Handle price change filters
    if 'percentChange24h[from]' in params:
        validated['percentChange24h[from]'] = float(params['percentChange24h[from]'])
    if 'percentChange24h[to]' in params:
        validated['percentChange24h[to]'] = float(params['percentChange24h[to]'])
        
    return validated

def validate_response(response_data: Dict[str, Any]) -> bool:
    """Validate API response format"""
    if not isinstance(response_data, dict):
        return False
        
    # Check for V2 response structure
    if 'data' not in response_data:
        return False
        
    # Check if data is list for endpoints that return arrays
    if isinstance(response_data['data'], list):
        return True
        
    # Check if data is object for single-item responses
    if isinstance(response_data['data'], dict):
        return True
        
    return False
