"""
Data parsing utilities for CryptoRank API V2 responses
"""

from typing import Dict, List, Any, Optional

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float, handling various formats"""
    try:
        if value is None:
            return default
            
        if isinstance(value, dict):
            # Handle nested value objects
            if 'value' in value:
                return float(value['value'])
            if 'USD' in value:
                return float(value['USD'])
            return default
            
        if isinstance(value, str):
            # Remove any currency symbols or commas
            value = value.replace('$', '').replace(',', '')
            
        return float(value)
    except (ValueError, TypeError):
        return default

def parse_currency_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse raw currency data into standardized format"""
    try:
        # Get price changes from ATH/ATL
        ath = raw_data.get('ath', {})
        atl = raw_data.get('atl', {})
        price_change = abs(safe_float(ath.get('percentChange', 0)))
            
        return {
            'id': raw_data.get('id'),
            'key': raw_data.get('key'),
            'name': raw_data.get('name'),
            'symbol': raw_data.get('symbol'),
            'rank': raw_data.get('rank'),
            'type': raw_data.get('type'),
            'category': raw_data.get('categoryId'),
            'price': safe_float(raw_data.get('price')),
            'volume_24h': safe_float(raw_data.get('volume24h')),
            'market_cap': safe_float(raw_data.get('marketCap')),
            'price_change_24h': price_change,  # Using ATH percent change for now
            'high_24h': safe_float(raw_data.get('high24h')),
            'low_24h': safe_float(raw_data.get('low24h')),
            'circulating_supply': safe_float(raw_data.get('circulatingSupply')),
            'total_supply': safe_float(raw_data.get('totalSupply')),
            'max_supply': safe_float(raw_data.get('maxSupply')),
            'fully_diluted_value': safe_float(raw_data.get('fullyDilutedValuation')),
            'volume_24h_base': safe_float(raw_data.get('volume24hBase')),
            'last_updated': raw_data.get('lastUpdated'),
            'status': 'active'  # Since we're filtering for active coins
        }
    except Exception as e:
        print(f"Error parsing currency data: {e}")
        return {}

def parse_currencies_list(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse list of currencies from API response"""
    currencies = []
    
    try:
        if not raw_data:
            return currencies
            
        if 'status' in raw_data:
            print(f"API Status: {raw_data['status']}")
            
        data = raw_data.get('data', [])
        if not data:
            return currencies
            
        for coin in data:
            parsed = parse_currency_data(coin)
            if parsed:  # Only add if parsing was successful
                currencies.append(parsed)
                
        return currencies
        
    except Exception as e:
        print(f"Error parsing currencies list: {e}")
        return currencies

def extract_error_message(response_data: Dict[str, Any]) -> Optional[str]:
    """Extract error message from API response"""
    if isinstance(response_data, dict):
        # Check various error message locations in response
        if 'message' in response_data:
            return response_data['message']
        if 'error' in response_data:
            return response_data['error']
        if 'status' in response_data and isinstance(response_data['status'], dict):
            return response_data['status'].get('message')
    return None
