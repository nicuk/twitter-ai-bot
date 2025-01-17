"""
Market analysis service using LLM
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from .base import BaseDataSource
from custom_llm import MetaLlamaComponent

class MarketAnalysisService(BaseDataSource):
    """Market analysis service"""
    
    def __init__(self, llm):
        """Initialize market analysis service"""
        super().__init__()
        self.llm = llm
        
    def _validate_data(self, data: Any) -> bool:
        """Validate market data"""
        return isinstance(data, dict)
        
    def analyze_market_conditions(self, market_data: Optional[Dict] = None) -> Dict:
        """Analyze market conditions using LLM"""
        try:
            if not market_data:
                return {
                    'sentiment': 'NEUTRAL',
                    'condition': 'UNKNOWN',
                    'analysis': 'No market data available'
                }
                
            # Extract key metrics
            btc_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'BTC'), None)
            eth_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'ETH'), None)
            
            if not btc_data or not eth_data:
                return {
                    'sentiment': 'NEUTRAL',
                    'condition': 'UNKNOWN',
                    'analysis': 'Missing BTC/ETH data'
                }
                
            # Get market sentiment
            sentiment = self._get_market_sentiment(btc_data)
            condition = self._get_market_condition(market_data.get('coins', []))
            
            # Generate LLM analysis
            prompt = f"""
            Analyze the current crypto market conditions:
            
            BTC Price: ${btc_data['price']:,.2f}
            BTC 24h Change: {btc_data['price_change_24h']:+.1f}%
            ETH Price: ${eth_data['price']:,.2f}
            ETH 24h Change: {eth_data['price_change_24h']:+.1f}%
            Market Sentiment: {sentiment}
            Market Condition: {condition}
            
            Provide a concise market analysis in 2-3 sentences.
            """
            
            analysis = self.llm.generate(prompt)
            
            return {
                'sentiment': sentiment,
                'condition': condition,
                'analysis': analysis
            }
            
        except Exception as e:
            print(f"Error analyzing market conditions: {e}")
            return {
                'sentiment': 'NEUTRAL',
                'condition': 'ERROR',
                'analysis': f'Error: {str(e)}'
            }
            
    def _get_market_sentiment(self, btc_data: Dict) -> str:
        """Get market sentiment based on BTC performance"""
        try:
            # Get price changes
            btc_24h = btc_data.get('price_change_24h', 0)
            btc_7d = btc_data.get('price_change_7d', 0)
            
            # Determine sentiment
            if btc_24h >= 5 or btc_7d >= 10:
                return 'BULLISH'
            elif btc_24h <= -5 or btc_7d <= -10:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            return 'NEUTRAL'
            
    def _get_market_condition(self, data: List[Dict]) -> str:
        """Determine market condition based on market data"""
        try:
            # Get BTC data
            btc_data = next((coin for coin in data if coin['symbol'] == 'BTC'), None)
            if not btc_data:
                return 'UNKNOWN'
                
            # Get price changes
            btc_24h = btc_data.get('price_change_24h', 0)
            btc_7d = btc_data.get('price_change_7d', 0)
            
            # Determine market condition
            if btc_24h >= 5 or btc_7d >= 10:
                return 'HOT'
            elif btc_24h <= -5 or btc_7d <= -10:
                return 'COLD'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            print(f"Error getting market condition: {e}")
            return 'UNKNOWN'
            
    def analyze_onchain_metrics(self, data: Dict) -> Dict:
        """Analyze on-chain metrics"""
        # TODO: Implement on-chain analysis using LLM
        pass
        
    def analyze_whale_activity(self, data: Dict) -> Dict:
        """Analyze whale activity"""
        # TODO: Implement whale analysis using LLM
        pass
        
    def analyze_technical_indicators(self, data: Dict) -> Dict:
        """Analyze technical indicators"""
        # TODO: Implement technical analysis using LLM
        pass
