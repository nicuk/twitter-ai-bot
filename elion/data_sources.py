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
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from custom_llm import MetaLlamaComponent

class CryptoRankAPI:
    """CryptoRank API wrapper"""
    
    def __init__(self):
        """Initialize the API wrapper"""
        load_dotenv()
        self.api_key = os.getenv('CRYPTORANK_API_KEY')
        self.base_url = 'https://api.cryptorank.io/v2'
        self.headers = {
            'X-Api-Key': self.api_key
        }

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            print(f"Making request to {url}")
            print(f"Headers: {self.headers}")
            print(f"Params: {params}")
            
            response = requests.get(url, headers=self.headers, params=params)
            print(f"Response status: {response.status_code}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response text: {e.response.text}")
            return {}

    def get_currencies(self, limit: int = 100) -> List[Dict]:
        """Get list of currencies with market data"""
        params = {
            'limit': limit,
            'sortBy': 'rank',
            'sortDirection': 'ASC',
            'include': ['percentChange']
        }
        response = self._make_request('currencies', params)
        return response.get('data', [])

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
            'limit': 500,  # Get more coins to filter from
            'sortBy': 'volume24h',
            'sortDirection': 'DESC',
            'include': ['percentChange']
        }
        response = self._make_request('currencies', params)
        coins = response.get('data', [])
        
        opportunities = []
        for coin in coins:
            try:
                # Extract metrics
                market_cap = float(coin.get('marketCap', 0))
                volume_24h = float(coin.get('volume24h', 0))
                price_change_24h = float(coin.get('percentChange', {}).get('h24', 0))
                price_change_7d = float(coin.get('percentChange', {}).get('d7', 0))
                
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
            'limit': 500,
            'sortBy': 'marketCap',
            'sortDirection': 'ASC',  # Start from smaller market caps
            'include': ['percentChange']
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
                    changes = coin.get('percentChange', {})
                    if not changes:
                        continue
                        
                    price_change_24h = float(changes.get('h24', 0))
                    price_change_7d = float(changes.get('d7', 0))
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
        # Load environment variables
        load_dotenv()
        
        # Initialize LLM with working configuration
        api_url = "https://api-user.ai.aitech.io/api/v1/user/products/209/use/chat/completions"
        model_name = "Meta-Llama-3.3-70B-Instruct"
        access_token = "QcKYEB9n875ZniLkBgfPf4t8eywevB6CpSKVj7pQrtUvQeWN47fzJwjKAbGtQ3ch"
        
        self.llm = MetaLlamaComponent(
            api_key=access_token,
            api_base=api_url
        )
        
        # Initialize data sources
        self.crypto_rank_api_key = os.getenv('CRYPTO_RANK_API_KEY', '').strip()
        self.crypto_rank_base_url = "https://api.cryptorank.io/v1"
        
        # Cache for API responses
        self._cache = {}
        
        # Initialize CryptoRank API
        self.cryptorank_api = CryptoRankAPI()
        
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
        # Common stablecoin indicators in symbol
        stablecoin_indicators = ['USD', 'DAI', 'TUSD', 'USDT', 'USDC', 'BUSD', 'CUSD', 'USDD']
        
        # Check symbol
        if any(indicator in symbol.upper() for indicator in stablecoin_indicators):
            return True
            
        # Check if price is pegged near $1 and has low volatility
        if 0.95 <= price <= 1.05 and abs(price_change_24h) < 5:
            return True
            
        return False

    def get_market_alpha(self) -> Dict:
        """Get market alpha data including price, volume, and market cap"""
        try:
            # Try to get from cache first
            if (self.cache['market_data']['data'] and 
                self.cache['market_data']['timestamp'] > datetime.utcnow() - timedelta(minutes=5)):
                return self.cache['market_data']['data']

            # Get fresh data from v2 currencies endpoint
            coins = self.cryptorank_api.get_currencies()
            
            if not coins:
                print("No coins found in response")
                return {}
                
            # Process and format data
            market_data = self._get_default_market_data()
            
            # Get the first coin (usually BTC) for market sentiment
            if coins:
                coin = coins[0]
                try:
                    market_data['price'] = float(coin.get('values', {}).get('USD', {}).get('price', 0))
                    market_data['price_change_24h'] = float(coin.get('values', {}).get('USD', {}).get('percentChange', {}).get('24h', 0))
                    market_data['volume_24h'] = float(coin.get('values', {}).get('USD', {}).get('volume24h', 0))
                    market_data['market_cap'] = float(coin.get('values', {}).get('USD', {}).get('marketCap', 0))
                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Error processing coin data: {e}")
            
            # Update cache
            self.cache['market_data'] = {
                'data': market_data,
                'timestamp': datetime.utcnow()
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error getting market alpha: {e}")
            return {}
            
    def _get_default_market_data(self) -> Dict:
        """Get default market data structure"""
        return {
            'price': 0.0,
            'price_change_24h': 0.0,
            'volume_24h': 0.0,
            'market_cap': 0.0,
            'social_sentiment': 0.5  # Neutral sentiment
        }
            
    def get_market_overview(self) -> Dict:
        """Get market overview data including price, volume, and market cap"""
        return self.get_market_alpha()

    def get_alpha_opportunities(self) -> List[Dict]:
        """Get potential alpha opportunities from CryptoRank"""
        try:
            # Get top 500 coins by volume
            params = {
                'limit': 500,
                'sortBy': 'volume24h',
                'sortDirection': 'DESC',
                'include': ['percentChange']
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
                    price = float(coin.get('price', 0) or 0)
                    market_cap = float(coin.get('marketCap', 0) or 0)
                    volume_24h = float(coin.get('volume24h', 0) or 0)
                    
                    # Skip if missing essential data
                    if not all([name, symbol, price > 0, market_cap > 0, volume_24h > 0]):
                        continue
                        
                    # Extract price changes (already in percentage)
                    changes = coin.get('percentChange', {})
                    price_change_24h = float(changes.get('h24', 0) or 0)
                    price_change_7d = float(changes.get('d7', 0) or 0)
                    
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
            
    def _get_market_condition(self, data: List[Dict]) -> Tuple[str, float, float]:
        """Determine market condition based on BTC performance
        Returns: (condition, btc_24h_change, btc_7d_change)
        where condition is one of: 'hot', 'neutral', 'cold'
        """
        # Try to find BTC in the first few entries (more reliable data)
        btc_entries = []
        for coin in data[:20]:  # Look in first 20 entries
            if coin.get('symbol', '').upper() == 'BTC':
                try:
                    changes = coin.get('percentChange', {})
                    # Values are already percentages, no need to multiply by 100
                    change_24h = float(changes.get('h24', 0) or 0)
                    change_7d = float(changes.get('d7', 0) or 0)
                    
                    # Only accept reasonable values
                    if -20 <= change_24h <= 20 and -40 <= change_7d <= 40:
                        btc_entries.append((change_24h, change_7d))
                except (TypeError, ValueError):
                    continue
        
        # Use median if we have multiple entries
        if btc_entries:
            if len(btc_entries) > 1:
                # Sort by 24h change and take median
                btc_entries.sort(key=lambda x: x[0])
                median_idx = len(btc_entries) // 2
                change_24h, change_7d = btc_entries[median_idx]
            else:
                change_24h, change_7d = btc_entries[0]
                
            # Determine market condition based on real-world thresholds
            if change_24h >= 4 or change_7d >= 8:  # Hot: BTC up >4% 24h or >8% weekly
                return 'hot', change_24h, change_7d
            elif change_24h <= -4 or change_7d <= -8:  # Cold: BTC down >4% 24h or >8% weekly
                return 'cold', change_24h, change_7d
            else:
                return 'neutral', change_24h, change_7d
                    
        return 'neutral', 0, 0  # Default if no valid BTC data found

    def get_shill_opportunities(self) -> List[Dict]:
        """Get potential shill opportunities from CryptoRank based on market conditions"""
        try:
            # Get top 500 coins by volume
            params = {
                'limit': 500,
                'sortBy': 'volume24h',
                'sortDirection': 'DESC',
                'include': ['percentChange']
            }
            
            response = self.cryptorank_api._make_request('currencies', params)
            if not response or 'data' not in response:
                print("No data received from API")
                return []
                
            # Determine market condition
            market_condition, btc_24h, btc_7d = self._get_market_condition(response['data'])
            print(f"\nMarket Condition: {market_condition.upper()}")
            print(f"BTC 24h Change: {btc_24h:.2f}%")
            print(f"BTC 7d Change: {btc_7d:.2f}%\n")
                
            opportunities = []
            for coin in response['data']:
                try:
                    # Extract basic info
                    name = coin.get('name', '').encode('ascii', 'ignore').decode()  # Remove non-ASCII chars
                    symbol = coin.get('symbol', '').encode('ascii', 'ignore').decode()
                    price = float(coin.get('price', 0) or 0)
                    market_cap = float(coin.get('marketCap', 0) or 0)
                    volume_24h = float(coin.get('volume24h', 0) or 0)
                    
                    # Skip if missing essential data
                    if not all([name, symbol, price > 0, market_cap > 0, volume_24h > 0]):
                        continue
                        
                    # Extract price changes (already in percentage)
                    changes = coin.get('percentChange', {})
                    price_change_24h = float(changes.get('h24', 0) or 0)
                    price_change_7d = float(changes.get('d7', 0) or 0)
                    price_change_30d = float(changes.get('d30', 0) or 0)
                    
                    # Skip stablecoins
                    if self._is_stablecoin(symbol, price, price_change_24h):
                        continue
                        
                    # Calculate volume to market cap ratio
                    volume_to_mcap = volume_24h / market_cap if market_cap > 0 else 0
                    
                    # Base criteria for all market conditions
                    if not (5_000_000 <= market_cap <= 100_000_000 and    # $5M to $100M mcap
                           volume_24h >= 1_000_000 and                     # >$1M volume
                           volume_to_mcap >= 0.05):                        # Decent trading activity
                        continue
                        
                    # Market condition specific criteria
                    is_opportunity = False
                    
                    if market_condition == 'hot':
                        # Look for coins consolidating after gains
                        # - Daily move less than BTC
                        # - Weekly stronger than BTC
                        # - Good volume
                        if (0 <= price_change_24h <= btc_24h and      # Not outperforming BTC today
                            price_change_7d >= btc_7d * 1.2 and       # But stronger weekly trend
                            price_change_30d >= -30 and               # Not heavily dumped
                            volume_to_mcap >= 0.10):                  # Good volume
                            is_opportunity = True
                            
                    elif market_condition == 'neutral':
                        # Look for steady gainers
                        # - Consistent positive moves
                        # - Weekly stronger than daily
                        if (5 <= price_change_24h <= 20 and          # Steady daily growth
                            price_change_7d >= price_change_24h and   # Building momentum
                            price_change_30d >= -30):                 # Not heavily dumped
                            is_opportunity = True
                            
                    else:  # cold market
                        # Look for strength in weakness
                        # - Positive while BTC negative
                        # - Showing relative strength
                        if (price_change_24h > abs(btc_24h/2) and    # Outperforming BTC
                            price_change_7d > abs(btc_7d/2) and      # Sustained outperformance
                            price_change_24h <= 25):                  # Not overheated
                            is_opportunity = True
                            
                    if is_opportunity:
                        opportunities.append({
                            'name': name,
                            'symbol': symbol,
                            'price': price,
                            'market_cap': market_cap,
                            'volume_24h': volume_24h,
                            'price_change_24h': price_change_24h,
                            'price_change_7d': price_change_7d,
                            'price_change_30d': price_change_30d,
                            'volume_to_mcap': volume_to_mcap
                        })
                        
                except (TypeError, ValueError) as e:
                    print(f"Error processing coin {coin.get('symbol', 'UNKNOWN')}: {str(e)}")
                    continue
                    
            # Sort based on market condition
            if market_condition == 'hot':
                # Prioritize strong weekly gainers that are calm today
                opportunities.sort(key=lambda x: (x['price_change_7d'] * (1 - x['price_change_24h']/100)), reverse=True)
            elif market_condition == 'neutral':
                # Prioritize steady gainers with good volume
                opportunities.sort(key=lambda x: (x['price_change_7d'] * x['volume_to_mcap']), reverse=True)
            else:  # cold
                # Prioritize strongest relative performers
                opportunities.sort(key=lambda x: (x['price_change_24h'] + x['price_change_7d']), reverse=True)
                
            return opportunities[:10]  # Return top 10
            
        except Exception as e:
            print(f"Error in get_shill_opportunities: {str(e)}")
            return []

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
