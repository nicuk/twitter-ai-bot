"""
Data sources package for Elion
"""

from .market_data import MarketDataSource
from .alpha_data import AlphaDataSource
from .social_data import SocialDataSource
from .news_data import NewsDataSource
from .shill_data import ShillDataSource
from .cryptorank_api import CryptoRankAPI
from .market_analysis import MarketAnalysisService

"""
Data sources coordinator for Elion
"""

from typing import Dict, Optional, Any

__all__ = [
    'DataSources',
    'MarketDataSource',
    'MarketAnalysisService',
    'AlphaDataSource',
    'SocialDataSource',
    'NewsDataSource',
    'ShillDataSource',
    'CryptoRankAPI'
]

class DataSources:
    """Coordinator for all data sources"""
    
    def __init__(self, llm, cryptorank_api_key: Optional[str] = None):
        """Initialize all data sources"""
        # Initialize CryptoRank API
        self.cryptorank_api = CryptoRankAPI(api_key=cryptorank_api_key)
        
        # Initialize all data sources
        self.market_data = MarketDataSource(self.cryptorank_api)
        self.market_analysis = MarketAnalysisService(llm)
        self.alpha_data = AlphaDataSource(self.cryptorank_api)
        self.social_data = SocialDataSource(None)  # TODO: Add Twitter API
        self.news_data = NewsDataSource()
        self.shill_data = ShillDataSource(self.cryptorank_api, llm)
        
    def get_market_data(self):
        """Get market data"""
        return self.market_data.get_market_data()
        
    def get_market_alpha(self):
        """Get market alpha data and analysis"""
        data = self.market_data.get_market_data()
        if not data:
            return None
            
        analysis = self.market_analysis.analyze_market_conditions(data)
        return {
            'market_data': data,
            'analysis': analysis
        }
        
    def get_undervalued_gems(self):
        """Get undervalued gems"""
        return self.alpha_data.get_undervalued_gems()
        
    def get_alpha_opportunities(self):
        """Get alpha opportunities"""
        return self.alpha_data.get_alpha_opportunities()
        
    def get_latest_news(self):
        """Get latest news"""
        return self.news_data.get_latest_news()
        
    def get_market_events(self):
        """Get market events"""
        return self.news_data.get_market_events()
        
    def get_social_sentiment(self):
        """Get social sentiment"""
        return self.social_data.get_social_sentiment()
        
    def get_shill_review(self, symbol: str):
        """Get shill review"""
        return self.shill_data.get_shill_review(symbol)
        
    def get_shill_opportunities(self):
        """Get shill opportunities"""
        return self.shill_data.get_shill_opportunities()
        
    def get_market_search(self, query: str):
        """Search market data"""
        return self.market_data.get_market_search(query)
        
    def has_market_data(self) -> bool:
        """Check if market data is available"""
        return bool(self.cryptorank_api and self.cryptorank_api.api_key)
        
    def analyze_market_conditions(self):
        """Analyze market conditions"""
        data = self.market_data.get_market_data()
        return self.market_analysis.analyze_market_conditions(data)
