"""
Market analysis functionality for Elion
"""

from typing import Dict, List, Optional
import requests

class MarketAnalyzer:
    """Analyzes market data and trends"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize market analyzer"""
        self.api_key = api_key
        self.base_url = "https://api.cryptorank.io/v1"
        
    def get_current_data(self) -> Dict:
        """Get current market data"""
        try:
            # For testing purposes
            return {
                'price': 42000,
                'volume': 1000000,
                'market_cap': 1000000000,
                'change_24h': 5.5,
                'whale_data': {
                    'inflow_24h': 500,
                    'outflow_24h': 300
                }
            }
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return {}

    def analyze_market_conditions(self) -> Dict:
        """Comprehensive market analysis"""
        try:
            market_data = self.get_current_data()
            technical = self.analyze_technical(market_data)
            onchain = self.analyze_onchain_metrics()
            sentiment = self.analyze_market_sentiment(market_data)
            
            return {
                'technical': technical,
                'onchain': onchain,
                'sentiment': sentiment,
                'confidence': self.calculate_confidence(technical, onchain)
            }
            
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return {
                'technical': {},
                'onchain': {},
                'sentiment': 'neutral',
                'confidence': 0.5
            }

    def analyze_technical(self, market_data: Dict) -> Dict:
        """Analyze technical indicators and patterns"""
        try:
            if not market_data:
                return {}
                
            prices = market_data.get('price_history', [])
            volume = market_data.get('volume_history', [])
            
            ma_analysis = self.analyze_moving_averages(prices)
            momentum = self.calculate_momentum(prices)
            volume_patterns = self.analyze_volume_patterns(volume)
            support_resistance = self.find_support_resistance(prices)
            
            confidence = (
                ma_analysis.get('confidence', 0.5) * 0.3 +
                momentum.get('confidence', 0.5) * 0.3 +
                volume_patterns.get('confidence', 0.5) * 0.2 +
                support_resistance.get('confidence', 0.5) * 0.2
            )
            
            return {
                'trend': ma_analysis.get('trend', 'neutral'),
                'momentum': momentum.get('signal', 'neutral'),
                'volume_analysis': volume_patterns,
                'support_resistance': support_resistance,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {
                'trend': 'neutral',
                'momentum': 'neutral',
                'volume_analysis': {},
                'support_resistance': {},
                'confidence': 0.5
            }

    def analyze_onchain_metrics(self) -> Dict:
        """Analyze on-chain metrics"""
        try:
            metrics = self.get_onchain_metrics()
            if not metrics:
                return {}
                
            network_growth = metrics.get('active_addresses', 0) / metrics.get('total_addresses', 1)
            whale_confidence = metrics.get('whale_confidence', 0.5)
            
            return {
                'network_growth': 'high' if network_growth > 0.1 else 'low',
                'whale_confidence': whale_confidence,
                'retail_sentiment': metrics.get('retail_sentiment', 'neutral')
            }
            
        except Exception as e:
            print(f"Error in onchain analysis: {e}")
            return {
                'network_growth': 'low',
                'whale_confidence': 0.5,
                'retail_sentiment': 'neutral'
            }

    def analyze_market_sentiment(self, market_data: Optional[Dict] = None) -> str:
        """Analyze market sentiment based on available data"""
        try:
            if not market_data:
                market_data = self.get_current_data()
                
            price_change = market_data.get('change_24h', 0)
            volume_change = market_data.get('volume_change_24h', 0)
            
            if price_change > 5 and volume_change > 20:
                return 'very_bullish'
            elif price_change > 2:
                return 'bullish'
            elif price_change < -5 and volume_change > 20:
                return 'very_bearish'
            elif price_change < -2:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return 'neutral'

    def calculate_confidence(self, technical: Dict, onchain: Dict) -> float:
        """Calculate overall confidence score"""
        try:
            technical_confidence = technical.get('confidence', 0.5)
            onchain_confidence = onchain.get('whale_confidence', 0.5)
            
            # Weight technical analysis more heavily
            return (technical_confidence * 0.7) + (onchain_confidence * 0.3)
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.5

    def analyze_moving_averages(self, prices: List[float], short_period: int = 20, long_period: int = 50) -> Dict:
        """Analyze moving averages for a list of prices"""
        try:
            if len(prices) < long_period:
                return {'trend': 'neutral', 'confidence': 0.5}
                
            short_ma = sum(prices[-short_period:]) / short_period
            long_ma = sum(prices[-long_period:]) / long_period
            
            if short_ma > long_ma * 1.05:
                return {'trend': 'bullish', 'confidence': 0.8}
            elif short_ma < long_ma * 0.95:
                return {'trend': 'bearish', 'confidence': 0.8}
            else:
                return {'trend': 'neutral', 'confidence': 0.5}
                
        except Exception as e:
            print(f"Error in MA analysis: {e}")
            return {'trend': 'neutral', 'confidence': 0.5}

    def analyze_volume_patterns(self, volume: List[float]) -> Dict:
        """Analyze volume patterns and trends"""
        try:
            if len(volume) < 24:
                return {'pattern': 'normal', 'confidence': 0.5}
                
            avg_volume = sum(volume[:-24]) / (len(volume) - 24)
            recent_volume = sum(volume[-24:]) / 24
            
            if recent_volume > avg_volume * 2:
                return {'pattern': 'high_volume', 'confidence': 0.7}
            elif recent_volume < avg_volume * 0.5:
                return {'pattern': 'low_volume', 'confidence': 0.6}
            else:
                return {'pattern': 'normal', 'confidence': 0.5}
                
        except Exception as e:
            print(f"Error in volume analysis: {e}")
            return {'pattern': 'normal', 'confidence': 0.5}

    def find_support_resistance(self, prices: List[float], num_levels: int = 3) -> Dict:
        """Find support and resistance levels using price action analysis"""
        try:
            if len(prices) < 100:
                return {'levels': [], 'confidence': 0.5}
                
            # Simple implementation - use local mins/maxs
            levels = []
            for i in range(1, len(prices) - 1):
                if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                    levels.append(('resistance', prices[i]))
                elif prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                    levels.append(('support', prices[i]))
                    
            # Sort by frequency of price levels
            levels = sorted(levels, key=lambda x: prices.count(x[1]), reverse=True)[:num_levels]
            
            return {
                'levels': levels,
                'confidence': 0.7 if levels else 0.5
            }
            
        except Exception as e:
            print(f"Error finding support/resistance: {e}")
            return {'levels': [], 'confidence': 0.5}

    def calculate_momentum(self, prices: List[float], period: int = 14) -> Dict:
        """Calculate price momentum indicators"""
        try:
            if len(prices) < period:
                return {'signal': 'neutral', 'confidence': 0.5}
                
            momentum = (prices[-1] - prices[-period]) / prices[-period] * 100
            
            if momentum > 10:
                return {'signal': 'strong_bullish', 'confidence': 0.8}
            elif momentum > 5:
                return {'signal': 'bullish', 'confidence': 0.7}
            elif momentum < -10:
                return {'signal': 'strong_bearish', 'confidence': 0.8}
            elif momentum < -5:
                return {'signal': 'bearish', 'confidence': 0.7}
            else:
                return {'signal': 'neutral', 'confidence': 0.5}
                
        except Exception as e:
            print(f"Error calculating momentum: {e}")
            return {'signal': 'neutral', 'confidence': 0.5}

    def get_onchain_metrics(self) -> Dict:
        """Get mock onchain metrics for testing"""
        return {
            'active_addresses': 1000000,
            'total_addresses': 10000000,
            'whale_confidence': 0.8,
            'retail_sentiment': 'positive'
        }
