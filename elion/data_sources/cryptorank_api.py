"""
CryptoRank API wrapper
"""

import os
import requests
from typing import Dict, List, Optional

class CryptoRankAPI:
    """CryptoRank API wrapper"""
    
    def __init__(self, api_key=None):
        """Initialize the API wrapper"""
        self.api_key = api_key
        if not self.api_key:
            print("\nCryptoRank API Status: Limited Mode")
            print("- Market data features will be disabled")
            print("- Elion will focus on community engagement and AI discussions")
            print("- Self-aware tweets and giveaways will continue as normal")
            
        self.base_url = 'https://api.cryptorank.io/v1'  # Using v1 API
        
        # Test v1 API only if we have an API key
        if self.api_key:
            self.test_v1()
        
    def test_v1(self):
        """Test v1 API endpoint"""
        params = {
            'api_key': self.api_key,
            'limit': 1
        }
        print("\nTesting CryptoRank v1 API...")
        try:
            response = requests.get(f"{self.base_url}/currencies", params=params)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    coin = data['data'][0]
                    print(f"Success! Sample data: {coin['name']} ({coin['symbol']})")
                    
        except Exception as e:
            print(f"Error testing API: {e}")
            
    def get_currencies(self, limit: int = 100) -> List[Dict]:
        """Get currency data from CryptoRank"""
        if not self.api_key:
            return []
            
        params = {
            'api_key': self.api_key,
            'limit': limit
        }
        
        try:
            response = requests.get(f"{self.base_url}/currencies", params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return [
                        {
                            'symbol': coin['symbol'],
                            'name': coin['name'],
                            'price': coin['values']['USD']['price'],
                            'market_cap': coin['values']['USD']['marketCap'],
                            'volume_24h': coin['values']['USD']['volume24h'],
                            'price_change_24h': coin['values']['USD'].get('percentChange24h', 0),
                            'price_change_7d': coin['values']['USD'].get('percentChange7d', 0),
                            'holders': coin.get('holdersCount', 0)
                        }
                        for coin in data['data']
                    ]
            return []
            
        except Exception as e:
            print(f"Error getting currencies: {e}")
            return []
            
    def get_currency(self, symbol: str) -> Optional[Dict]:
        """Get data for a specific currency"""
        if not self.api_key:
            return None
            
        params = {
            'api_key': self.api_key,
            'symbols': symbol
        }
        
        try:
            response = requests.get(f"{self.base_url}/currencies", params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    coin = data['data'][0]
                    return {
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'price': coin['values']['USD']['price'],
                        'market_cap': coin['values']['USD']['marketCap'],
                        'volume_24h': coin['values']['USD']['volume24h'],
                        'price_change_24h': coin['values']['USD'].get('percentChange24h', 0),
                        'price_change_7d': coin['values']['USD'].get('percentChange7d', 0),
                        'holders': coin.get('holdersCount', 0)
                    }
            return None
            
        except Exception as e:
            print(f"Error getting currency: {e}")
            return None
