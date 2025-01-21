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

_token_cache = {}
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
    """Format token info into a standardized dictionary"""
    return {
        'symbol': token.get('symbol', ''),
        'price_change': float(token.get('priceChange24h', 0)),
        'volume': float(token.get('volume24h', 0))
    }

def get_movement_description(change: float) -> str:
    """Get descriptive text for price movement"""
    if change > 15:
        return "surging"
    elif change > 5:
        return "rising"
    elif change < -15:
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
    
    for token in tokens:
        try:
            # Skip stablecoins
            if is_likely_stablecoin(token.get('symbol', '')):
                print(f"Skipping stablecoin: {token.get('symbol', '')}")
                continue
                
            # Get price change
            price_change = float(token.get('priceChange24h', 0))
            
            # Check if meets minimum change threshold
            if abs(price_change) >= min_price_change:
                print(f"Found trending token: {token.get('symbol', '')} ({price_change:+.1f}%)")
                trend_tokens.append(token)
                
        except Exception as e:
            print(f"Error filtering token: {str(e)}")
            continue
            
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

def fetch_tokens(api_key: str, sort_by='volume24h', direction='DESC', print_first=0) -> list:
    """Fetch tokens from CryptoRank API with specified sorting"""
    try:
        # Build API URL
        base_url = "https://api.cryptorank.io/v1"
        endpoint = "/currencies"
        params = {
            'api_key': api_key,
            'sortBy': sort_by,
            'dir': direction.upper(),
            'limit': 1000
        }
        
        # Make API request
        response = requests.get(f"{base_url}{endpoint}", params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error fetching data: {response.text}")
            return []
            
        # Parse response
        data = response.json()
        raw_tokens = data.get('data', [])
        
        if print_first > 0:
            print("\nFirst token raw data:")
            print(json.dumps(raw_tokens[0], indent=2))
            
        # Format token data
        formatted_tokens = []
        for token in raw_tokens:
            try:
                values = token.get('values', {}).get('USD', {})
                if not values:
                    continue
                    
                formatted_token = {
                    'symbol': token.get('symbol', ''),
                    'price': values.get('price', 0),
                    'priceChange24h': values.get('percentChange24h', 0),
                    'volume24h': values.get('volume24h', 0),
                    'marketCap': values.get('marketCap', 0)
                }
                formatted_tokens.append(formatted_token)
            except Exception as e:
                print(f"Error formatting token {token.get('symbol')}: {str(e)}")
                continue
                
        print(f"Found {len(formatted_tokens)} tokens")
        return formatted_tokens
        
    except Exception as e:
        print(f"Error fetching tokens: {str(e)}")
        return []
