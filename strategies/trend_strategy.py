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
from custom_llm import MetaLlamaComponent

class TrendStrategy:
    """Analyzes market trends"""
    
    def __init__(self, api_key: str = None):
        """Initialize trend strategy"""
        self.api_key = api_key
        
    def analyze(self) -> Dict:
        """Analyze current market trends"""
        try:
            # Get trending tokens
            tokens = fetch_tokens(self.api_key, sort_by='priceChange24h', direction='DESC')
            if not tokens:
                print("No tokens found or error fetching tokens")
                return {'signal': 'neutral', 'confidence': 0.0}
                
            print("\nScanning for significant price moves (>5%):")
            print("-" * 50)
            
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
                            'vol_mcap_ratio': (volume / mcap * 100) if mcap > 0 else 0
                        })
                        
                    # Original high-engagement criteria
                    if (abs(price_change) > 5 and 
                        volume/mcap*100 > 20 and 
                        1_000_000 < mcap < 50_000_000_000):
                        trend_info.append(f"${symbol} {price_change:+.1f}% 🚀 Vol/MCap: {volume/mcap*100:.1f}%")
                        
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
                    print(f"Volume/MCap Ratio: {mover['vol_mcap_ratio']:.2f}%")
                    
            # Calculate overall trend signal based on top movers we're showing
            top_movers = big_movers[:5]  # Same as what we show in tweet
            up_moves = sum(1 for x in top_movers if x['price_change'] > 0)
            down_moves = len(top_movers) - up_moves
            
            signal = 'bullish' if up_moves > down_moves else 'bearish'
            confidence = abs(up_moves - down_moves) / len(top_movers) if top_movers else 0.0
            
            # Format trend tokens for tweet
            trend_tokens = []
            for mover in big_movers[:6]:  # Try top 6 movers
                trend_tokens.append(f"${mover['symbol']} {mover['price_change']:+.1f}% (${mover['mcap']/1e6:.1f}M) 🚀")
            
            return {
                'signal': signal,
                'confidence': confidence,
                'trend_tokens': trend_tokens
            }
            
        except Exception as e:
            print(f"Error analyzing trends: {str(e)}")
            return {'signal': 'neutral', 'confidence': 0.0}

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

def get_trend_insight(tokens: list) -> str:
    """Generate a brief market insight about trending tokens"""
    # Format token data for LLM
    token_info = []
    total_volume = 0
    for _, t in tokens[:3]:  # Just use top 3 tokens
        volume = float(t['volume'])
        total_volume += volume
        token_info.append({
            'symbol': t['symbol'],
            'price_change': f"{float(t['price_change']):+.1f}%",
            'volume': f"${volume/1e6:.1f}M"
        })
    
    # Create prompt with key metrics
    prompt = f"""Analyze these trending crypto tokens and give a very brief insight (max 100 chars):

Top Movers:
{', '.join(f"${t['symbol']} ({t['price_change']})" for t in token_info)}

Volumes:
{', '.join(f"${t['symbol']}: {t['volume']}" for t in token_info)}

Total Volume: ${total_volume/1e6:.1f}M

Focus on the most interesting metric or pattern. Add 1-2 relevant emojis."""

    # Generate insight using Llama
    insight = MetaLlamaComponent().generate(prompt, max_tokens=60)
    return insight if insight else "Market moves catching attention... 👀"

def format_twitter_output(trend_tokens: list) -> str:
    """Format output for Twitter"""
    tweet = "🚨 Market Movers Alert! 🚨\n\n"
    shown_symbols = set()
    
    for _, token in trend_tokens[:5]:  # Show top 5 movers
        symbol = token['symbol']
        if symbol in shown_symbols:
            continue
            
        direction = "🟢" if token['price_change'] > 0 else "🔴"
        price_change = float(token['price_change'])
        movement = get_movement_description(price_change)
        
        section = f"{direction} ${symbol}: {price_change:+.1f}% {movement}\n"
        
        if len(tweet + section) < 280:
            tweet += section
            shown_symbols.add(symbol)
            
    # Add ELAI's insight
    if price_change > 0:
        insight = "\nELAI: Bulls are charging! Keep an eye on these gems 💎"
    else:
        insight = "\nELAI: Dips detected! Time to do your research 🔍"
        
    if len(tweet + insight) < 280:
        tweet += insight
            
    return tweet.strip()

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
        
        # Format tweet like in ELAI
        if trend_info and trend_info.get('trend_tokens'):
            tweet = "🔥 Top Movers:\n" + "\n".join(trend_info['trend_tokens'])
            
            # Add volume insight
            volume_insight = "\n\n💡 High volume activity detected"
            if len(tweet + volume_insight) < 280:
                tweet += volume_insight
            
            # Add market sentiment without confidence
            sentiment = f"\n\nMarket is {trend_info['signal']} 📊"
            if len(tweet + sentiment) < 280:
                tweet += sentiment
                
            print("\nTweet Generated:")
            print("-" * 40)
            print(tweet)
            print("-" * 40)
            print(f"Character count: {len(tweet)}")
        else:
            print("No significant trends found")
            
    except Exception as e:
        print(f"Error testing trend strategy: {str(e)}")

def test_analyze():
    """Test just the analyze function"""
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    if not api_key:
        print("Error: CRYPTORANK_API_KEY not found in environment")
        return
        
    strategy = TrendStrategy(api_key)
    result = strategy.analyze()
    print("\nAnalyze result:", json.dumps(result, indent=2))
    
    # Format tweet from trend tokens
    if result.get('trend_tokens'):
        print("\nTWEET OUTPUT:")
        print("-" * 40)
        tweet = format_twitter_output([(1, {'symbol': t.split()[1], 
                                          'price': 0.0,
                                          'price_change': float(t.split()[2].strip('%')),
                                          'volume': 0.0}) for t in result['trend_tokens']])
        print(tweet)
        print("-" * 40)
        print(f"Character count: {len(tweet)}")

if __name__ == "__main__":
    test_analyze()
