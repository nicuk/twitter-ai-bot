"""
Market analysis functionality for Elion
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MarketAnalyzer:
    """Handles market analysis using LLM-based analysis"""
    
    def __init__(self, data_sources):
        self.data_sources = data_sources
        self.market_state = {
            'last_analysis': None,
            'analysis_cache': {},
            'market_mood': 'neutral'
        }
    
    def analyze_market_conditions(self) -> Dict:
        """Analyze current market conditions using LLM"""
        current_time = datetime.utcnow()
        
        # Use cached analysis if recent enough
        if (self.market_state['last_analysis'] and 
            (current_time - self.market_state['last_analysis']) <= timedelta(minutes=15)):
            return self.market_state['analysis_cache']
        
        try:
            # Get market data
            market_data = self.data_sources.get_market_data()
            if not market_data:
                return {}
                
            # Get BTC and ETH data
            btc = next((coin for coin in market_data if coin['symbol'] == 'BTC'), None)
            eth = next((coin for coin in market_data if coin['symbol'] == 'ETH'), None)
            
            if not btc or not eth:
                return {}
                
            # Calculate total market cap and volume
            total_mcap = sum(coin.get('market_cap', 0) for coin in market_data)
            total_volume = sum(coin.get('volume_24h', 0) for coin in market_data)
            
            # Get top gainers (excluding BTC/ETH)
            gainers = [coin for coin in market_data 
                      if coin['symbol'] not in ['BTC', 'ETH'] 
                      and coin.get('price_change_24h', 0) > 0]
            gainers.sort(key=lambda x: x['price_change_24h'], reverse=True)
            
            # Determine market sentiment
            sentiment = self._get_market_sentiment(btc)
            condition = self._get_market_condition(market_data)
            
            result = {
                'btc_price': btc['price'],
                'eth_price': eth['price'],
                'btc_change_24h': btc['price_change_24h'],
                'eth_change_24h': eth['price_change_24h'],
                'total_mcap': total_mcap,
                'total_volume': total_volume,
                'sentiment': sentiment,
                'condition': condition,
                'top_gainers': gainers[:3]
            }
            
            # Cache results
            self.market_state.update({
                'last_analysis': current_time,
                'analysis_cache': result,
                'market_mood': sentiment
            })
            
            return result
            
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return {}
            
    def _get_market_sentiment(self, btc_data: Dict) -> str:
        """Determine market sentiment based on BTC performance"""
        try:
            change_24h = btc_data.get('price_change_24h', 0)
            
            if change_24h >= 5:
                return "Strongly Bullish 🚀"
            elif change_24h >= 2:
                return "Bullish 📈"
            elif change_24h <= -5:
                return "Strongly Bearish 📉"
            elif change_24h <= -2:
                return "Bearish 🔻"
            else:
                return "Neutral ⚖️"
                
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            return "Neutral ⚖️"
            
    def _get_market_condition(self, market_data: List[Dict]) -> str:
        """Determine overall market condition"""
        try:
            # Calculate percentage of coins with positive 24h change
            total_coins = len(market_data)
            if total_coins == 0:
                return "Uncertain"
                
            positive_coins = sum(1 for coin in market_data 
                               if coin.get('price_change_24h', 0) > 0)
            positive_ratio = positive_coins / total_coins
            
            if positive_ratio >= 0.7:
                return "Strong Uptrend 🌙"
            elif positive_ratio >= 0.6:
                return "Uptrend 📈"
            elif positive_ratio <= 0.3:
                return "Strong Downtrend 🔻"
            elif positive_ratio <= 0.4:
                return "Downtrend 📉"
            else:
                return "Consolidation ⚖️"
                
        except Exception as e:
            print(f"Error getting market condition: {e}")
            return "Uncertain"
