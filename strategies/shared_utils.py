"""Shared utilities for all crypto analysis strategies"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from strategies.cryptorank_client import CryptoRankAPI

# Cache settings
_token_cache = {}  # Dict to store different sorted results
_last_fetch_time = 0
CACHE_DURATION = 300  # Cache duration in seconds

def calculate_activity_score(volume: float, mcap: float, price_change: float) -> int:
    """Calculate token activity score (0-100)"""
    # Volume/MCap component (0-50 points)
    vol_mcap_ratio = (volume/mcap*100) if mcap > 0 else 0
    volume_score = min(50, int(vol_mcap_ratio/10))  # 10% vol/mcap = 5 points, max 50 points
    
    # Price movement component (0-30 points)
    price_score = min(30, int(abs(price_change) * 2))  # Each % = 2 points, max 30 points
    
    # Volume size component (0-20 points)
    volume_size_score = min(20, int(volume/1e6/10))  # Each $10M = 1 point, max 20 points
    
    return volume_score + price_score + volume_size_score

def get_price_change(token: Dict) -> tuple:
    """Get price change and amount from token data"""
    try:
        # Get current price
        price = float(token.get('price', 0))
        
        # Get 24h change directly from API
        change = float(token.get('percentChange24h', 0))
        
        # Fallback to high/low calculation if percentChange24h not available
        if change == 0:
            high = float(token.get('high24h', 0))
            low = float(token.get('low24h', 0))
            
            if high > 0 and low > 0:
                avg = (high + low) / 2
                change = ((price - avg) / avg) * 100
        
        return change, price
        
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error calculating price change: {str(e)}")
        return 0.0, 0.0

def format_token_info(token: Dict) -> Dict:
    """Format token information for consistent display"""
    price_change, price = get_price_change(token)
    
    volume = float(token.get('volume24h', 0) or 0)
    mcap = float(token.get('marketCap', 0) or 0)
    
    token_info = {
        'symbol': token.get('symbol', ''),
        'name': token.get('name', ''),
        'price': float(token.get('price', 0) or 0),  # Get price directly
        'price_change': price_change,
        'volume': volume,
        'mcap': mcap,
        'activity_score': calculate_activity_score(volume, mcap, price_change)
    }
    
    return token_info

def get_movement_description(change: float) -> str:
    """Get descriptive text for price movement"""
    if change > 30:
        return "mooning"
    elif change > 5:
        return "rising"
    elif change < -30:
        return "bleeding"
    elif change < -5:
        return "dipping"
    else:
        return "stable"

def print_token_details(token_info: Dict) -> None:
    """Print formatted token details"""
    print(f"\n⚡ MAJOR Activity: ${token_info['symbol']}")
    print(f"Activity Score: {token_info.get('activity_score', 0)}/100 🚨")
    # Format price based on its value
    if token_info['price'] < 1:
        price_str = f"${token_info['price']:.6f}"
    elif token_info['price'] < 100:
        price_str = f"${token_info['price']:.3f}"
    else:
        price_str = f"${token_info['price']:.2f}"
    print(price_str)
    
    # Format percentage with appropriate precision
    if abs(token_info['price_change']) < 1:
        print(f"{token_info['price_change']:+.2f}%")
    else:
        print(f"{token_info['price_change']:+.1f}%")
    
    print(f"(${token_info.get('price_change_usd', 0):+.2f})")
    print(f"Volume: ${token_info['volume']/1e6:.1f}M")
    print("DYOR! 🔍")

def filter_tokens_by_volume(tokens: list, min_volume_mcap_ratio: float = 1.0) -> list:
    """Filter tokens by volume/mcap ratio for volume strategy"""
    volume_filtered = []
    seen_symbols = set()
    
    for token in tokens:
        try:
            token_info = format_token_info(token)
            symbol = token_info['symbol']
            
            # Skip if already seen or likely stablecoin
            if symbol in seen_symbols or is_likely_stablecoin(symbol):
                continue
                
            # Calculate volume/mcap ratio
            mcap = float(token_info['mcap'])
            volume = float(token_info['volume'])
            
            if mcap > 0:
                ratio = volume / mcap
                if ratio > min_volume_mcap_ratio:  # More than 100% volume/mcap
                    volume_filtered.append((ratio, token_info))
                    seen_symbols.add(symbol)
        except Exception as e:
            continue
            
    # Sort by ratio
    volume_filtered.sort(key=lambda x: x[0], reverse=True)
    return volume_filtered

def filter_tokens_by_trend(tokens: List[Dict], min_price_change: float = 5.0) -> List[Dict]:
    """Filter tokens by price trend"""
    trend_tokens = []
    print(f"\nFiltering {len(tokens)} tokens for trends...")
    print("First token data:", json.dumps(tokens[0], indent=2))
    
    for token in tokens:
        try:
            symbol = token.get('symbol', '')
            
            # Skip stablecoins
            if is_likely_stablecoin(symbol):
                print(f"Skipping stablecoin: {symbol}")
                continue
                
            # Get price change
            price_change = float(token.get('priceChange24h', 0))
            print(f"Token {symbol}: Price change = {price_change:+.1f}%")
            
            # Check if meets minimum change threshold
            if abs(price_change) >= min_price_change:
                print(f"Found trending token: {symbol} ({price_change:+.1f}%)")
                trend_tokens.append(token)
                
        except Exception as e:
            print(f"Error filtering token: {str(e)}")
            continue
            
    print(f"\nFound {len(trend_tokens)} trending tokens")
    return trend_tokens

def format_token_data(token: Dict) -> Dict:
    """Format raw token data from API into standardized format"""
    try:
        values = token.get('values', {}).get('USD', {})
        if not values:
            return None
            
        return {
            'symbol': token.get('symbol', ''),
            'price': values.get('price', 0),
            'priceChange24h': values.get('percentChange24h', 0),
            'volume24h': values.get('volume24h', 0),
            'marketCap': values.get('marketCap', 0)
        }
    except Exception as e:
        print(f"Error formatting token data: {str(e)}")
        return None

def process_tokens(tokens: List[Dict]) -> List[Dict]:
    """Process a list of tokens into standardized format"""
    formatted_tokens = []
    for token in tokens:
        formatted = format_token_data(token)
        if formatted:
            formatted_tokens.append(formatted)
    return formatted_tokens

def is_likely_stablecoin(symbol: str) -> bool:
    """Check if token is likely a stablecoin based on symbol"""
    # Common stablecoin identifiers
    stablecoin_patterns = [
        'usd', 'usdt', 'usdc', 'dai', 'busd', 'tusd', 'susd', 'lusd', 'frax', 'ausd', 'cusd', 'ousd'
    ]
    
    # Convert symbol to lowercase
    symbol = symbol.lower()
    
    # Check if symbol contains stablecoin pattern
    for pattern in stablecoin_patterns:
        if pattern in symbol:
            return True
            
    return False

def fetch_tokens(api_key: str, sort_by='volume24h', direction='DESC', print_first=0, limit=500) -> list:
    """Fetch tokens from CryptoRank API with specified sorting"""
    global _token_cache, _last_fetch_time
    
    # Check cache first
    current_time = time.time()
    cache_key = f"{sort_by}_{direction}_{limit}"
    
    if _token_cache.get(cache_key) and current_time - _last_fetch_time < CACHE_DURATION:
        print("Using cached token data")
        return _token_cache[cache_key]
    
    # Add delay between API calls
    if current_time - _last_fetch_time < 2:  # Wait at least 2 seconds between calls
        time.sleep(2)
    
    try:
        # Build API URL
        base_url = "https://api.cryptorank.io/v2"
        endpoint = "/currencies"
        params = {
            'limit': limit,
            'convert': 'USD',
            'status': 'active',
            'orderBy': sort_by if sort_by == 'volume24h' else 'percentChange.h24',
            'orderDirection': direction,
            'type': None,
            'offset': None
        }
        
        # Make API request with key in header
        headers = {'X-Api-Key': api_key}
        response = requests.get(f"{base_url}{endpoint}", params=params, headers=headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error fetching data: {response.text}")
            print("Rate limit headers:", dict(response.headers))
            return []
            
        # Parse response
        data = response.json()
        raw_tokens = data.get('data', [])
        
        # Debug: Show raw data for first token
        if raw_tokens:
            print("\nRaw data for first token:")
            print(json.dumps(raw_tokens[0], indent=2))
        
        if print_first > 0:
            print("\nFirst token raw data:")
            print(json.dumps(raw_tokens[0], indent=2))
            print("\nFirst token values:")
            values = raw_tokens[0].get('values', {}).get('USD', {})
            print(json.dumps(values, indent=2))
            
        # Format token data
        formatted_tokens = []
        for token in raw_tokens:
            try:
                formatted_token = {
                    'symbol': token.get('symbol', ''),
                    'price': float(token.get('price', 0)),
                    'volume24h': float(token.get('volume24h', 0)),
                    'marketCap': float(token.get('marketCap', 0))
                }
                
                # Calculate price change from high/low
                high24h = float(token.get('high24h', 0))
                low24h = float(token.get('low24h', 0))
                current_price = float(token.get('price', 0))
                
                if high24h > 0 and low24h > 0:
                    # Calculate price change as percentage from average of high/low
                    avg_price = (high24h + low24h) / 2
                    price_change = ((current_price - avg_price) / avg_price) * 100
                    formatted_token['priceChange24h'] = price_change
                else:
                    formatted_token['priceChange24h'] = 0
                
                formatted_tokens.append(formatted_token)
            except Exception as e:
                print(f"Error formatting token {token.get('symbol')}: {str(e)}")
                continue
                
        print(f"Found {len(formatted_tokens)} tokens")
        
        # Update cache with new data
        _token_cache[cache_key] = formatted_tokens
        _last_fetch_time = current_time
        
        return formatted_tokens
        
    except Exception as e:
        print(f"Error fetching tokens: {str(e)}")
        return []

def get_portfolio_data(tokens: List[Dict], holdings: Dict) -> Dict:
    """Calculate portfolio metrics from token data
    
    Args:
        tokens: List of token data from API
        holdings: Dict of {symbol: amount} representing user's holdings
        
    Returns:
        Dict containing portfolio metrics for each token
    """
    portfolio = {}
    for symbol, amount in holdings.items():
        token = next((t for t in tokens if t['symbol'] == symbol), None)
        if token:
            token_info = format_token_info(token)
            portfolio[symbol] = {
                'amount': amount,
                'value': amount * token_info['price'],
                'change_24h': token_info['price_change'],
                'volume': token_info['volume'],
                'mcap': token_info['mcap'],
                'price': token_info['price']
            }
    return portfolio

def calculate_portfolio_metrics(portfolio: Dict) -> Dict:
    """Calculate overall portfolio metrics
    
    Args:
        portfolio: Dict of portfolio data from get_portfolio_data()
        
    Returns:
        Dict containing total value, 24h change, etc.
    """
    if not portfolio:
        return {
            'total_value': 0,
            'total_change_24h': 0,
            'total_change_percent': 0,
            'tokens': 0,
            'biggest_gainer': None,
            'biggest_loser': None
        }
        
    total_value = sum(t['value'] for t in portfolio.values())
    total_change = sum(t['value'] * t['change_24h']/100 for t in portfolio.values())
    
    # Find biggest gainer and loser
    sorted_tokens = sorted(portfolio.items(), key=lambda x: x[1]['change_24h'])
    biggest_loser = sorted_tokens[0] if sorted_tokens else None
    biggest_gainer = sorted_tokens[-1] if sorted_tokens else None
    
    return {
        'total_value': total_value,
        'total_change_24h': total_change,
        'total_change_percent': (total_change / total_value * 100) if total_value > 0 else 0,
        'tokens': len(portfolio),
        'biggest_gainer': biggest_gainer[0] if biggest_gainer else None,
        'biggest_loser': biggest_loser[0] if biggest_loser else None
    }

def get_movement_icon_portfolio(change: float) -> str:
    """Get movement icon for portfolio token
    Uses same thresholds as trend/volume for consistency
    """
    if change > 30:
        return "🌙"  # Mooning
    elif change > 3:
        return "🚀"  # Surging
    elif change < -30:
        return "🩸"  # Bleeding
    elif change < -3:
        return "📉"  # Dipping
    else:
        return "➡️"  # Stable
