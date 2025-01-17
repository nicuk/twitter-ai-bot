"""
Market analysis functionality for Elion
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

class MarketAnalyzer:
    """Handles market analysis using sentiment, on-chain metrics, and whale activity"""
    
    def __init__(self, data_sources):
        self.data_sources = data_sources
        self.market_state = {
            'last_analysis': None,
            'analysis_cache': {},
            'market_mood': 'neutral'
        }
    
    def analyze_market_conditions(self) -> Dict:
        """Analyze current market conditions using multiple indicators"""
        current_time = datetime.utcnow()
        
        # Use cached analysis if recent enough
        if (self.market_state['last_analysis'] and 
            (current_time - self.market_state['last_analysis']) <= timedelta(minutes=15)):
            return self.market_state['analysis_cache']
            
        try:
            # Gather all required data
            market_data = self.data_sources.get_market_alpha()
            onchain_data = self.data_sources.get_onchain_metrics()
            whale_data = self.data_sources.get_whale_movements()
            
            # Analyze each component
            sentiment = self._analyze_market_sentiment(market_data)
            onchain = self._analyze_onchain_metrics(onchain_data)
            whales = self._analyze_whale_movements(whale_data)
            
            # Combine analyses
            analysis = {
                'sentiment': sentiment['mood'],
                'confidence': max(sentiment['confidence'], onchain['confidence']),
                'signals': {
                    'market': sentiment['signals'],
                    'onchain': onchain['signals'],
                    'whales': whales['signals']
                },
                'summary': self._generate_summary(sentiment, onchain, whales),
                'timestamp': current_time
            }
            
            # Cache results
            self.market_state.update({
                'last_analysis': current_time,
                'analysis_cache': analysis,
                'market_mood': sentiment['mood']
            })
            
            return analysis
            
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.3,
                'signals': {'market': [], 'onchain': [], 'whales': []},
                'summary': "Unable to analyze market conditions",
                'timestamp': current_time
            }
    
    def _analyze_market_sentiment(self, data: Dict) -> Dict:
        """Analyze market sentiment from price, volume, and social indicators"""
        if not data:
            return {'mood': 'neutral', 'confidence': 0.3, 'signals': []}
            
        signals = []
        score = 0.5  # Start neutral
        confidence = 0.0
        signal_count = 0
        
        # Social sentiment
        if social := data.get('social_sentiment'):
            signal_count += 1
            if social > 0.6:
                score += 0.2
                signals.append('positive_social_sentiment')
            elif social < 0.4:
                score -= 0.2
                signals.append('negative_social_sentiment')
            confidence += abs(social - 0.5) * 2
        
        # Volume
        if volume := data.get('volume_change'):
            signal_count += 1
            if volume > 0.2:
                score += 0.15
                signals.append('increasing_volume')
            elif volume < -0.2:
                score -= 0.15
                signals.append('decreasing_volume')
            confidence += min(abs(volume), 1.0)
        
        # Price momentum
        if price := data.get('price_change'):
            signal_count += 1
            if price > 0:
                score += 0.25
                signals.append('positive_price_momentum')
            else:
                score -= 0.25
                signals.append('negative_price_momentum')
            confidence += min(abs(price), 1.0)
        
        # Normalize scores
        score = max(0.0, min(1.0, score))
        confidence = confidence / max(1, signal_count)
        
        # Determine mood
        mood = 'very_bullish' if score > 0.7 and confidence > 0.7 else \
               'bullish' if score > 0.6 else \
               'very_bearish' if score < 0.3 and confidence > 0.7 else \
               'bearish' if score < 0.4 else \
               'neutral'
        
        return {'mood': mood, 'confidence': confidence, 'signals': signals}
    
    def _analyze_onchain_metrics(self, data: Dict) -> Dict:
        """Analyze on-chain metrics for market health"""
        if not data:
            return {'confidence': 0.3, 'signals': []}
            
        signals = []
        confidence = 0.5
        
        # Network growth
        if growth := data.get('network_growth', 0):
            if growth > 0.1:
                signals.append('growing_network')
                confidence += 0.2
            elif growth < -0.1:
                signals.append('shrinking_network')
                confidence -= 0.2
        
        # Whale confidence
        if whale_conf := data.get('whale_confidence', 0.5):
            if whale_conf > 0.7:
                signals.append('high_whale_confidence')
                confidence += 0.2
            elif whale_conf < 0.3:
                signals.append('low_whale_confidence')
                confidence -= 0.2
        
        # Active addresses
        if active := data.get('active_addresses', 0):
            if active > data.get('avg_active_addresses', active):
                signals.append('increasing_activity')
                confidence += 0.1
        
        confidence = max(0.1, min(1.0, confidence))
        return {'confidence': confidence, 'signals': signals}
    
    def _analyze_whale_movements(self, data: List) -> Dict:
        """Analyze whale movements for market signals"""
        if not data:
            return {'signals': []}
            
        signals = []
        buy_volume = sum(m['volume'] for m in data if m['type'] == 'buy')
        sell_volume = sum(m['volume'] for m in data if m['type'] == 'sell')
        
        if buy_volume > sell_volume * 1.5:
            signals.append('whale_accumulation')
        elif sell_volume > buy_volume * 1.5:
            signals.append('whale_distribution')
        
        return {'signals': signals}
    
    def _generate_summary(self, sentiment: Dict, onchain: Dict, whales: Dict) -> str:
        """Generate a human-readable market summary"""
        summary = []
        
        # Add sentiment if confident
        if sentiment['confidence'] > 0.6:
            summary.append(f"Market sentiment is {sentiment['mood']}")
            if sentiment['signals']:
                summary.append(f"Key signals: {', '.join(sentiment['signals'])}")
        
        # Add strong on-chain signals
        if onchain['confidence'] > 0.6 and onchain['signals']:
            summary.append(f"On-chain metrics show: {', '.join(onchain['signals'])}")
        
        # Add whale activity if present
        if whales['signals']:
            summary.append(f"Whale activity: {', '.join(whales['signals'])}")
        
        return " | ".join(summary) if summary else "No significant market signals"
