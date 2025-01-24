"""Shared CryptoRank API client for all strategies"""

import os
import requests
import time
from typing import Dict, List, Any, Optional

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
        
        if not response or not hasattr(response, 'status_code'):
            print("Error: Invalid response from API")
            return
            
        if response.status_code != 200:
            print(f"Error testing API connection: {response.text}")
            return
            
        data = response.json()
        if 'error' not in data:
            print("✅ API connection successful")
            data = data.get('data', [])
            if data:
                print(f"Found {len(data)} active currencies")
                # Debug first token
                if data:
                    token = data[0]
                    print("\nDebug: First token data:")
                    print(f"Name: {token.get('name')}")
                    print(f"Symbol: {token.get('symbol')}")
                    print(f"Current Price: {token.get('price')}")
                    print(f"24h Price: {token.get('price24h')}")
                    print(f"Percent Change: {token.get('percentChange', {}).get('h24')}")
        else:
            print(f"❌ API connection failed: {data['error']}")
            
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[requests.Response]:
        """Make API request with retries and error handling"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params['api_key'] = self.api_key
        
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, params=params, timeout=10)
                
                # Handle rate limits
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', retry_delay))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                    
                # Handle server errors
                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        print(f"Server error {response.status_code}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"Failed after {max_retries} attempts. Server error: {response.status_code}")
                        return None
                        
                return response
                
            except (requests.RequestException, ValueError) as e:
                if attempt < max_retries - 1:
                    print(f"Request failed: {str(e)}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"Failed after {max_retries} attempts. Error: {str(e)}")
                    return None
                    
        return None

    def get_tokens(self, orderBy='volume24h', orderDirection='DESC') -> List[Dict]:
        """Get top 500 tokens from CryptoRank API"""
        params = {
            'limit': 500,
            'convert': 'USD',
            'status': 'active',
            'orderBy': orderBy,
            'orderDirection': orderDirection,
            'type': None,
            'offset': None
        }
        
        response = self._make_request('currencies', params)
        if not response or not hasattr(response, 'status_code'):
            print("Error: Invalid response from API")
            return []
            
        if response.status_code != 200:
            print(f"Error fetching tokens: {response.text}")
            return []
            
        data = response.json()
        return data.get('data', [])

def calculate_price_change(token: Dict) -> float:
    """Calculate 24h price change with fallback methods"""
    try:
        # Method 1: Use API-reported change
        reported_change = float(token.get('percentChange', {}).get('h24', 0) or 0)
        if -100 < reported_change < 100:
            return reported_change
            
        # Method 2: Calculate from current and 24h price
        current_price = float(token.get('price', 0) or 0)
        price_24h = float(token.get('price24h', current_price) or current_price)
        
        if price_24h > 0:
            price_change = ((current_price - price_24h) / price_24h) * 100
            return price_change
            
        # Method 3: Last resort - no change
        return 0
    except Exception as e:
        print(f"Error calculating price change: {str(e)}")
        return 0

def format_token_info(token: Dict) -> Dict:
    """Format token information for consistent display"""
    try:
        return {
            'name': token.get('name', 'Unknown'),
            'symbol': token.get('symbol', '???'),
            'price': float(token.get('price', 0) or 0),
            'volume': float(token.get('volume24h', 0) or 0),
            'mcap': float(token.get('marketCap', 0) or 0),
            'change_24h': calculate_price_change(token)
        }
    except (ValueError, TypeError):
        return None

def print_token_details(token_info: Dict) -> None:
    """Print formatted token details"""
    print(f"\n{token_info['name']} ({token_info['symbol']})")
    print(f"Price: ${token_info['price']:.4f}")
    print(f"24h Volume: ${token_info['volume']:,.0f}")
    print(f"Market Cap: ${token_info['mcap']:,.0f}")
    print(f"24h Change: {token_info['change_24h']:+.2f}%")
