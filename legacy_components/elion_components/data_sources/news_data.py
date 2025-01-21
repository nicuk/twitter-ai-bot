"""
News data source for Elion
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import feedparser
from .base import BaseDataSource

class NewsDataSource(BaseDataSource):
    """News data source"""
    
    def __init__(self):
        """Initialize news data source"""
        super().__init__()
        
        # Configure cache durations
        self.cache_durations.update({
            'latest_news': timedelta(minutes=30),
            'trending_topics': timedelta(hours=1),
            'market_events': timedelta(hours=1)
        })
        
        # Configure news feeds
        self.news_feeds = [
            'https://cointelegraph.com/rss',
            'https://cryptonews.com/news/feed/',
            'https://decrypt.co/feed',
            'https://www.coindesk.com/feed',
            'https://news.bitcoin.com/feed',
            'https://www.ccn.com/feed',
            'https://ethereumworldnews.com/feed',
            'https://www.cryptoglobe.com/feed',
            'https://www.newsbtc.com/feed',
            'https://www.livebitcoinnews.com/feed'
        ]
        
    def _validate_data(self, data: Any) -> bool:
        """Validate news data"""
        if not isinstance(data, (list, dict)):
            return False
        return True
        
    def get_latest_news(self, limit: int = 10) -> List[Dict]:
        """Get latest crypto news"""
        # Check cache first
        cached = self._get_cached('latest_news')
        if cached:
            return cached[:limit]
            
        try:
            all_news = []
            for feed_url in self.news_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:limit]:
                        news_item = {
                            'title': entry.title,
                            'link': entry.link,
                            'summary': entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'source': feed.feed.title
                        }
                        all_news.append(news_item)
                        
                except Exception as e:
                    print(f"Error parsing feed {feed_url}: {e}")
                    continue
                    
            # Sort by publication date
            all_news.sort(key=lambda x: x['published'], reverse=True)
            
            # Cache and return
            self._cache_data('latest_news', all_news)
            return all_news[:limit]
            
        except Exception as e:
            print(f"Error getting latest news: {e}")
            return []
            
    def get_trending_topics(self) -> List[Dict]:
        """Get trending crypto topics from news"""
        # Check cache first
        cached = self._get_cached('trending_topics')
        if cached:
            return cached
            
        try:
            # Get latest news
            news = self.get_latest_news(limit=50)
            
            # Extract topics and count mentions
            topics = {}
            for item in news:
                title = item['title'].lower()
                summary = item['summary'].lower()
                
                # Check for key topics
                key_topics = ['bitcoin', 'ethereum', 'defi', 'nft', 'regulation',
                            'sec', 'altcoin', 'mining', 'wallet', 'exchange']
                            
                for topic in key_topics:
                    if topic in title or topic in summary:
                        topics[topic] = topics.get(topic, 0) + 1
                        
            # Convert to list and sort by count
            trending = [
                {'topic': topic, 'mentions': count}
                for topic, count in topics.items()
            ]
            trending.sort(key=lambda x: x['mentions'], reverse=True)
            
            # Cache and return
            self._cache_data('trending_topics', trending)
            return trending
            
        except Exception as e:
            print(f"Error getting trending topics: {e}")
            return []
            
    def get_market_events(self) -> List[Dict]:
        """Get significant market events from news"""
        # Check cache first
        cached = self._get_cached('market_events')
        if cached:
            return cached
            
        try:
            # Get latest news
            news = self.get_latest_news(limit=20)
            
            # Filter for market-moving events
            events = []
            key_terms = ['crash', 'surge', 'rally', 'dump', 'hack', 'scam',
                        'partnership', 'launch', 'listing', 'delisting',
                        'regulation', 'ban', 'approval']
                        
            for item in news:
                title = item['title'].lower()
                if any(term in title for term in key_terms):
                    events.append({
                        'title': item['title'],
                        'link': item['link'],
                        'source': item['source'],
                        'published': item['published']
                    })
                    
            # Cache and return
            self._cache_data('market_events', events)
            return events
            
        except Exception as e:
            print(f"Error getting market events: {e}")
            return []
