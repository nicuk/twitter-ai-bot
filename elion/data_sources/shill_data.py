"""
Shill data source for Elion
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from .base import BaseDataSource
from .cryptorank_api import CryptoRankAPI
from custom_llm import MetaLlamaComponent

class ShillDataSource(BaseDataSource):
    """Handles shill opportunities and reviews"""
    
    def __init__(self, cryptorank_api: CryptoRankAPI, llm: MetaLlamaComponent):
        """Initialize shill data source"""
        super().__init__()
        self.cryptorank_api = cryptorank_api
        self.llm = llm
        
        # Configure cache durations
        self.cache_durations.update({
            'shill_opportunities': timedelta(hours=1),
            'shill_reviews': timedelta(hours=2)
        })
        
    def _validate_data(self, data: Any) -> bool:
        """Validate shill data"""
        if not isinstance(data, (list, dict)):
            return False
        return True
        
    def get_shill_opportunities(self) -> List[Dict]:
        """Get potential shill opportunities"""
        # Check cache first
        cached = self._get_cached('shill_opportunities')
        if cached:
            return cached
            
        try:
            # Get market data
            market_data = self.cryptorank_api.get_currencies()
            if not market_data:
                return []
                
            # Filter for potential opportunities
            opportunities = []
            for coin in market_data:
                # Skip stablecoins
                if self._is_stablecoin(coin):
                    continue
                    
                mcap = coin.get('market_cap', 0)
                if mcap > 500e6:  # Skip coins with mcap > $500M
                    continue
                    
                # Look for strong fundamentals
                volume = coin.get('volume_24h', 0)
                holders = coin.get('holders', 0)
                
                if volume > 1e6 and holders > 1000:
                    opportunities.append({
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'price': coin['price'],
                        'market_cap': mcap,
                        'volume_24h': volume,
                        'holders': holders,
                        'opportunity_type': 'fundamental_growth'
                    })
                    
            # Cache and return
            self._cache_data('shill_opportunities', opportunities)
            return opportunities
            
        except Exception as e:
            print(f"Error getting shill opportunities: {e}")
            return []
            
    def get_shill_review(self, symbol: str) -> Dict:
        """Get shill review data for a token"""
        cache_key = f'shill_review_{symbol}'
        
        # Check cache first
        cached = self._get_cached(cache_key)
        if cached:
            return cached
            
        try:
            # Get token data
            token_data = self.cryptorank_api.get_currency(symbol)
            if not token_data:
                return {}
                
            # Generate review using LLM
            review = self._generate_shill_review(token_data)
            
            # Cache and return
            self._cache_data(cache_key, review)
            return review
            
        except Exception as e:
            print(f"Error getting shill review: {e}")
            return {}
            
    def _generate_shill_review(self, token_data: Dict) -> Dict:
        """Generate a shill review using LLM"""
        try:
            # Format prompt
            prompt = f"""Analyze this crypto project and provide a balanced review:

Project: {token_data['name']} ({token_data['symbol']})
Price: ${token_data['price']:,.4f}
Market Cap: ${token_data['market_cap']:,.0f}
24h Volume: ${token_data['volume_24h']:,.0f}
Holders: {token_data.get('holders', 'Unknown')}

Your review should include:
1. Key strengths
2. Potential risks
3. Market opportunity
4. Investment thesis

Respond in a structured format:
STRENGTHS: [strength1, strength2, ...]
RISKS: [risk1, risk2, ...]
OPPORTUNITY: [brief description]
THESIS: [investment thesis]
"""
            
            # Get LLM analysis
            analysis = self.llm.chat_completion(prompt)
            
            # Parse response
            return self._parse_shill_review(analysis)
            
        except Exception as e:
            print(f"Error generating shill review: {e}")
            return {}
            
    def _parse_shill_review(self, review: str) -> Dict:
        """Parse LLM shill review into structured format"""
        try:
            lines = review.strip().split('\n')
            result = {
                'strengths': [],
                'risks': [],
                'opportunity': "",
                'thesis': ""
            }
            
            current_section = None
            for line in lines:
                if line.startswith('STRENGTHS:'):
                    current_section = 'strengths'
                    strengths = line.split(':')[1].strip()
                    result['strengths'] = [s.strip() for s in strengths.split(',')]
                elif line.startswith('RISKS:'):
                    current_section = 'risks'
                    risks = line.split(':')[1].strip()
                    result['risks'] = [r.strip() for r in risks.split(',')]
                elif line.startswith('OPPORTUNITY:'):
                    result['opportunity'] = line.split(':')[1].strip()
                elif line.startswith('THESIS:'):
                    result['thesis'] = line.split(':')[1].strip()
                    
            return result
            
        except Exception as e:
            print(f"Error parsing shill review: {e}")
            return {}
