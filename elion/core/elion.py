"""
Core Elion class - Streamlined for better maintainability
"""

from datetime import datetime
from typing import Dict, List, Optional

from ..analysis.market import MarketAnalyzer
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.onchain import OnChainAnalyzer
from ..content.generator import ContentGenerator
from ..personality.traits import PersonalityManager
from ..utils.metrics import MetricsTracker

class Elion:
    """Elion AI Agent for Crypto Twitter - Core functionality"""
    
    def __init__(self, api_key: str = None):
        """Initialize Elion with core components"""
        self.api_key = api_key
        
        # Initialize core components
        self.market = MarketAnalyzer(api_key)
        self.technical = TechnicalAnalyzer()
        self.onchain = OnChainAnalyzer(api_key)
        self.content = ContentGenerator()
        self.personality = PersonalityManager()
        self.metrics = MetricsTracker()
        
        # Track current state
        self.state = {
            'last_analysis': None,
            'market_mood': 'neutral',
            'confidence': 0.0
        }

    def generate_tweet(self, content_type: str, context: Optional[Dict] = None) -> str:
        """Generate a tweet based on content type and context"""
        try:
            # Get market analysis
            market_data = self.market.get_current_data()
            technical_analysis = self.technical.analyze(market_data)
            onchain_data = self.onchain.analyze(market_data)
            
            # Update state
            self.state.update({
                'last_analysis': datetime.now(),
                'market_mood': self._determine_mood(market_data),
                'confidence': self._calculate_confidence(technical_analysis, onchain_data)
            })
            
            # Generate content
            content = self.content.generate(
                content_type=content_type,
                market_data=market_data,
                technical_analysis=technical_analysis,
                onchain_data=onchain_data,
                context=context,
                state=self.state
            )
            
            # Add personality
            if content:
                content = self.personality.enhance_content(
                    content=content,
                    mood=self.state['market_mood'],
                    confidence=self.state['confidence']
                )
            
            # Track metrics
            self.metrics.track_content(content_type, content, self.state['confidence'])
            
            return content
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def analyze_performance(self, tweet_data: Dict) -> Dict:
        """Analyze tweet performance and update strategies"""
        try:
            # Track performance
            performance = self.metrics.analyze_tweet(tweet_data)
            
            # Update personality based on performance
            self.personality.adapt(performance)
            
            # Update content generator
            self.content.optimize(performance)
            
            return performance
            
        except Exception as e:
            print(f"Error analyzing performance: {e}")
            return None

    def _determine_mood(self, market_data: Dict) -> str:
        """Determine market mood based on analysis"""
        try:
            sentiment = market_data.get('sentiment', 'neutral')
            trend = market_data.get('trend', 'neutral')
            volatility = market_data.get('volatility', 'normal')
            
            if sentiment == 'bullish' and trend == 'up':
                return 'confident'
            elif sentiment == 'bearish' and trend == 'down':
                return 'cautious'
            elif volatility == 'high':
                return 'mysterious'
            else:
                return 'neutral'
                
        except Exception as e:
            print(f"Error determining mood: {e}")
            return 'neutral'

    def _calculate_confidence(self, technical: Dict, onchain: Dict) -> float:
        """Calculate overall confidence score"""
        try:
            technical_confidence = technical.get('confidence', 0.0)
            onchain_confidence = onchain.get('confidence', 0.0)
            
            # Weight technical and onchain signals
            return (technical_confidence * 0.6) + (onchain_confidence * 0.4)
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.0
