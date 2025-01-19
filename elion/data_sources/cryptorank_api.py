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
            'limit': 100,  # Get more coins to filter
            'sort': 'volume24h',  # Sort by 24h volume for trending coins
            'marketCapUsd[to]': 100000000  # Max $100M market cap
        }
        print("\nTesting CryptoRank v1 API...")
        try:
            response = requests.get(f"{self.base_url}/currencies", params=params)
            status_messages = {
                200: "✅ API connection successful",
                401: "❌ API key invalid or expired",
                403: "❌ API access forbidden - check permissions",
                429: "⚠️ Rate limit exceeded - try again later",
                500: "❌ CryptoRank server error",
                502: "❌ CryptoRank gateway error",
                503: "⚠️ CryptoRank service temporarily unavailable"
            }
            status_msg = status_messages.get(
                response.status_code, 
                f"❓ Unexpected response (code: {response.status_code})"
            )
            print(f"Status: {status_msg}")
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    # Filter for coins with good volume and recent price action
                    trending = [
                        coin for coin in data['data']
                        if coin['values']['USD'].get('volume24h', 0) > 100000  # Min $100k daily volume
                        and abs(coin['values']['USD'].get('percentChange24h', 0)) > 5  # >5% price move
                    ]
                    if trending:
                        coin = trending[0]  # Get the most interesting one
                        print(f"\n🔥 Found trending gem! {coin['name']} ({coin['symbol']})")
                        print(f"📈 24h Change: {coin['values']['USD'].get('percentChange24h', 0):.1f}%")
                        print(f"💰 24h Volume: ${coin['values']['USD'].get('volume24h', 0)/1000000:.1f}M")
                    else:
                        print("\n😴 No trending gems found at the moment")
            else:
                print(f"\n❌ API request failed: {response.text}")
                    
        except Exception as e:
            print(f"❌ Error testing API: {e}")
            
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
