"""
Data parsing utilities for API responses
"""

from typing import Any, Dict, List, Optional, Union

def parse_currency_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse raw currency data into standardized format"""
    try:
        usd_values = raw_data.get('values', {}).get('USD', {})
        return {
            'symbol': raw_data.get('symbol'),
            'name': raw_data.get('name'),
            'price': usd_values.get('price', 0),
            'market_cap': usd_values.get('marketCap', 0),
            'volume_24h': usd_values.get('volume24h', 0),
            'price_change_24h': usd_values.get('percentChange24h', 0),
            'price_change_7d': usd_values.get('percentChange7d', 0),
            'holders': raw_data.get('holdersCount', 0)
        }
    except Exception as e:
        print(f"Error parsing currency data: {e}")
        return {}
        
def parse_trending_coins(
    data: List[Dict[str, Any]], 
    min_volume: float = 100000,  # Min $100k daily volume
    min_price_change: float = 5  # Min 5% price move
) -> List[Dict[str, Any]]:
    """Parse and filter trending coins based on volume and price action"""
    try:
        trending = []
        for coin in data:
            parsed = parse_currency_data(coin)
            if (parsed.get('volume_24h', 0) > min_volume and 
                abs(parsed.get('price_change_24h', 0)) > min_price_change):
                trending.append(parsed)
        return trending
    except Exception as e:
        print(f"Error parsing trending coins: {e}")
        return []
