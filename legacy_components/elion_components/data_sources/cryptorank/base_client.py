"""
Base client functionality for CryptoRank API V2
"""

import requests
from typing import Dict, Any, Optional
from .param_validator import validate_response, validate_api_key
from .data_parser import extract_error_message

class BaseClient:
    """Base client for making API requests"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize base client"""
        self.api_key = api_key
        self.base_url = 'https://api.cryptorank.io/v2'  # V2 API
        self.session = requests.Session()
        
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API endpoint"""
        if not validate_api_key(self.api_key):
            return {'error': 'No API key provided'}
            
        # Build headers with API key
        headers = {'X-Api-Key': self.api_key}
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            print(f"\nMaking request to: {url}")
            print(f"Parameters: {params}")
            
            response = self.session.get(url, params=params, headers=headers)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    if validate_response(data):
                        if 'data' in data:
                            print(f"Found {len(data['data'])} items")
                        return data
                    return {'error': extract_error_message(data)}
                except ValueError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"Response text: {response.text[:200]}...")  # Show first 200 chars
                    return {'error': 'Invalid JSON response'}
            else:
                error_msg = None
                try:
                    error_msg = extract_error_message(response.json())
                except:
                    error_msg = response.text
                    
                return {
                    'error': error_msg or f"API request failed: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return {'error': f"Request failed: {str(e)}"}
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {'error': f"Unexpected error: {str(e)}"}
            
    def check_api_status(self) -> bool:
        """Check if API is accessible"""
        response = self._make_request('currencies', {'limit': 1})
        return 'error' not in response
