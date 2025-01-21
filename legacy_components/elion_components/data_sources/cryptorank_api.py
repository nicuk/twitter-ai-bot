"""CryptoRank API client for market data"""

import requests
from typing import Dict, Any, Optional

class CryptoRankAPI:
    """CryptoRank API V2 client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize API client"""
        self.api_key = api_key
        self.base_url = 'https://api.cryptorank.io/v2'
        self.session = requests.Session()
        
        if not self.api_key:
            print("\nCryptoRank API Status: Limited Mode")
            print("- Market data features will be disabled")
        else:
            self.test_connection()
            
    def test_connection(self) -> None:
        """Test V2 API connection"""
        params = {
            'limit': 500,
            'category': None,
            'convert': 'USD',
            'status': 'active',
            'type': None,
            'offset': None
        }
        
        print("\nTesting CryptoRank V2 API...")
        response = self._make_request('currencies', params)
        
        if 'error' not in response:
            print("✅ API connection successful")
            data = response.get('data', [])
            if data:
                print(f"Found {len(data)} active currencies")
        else:
            print(f"❌ API connection failed: {response['error']}")
            
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to API endpoint"""
        if not self.api_key:
            return {'error': 'No API key provided'}
            
        url = f"{self.base_url}/{endpoint}"
        headers = {'X-Api-Key': self.api_key}
        
        try:
            response = self.session.get(url, params=params, headers=headers)
            return response.json()
        except Exception as e:
            return {'error': str(e)}
