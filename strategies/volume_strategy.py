"""Volume-based analysis strategies"""

import os
import sys
import codecs
from pathlib import Path
import requests
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import datetime
import time
import logging

# Set console encoding to UTF-8
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Set up logging
logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from strategies.scoring_base import BaseScoring

class CryptoRankAPI:
    """CryptoRank API V2 client"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize API client"""
        self.api_key = api_key
        self.base_url = 'https://api.cryptorank.io/v2'  # Using v2 API
        self.session = requests.Session()
        
        if not self.api_key:
            print("\nCryptoRank API Status: Limited Mode")
            print("- Market data features will be disabled")
        else:
            self.test_connection()
            
    def test_connection(self):
        """Test API connection"""
        try:
            response = self._make_request('currencies', {'limit': 1})
            if response and 'data' in response:
                print("✓ CryptoRank API connection successful")
            else:
                print("✗ CryptoRank API connection failed")
        except Exception as e:
            print(f"✗ CryptoRank API error: {e}")
            
    def _make_request(self, endpoint: str, params: Dict[str, Any] = None):
        """Make HTTP request to API endpoint"""
        if not params:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"API request failed: {e}")
            return {'error': str(e)}
            
    def get_tokens(self):
        """Get tokens from CryptoRank API"""
        return self._make_request('currencies', {
            'limit': 1000,
            'sort': 'volume24h',
            'order': 'DESC'
        })

def fetch_tokens(api_key: str, sort_by='volume24h', direction='DESC', print_first=0):
    """Fetch tokens from CryptoRank API with specified sorting"""
    api = CryptoRankAPI(api_key)
    
    params = {
        'limit': 1000,  # Increased from 500 to 1000 to analyze more tokens
        'sort': sort_by,
        'order': direction
    }
    
    response = api.get_tokens()
    
    if 'error' in response:
        print(f"Error fetching tokens: {response['error']}")
        return None
        
    tokens = response.get('data', [])
    
    if print_first > 0:
        print(f"\nFirst {print_first} tokens sorted by {sort_by}:")
        for token in tokens[:print_first]:
            token_info = format_token_info(token)
            if token_info:  # Only print if formatting succeeded
                print_token_details(token_info)
            
    return tokens

def get_price_change(token: Dict) -> tuple:
    """Get price change and amount from token data"""
    try:
        # Get price and change directly from v2 API response
        price = float(token.get('price', 0))
        change = float(token.get('percentChange24h', 0))
        return change, price
        
    except (KeyError, ValueError, TypeError) as e:
        print(f"Error calculating price change: {str(e)}")
        return 0.0, 0.0

def format_token_info(token: Dict) -> Dict:
    """Format token information for consistent display"""
    try:
        # Extract and format data for v2 API response
        formatted = {
            'symbol': token['symbol'],
            'name': token['name'],
            'price': float(token.get('price', 0)),
            'volume24h': float(token.get('volume24h', 0)),
            'marketCap': float(token.get('marketCap', 0)),
            'priceChange24h': float(token.get('percentChange24h', 0))
        }
        
        return formatted
        
    except Exception as e:
        print(f"Error formatting token {token.get('symbol', 'UNKNOWN')}: {e}")
        return None

def calculate_activity_score(volume: float, mcap: float, price_change: float) -> int:
    """Calculate token activity score (0-100)"""
    # Volume/MCap component (0-50 points)
    volume_mcap_ratio = volume / mcap if mcap > 0 else 0
    volume_score = min(50, int(volume_mcap_ratio * 500))  # Scale up for better distribution
    
    # Price change component (0-50 points)
    abs_change = abs(price_change)
    change_score = min(50, int(abs_change * 2))  # 25% change = 50 points
    
    return volume_score + change_score

def print_token_details(token_info: Dict) -> None:
    """Print formatted token details"""
    direction = "🟢" if token_info['priceChange24h'] > 0 else "🔴"
    print(f"\n{direction} ${token_info['symbol']}")
    print(f"Price: ${token_info['price']:.6f} ({token_info['priceChange24h']:+.1f}%)")
    print(f"Volume: ${token_info['volume24h']/1e6:.1f}M")
    print(f"MCap: ${token_info['marketCap']/1e6:.1f}M")
    print(f"Activity Score: {calculate_activity_score(token_info['volume24h'], token_info['marketCap'], token_info['priceChange24h'])}/100")

def is_valid_price_change(price_change: float) -> bool:
    """Check if price change is within reasonable bounds"""
    return -30 <= price_change <= 30  # Filter out extreme price movements

def is_likely_stablecoin(token_info):
    """Check if token is likely a stablecoin based on price and name"""
    try:
        price = float(token_info['price'])
        symbol = str(token_info['symbol']).upper()
        name = str(token_info.get('name', '')).upper()
        
        # Price near $1
        if 0.95 <= price <= 1.05:
            # Common stablecoin indicators in name/symbol
            stablecoin_indicators = ['USD', 'USDT', 'USDC', 'DAI', 'BUSD', 'TUSD', 'USDD', 'FDUSD']
            return any(indicator in symbol or indicator in name for indicator in stablecoin_indicators)
        return False
    except (ValueError, TypeError, KeyError):
        return False  # If we can't parse the price, assume it's not a stablecoin

def analyze_volume_leaders(tokens, limit=5):
    """Analyze tokens with highest volume"""
    print("\n🚨 VOLUME LEADERS DETECTED 🚨")
    print("*ELAI's quantum processors analyzing market activity*\n")
    
    # Process top volume tokens
    leaders = []
    seen_symbols = set()
    
    for token in tokens[:limit*2]:  # Look at more tokens to account for filtering
        token_info = format_token_info(token)
        if not token_info:  # Skip if formatting failed
            continue
            
        symbol = token_info.get('symbol')
        if not symbol or symbol in seen_symbols:
            continue
            
        if is_likely_stablecoin(token_info):
            continue
            
        leaders.append(token_info)
        seen_symbols.add(symbol)
        
        if len(leaders) >= limit:
            break
    
    # Print details for each leader
    for token_info in leaders:
        print_token_details(token_info)

def filter_tokens_by_volume(tokens, min_volume_mcap_ratio=0.1):
    """Filter tokens by volume/mcap ratio"""
    filtered_tokens = []
    seen_symbols = set()
    
    for token in tokens:
        try:
            token_info = format_token_info(token)
            symbol = token_info['symbol']
            
            # Skip if already seen or likely stablecoin
            if symbol in seen_symbols or is_likely_stablecoin(token_info):
                continue
                
            # Calculate volume/mcap ratio
            mcap = float(token_info['marketCap'])
            volume = float(token_info['volume24h'])
            
            if mcap > 0:
                ratio = (volume / mcap) * 100  # Convert to percentage
                logger.info(f"Token: {symbol}, Volume: ${volume:,.2f}, MCap: ${mcap:,.2f}, V/MC: {ratio:.1f}%")
                if ratio >= min_volume_mcap_ratio * 100:  # More than 10% volume/mcap
                    filtered_tokens.append((ratio, token_info))
                    seen_symbols.add(symbol)
        except Exception as e:
            continue
    
    # Sort by ratio
    filtered_tokens.sort(key=lambda x: x[0], reverse=True)
    return filtered_tokens

def find_volume_anomalies(tokens, limit=10):
    """Find tokens with unusual volume patterns"""
    # Use shared filtering function with lower threshold for anomalies
    anomalies = filter_tokens_by_volume(tokens, min_volume_mcap_ratio=0.8)  # Lowered from 1.0 to 0.8
    return anomalies[:limit]

def find_volume_spikes(tokens, limit=20):
    """Find tokens with sudden volume increases"""
    try:
        # Format all tokens first
        formatted_tokens = []
        for token in tokens:
            token_info = format_token_info(token)
            if token_info:
                formatted_tokens.append(token_info)
        
        # Filter out stablecoins and tokens with invalid price changes
        filtered_tokens = [
            token for token in formatted_tokens
            if not is_likely_stablecoin(token) and is_valid_price_change(token['priceChange24h'])
        ]
        
        # Calculate scores
        scored_tokens = []
        for token in filtered_tokens:
            try:
                # Calculate volume/mcap ratio score (0-50 points)
                volume = float(token['volume24h'])
                mcap = float(token['marketCap'])
                if mcap == 0:  # Skip if market cap is 0
                    continue
                    
                ratio = volume / mcap
                ratio_score = min(50, ratio * 100)  # Cap at 50 points
                
                # Calculate price change score (0-50 points)
                price_change = abs(float(token['priceChange24h']))
                price_score = min(50, price_change)  # Cap at 50 points
                
                # Calculate total score
                total_score = ratio_score + price_score
                
                # Apply penalties
                if price_change > 40:  # Extreme volatility penalty
                    total_score *= 0.7
                if ratio < 0.1:  # Low volume penalty
                    total_score *= 0.8
                    
                scored_tokens.append((total_score, token))
                
            except Exception as e:
                print(f"Error scoring token {token['symbol']}: {e}")
                continue
                
        # Sort by score and return top tokens
        scored_tokens.sort(key=lambda x: x[0], reverse=True)
        return scored_tokens[:limit]
        
    except Exception as e:
        print(f"Error finding volume spikes: {e}")
        return []

def calculate_volume_score(token: Dict) -> float:
    """Calculate volume-based score (0-100) with strict criteria"""
    try:
        # Get base metrics
        volume = float(token.get('volume24h', 0) or 0)
        mcap = float(token.get('marketCap', 0) or 0)
        
        if mcap == 0:
            return 0
            
        # Calculate volume/mcap ratio (0-50 points)
        ratio = volume / mcap
        ratio_score = ratio * 100
        
        # Get price metrics
        price = float(token.get('price', 0) or 0)
        price_24h = float(token.get('price24h', price) or price)
        
        if price_24h == 0:
            return 0
            
        # Calculate price change (0-50 points)
        price_change = abs(price - price_24h) / price_24h * 100
        price_score = min(50, price_change)
        
        # Calculate total score
        total_score = ratio_score + price_score
        
        # Apply penalties
        if price_change > 40:  # Extreme volatility penalty
            total_score *= 0.7
        if ratio < 0.1:  # Low volume penalty
            total_score *= 0.8
            
        return round(total_score, 1)
        
    except Exception as e:
        print(f"Error calculating score: {e}")
        return 0

def calculate_volume_change(current_volume: float, previous_volume: float) -> float:
    """Calculate percentage change in volume
    
    Args:
        current_volume: Current 24h volume
        previous_volume: Previous 24h volume
        
    Returns:
        Percentage change in volume
    """
    if previous_volume == 0:
        return 0
    
    change = ((current_volume - previous_volume) / previous_volume) * 100
    return round(change, 2)

class VolumeStrategy:
    """Volume-based analysis strategy"""
    
    def __init__(self, api_key: str = None, llm = None):
        """Initialize strategy with optional LLM for enhanced insights"""
        self.api_key = api_key
        self.llm = llm
        self.recent_tokens = set()  # Track recently posted tokens
        
    def analyze(self) -> Dict:
        """Analyze volume patterns and return market data"""
        try:
            # Get tokens sorted by volume
            tokens = fetch_tokens(self.api_key, sort_by='volume24h', direction='DESC')
            if not tokens:
                print("No tokens found or error fetching tokens")
                return None

            # Format all tokens
            all_tokens = []
            for token in tokens:
                formatted = format_token_info(token)
                if formatted:
                    all_tokens.append(formatted)

            # Find volume spikes and anomalies
            spikes = find_volume_spikes(tokens)
            anomalies = find_volume_anomalies(tokens)
    
            # Filter out recently posted tokens
            filtered_spikes = []
            for spike in spikes:
                symbol = spike[1]['symbol']
                if symbol not in self.recent_tokens:
                    filtered_spikes.append(spike)
                    self.recent_tokens.add(symbol)
                    if len(filtered_spikes) >= 4:  # Show up to 4 spikes
                        break

            filtered_anomalies = []
            for anomaly in anomalies:
                symbol = anomaly[1]['symbol']
                if symbol not in self.recent_tokens:
                    filtered_anomalies.append(anomaly)
                    self.recent_tokens.add(symbol)
                    if len(filtered_anomalies) >= 1:  # Keep 1 anomaly to make total of 4
                        break
    
            # Reset token history if we're not finding new tokens
            if not filtered_spikes and not filtered_anomalies:
                print("Resetting token history to allow rotation")
                self.recent_tokens.clear()
                return self.analyze()
            
            # Format data for tweet generation and token history tracking
            return {
                'spikes': filtered_spikes,
                'anomalies': filtered_anomalies,
                'all_tokens': all_tokens  # Add all formatted tokens
            }
        
        except Exception as e:
            print(f"Error analyzing volume: {str(e)}")
            return None

    def format_twitter_output(self, spikes: list, anomalies: list, history: Dict = None) -> str:
        """Format output for Twitter (max 280 chars)"""
        tweet = ""
        shown_symbols = set()  # Track which symbols we've shown
        
        # Helper function to format token info
        def format_token_section(token, ratio, is_anomaly=False):
            # Strip any $ from the symbol
            symbol = token['symbol'].lstrip('$')
            if symbol in shown_symbols:
                return ""
                
            # Get price change
            high = float(token.get('high24h', 0))
            low = float(token.get('low24h', 0))
            price = float(token['price'])
            
            if high > 0 and low > 0:
                avg = (high + low) / 2
                price_change = ((price - avg) / avg) * 100
            else:
                price_change = 0
                
            direction = "🟢" if price_change > 0 else "🔴"
            volume = float(token.get('volume24h', token.get('volume', 0)))/1e6  # Convert to millions
            movement = get_movement_description(price_change)
            vol_mcap = ratio  # ratio is already a percentage
            
            section = f"{direction} ${symbol} DETECTED!\n"
            section += f"💰 ${price:.4f} {movement}\n"
            section += f"📊 Vol: ${volume:.1f}M\n"
            section += f"🎯 V/MC: {vol_mcap:.1f}%\n"
            
            return section
        
        # First add volume anomalies
        for ratio, token in anomalies:
            section = format_token_section(token, ratio, is_anomaly=True)
            if section and len(tweet + section) < 280:
                tweet += section
                shown_symbols.add(token['symbol'])
                
        # Then add volume spikes
        for ratio, token in spikes:
            section = format_token_section(token, ratio)
            if section and len(tweet + section) < 280:
                tweet += section
                shown_symbols.add(token['symbol'])
        
        return tweet.strip()

    def get_elai_insight(self, tokens) -> str:
        """Generate ELAI's insight based on the detected tokens"""
        if not tokens:
            return "ELAI: Market seems quiet... for now 🤫"
            
        try:
            # Get total volume and average price change
            total_volume = 0
            avg_change = 0
            count = 0
            token_data = []
            
            for token in tokens:
                try:
                    symbol = token[0]
                    volume = float(token[1]['volume24h'])
                    change = float(token[1]['priceChange24h'])
                    mcap = float(token[1].get('marketCap', 0))
                    
                    total_volume += volume
                    avg_change += change
                    count += 1
                    
                    token_data.append({
                        'symbol': symbol,
                        'volume': volume,
                        'change': change,
                        'mcap': mcap,
                        'vol_mcap_ratio': (volume/mcap*100) if mcap > 0 else 0
                    })
                except:
                    continue
                    
            if count == 0:
                return "ELAI: No significant volume patterns detected 🔍"
                
            avg_change = avg_change / count
            
            # Use LLM if available
            if self.llm:
                prompt = f"""You are ELAI, an AI crypto trading assistant analyzing market-wide volume patterns.
                Generate a short, insightful comment about the current market volume action:
                
                Overall Stats:
                - Total Volume: ${total_volume:,.0f}
                - Average Price Change: {avg_change:+.1f}%
                
                Top Tokens by Volume:
                {chr(10).join([f'${t["symbol"]}: {t["change"]:+.1f}%, Vol/MCap: {t["vol_mcap_ratio"]:.1f}%' for t in token_data[:3]])}
                
                Your insight should be:
                1. Start with "ELAI:"
                2. Focus on what the volume patterns suggest
                3. Include relevant emojis
                4. Under 100 characters
                
                Insight:"""
                
                try:
                    response = self.llm.generate(prompt)
                    if response:
                        return response.strip()
                except Exception as e:
                    print(f"LLM error, falling back to template: {e}")
            
            # Fall back to template-based insights
            if total_volume > 10_000_000_000:  # $10B+
                if avg_change > 5:
                    return "ELAI: Massive volume + green candles = opportunity? 🎯"
                elif avg_change < -5:
                    return "ELAI: Heavy volume on red candles... interesting 🤔"
                else:
                    return "ELAI: Huge volume spike detected! Stay alert 🔍"
            else:
                if avg_change > 5:
                    return "ELAI: Volume rising with price... watching closely 👀"
                elif avg_change < -5:
                    return "ELAI: Monitoring these dips with interest 📊"
                else:
                    return "ELAI: Unusual volume patterns detected 🧪"
                    
        except Exception as e:
            print(f"Error generating insight: {e}")
            return "ELAI: Analyzing volume patterns... 🔄"

def get_elai_message(change: float, volume_ratio: float) -> str:
    """Get ELAI's insight message based on price change and volume"""
    if change < -10 and volume_ratio > 500:
        return "ELAI detected a major setup forming 🎯"
    elif change < -5 and volume_ratio > 300:
        return "ELAI found a potential setup 💫"
    elif change > 10 and volume_ratio > 400:
        return "ELAI spotted unusual activity 👀"
    else:
        return "ELAI is analyzing the pattern 🔄"

def get_elai_insight(tokens) -> str:
    """Generate ELAI's insight based on the detected tokens"""
    # Get total volume and average price change
    total_volume = 0
    avg_change = 0
    count = 0
    
    for token in tokens:
        try:
            volume = float(token[1]['volume24h'])
            change = float(token[1]['priceChange24h'])
            total_volume += volume
            avg_change += change
            count += 1
        except:
            continue
            
    if count == 0:
        return "ELAI: Market seems quiet... for now 🤫"
        
    avg_change = avg_change / count
    
    # Generate insight based on volume and price action
    if total_volume > 10_000_000_000:  # $10B+
        if avg_change > 5:
            return "ELAI: Massive volume + green candles = opportunity? 🎯"
        elif avg_change < -5:
            return "ELAI: Heavy volume on red candles... interesting 🤔"
        else:
            return "ELAI: Huge volume spike detected! Stay alert 🔍"
    else:
        if avg_change > 5:
            return "ELAI: Volume rising with price... watching closely 👀"
        elif avg_change < -5:
            return "ELAI: Monitoring these dips with interest 📊"
        else:
            return "ELAI: Unusual volume patterns detected 🧪"

def get_opportunity_message() -> str:
    """Generate varied opportunity messages"""
    messages = [
        "ELAI senses opportunity 🧪",
        "ELAI's algorithms tingling 🔮",
        "ELAI detected something interesting 🎯",
        "ELAI's radar is beeping 📡",
        "ELAI found a potential setup 💫"
    ]
    return messages[int(datetime.datetime.now().timestamp()) % len(messages)]

def get_movement_description(change: float) -> str:
    """Get a descriptive term for the price movement"""
    if change > 30:
        return "🌙 Mooning"
    elif change > 3:
        return "🚀 Surging"
    elif change < -30:
        return "🩸 Bleeding"
    elif change < -3:
        return "📉 Dipping"
    else:
        return "➡️ Stable"

def test_volume_strategy():
    """Test the volume-based sorting strategy"""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\nTesting Volume Strategy...")
    api_key = os.getenv('CRYPTORANK_API_KEY')
    
    if not api_key:
        print("Error: No API key found in environment")
        return
        
    strategy = VolumeStrategy(api_key)
    
    # Test 1: First Analysis
    print("\nFirst Volume Post:")
    print("-" * 50)
    result1 = strategy.analyze()
    if result1:
        print(f"Found {len(result1['spikes'])} spikes and {len(result1['anomalies'])} anomalies")
        print("\nTokens in this batch:")
        for spike in result1['spikes']:
            print(f"Spike: {spike[1]['symbol']}")
        for anomaly in result1['anomalies']:
            print(f"Anomaly: {anomaly[1]['symbol']}")
            
        print("\nTweet Content:")
        print(strategy.format_twitter_output(result1['spikes'], result1['anomalies']))
    else:
        print("No results from first analysis")
    
    # Test 2: Second Analysis
    print("\nSecond Volume Post:")
    print("-" * 50)
    result2 = strategy.analyze()
    if result2:
        print(f"Found {len(result2['spikes'])} spikes and {len(result2['anomalies'])} anomalies")
        print("\nTokens in this batch:")
        for spike in result2['spikes']:
            print(f"Spike: {spike[1]['symbol']}")
        for anomaly in result2['anomalies']:
            print(f"Anomaly: {anomaly[1]['symbol']}")
            
        print("\nTweet Content:")
        print(strategy.format_twitter_output(result2['spikes'], result2['anomalies']))
    else:
        print("No results from second analysis")
        
    # Test 3: Third Analysis
    print("\nThird Volume Post:")
    print("-" * 50)
    print(f"Token history size before: {len(strategy.recent_tokens)}")
    result3 = strategy.analyze()
    print(f"Token history size after: {len(strategy.recent_tokens)}")
    
    if result3:
        print(f"Found {len(result3['spikes'])} spikes and {len(result3['anomalies'])} anomalies")
        print("\nTokens in this batch:")
        for spike in result3['spikes']:
            print(f"Spike: {spike[1]['symbol']}")
        for anomaly in result3['anomalies']:
            print(f"Anomaly: {anomaly[1]['symbol']}")
            
        print("\nTweet Content:")
        print(strategy.format_twitter_output(result3['spikes'], result3['anomalies']))
    else:
        print("No results from third analysis")
            
    print("\nVolume Strategy Test Complete")

if __name__ == "__main__":
    print("Warning: This is a module and should not be run directly.")
    print("Use the bot's main.py instead.")
