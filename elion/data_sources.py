"""
Data sources integration for Elion AI using CryptoRank API
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import requests
from dotenv import load_dotenv
import feedparser
import tweepy
from collections import defaultdict
from .data_storage import DataStorage
import sys
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_llm import MetaLlamaComponent

class CryptoRankAPI:
    """CryptoRank API wrapper"""
    
    def __init__(self):
        """Initialize the API wrapper"""
        try:
            load_dotenv()  # Try to load .env file, but don't fail if it doesn't exist
        except:
            pass  # In Railway, env vars are already set
            
        self.api_key = os.getenv('CRYPTORANK_API_KEY')
        if not self.api_key:
            raise ValueError("CRYPTORANK_API_KEY environment variable is not set")
            
        self.base_url = 'https://api.cryptorank.io/v1'  # Changed to v1
        print(f"Using API key: {self.api_key[:10]}...")  # Print first 10 chars
        self._cache = {}

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the API"""
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        try:
            # Make request
            response = requests.get(url, params=params)
            
            # Print debug info
            print(f"\nAPI Request:")
            print(f"URL: {url}")
            print(f"Status: {response.status_code}")
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                print(f"Got {len(data.get('data', []))} coins")
                return data
                
            # Handle errors
            print(f"Error: {response.text}")
            return {'error': f'API error: {response.status_code}'}
            
        except Exception as e:
            print(f"Request failed: {e}")
            return {'error': str(e)}

    def _get_cached_response(self, endpoint: str) -> Optional[Dict]:
        """Get cached response for an endpoint"""
        if endpoint in self._cache:
            print(f"Using cached response for {endpoint}")
            return self._cache[endpoint]
        return None

    def _cache_response(self, endpoint: str, data: Dict):
        """Cache response data"""
        self._cache[endpoint] = data

    def get_currencies(self, limit: int = 100) -> List[Dict]:
        """Get list of currencies with market data"""
        params = {
            'limit': limit,
            'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
        }
        
        response = self._make_request('currencies', params=params)
        data = response.get('data', [])
        
        if not data:
            print("No coins found in response")
            return []
            
        return data

    def get_alpha_opportunities(self, limit: int = 100) -> List[Dict]:
        """
        Get potential alpha opportunities based on:
        - Market cap between $1M and $100M
        - 24h volume > $100K
        - Significant price movement (>5% in 24h)
        - Recent listing date (within last 3 months)
        """
        # Get a larger sample size to filter from
        params = {
            'limit': 30,  # Reduced from 500 to save credits
            'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
        }
        response = self._make_request('currencies', params)
        coins = response.get('data', [])
        
        opportunities = []
        for coin in coins:
            try:
                # Extract metrics
                market_cap = float(coin.get('marketCap', 0))
                volume_24h = float(coin.get('volume24h', 0))
                price_change_24h = float(coin.get('percentChange24h', 0))
                price_change_7d = float(coin.get('percentChange7d', 0))
                
                # Apply filters
                if (1_000_000 <= market_cap <= 100_000_000 and  # Market cap between $1M and $100M
                    volume_24h >= 100_000 and  # Volume over $100K
                    abs(price_change_24h) >= 5 and  # Significant price movement
                    abs(price_change_7d) >= 10):  # Sustained momentum
                    
                    opportunities.append({
                        'symbol': coin.get('symbol', ''),
                        'name': coin.get('name', ''),
                        'price': float(coin.get('price', 0)),
                        'market_cap': market_cap,
                        'volume_24h': volume_24h,
                        'price_change_24h': price_change_24h,
                        'price_change_7d': price_change_7d,
                        'opportunity_type': 'emerging_momentum'
                    })
            except (ValueError, TypeError, AttributeError) as e:
                print(f"Error processing coin {coin.get('symbol', 'UNKNOWN')}: {e}")
                continue
                
        # Sort by combination of volume growth and price momentum
        opportunities.sort(key=lambda x: (x['volume_24h'] * abs(x['price_change_24h'])), reverse=True)
        return opportunities[:10]  # Return top 10 opportunities

    def get_shill_opportunities(self, limit: int = 100) -> List[Dict]:
        """
        Get potential shill opportunities based on:
        - Market cap under $50M
        - 24h volume between $100K and $1M
        - Price stability (not too volatile)
        - Strong fundamentals
        """
        # Get a larger sample size to filter from
        params = {
            'limit': 20,  # Reduced from 500 to save credits
            'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
        }
        response = self._make_request('currencies', params)
        coins = response.get('data', [])
        
        opportunities = []
        for coin in coins:
            try:
                # Extract metrics safely with proper error handling
                try:
                    market_cap = float(coin.get('marketCap', 0))
                    volume_24h = float(coin.get('volume24h', 0))
                    price = float(coin.get('price', 0))
                    
                    # Skip if no market cap or volume
                    if market_cap <= 0 or volume_24h <= 0:
                        continue
                        
                    # Get percent changes safely
                    changes = coin.get('percentChange24h', 0), coin.get('percentChange7d', 0)
                    if not changes:
                        continue
                        
                    price_change_24h = float(changes[0])
                    price_change_7d = float(changes[1])
                except (ValueError, TypeError):
                    continue
                
                # Apply filters
                if (market_cap <= 50_000_000 and  # Market cap under $50M
                    100_000 <= volume_24h <= 1_000_000 and  # Volume between $100K and $1M
                    abs(price_change_24h) <= 10 and  # Not too volatile
                    abs(price_change_7d) <= 20):  # Relatively stable
                    
                    opportunities.append({
                        'symbol': coin.get('symbol', ''),
                        'name': coin.get('name', ''),
                        'price': price,
                        'market_cap': market_cap,
                        'volume_24h': volume_24h,
                        'price_change_24h': price_change_24h,
                        'price_change_7d': price_change_7d,
                        'opportunity_type': 'undervalued_gem'
                    })
            except Exception as e:
                # Skip any coins that cause errors
                continue
                
        # Sort by volume to market cap ratio, but handle zero market caps
        opportunities.sort(key=lambda x: x['volume_24h'] / (x['market_cap'] or 1), reverse=True)
        return opportunities[:10]  # Return top 10 opportunities

class DataSources:
    """Data sources for Elion"""
    
    def __init__(self):
        """Initialize data sources"""
        try:
            load_dotenv()  # Try to load .env file, but don't fail if it doesn't exist
        except:
            pass  # In Railway, env vars are already set
            
        # Initialize LLM with working configuration
        api_url = "https://api-user.ai.aitech.io/api/v1/user/products/209/use/chat/completions"
        model_name = "Meta-Llama-3.3-70B-Instruct"
        access_token = "QcKYEB9n875ZniLkBgfPf4t8eywevB6CpSKVj7pQrtUvQeWN47fzJwjKAbGtQ3ch"
        
        self.llm = MetaLlamaComponent(
            api_key=access_token,
            api_base=api_url
        )
        
        # Initialize CryptoRank API (optional)
        self.crypto_rank_api_key = os.getenv('CRYPTORANK_API_KEY')
        self.crypto_rank_base_url = "https://api.cryptorank.io/v1"
        
        # Cache for API responses
        self._cache = {}
        
        # Initialize CryptoRank API
        if self.crypto_rank_api_key:
            self.cryptorank_api = CryptoRankAPI()
        else:
            self.cryptorank_api = None
        
        # Initialize data caches with timestamps
        self.cache = {
            'market_data': {'data': None, 'timestamp': None},
            'trending': {'data': None, 'timestamp': None},
            'token_unlocks': {'data': None, 'timestamp': None},
            'funding_rounds': {'data': None, 'timestamp': None},
            'news': {'data': None, 'timestamp': None}
        }
        
        # Configure data sources
        self.news_feeds = [
            'https://cointelegraph.com/rss',
            'https://cryptonews.com/news/feed/',
            'https://decrypt.co/feed'
        ]
        
        self.key_influencers = [
            'VitalikButerin',
            'cz_binance',
            'elonmusk',
            'CryptoCapo_',
            'inversebrah',
            'AltcoinGordon',
            'CryptoCred'
        ]
        
        # Cache durations
        self.cache_durations = {
            'market_data': timedelta(minutes=5),
            'trending': timedelta(hours=1),
            'token_unlocks': timedelta(hours=6),
            'funding_rounds': timedelta(hours=12),
            'news': timedelta(hours=1)
        }

    def _is_stablecoin(self, symbol: str, price: float, price_change_24h: float) -> bool:
        """Check if a coin is likely a stablecoin"""
        # Common stablecoin symbols
        stablecoin_symbols = {'USDT', 'USDC', 'DAI', 'BUSD', 'UST', 'TUSD', 'USDP', 'USDD'}
        
        # Check symbol
        if symbol.upper() in stablecoin_symbols:
            return True
            
        # Check price and volatility
        if price is not None and price_change_24h is not None:
            if 0.95 <= price <= 1.05 and abs(price_change_24h) < 1:
                return True
                
        return False

    def get_market_data(self) -> Dict:
        """Get market data from CryptoRank"""
        try:
            # Get currencies data from CryptoRank
            response = self.cryptorank_api._make_request('currencies', {
                'limit': 20,  # Reduced from 25 to save credits
                'convert': 'USD'
            })
            
            if 'error' in response:
                return {'error': response['error']}
                
            # Extract data
            data = response.get('data', [])
            if not data:
                return {'error': 'No data found'}
                
            # Process all coins first
            processed_coins = []
            for coin in data:
                try:
                    symbol = coin['symbol']
                    values = coin.get('values', {}).get('USD', {})
                    
                    price = float(values.get('price', 0))
                    change_24h = float(values.get('percentChange24h', 0))
                    volume = float(values.get('volume24h', 0))
                    mcap = float(values.get('marketCap', 0))
                    
                    # Skip invalid data
                    if price <= 0 or mcap <= 0:
                        continue
                        
                    # Skip stablecoins and major coins
                    if self._is_stablecoin(symbol, price, change_24h) or symbol in ['BTC', 'ETH', 'BNB', 'SOL']:
                        continue
                        
                    # Gem criteria:
                    # 1. >30% price increase
                    # 2. Market cap between $5M and $100M
                    # 3. 24h volume > $1M
                    if (change_24h >= 30 and 
                        5_000_000 <= mcap <= 100_000_000 and
                        volume >= 1_000_000):
                        processed_coins.append({
                            'symbol': symbol,
                            'price': price,
                            'change_24h': change_24h,
                            'volume': volume,
                            'mcap': mcap
                        })
                except (ValueError, TypeError) as e:
                    print(f"Error processing coin {coin.get('symbol')}: {e}")
                    continue
                    
            # Sort by combination of market cap and volume
            processed_coins.sort(key=lambda x: (x['change_24h'], x['volume']), reverse=True)
            
            # Get BTC/ETH data
            btc = next((c for c in data if c['symbol'] == 'BTC'), None)
            eth = next((c for c in data if c['symbol'] == 'ETH'), None)
            
            if not btc or not eth:
                return {'error': 'BTC or ETH data not found'}
                
            # Format BTC/ETH data
            btc_data = {
                'price': float(btc.get('values', {}).get('USD', {}).get('price', 0)),
                'change_24h': float(btc.get('values', {}).get('USD', {}).get('percentChange24h', 0)),
                'volume': float(btc.get('values', {}).get('USD', {}).get('volume24h', 0)),
                'mcap': float(btc.get('values', {}).get('USD', {}).get('marketCap', 0))
            }
            eth_data = {
                'price': float(eth.get('values', {}).get('USD', {}).get('price', 0)),
                'change_24h': float(eth.get('values', {}).get('USD', {}).get('percentChange24h', 0))
            }
            
            # Print debug info for top performers
            print("\nTop Performing Coins:")
            for coin in processed_coins[:3]:
                print(f"{coin['symbol']}: ${coin['price']:.4f} | +{coin['change_24h']:.1f}% | Vol: ${coin['volume']:,.0f} | MCap: ${coin['mcap']:,.0f}")
            
            # Format market data
            market_data = {
                'btc_price': btc_data['price'],
                'eth_price': eth_data['price'],
                'btc_change_24h': btc_data['change_24h'],
                'eth_change_24h': eth_data['change_24h'],
                'total_mcap': sum(float(c.get('values', {}).get('USD', {}).get('marketCap', 0)) for c in data),
                'total_volume': sum(float(c.get('values', {}).get('USD', {}).get('volume24h', 0)) for c in data),
                'market_sentiment': self._get_market_sentiment(btc_data),
                'top_gainers': processed_coins[:3]  # Include top 3 performing coins
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error getting market data: {e}")
            return {'error': str(e)}

    def _get_market_sentiment(self, btc_data: Dict) -> str:
        """Get market sentiment based on BTC performance"""
        try:
            change_24h = float(btc_data.get('change_24h', 0))
            volume_24h = float(btc_data.get('volume', 0))
            market_cap = float(btc_data.get('mcap', 0))
            
            # Volume to market cap ratio
            volume_mcap_ratio = volume_24h / market_cap if market_cap > 0 else 0
            
            # Determine sentiment
            if change_24h >= 5 and volume_mcap_ratio >= 0.1:
                return 'BULLISH'
            elif change_24h <= -5 and volume_mcap_ratio >= 0.1:
                return 'BEARISH'
            elif abs(change_24h) >= 2:
                return 'VOLATILE'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            return 'NEUTRAL'

    def get_alpha_opportunities(self) -> List[Dict]:
        """Get potential alpha opportunities from CryptoRank"""
        try:
            # Get top 30 coins by volume
            params = {
                'limit': 30,  # Reduced from 500 to save credits
                'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
            }
            
            response = self.cryptorank_api._make_request('currencies', params)
            if not response or 'data' not in response:
                print("No data received from API")
                return []
                
            opportunities = []
            for coin in response['data']:
                try:
                    # Extract basic info
                    name = coin.get('name', '').encode('ascii', 'ignore').decode()  # Remove non-ASCII chars
                    symbol = coin.get('symbol', '').encode('ascii', 'ignore').decode()
                    price = float(coin.get('price', 0))
                    market_cap = float(coin.get('marketCap', 0))
                    volume_24h = float(coin.get('volume24h', 0))
                    
                    # Skip if missing essential data
                    if not all([name, symbol, price > 0, market_cap > 0, volume_24h > 0]):
                        continue
                        
                    # Extract price changes (already in percentage)
                    changes = coin.get('percentChange24h', 0), coin.get('percentChange7d', 0)
                    if not changes:
                        continue
                        
                    price_change_24h = float(changes[0])
                    price_change_7d = float(changes[1])
                    
                    # Skip stablecoins
                    if self._is_stablecoin(symbol, price, price_change_24h):
                        continue
                        
                    # Skip unrealistic price changes
                    if abs(price_change_24h) > 200 or abs(price_change_7d) > 400:
                        continue
                        
                    # Calculate volume to market cap ratio
                    volume_to_mcap = volume_24h / market_cap if market_cap > 0 else 0
                    
                    # Apply filters - looking for strong movers with good volume
                    if (5_000_000 <= market_cap <= 150_000_000 and     # $5M to $150M mcap
                        volume_24h >= 3_000_000 and                     # >$3M volume
                        volume_to_mcap >= 0.08 and                      # Volume at least 8% of mcap
                        price_change_24h >= 20 and                      # >20% price gain in 24h
                        price_change_24h <= 200):                       # <200% to avoid P&Ds
                        
                        opportunities.append({
                            'name': name,
                            'symbol': symbol,
                            'price': price,
                            'market_cap': market_cap,
                            'volume_24h': volume_24h,
                            'price_change_24h': price_change_24h,
                            'price_change_7d': price_change_7d,
                            'volume_to_mcap': volume_to_mcap
                        })
                        
                except (TypeError, ValueError) as e:
                    print(f"Error processing coin {coin.get('symbol', 'UNKNOWN')}: {str(e)}")
                    continue
                    
            # Sort by combination of price change and volume
            opportunities.sort(key=lambda x: (x['price_change_24h'] * x['volume_to_mcap']), reverse=True)
            return opportunities[:10]  # Return top 10
            
        except Exception as e:
            print(f"Error in get_alpha_opportunities: {str(e)}")
            return []
            
    def get_shill_opportunities(self) -> Dict:
        """Get shill review opportunities"""
        try:
            # Get currencies data from CryptoRank
            response = self.cryptorank_api._make_request('currencies', {
                'limit': 20,  # Reduced from 100 to save credits
                'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
            })
            
            if 'error' in response:
                return {'error': response['error']}
                
            # Extract data
            data = response.get('data', [])
            if not data:
                return {'error': 'No data found'}
                
            # If symbol provided, find that specific coin
            coins = sorted(data, key=lambda x: float(x.get('priceChange24h', 0)), reverse=True)[:5]
                
            # Format review data
            reviews = []
            for coin in coins:
                if self._is_stablecoin(coin['symbol'], float(coin.get('price', 0)), float(coin.get('priceChange24h', 0))):
                    continue
                    
                review = {
                    'project': {
                        'symbol': coin['symbol'],
                        'name': coin.get('name', '')
                    },
                    'metrics': {
                        'price': float(coin.get('price', 0)),
                        'price_change_24h': float(coin.get('priceChange24h', 0)),
                        'price_change_7d': float(coin.get('priceChange7d', 0)),
                        'market_cap': float(coin.get('marketCap', 0)) / 1e6,  # Convert to millions
                        'volume_24h': float(coin.get('volume24h', 0)) / 1e6,  # Convert to millions
                        'volume_to_mcap': float(coin.get('volume24h', 0)) / float(coin.get('marketCap', 1))
                    }
                }
                reviews.append(review)
                
            return reviews[0] if reviews else {'error': 'No suitable tokens found'}
            
        except Exception as e:
            print(f"Error getting shill opportunities: {e}")
            return {'error': str(e)}

    def get_market_search(self, query: str) -> Dict:
        """Search for market data"""
        try:
            # Get currencies data from CryptoRank
            response = self.cryptorank_api._make_request('currencies', {
                'limit': 30,  # Reduced from 200 to save credits
                'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
            })
            
            if 'error' in response:
                return {'error': response['error']}
                
            # Extract data
            data = response.get('data', [])
            if not data:
                return {'error': 'No data found'}
                
            # Filter results by query
            query = query.lower()
            results = []
            for coin in data:
                try:
                    # Check if coin matches query
                    symbol = coin['symbol'].lower()
                    name = coin.get('name', '').lower()
                    category = coin.get('category', '').lower()
                    
                    if (query in symbol or query in name or query in category):
                        # Skip stablecoins
                        if self._is_stablecoin(coin['symbol'], float(coin.get('price', 0)), float(coin.get('priceChange24h', 0))):
                            continue
                            
                        # Format coin data
                        results.append({
                            'symbol': coin['symbol'],
                            'name': coin.get('name', ''),
                            'price': float(coin.get('price', 0)),
                            'price_change_24h': float(coin.get('priceChange24h', 0)),
                            'volume_24h': float(coin.get('volume24h', 0)),
                            'market_cap': float(coin.get('marketCap', 0)),
                            'category': coin.get('category', '')
                        })
                except (ValueError, TypeError) as e:
                    print(f"Error processing coin {coin.get('symbol')}: {e}")
                    continue
                    
            # Sort by combination of market cap and volume
            results.sort(key=lambda x: (x['market_cap'] * x['volume_24h']), reverse=True)
            
            # Print debug info
            print(f"\nSearch Results for '{query}':")
            for coin in results[:5]:
                print(f"{coin['symbol']}: ${coin['price']:.4f} | {coin['price_change_24h']:+.1f}% | MCap: ${coin['market_cap']:,.0f}")
            
            return {
                'query': query,
                'results': results[:5],  # Return top 5 results
                'total_found': len(results)
            }
            
        except Exception as e:
            print(f"Error searching market data: {e}")
            return {'error': str(e)}

    def _get_market_condition(self, data: List[Dict]) -> Tuple[str, float, float]:
        """Determine market condition based on BTC performance"""
        try:
            # Get BTC data
            btc_data = next((coin for coin in data if coin['symbol'] == 'BTC'), None)
            if not btc_data:
                return 'NEUTRAL', 0, 0
                
            # Get price changes
            btc_24h = btc_data.get('priceChange24h', 0)
            btc_7d = btc_data.get('priceChange7d', 0)
            
            # Determine market condition
            if btc_24h >= 5 or btc_7d >= 10:
                condition = 'HOT'
            elif btc_24h <= -5 or btc_7d <= -10:
                condition = 'COLD'
            else:
                condition = 'NEUTRAL'
                
            return condition, btc_24h, btc_7d
            
        except Exception as e:
            print(f"Error getting market condition: {e}")
            return 'NEUTRAL', 0, 0

    def get_shill_review(self, symbol: str = None) -> Dict:
        """Get shill review data for a token"""
        try:
            # Get currencies data from CryptoRank
            response = self.cryptorank_api._make_request('currencies', {
                'limit': 20,  # Reduced from 100 to save credits
                'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
            })
            
            if 'error' in response:
                return {'error': response['error']}
                
            # Extract data
            data = response.get('data', [])
            if not data:
                return {'error': 'No data found'}
                
            # If symbol provided, find that specific coin
            if symbol:
                coin = next((c for c in data if c['symbol'].lower() == symbol.lower()), None)
                if not coin:
                    return {'error': f'Token {symbol} not found'}
                coins = [coin]
            else:
                # Otherwise get top gainers
                coins = sorted(data, key=lambda x: float(x.get('priceChange24h', 0)), reverse=True)[:5]
                
            # Format review data
            reviews = []
            for coin in coins:
                if self._is_stablecoin(coin['symbol'], float(coin.get('price', 0)), float(coin.get('priceChange24h', 0))):
                    continue
                    
                review = {
                    'project': {
                        'symbol': coin['symbol'],
                        'name': coin.get('name', '')
                    },
                    'metrics': {
                        'price': float(coin.get('price', 0)),
                        'price_change_24h': float(coin.get('priceChange24h', 0)),
                        'price_change_7d': float(coin.get('priceChange7d', 0)),
                        'market_cap': float(coin.get('marketCap', 0)) / 1e6,  # Convert to millions
                        'volume_24h': float(coin.get('volume24h', 0)) / 1e6,  # Convert to millions
                        'volume_to_mcap': float(coin.get('volume24h', 0)) / float(coin.get('marketCap', 1))
                    }
                }
                reviews.append(review)
                
            return reviews[0] if reviews else {'error': 'No suitable tokens found'}
            
        except Exception as e:
            print(f"Error getting shill review: {e}")
            return {'error': str(e)}

    def get_latest_news(self) -> List[Dict]:
        """Get latest news from RSS feeds and cache"""
        try:
            # Check cache first
            if (self.cache['news']['data'] and 
                self.cache['news']['timestamp'] > datetime.utcnow() - self.cache_durations['news']):
                return self.cache['news']['data']
            
            news_items = []
            for feed_url in self.news_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:  # Get latest 5 from each feed
                        news_items.append({
                            'title': entry.get('title', ''),
                            'summary': entry.get('summary', ''),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'source': feed_url
                        })
                except Exception as e:
                    print(f"Error parsing feed {feed_url}: {e}")
                    continue
            
            # Sort by published date (newest first)
            news_items.sort(key=lambda x: x['published'], reverse=True)
            
            # Cache the results
            self.cache['news'] = {
                'data': news_items,
                'timestamp': datetime.utcnow()
            }
            
            return news_items
            
        except Exception as e:
            print(f"Error getting latest news: {e}")
            return []

    def _get_viral_tweets(self, limit: int = 10) -> List[Dict]:
        """Get viral tweets from followed accounts"""
        try:
            # Get tweets from key influencers
            viral_tweets = []
            
            # Define viral thresholds
            viral_thresholds = {
                'likes': 1000,
                'retweets': 100,
                'replies': 50
            }
            
            # Search tweets from each influencer
            for influencer in self.key_influencers:
                try:
                    # Search recent tweets from this influencer
                    tweets = self._search_tweets(f"from:{influencer}", limit=20)
                    
                    # Filter for viral tweets
                    for tweet in tweets:
                        if (tweet.get('likes', 0) >= viral_thresholds['likes'] or
                            tweet.get('retweets', 0) >= viral_thresholds['retweets'] or
                            tweet.get('replies', 0) >= viral_thresholds['replies']):
                            viral_tweets.append(tweet)
                            
                except Exception as e:
                    print(f"Error getting tweets from {influencer}: {e}")
                    continue
            
            # Sort by engagement (likes + retweets * 2 + replies * 3)
            viral_tweets.sort(
                key=lambda x: (
                    x.get('likes', 0) + 
                    x.get('retweets', 0) * 2 + 
                    x.get('replies', 0) * 3
                ),
                reverse=True
            )
            
            return viral_tweets[:limit]
            
        except Exception as e:
            print(f"Error getting viral tweets: {e}")
            return []

    def _search_tweets(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for tweets using Twitter API"""
        try:
            # Initialize Twitter client
            client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_CLIENT_ID'),
                consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            
            # Search tweets
            tweets = client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not tweets.data:
                return []
                
            return [tweet.data for tweet in tweets.data]
            
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return []

    def get_market_search(self, query: str) -> Dict:
        """Search for market data"""
        try:
            # Get currencies data from CryptoRank
            response = self.cryptorank_api._make_request('currencies', {
                'limit': 30,  # Reduced from 200 to save credits
                'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
            })
            
            if 'error' in response:
                return {'error': response['error']}
                
            # Extract data
            data = response.get('data', [])
            if not data:
                return {'error': 'No data found'}
                
            # Filter results by query
            query = query.lower()
            results = []
            for coin in data:
                if (query in coin['symbol'].lower() or 
                    query in coin.get('name', '').lower()):
                    results.append({
                        'symbol': coin['symbol'],
                        'name': coin.get('name', ''),
                        'price': float(coin.get('price', 0)),
                        'price_change_24h': float(coin.get('priceChange24h', 0)),
                        'volume_24h': float(coin.get('volume24h', 0)) / 1e6,  # Convert to millions
                        'market_cap': float(coin.get('marketCap', 0)) / 1e6  # Convert to millions
                    })
                    
            # Sort by market cap
            results.sort(key=lambda x: x['market_cap'], reverse=True)
            
            return {
                'query': query,
                'results': results[:5],  # Return top 5 results
                'total_found': len(results)
            }
            
        except Exception as e:
            print(f"Error searching market data: {e}")
            return {'error': str(e)}
            
    def get_shill_review(self, symbol: str = None) -> Dict:
        """Get shill review data for a token"""
        try:
            # Get currencies data from CryptoRank
            response = self.cryptorank_api._make_request('currencies', {
                'limit': 20,  # Reduced from 100 to save credits
                'includeFields': 'price,marketCap,volume24h,percentChange24h,percentChange7d'
            })
            
            if 'error' in response:
                return {'error': response['error']}
                
            # Extract data
            data = response.get('data', [])
            if not data:
                return {'error': 'No data found'}
                
            # If symbol provided, find that specific coin
            if symbol:
                coin = next((c for c in data if c['symbol'].lower() == symbol.lower()), None)
                if not coin:
                    return {'error': f'Token {symbol} not found'}
                coins = [coin]
            else:
                # Otherwise get top gainers
                coins = sorted(data, key=lambda x: float(x.get('priceChange24h', 0)), reverse=True)[:5]
                
            # Format review data
            reviews = []
            for coin in coins:
                if self._is_stablecoin(coin['symbol'], float(coin.get('price', 0)), float(coin.get('priceChange24h', 0))):
                    continue
                    
                review = {
                    'project': {
                        'symbol': coin['symbol'],
                        'name': coin.get('name', '')
                    },
                    'metrics': {
                        'price': float(coin.get('price', 0)),
                        'price_change_24h': float(coin.get('priceChange24h', 0)),
                        'price_change_7d': float(coin.get('priceChange7d', 0)),
                        'market_cap': float(coin.get('marketCap', 0)) / 1e6,  # Convert to millions
                        'volume_24h': float(coin.get('volume24h', 0)) / 1e6,  # Convert to millions
                        'volume_to_mcap': float(coin.get('volume24h', 0)) / float(coin.get('marketCap', 1))
                    }
                }
                reviews.append(review)
                
            return reviews[0] if reviews else {'error': 'No suitable tokens found'}
            
        except Exception as e:
            print(f"Error getting shill review: {e}")
            return {'error': str(e)}
