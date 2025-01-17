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
            # Gather all required data with safe defaults
            market_data = {}
            onchain_data = {}
            whale_data = []
            
            try:
                market_data = self.data_sources.get_market_alpha() or {}
            except Exception as e:
                print(f"Error getting market alpha: {e}")
                
            try:
                onchain_data = self.data_sources.get_market_data() or {}
            except Exception as e:
                print(f"Error getting market data: {e}")
                
            try:
                whale_data = self.data_sources.get_whale_movements() or []
            except Exception as e:
                print(f"Error getting whale data: {e}")
            
            # Analyze each component with safe defaults
            sentiment = self._analyze_market_sentiment(market_data)
            onchain = self._analyze_onchain_metrics(onchain_data)
            whales = self._analyze_whale_movements(whale_data)
            
            # Combine analyses
            analysis = {
                'sentiment': sentiment.get('mood', 'neutral'),
                'confidence': max(
                    sentiment.get('confidence', 0.3),
                    onchain.get('confidence', 0.3),
                    whales.get('confidence', 0.3)
                ),
                'signals': {
                    'market': sentiment.get('signals', []),
                    'onchain': onchain.get('signals', []),
                    'whales': whales.get('signals', [])
                },
                'summary': self._generate_summary(sentiment, onchain, whales),
                'timestamp': current_time
            }
            
            # Cache results
            self.market_state.update({
                'last_analysis': current_time,
                'analysis_cache': analysis,
                'market_mood': sentiment.get('mood', 'neutral')
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
        if not isinstance(data, dict):
            return {'mood': 'neutral', 'confidence': 0.3, 'signals': []}
            
        signals = []
        score = 0.5  # Start neutral
        confidence = 0.0
        signal_count = 0
        
        # Social sentiment (safely handle non-numeric values)
        try:
            social = float(data.get('social_sentiment', 0.5))
            signal_count += 1
            if social > 0.6:
                score += 0.2
                signals.append('positive_social_sentiment')
            elif social < 0.4:
                score -= 0.2
                signals.append('negative_social_sentiment')
            confidence += abs(social - 0.5) * 2
        except (ValueError, TypeError):
            pass
        
        # Volume (safely handle non-numeric values)
        try:
            volume = float(data.get('volume_change', 0))
            if abs(volume) > 0:  # Only count if we have valid data
                signal_count += 1
                if volume > 20:
                    score += 0.15
                    signals.append('high_volume')
                elif volume < -20:
                    score -= 0.15
                    signals.append('low_volume')
                confidence += min(abs(volume) / 100, 0.5)
        except (ValueError, TypeError):
            pass
            
        # Normalize results
        if signal_count > 0:
            confidence = min(confidence / signal_count, 1.0)
        else:
            confidence = 0.3  # Default confidence
            
        # Determine mood
        if score > 0.6:
            mood = 'bullish'
        elif score < 0.4:
            mood = 'bearish'
        else:
            mood = 'neutral'
            
        return {
            'mood': mood,
            'confidence': confidence,
            'signals': signals
        }
    
    def _analyze_onchain_metrics(self, data: Dict) -> Dict:
        """Analyze on-chain metrics for market health"""
        if not isinstance(data, dict):
            return {'confidence': 0.3, 'signals': []}
            
        signals = []
        confidence = 0.5
        
        # Network growth
        try:
            growth = float(data.get('network_growth', 0))
            if growth > 0.1:
                signals.append('growing_network')
                confidence += 0.2
            elif growth < -0.1:
                signals.append('shrinking_network')
                confidence -= 0.2
        except (ValueError, TypeError):
            pass
        
        # Whale confidence
        try:
            whale_conf = float(data.get('whale_confidence', 0.5))
            if whale_conf > 0.7:
                signals.append('high_whale_confidence')
                confidence += 0.2
            elif whale_conf < 0.3:
                signals.append('low_whale_confidence')
                confidence -= 0.2
        except (ValueError, TypeError):
            pass
        
        # Active addresses
        try:
            active = int(data.get('active_addresses', 0))
            avg_active = int(data.get('avg_active_addresses', active))
            if active > avg_active:
                signals.append('increasing_activity')
                confidence += 0.1
        except (ValueError, TypeError):
            pass
        
        confidence = max(0.1, min(1.0, confidence))
        return {'confidence': confidence, 'signals': signals}
    
    def _analyze_whale_movements(self, data: List) -> Dict:
        """Analyze whale movements for market signals"""
        if not isinstance(data, list):
            return {'signals': []}
            
        signals = []
        buy_volume = sum(m.get('volume', 0) for m in data if m.get('type') == 'buy')
        sell_volume = sum(m.get('volume', 0) for m in data if m.get('type') == 'sell')
        
        if buy_volume > sell_volume * 1.5:
            signals.append('whale_accumulation')
        elif sell_volume > buy_volume * 1.5:
            signals.append('whale_distribution')
        
        return {'signals': signals}
    
    def _generate_summary(self, sentiment: Dict, onchain: Dict, whales: Dict) -> str:
        """Generate a human-readable market summary"""
        summary = []
        
        # Add sentiment if confident
        if sentiment.get('confidence', 0.3) > 0.6:
            summary.append(f"Market sentiment is {sentiment.get('mood', 'neutral')}")
            if sentiment.get('signals'):
                summary.append(f"Key signals: {', '.join(sentiment['signals'])}")
        
        # Add strong on-chain signals
        if onchain.get('confidence', 0.3) > 0.6 and onchain.get('signals'):
            summary.append(f"On-chain metrics show: {', '.join(onchain['signals'])}")
        
        # Add whale activity if present
        if whales.get('signals'):
            summary.append(f"Whale activity: {', '.join(whales['signals'])}")
        
        return " | ".join(summary) if summary else "No significant market signals"
