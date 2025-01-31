"""Price trend and category analysis strategies"""

import os
import sys
import json
from pathlib import Path
import requests

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from typing import Dict, List
from dotenv import load_dotenv
from strategies.shared_utils import (
    fetch_tokens,
    filter_tokens_by_trend,
    format_token_info,
    is_likely_stablecoin,
    get_movement_description
)

class TrendStrategy:
    """Analyzes market trends"""
    
    def __init__(self, api_key: str = None):
        """Initialize trend strategy"""
        self.api_key = api_key
        
    def analyze(self) -> Dict:
        """Analyze current market trends"""
        try:
            # Get trending tokens
            tokens = fetch_tokens(self.api_key, sort_by='priceChange24h', direction='DESC', limit=500)
            if not tokens:
                print("No tokens found or error fetching tokens")
                return {'signal': 'neutral', 'confidence': 0.0, 'trend_tokens': []}
                
            print("\nScanning for significant price moves (>5%):")
            print("-" * 50)
            
            # Debug: Show top 5 price movements
            print("\nTop 5 price movements:")
            for i, token in enumerate(tokens[:5]):
                price_change = float(token.get('priceChange24h', 0))
                volume = float(token.get('volume24h', 0))
                mcap = float(token.get('marketCap', 0))
                vol_mcap_ratio = (volume/mcap*100) if mcap > 0 else 0
                print(f"{token['symbol']}: {price_change:+.1f}% (Vol/MCap: {vol_mcap_ratio:.1f}%)")
            
            # Format trend info
            trend_info = []
            big_movers = []
            
            for token in tokens:
                try:
                    symbol = token.get('symbol', '')
                    price_change = float(token.get('priceChange24h', 0))
                    volume = float(token.get('volume24h', 0))
                    price = float(token.get('price', 0))
                    mcap = float(token.get('marketCap', 0))
                    
                    # Track any big moves
                    if abs(price_change) > 5:
                        big_movers.append({
                            'symbol': symbol,
                            'price_change': price_change,
                            'volume': volume,
                            'mcap': mcap,
                            'price': price,
                            'vol_mcap_ratio': (volume / mcap * 100) if mcap > 0 else 0
                        })
                        
                except (ValueError, TypeError) as e:
                    continue
                    
            if big_movers:
                print(f"\nFound {len(big_movers)} tokens with >5% moves:")
                # Sort by absolute price change
                big_movers.sort(key=lambda x: abs(x['price_change']), reverse=True)
                
                for mover in big_movers[:10]:  # Show top 10 biggest moves
                    print(f"\n{mover['symbol']}:")
                    print(f"Price Change: {mover['price_change']:+.1f}%")
                    print(f"Volume: ${mover['volume']:,.0f}")
                    print(f"Market Cap: ${mover['mcap']:,.0f}")
                    
            # Calculate overall trend signal based on top movers we're showing
            top_movers = big_movers[:5]  # Same as what we show in tweet
            up_moves = sum(1 for x in top_movers if x['price_change'] > 0)
            down_moves = len(top_movers) - up_moves
            
            signal = 'bullish' if up_moves > down_moves else 'bearish'
            confidence = abs(up_moves - down_moves) / len(top_movers) if top_movers else 0.0
            
            # Return formatted trend data
            return {
                'signal': signal,
                'confidence': confidence,
                'trend_tokens': big_movers  # Return all big movers as trend tokens
            }
                
        except Exception as e:
            print(f"Error in trend analysis: {e}")
            return {'signal': 'neutral', 'confidence': 0.0, 'trend_tokens': []}

    def get_movement_icon(self, change: float) -> str:
        """Get icon for the price movement"""
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

    def format_twitter_output(self, trend_tokens: list) -> str:
        """Format output for Twitter (max 280 chars)"""
        if not trend_tokens:
            return None
            
        tweet = ""
        shown_symbols = set()
        trend_data = self.analyze()
        
        # Calculate market signal first
        signal = trend_data['signal']
        confidence = trend_data['confidence']
        signal_emoji = "🐂" if signal == "bullish" else "🐻"
        confidence_str = f"{confidence*100:.0f}%" if confidence > 0 else "Low"
        signal_str = f"\n\n{signal_emoji} Market: {signal.title()} ({confidence_str} conf)"
        
        # Show max 6 tokens to ensure room for market signal
        for token in trend_tokens[:6]:
            symbol = token.get('symbol', '')
            if symbol in shown_symbols:
                continue
                
            direction = "🟢" if token['price_change'] > 0 else "🔴"
            price = float(token['price'])
            
            # Format price with dynamic decimals based on size
            if price < 0.0001:
                price_str = f"${price:.8f}"
            elif price < 0.01:
                price_str = f"${price:.6f}"
            elif price < 1:
                price_str = f"${price:.4f}"
            else:
                price_str = f"${price:.2f}"
                
            movement_icon = self.get_movement_icon(token['price_change'])
            
            section = f"{direction} ${symbol} TRENDING! {movement_icon}\n"
            section += f"💰 {price_str} ({token['price_change']:+.1f}%)"
            
            if len(tweet + "\n" + section) < 280:
                if tweet:  # If not the first token, add a newline
                    tweet += "\n"
                tweet += section
                shown_symbols.add(symbol)
                
        # Add market signal at the end
        if len(tweet + signal_str) < 280:
            tweet += signal_str
            
        return tweet.strip()

def calculate_trend_score(token: Dict) -> float:
    """Calculate trend-based score (0-100) with strict criteria"""
    try:
        # Get base metrics
        volume = float(token.get('volume24h', 0) or 0)
        mcap = float(token.get('marketCap', 0) or 0)
        
        if mcap == 0 or mcap < 1_000_000:  # Minimum $1M market cap
            return 0
            
        # Calculate volume/mcap ratio (0-30 points)
        ratio = volume / mcap
        ratio_score = min(30, ratio * 100)
        
        # Get price metrics
        price = float(token.get('price', 0) or 0)
        price_24h = float(token.get('price24h', price) or price)
        
        if price_24h == 0:
            return 0
            
        # Calculate price change (0-70 points)
        price_change = abs(price - price_24h) / price_24h * 100
        price_score = min(70, price_change * 2)  # More weight on price change
        
        # Calculate total score
        total_score = ratio_score + price_score
        
        # Apply penalties
        if price_change > 40:  # Extreme volatility penalty
            total_score *= 0.7
        if ratio < 0.05:  # Very low volume penalty
            total_score *= 0.7
        if volume < 1_000_000:  # Minimum $1M volume
            total_score = 0
            
        return round(total_score, 1)
        
    except Exception as e:
        print(f"Error calculating trend score: {e}")
        return 0

def analyze_ai_tokens(tokens: List[Dict], limit: int = 3) -> List[Dict]:
    """Find and analyze AI-related tokens"""
    ai_keywords = ['ai', 'artificial', 'intelligence', 'neural', 'brain', 'machine', 'learning', 'gpt', 'llm', 'cognitive', 'deep']
    
    filtered_tokens = []
    seen_symbols = set()
    
    for token in tokens:
        try:
            # Skip if missing required fields
            if not all(key in token for key in ['name', 'symbol', 'price', 'percentChange24h']):
                continue
                
            token_info = format_token_info(token)
            if not token_info:  # Skip if formatting failed
                continue
                
            name = token_info['name'].lower()
            symbol = token_info['symbol'].lower()
            mcap = float(token_info['mcap'])
            volume = float(token_info['volume'])
            
            if symbol in seen_symbols or is_likely_stablecoin(token_info):
                continue
                
            if any(keyword in name or keyword in symbol for keyword in ai_keywords):
                trend_score = calculate_trend_score(token_info)
                if trend_score > 30 and volume > 100_000:  # Only require volume
                    token_info['trend_score'] = trend_score
                    filtered_tokens.append(token_info)
                    seen_symbols.add(symbol)
                    print(f"Found AI token: ${symbol.upper()} (Score: {trend_score:.1f})")
                    
        except Exception as e:
            print(f"Error processing token: {str(e)}")
            continue
            
    filtered_tokens.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
    return filtered_tokens[:limit]

def analyze_gaming_tokens(tokens: List[Dict], limit: int = 3) -> List[Dict]:
    """Find and analyze gaming-related tokens"""
    gaming_tokens = []
    gaming_keywords = ['game', 'gaming', 'play', 'metaverse', 'nft', 'guild']
    seen_symbols = set()
    
    for token in tokens:
        try:
            # Skip if missing required fields
            if not all(key in token for key in ['name', 'symbol', 'price', 'percentChange24h']):
                continue
                
            token_info = format_token_info(token)
            if not token_info:  # Skip if formatting failed
                continue
                
            name = token_info.get('name', '').lower()
            symbol = token_info.get('symbol', '').lower()
            mcap = float(token_info.get('mcap', 0))
            volume = float(token_info.get('volume', 0))
            
            if symbol in seen_symbols or is_likely_stablecoin(token_info):
                continue
                
            if any(keyword in name or keyword in symbol for keyword in gaming_keywords):
                trend_score = calculate_trend_score(token_info)
                if trend_score > 30 and volume > 100_000:
                    token_info['trend_score'] = trend_score
                    gaming_tokens.append(token_info)
                    seen_symbols.add(symbol)
                    print(f"Found gaming token: ${symbol.upper()} (Score: {trend_score:.1f})")
                    
        except Exception as e:
            print(f"Error processing gaming token: {str(e)}")
            continue
            
    gaming_tokens.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
    return gaming_tokens[:limit]

def analyze_meme_tokens(tokens: List[Dict], limit: int = 3) -> List[Dict]:
    """Find and analyze meme-related tokens"""
    meme_tokens = []
    meme_keywords = ['doge', 'shib', 'pepe', 'wojak', 'meme', 'chad', 'elon', 'cat', 'dog', 'inu', 'moon', 'safe', 'baby', 'erc404']
    seen_symbols = set()
    
    for token in tokens:
        try:
            # Skip if missing required fields
            if not all(key in token for key in ['name', 'symbol', 'price', 'percentChange24h']):
                continue
                
            token_info = format_token_info(token)
            if not token_info:  # Skip if formatting failed
                continue
                
            name = token_info.get('name', '').lower()
            symbol = token_info.get('symbol', '').lower()
            mcap = float(token_info.get('mcap', 0))
            volume = float(token_info.get('volume', 0))
            
            if symbol in seen_symbols or is_likely_stablecoin(token_info):
                continue
                
            if any(keyword in name or keyword in symbol for keyword in meme_keywords):
                trend_score = calculate_trend_score(token_info)
                if trend_score > 30 and volume > 100_000:
                    token_info['trend_score'] = trend_score
                    meme_tokens.append(token_info)
                    seen_symbols.add(symbol)
                    print(f"Found meme token: ${symbol.upper()} (Score: {trend_score:.1f})")
                    
        except Exception as e:
            print(f"Error processing meme token: {str(e)}")
            continue
            
    meme_tokens.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
    return meme_tokens[:limit]

def analyze_memeai_tokens(tokens: List[Dict], limit: int = 3) -> List[Dict]:
    """Find and analyze meme+AI hybrid tokens"""
    ai_keywords = ['ai', 'artificial', 'intelligence', 'neural', 'brain', 'machine', 'learning', 'gpt', 'llm', 'cognitive']
    meme_keywords = ['meme', 'doge', 'shib', 'pepe', 'wojak', 'chad', 'inu', 'elon', 'moon', 'frog', 'cat', 'dog', 'coin', 'safe', 'baby']
    
    filtered_tokens = []
    seen_symbols = set()
    
    for token in tokens:
        if len(filtered_tokens) >= limit:
            break
            
        token_info = format_token_info(token)
        if not token_info:  # Skip if formatting failed
            continue
            
        name = token_info['name'].lower()
        symbol = token_info['symbol'].lower()
        mcap = float(token_info['mcap'])
        volume = float(token_info['volume'])
        
        if symbol in seen_symbols or is_likely_stablecoin(token_info):
            continue
            
        # Check if token has both AI and meme keywords
        has_ai = any(keyword in name or keyword in symbol for keyword in ai_keywords)
        has_meme = any(keyword in name or keyword in symbol for keyword in meme_keywords)
        
        if has_ai and has_meme:
            trend_score = calculate_trend_score(token_info)
            if trend_score > 30 and volume > 100_000:  # Only require volume
                token_info['trend_score'] = trend_score
                filtered_tokens.append(token_info)
                seen_symbols.add(symbol)
                print(f"Found meme+AI token: ${symbol.upper()} (Score: {trend_score:.1f})")
    
    filtered_tokens.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
    return filtered_tokens[:limit]

def test_trend_strategy():
    """Test the trend-based analysis strategy"""
    try:
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('CRYPTORANK_API_KEY')
        
        if not api_key:
            print("Error: CRYPTORANK_API_KEY not found in environment variables")
            return
            
        print("\nTesting Trend Strategy...")
        strategy = TrendStrategy(api_key)
        trend_info = strategy.analyze()
        
        # Format tweet using our formatter
        if trend_info and trend_info.get('trend_tokens'):
            tweet = strategy.format_twitter_output(trend_info['trend_tokens'])
            
            if tweet:
                print("\nTweet Generated:")
                print("-" * 40)
                print(tweet)
                print("-" * 40)
                print(f"Character count: {len(tweet)}")
            else:
                print("No tweet generated")
        else:
            print("No significant trends found")
            
    except Exception as e:
        print(f"Error testing trend strategy: {str(e)}")

def test_analyze():
    """Test just the analyze function"""
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    
    print("\nTesting just analyze()...")
    strategy = TrendStrategy(api_key)
    result = strategy.analyze()
    print("\nAnalyze result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    test_analyze()
