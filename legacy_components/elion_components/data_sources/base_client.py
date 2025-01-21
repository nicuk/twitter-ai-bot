"""
Base HTTP client functionality
"""

import requests
from typing import Dict, Optional

class BaseAPIClient:
    """Base class for API clients"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize base client with URL and optional API key"""
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        
    def _get(self, endpoint: str, params: Dict = None, headers: Dict = None) -> requests.Response:
        """Make GET request with error handling"""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
            
    def _build_headers(self, additional_headers: Dict = None) -> Dict:
        """Build request headers"""
        headers = {}
        if self.api_key:
            headers['X-Api-Key'] = self.api_key
        if additional_headers:
            headers.update(additional_headers)
        return headers
