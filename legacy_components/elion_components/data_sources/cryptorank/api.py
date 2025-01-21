"""
CryptoRank API V2 client implementation
"""

from typing import Dict, List, Any, Optional
from elion.data_sources.cryptorank.base_client import BaseClient
from elion.data_sources.cryptorank.data_parser import parse_currencies_list

class CryptoRankAPI(BaseClient):
    """CryptoRank API V2 client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize API client"""
        super().__init__(api_key)
        self.base_url = 'https://api.cryptorank.io/v2'  # Use V2 API
        
        if not self.api_key:
            print("\nCryptoRank API Status: Limited Mode")
            print("- Market data features will be disabled")
            print("- Elion will focus on community engagement and AI discussions")
            print("- Self-aware tweets and giveaways will continue as normal")
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
                # Find potential gems
                gems = [
                    coin for coin in data 
                    if coin.get('market_cap', 0) <= 20e6
                    and coin.get('volume_24h', 0) > 250000
                    and abs(coin.get('price_change_24h', 0)) > 15
                ]
                
                if gems:
                    gem = gems[0]  # Get first gem
                    print(f"\n🔥 Found potential gem!")
                    print(f"Name: {gem.get('name')} ({gem.get('symbol')})")
                    print(f"Price: ${gem.get('price', 0):,.8f}")
                    print(f"Market Cap: ${gem.get('market_cap', 0)/1e6:.1f}M")
                    print(f"Volume 24h: ${gem.get('volume_24h', 0)/1e6:.1f}M")
                    print(f"Price Change 24h: {gem.get('price_change_24h', 0):+.1f}%")
                else:
                    print("\n😴 No gems found matching criteria")
            else:
                print("⚠️ No data returned from API")
        else:
            print(f"❌ API connection failed: {response['error']}")
            
    def get_currencies(
        self,
        limit: int = 500,
        offset: int = 0,
        convert: str = 'USD',
        status: str = 'active',
        category: Optional[str] = None,
        type: Optional[str] = None,
        sort: str = 'volume24h',  # Default sort by 24h volume
        order: str = 'desc'  # Default descending order
    ) -> List[Dict[str, Any]]:
        """Get list of currencies
        
        Args:
            limit: Number of results to return (max 500)
            offset: Number of results to skip
            convert: Currency to convert values to
            status: Filter by status (active, inactive)
            category: Filter by category
            type: Filter by type (coin, token)
            sort: Sort field (marketCap, volume24h, rank)
            order: Sort order (asc, desc)
        """
        # Build parameters
        params = {
            'limit': min(limit, 500),  # API max is 500
            'offset': offset,
            'convert': convert,
            'status': status
        }
        
        # Add optional filters
        if category:
            params['category'] = category
        if type:
            params['type'] = type
            
        # Make request
        response = self._make_request('currencies', params)
        
        # Parse response
        if 'error' in response:
            print(f"API Error: {response['error']}")
            return []
            
        # Parse and sort results
        coins = parse_currencies_list(response)
        
        # Sort results
        reverse = order.lower() == 'desc'
        if sort == 'volume24h':
            coins.sort(key=lambda x: x['volume_24h'], reverse=reverse)
        elif sort == 'marketCap':
            coins.sort(key=lambda x: x['market_cap'], reverse=reverse)
        elif sort == 'rank':
            coins.sort(key=lambda x: x['rank'], reverse=not reverse)  # Lower rank is better
            
        return coins
        
    def find_gems(
        self,
        max_market_cap: float = 50e6,  # $50M max market cap
        min_volume: float = 100000,  # $100K min volume
        min_price_change: float = 10,  # 10% min price change
        min_volume_market_cap_ratio: float = 0.05,  # 5% min volume/market cap ratio
        limit: int = 500,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find potential gem coins based on criteria
        
        Args:
            max_market_cap: Maximum market cap in USD
            min_volume: Minimum 24h volume in USD
            min_price_change: Minimum absolute 24h price change percentage
            min_volume_market_cap_ratio: Minimum volume/market cap ratio
            limit: Number of results to return
            offset: Number of results to skip
        """
        # Get active coins sorted by volume
        coins = self.get_currencies(
            limit=limit,
            offset=offset,
            status='active',
            sort='volume24h',
            order='desc'
        )
        
        # Filter by criteria
        gems = [
            coin for coin in coins
            if (coin['market_cap'] > 0 and coin['market_cap'] <= max_market_cap and
                coin['volume_24h'] >= min_volume and
                coin['volume_24h']/coin['market_cap'] >= min_volume_market_cap_ratio and
                abs(coin['price_change_24h']) >= min_price_change)
        ]
        
        return gems
