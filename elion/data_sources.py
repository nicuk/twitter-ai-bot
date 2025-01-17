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
            'trending': timedelta(hours=1),
            'token_unlocks': timedelta(hours=6),
            'funding_rounds': timedelta(hours=12),
            'news': timedelta(hours=1)
        }

    def get_market_overview(self) -> Dict:
        """Get market overview data including price, volume, and market cap"""
        return self.get_market_alpha()
