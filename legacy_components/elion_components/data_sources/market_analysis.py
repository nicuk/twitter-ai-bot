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

    def analyze_market_sentiment(self, market_data: Optional[Dict] = None) -> Dict:
        """Get detailed market sentiment analysis"""
        try:
            if not market_data:
                return {'overall': 'NEUTRAL', 'confidence': 0}

            # Get BTC and ETH data
            btc_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'BTC'), None)
            eth_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'ETH'), None)

            if not btc_data or not eth_data:
                return {'overall': 'NEUTRAL', 'confidence': 0}

            # Calculate sentiment scores
            btc_score = self._calculate_sentiment_score(btc_data)
            eth_score = self._calculate_sentiment_score(eth_data)
            
            # Overall sentiment
            avg_score = (btc_score + eth_score) / 2
            
            # Map score to sentiment
            if avg_score >= 0.7:
                sentiment = 'VERY BULLISH'
                confidence = 90
            elif avg_score >= 0.3:
                sentiment = 'BULLISH'
                confidence = 75
            elif avg_score >= -0.3:
                sentiment = 'NEUTRAL'
                confidence = 60
            elif avg_score >= -0.7:
                sentiment = 'BEARISH'
                confidence = 75
            else:
                sentiment = 'VERY BEARISH'
                confidence = 90

            return {
                'overall': sentiment,
                'confidence': confidence,
                'btc_sentiment': self._get_market_sentiment(btc_data),
                'eth_sentiment': self._get_market_sentiment(eth_data)
            }

        except Exception as e:
            print(f"Error analyzing market sentiment: {e}")
            return {'overall': 'NEUTRAL', 'confidence': 0}

    def _calculate_sentiment_score(self, coin_data: Dict) -> float:
        """Calculate sentiment score for a coin (-1 to 1)"""
        try:
            # Get price changes
            change_24h = coin_data.get('price_change_24h', 0) / 100
            change_7d = coin_data.get('price_change_7d', 0) / 100
            
            # Weight recent changes more heavily
            score = (change_24h * 0.7) + (change_7d * 0.3)
            
            # Clamp between -1 and 1
            return max(min(score, 1.0), -1.0)
            
        except Exception as e:
            print(f"Error calculating sentiment score: {e}")
            return 0.0

    def get_market_insights(self, market_data: Optional[Dict] = None) -> list:
        """Get key market insights"""
        try:
            if not market_data:
                return []

            # Extract insights from market data
            insights = []
            
            # BTC dominance insight
            btc_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'BTC'), None)
            if btc_data:
                dom = btc_data.get('market_cap_dominance', 0)
                if dom > 50:
                    insights.append(f"BTC dominance high at {dom:.1f}%")
                elif dom < 40:
                    insights.append(f"BTC dominance low at {dom:.1f}%")

            # Volume insights
            total_vol = sum(coin.get('volume_24h', 0) for coin in market_data.get('coins', []))
            if total_vol > 100e9:
                insights.append("High trading volume indicates active market")
            elif total_vol < 50e9:
                insights.append("Low trading volume suggests cautious market")

            # Market cap insights
            total_mcap = sum(coin.get('market_cap', 0) for coin in market_data.get('coins', []))
            if total_mcap > 2e12:
                insights.append("Total market cap above $2T - bullish signal")
            elif total_mcap < 1e12:
                insights.append("Market cap below $1T - bearish territory")

            return insights

        except Exception as e:
            print(f"Error getting market insights: {e}")
            return []

    def get_market_predictions(self, market_data: Optional[Dict] = None) -> Dict:
        """Get market predictions"""
        try:
            if not market_data:
                return {}

            predictions = {}
            
            # Get BTC and ETH data
            btc_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'BTC'), None)
            eth_data = next((coin for coin in market_data.get('coins', []) if coin['symbol'] == 'ETH'), None)

            if btc_data:
                # Generate BTC prediction
                btc_sentiment = self._get_market_sentiment(btc_data)
                if btc_sentiment == 'BULLISH':
                    predictions['BTC'] = "Likely to test higher levels"
                elif btc_sentiment == 'BEARISH':
                    predictions['BTC'] = "May see further downside"
                else:
                    predictions['BTC'] = "Range-bound trading likely"

            if eth_data:
                # Generate ETH prediction
                eth_sentiment = self._get_market_sentiment(eth_data)
                if eth_sentiment == 'BULLISH':
                    predictions['ETH'] = "Momentum favors upside"
                elif eth_sentiment == 'BEARISH':
                    predictions['ETH'] = "Downward pressure expected"
                else:
                    predictions['ETH'] = "Consolidation phase likely"

            return predictions

        except Exception as e:
            print(f"Error getting market predictions: {e}")
            return {}
