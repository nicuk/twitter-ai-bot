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
from typing import List, Dict

class DataSources:
    def __init__(self, twitter_api=None):
        load_dotenv()
        self.twitter = twitter_api
        
        # Initialize LLM
        from custom_llm import MetaLlamaComponent
        self.llm = MetaLlamaComponent(
            api_key=os.getenv('META_LLAMA_API_KEY'),
            api_base=os.getenv('META_LLAMA_API_BASE')
        )
        
        # CryptoRank API configuration
        self.cryptorank_api_key = os.getenv('CRYPTORANK_API_KEY')
        self.cryptorank_base_url = os.getenv('CRYPTORANK_BASE_URL', 'https://api.cryptorank.io/v1')
        
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

    def get_market_alpha(self) -> Dict:
        """Get market alpha data including price, volume, and market cap"""
        try:
            # Try to get from cache first
            if (self.cache['market_data']['data'] and 
                self.cache['market_data']['timestamp'] > datetime.utcnow() - timedelta(minutes=5)):
                return self.cache['market_data']['data']

            # Get fresh data
            url = f"{self.cryptorank_base_url}/coins"
            params = {
                'api_key': self.cryptorank_api_key,
                'limit': 100
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process and format data
            market_data = {
                'price': data['data'][0]['price'],
                'price_change_24h': data['data'][0]['priceChange24h'],
                'volume_24h': data['data'][0]['volume24h'],
                'market_cap': data['data'][0]['marketCap'],
                'social_sentiment': self._get_social_sentiment()
            }
            
            # Update cache
            self.cache['market_data'] = {
                'data': market_data,
                'timestamp': datetime.utcnow()
            }
            
            return market_data
            
        except Exception as e:
            print(f"Error getting market alpha: {e}")
            return {}
            
    def _get_social_sentiment(self) -> float:
        """Get social sentiment score from Twitter"""
        try:
            if not self.twitter:
                return 0.5
                
            # Get tweets from key influencers
            tweets = []
            for influencer in self.key_influencers[:3]:  # Limit to avoid rate limits
                try:
                    user_tweets = self.twitter.user_timeline(screen_name=influencer, count=5)
                    tweets.extend(user_tweets)
                except Exception as e:
                    print(f"Error getting tweets for {influencer}: {e}")
                    
            if not tweets:
                return 0.5  # Neutral if no data
                
            # Simple sentiment based on likes/retweets ratio
            total_sentiment = 0
            for tweet in tweets:
                ratio = tweet.favorite_count / (tweet.retweet_count + 1)  # Avoid division by zero
                sentiment = min(ratio / 100, 1.0)  # Normalize to 0-1
                total_sentiment += sentiment
                
            return total_sentiment / len(tweets)
            
        except Exception as e:
            print(f"Error calculating social sentiment: {e}")
            return 0.5

    def get_market_overview(self) -> Dict:
        """Get market overview data including price, volume, and market cap"""
        return self.get_market_alpha()

    def get_alpha_opportunities(self) -> List[Dict]:
        """Get potential alpha opportunities from various sources"""
        try:
            # Get trending coins
            url = f"{self.cryptorank_base_url}/currencies"
            params = {
                'api_key': self.cryptorank_api_key,
                'sort': 'price_change24h',
                'limit': 10
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            opportunities = []
            for coin in data.get('data', []):
                if coin.get('price_change24h', 0) > 5:  # 5% or more gain
                    opportunities.append({
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'price_change_24h': coin['price_change24h'],
                        'volume_24h': coin.get('volume24h', 0),
                        'reason': 'trending_up'
                    })
                    
            return opportunities
            
        except Exception as e:
            print(f"Error getting alpha opportunities: {e}")
            return []
