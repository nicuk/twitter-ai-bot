"""
Data sources integration for Elion AI using CryptoRank API
"""

import requests
import feedparser
from datetime import datetime, timedelta
import tweepy
from collections import defaultdict
import os
from dotenv import load_dotenv
from .data_storage import DataStorage

class DataSources:
    def __init__(self, twitter_api=None):
        load_dotenv()
        self.twitter = twitter_api
        
        # CryptoRank API configuration
        self.cryptorank_api_key = os.getenv('CRYPTORANK_API_KEY')
        self.cryptorank_base_url = os.getenv('CRYPTORANK_BASE_URL', 'https://api.cryptorank.io/v2')
        
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
            'trending': timedelta(minutes=15),
            'token_unlocks': timedelta(hours=1),
            'funding_rounds': timedelta(hours=4),
            'news': timedelta(hours=1)
        }
        
        # Credit tracking (max 400/day)
        self.daily_credits = 0
        self.last_credit_reset = datetime.now()
        self.storage = DataStorage()  # Initialize data storage
    
    def _reset_daily_credits(self):
        """Reset daily credit counter if it's a new day"""
        now = datetime.now()
        if now.date() > self.last_credit_reset.date():
            self.daily_credits = 0
            self.last_credit_reset = now
    
    def _make_request(self, endpoint, params=None):
        """Make API request with credit tracking"""
        self._reset_daily_credits()
        
        if self.daily_credits >= 380:  # Leave buffer for critical updates
            print("WARNING: Approaching daily credit limit")
            return None
            
        try:
            url = f"{self.cryptorank_base_url}{endpoint}"
            
            # Set up headers with API key
            headers = {'x-api-key': self.cryptorank_api_key}
            
            print(f"Making request to: {url}")  # Debug line
            print(f"API Key: {'*' * 4}{self.cryptorank_api_key[-4:] if self.cryptorank_api_key else None}")  # Debug line
            print(f"Full URL with params: {url}?{'&'.join([f'{k}={v}' for k,v in (params or {}).items()])}")  # Debug line
            
            response = requests.get(url, params=params, headers=headers)
            print(f"Response headers: {response.headers}")  # Debug line
            
            if response.status_code == 200:
                data = response.json()
                self.daily_credits += 1  # Increment credits used
                return data
            else:
                print(f"API request failed: {response.status_code}")
                if response.status_code in [400, 401, 403]:
                    print(f"Error details: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error making API request: {e}")
            return None
    
    def _is_cache_valid(self, cache_key):
        """Check if cached data is still valid"""
        cache_data = self.cache[cache_key]
        if not cache_data['data'] or not cache_data['timestamp']:
            return False
            
        age = datetime.now() - cache_data['timestamp']
        return age < self.cache_durations[cache_key]
    
    def _get_market_overview(self):
        """Get current market overview data"""
        try:
            response = self._make_request('/global')
            if response and isinstance(response, dict) and 'data' in response:
                data = response['data']
                return {
                    'total_mcap': float(data.get('totalMarketCap', 0)),
                    'total_volume': float(data.get('totalVolume24h', 0)),
                    'mcap_change': 0.0,  # Not available in current response
                    'volume_change': 0.0,  # Not available in current response
                    'btc_dominance': float(data.get('btcDominance', 0)),
                    'eth_dominance': float(data.get('ethDominance', 0))
                }
            return None
            
        except Exception as e:
            print(f"Error getting market overview: {str(e)}")
            return None

    def get_market_alpha(self):
        """Get comprehensive market alpha including sentiment, trends, and opportunities"""
        try:
            # Get market overview
            market_data = self._get_market_overview()
            if not market_data:
                return None
                
            # Get trending coins with detailed metrics
            trending = self._get_trending_coins(limit=5)
            
            # Get upcoming unlocks
            unlocks = self._get_token_unlocks()
            
            # Get recent funding
            funding = self._get_funding_rounds()
            
            # Analyze market sentiment based on top movers
            sentiment = 'neutral'
            if trending:
                avg_change = sum(coin['price_change_24h'] for coin in trending) / len(trending)
                if avg_change > 5:
                    sentiment = 'bullish'
                elif avg_change < -5:
                    sentiment = 'bearish'
                
            # Group projects by category for narrative analysis
            categories = {}
            if trending:
                for coin in trending:
                    cat = coin.get('category', 'Other')
                    if cat not in categories:
                        categories[cat] = {
                            'count': 0,
                            'total_volume': 0,
                            'avg_change': 0,
                            'coins': []
                        }
                    categories[cat]['count'] += 1
                    categories[cat]['total_volume'] += coin['volume_24h']
                    categories[cat]['avg_change'] += coin['price_change_24h']
                    categories[cat]['coins'].append(coin['symbol'])
                
                # Calculate averages and sort by strength
                for cat in categories:
                    categories[cat]['avg_change'] /= categories[cat]['count']
                
                # Get top 3 narratives
                top_narratives = sorted(
                    categories.items(),
                    key=lambda x: (x[1]['count'], x[1]['avg_change']),
                    reverse=True
                )[:3]
            
            # Compile market alpha
            return {
                'total_mcap': market_data.get('total_mcap', 0),
                'total_volume': market_data.get('total_volume', 0),
                'market_sentiment': sentiment,
                'btc_dominance': market_data.get('btc_dominance', 0),
                'eth_dominance': market_data.get('eth_dominance', 0),
                'hot_narratives': [
                    {
                        'category': cat,
                        'reason': f"{data['count']} coins pumping {data['avg_change']:.1f}% avg",
                        'coins': data['coins']
                    }
                    for cat, data in top_narratives
                ] if trending else [],
                'potential_plays': [
                    {
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'reason': coin['key_metric']
                    }
                    for coin in (trending or [])[:5]
                ],
                'risk_factors': [
                    {'symbol': unlock.get('symbol', '???'),
                     'reason': f"Unlock of {unlock.get('amount', '???')} tokens soon"}
                    for unlock in (unlocks or [])[:2]
                ] if unlocks else []
            }
            
        except Exception as e:
            print(f"Error generating alpha: {str(e)}")
            return None

    def get_coin_details(self, coin_id):
        """Get detailed data for a specific coin"""
        return self._make_request(f'/currencies/{coin_id}')
    
    def get_alpha_opportunities(self):
        """Generate alpha opportunities from market data"""
        opportunities = []
        
        # Get market overview
        overview = self.get_market_overview()
        if overview:
            opportunities.append({
                'type': 'market_overview',
                'btc_dominance': overview.get('btcDominance', 'N/A'),
                'eth_dominance': overview.get('ethDominance', 'N/A'),
                'total_mcap': overview.get('totalMarketCap', 'N/A')
            })
        
        # Get big movers
        trending = self._get_trending_coins()
        if trending:
            for coin in trending:
                change_24h = coin.get('values', {}).get('USD', {}).get('percentChange24h', 0)
                if change_24h and float(change_24h) > 10:  # Big movers
                    opportunities.append({
                        'type': 'price_movement',
                        'symbol': coin.get('symbol', 'Unknown'),
                        'change_24h': change_24h
                    })
        
        # Get upcoming unlocks
        unlocks = self._get_token_unlocks()
        if unlocks:
            for coin in unlocks:
                if coin.get('nextUnlockDate'):
                    opportunities.append({
                        'type': 'token_unlock',
                        'symbol': coin.get('symbol', 'Unknown'),
                        'unlock_date': coin.get('nextUnlockDate')
                    })
        
        # Get recent funding
        funding = self._get_funding_rounds()
        if funding:
            for coin in funding:
                if coin.get('lastRoundDate'):
                    opportunities.append({
                        'type': 'funding',
                        'symbol': coin.get('symbol', 'Unknown'),
                        'date': coin.get('lastRoundDate'),
                        'amount': coin.get('lastRoundAmount', 'N/A')
                    })
        
        return opportunities
    
    def get_news_opportunities(self):
        """Get breaking news and important updates"""
        news = []
        
        # Get RSS feed news
        rss_news = self._fetch_rss_news()
        if rss_news:
            news.extend(rss_news)
        
        # Get high-engagement crypto tweets
        tweet_news = self._get_viral_tweets()
        if tweet_news:
            news.extend(tweet_news)
        
        return news
    
    def get_shill_opportunities(self, user_suggested=None):
        """Get projects worth shilling, either discovered or user-suggested"""
        try:
            # Initialize project analyzer if not exists
            if not hasattr(self, 'project_analyzer'):
                from elion.project_analysis import ProjectAnalyzer
                self.project_analyzer = ProjectAnalyzer(self)
            
            opportunities = []
            
            if user_suggested:
                # Deep analysis of user-suggested project
                project_data = self.project_analyzer.analyze_project(user_suggested)
                if project_data:
                    opportunities.append(project_data)
            else:
                # Find trending projects
                trending = self._get_trending_projects()
                if trending:
                    opportunities.extend(trending)
            
            return opportunities
            
        except Exception as e:
            print(f"Error getting shill opportunities: {e}")
            return []
    
    def _fetch_rss_news(self):
        """Fetch news from RSS feeds"""
        try:
            news = []
            
            for feed_url in self.news_feeds:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:5]:  # Latest 5 entries
                    news.append({
                        'title': entry.title,
                        'link': entry.link,
                        'published': entry.published,
                        'source': feed_url,
                        'type': 'news'
                    })
            
            return news
            
        except Exception as e:
            print(f"Error fetching RSS news: {e}")
            return []
    
    def _get_viral_tweets(self):
        """Get viral crypto-related tweets"""
        try:
            viral_tweets = []
            
            # Search for viral crypto tweets
            crypto_tweets = self.twitter.search_tweets(
                q='crypto OR bitcoin OR ethereum min_faves:1000',
                result_type='popular',
                count=10
            )
            
            for tweet in crypto_tweets:
                viral_tweets.append({
                    'content': tweet.text,
                    'author': tweet.user.screen_name,
                    'engagement': tweet.favorite_count + tweet.retweet_count,
                    'type': 'viral_tweet'
                })
            
            return viral_tweets
            
        except Exception as e:
            print(f"Error getting viral tweets: {e}")
            return []
    
    def _analyze_project(self, project_info):
        """Analyze a specific project (user-suggested or discovered)"""
        try:
            # Basic project validation and analysis
            if isinstance(project_info, str):
                # It's just a name/symbol, try to get more info
                url = f"https://api.coingecko.com/api/v3/coins/{project_info}"
                response = requests.get(url)
                project_info = response.json()
            
            # Extract key metrics
            analysis = {
                'name': project_info.get('name'),
                'symbol': project_info.get('symbol'),
                'market_cap': project_info.get('market_cap'),
                'volume_24h': project_info.get('volume_24h'),
                'price_change_24h': project_info.get('price_change_percentage_24h'),
                'social_score': project_info.get('social_score'),
                'type': 'project_analysis'
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing project: {e}")
            return None
    
    def _get_trending_projects(self):
        """Discover trending crypto projects"""
        try:
            # Use CoinGecko trending search API
            url = "https://api.coingecko.com/api/v3/search/trending"
            response = requests.get(url)
            data = response.json()
            
            trending = []
            for coin in data['coins']:
                project = self._analyze_project(coin['item']['id'])
                if project:
                    trending.append(project)
            
            return trending
            
        except Exception as e:
            print(f"Error getting trending projects: {e}")
            return []

    def _get_token_unlocks(self):
        """Get upcoming token unlocks"""
        try:
            current_time = datetime.now()
            future_time = current_time + timedelta(days=7)
            
            params = {
                'hasUnlocks': True,
                'sort': 'nextUnlockDate',
                'dir': 'ASC',
                'limit': 100
            }
            response = self._make_request("/currencies", params)
            if response and 'data' in response:
                unlocks = []
                for token in response['data']:
                    if 'unlocks' not in token or not token['unlocks']:
                        continue
                        
                    for unlock in token['unlocks']:
                        unlock_date = datetime.fromtimestamp(unlock.get('date', 0))
                        if current_time <= unlock_date <= future_time:
                            unlocks.append({
                                'symbol': token.get('symbol', ''),
                                'name': token.get('name', ''),
                                'unlock_date': unlock_date,
                                'unlock_amount': unlock.get('value', 0),
                                'unlock_percent': unlock.get('percent', 0),
                                'current_price': token.get('values', {}).get('USD', {}).get('price', 0)
                            })
                return unlocks
            return None
        except Exception as e:
            print(f"Error fetching upcoming unlocks: {str(e)}")
            return None

    def _get_funding_rounds(self):
        """Get recent funding rounds"""
        try:
            params = {
                'hasRounds': True,
                'sort': 'lastRoundDate',
                'dir': 'DESC',
                'limit': 100
            }
            response = self._make_request("/currencies", params)
            current_time = datetime.now()
            lookback_time = current_time - timedelta(days=7)
            
            if response and 'data' in response:
                funding_rounds = []
                for token in response['data']:
                    if 'fundingRounds' not in token or not token['fundingRounds']:
                        continue
                        
                    for round in token['fundingRounds']:
                        round_date = datetime.fromtimestamp(round.get('date', 0))
                        if round_date >= lookback_time:
                            funding_rounds.append({
                                'symbol': token.get('symbol', ''),
                                'name': token.get('name', ''),
                                'round_name': round.get('name', ''),
                                'amount': round.get('amount', 0),
                                'date': round_date,
                                'investors': round.get('investors', []),
                                'current_price': token.get('values', {}).get('USD', {}).get('price', 0)
                            })
                return funding_rounds
            return None
        except Exception as e:
            print(f"Error fetching funding rounds: {str(e)}")
            return None
