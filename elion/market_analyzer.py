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
            market_data = self.data_sources.get_market_alpha() or {}
            
            # Extract required fields
            result = {
                'btc_price': float(market_data.get('btc', {}).get('price', 0)),
                'eth_price': float(market_data.get('eth', {}).get('price', 0)),
                'market_cap': float(market_data.get('total_market_cap', 0)) / 1e9,  # Convert to billions
                'volume_24h': float(market_data.get('total_volume_24h', 0)) / 1e9,  # Convert to billions
                'sentiment': market_data.get('market_sentiment', 'neutral'),
                'fear_greed': market_data.get('fear_greed_index', 50),
            }
            
            # Add top gainers if available
            if 'top_gainers' in market_data:
                result['top_gainers'] = [
                    {
                        'symbol': coin['symbol'],
                        'change_24h': float(coin.get('change_24h', 0))
                    }
                    for coin in market_data['top_gainers'][:3]
                ]
            
            # Cache results
            self.market_state.update({
                'last_analysis': current_time,
                'analysis_cache': result,
                'market_mood': result['sentiment']
            })
            
            return result
            
        except Exception as e:
            print(f"Error in market analysis: {e}")
            return {}
    
    def _format_market_prompt(self, data: Dict) -> str:
        """Format market data into LLM prompt"""
        prompt = """Analyze the following market data and provide insights:

Market Overview:
- Price: ${price}
- 24h Change: {change}%
- Volume: ${volume}
- Market Cap: ${market_cap}

Recent Events:
{events}

Social Sentiment:
{sentiment}

Your analysis should include:
1. Overall market sentiment (bullish/bearish/neutral)
2. Key signals or patterns
3. Confidence level (0.0-1.0)
4. Brief market summary

Respond in a structured format:
SENTIMENT: [sentiment]
CONFIDENCE: [confidence]
SIGNALS: [signal1, signal2, ...]
SUMMARY: [brief analysis]
"""
        
        # Format data
        events = "\n".join([f"- {e}" for e in data.get('recent_events', [])])
        if not events:
            events = "No significant events"
            
        return prompt.format(
            price=data.get('price', 'N/A'),
            change=data.get('price_change_24h', 'N/A'),
            volume=data.get('volume_24h', 'N/A'),
            market_cap=data.get('market_cap', 'N/A'),
            events=events,
            sentiment=data.get('social_sentiment', 'No sentiment data')
        )

    def _parse_llm_analysis(self, analysis: str) -> Dict:
        """Parse LLM analysis into structured format"""
        try:
            lines = analysis.strip().split('\n')
            result = {
                'sentiment': 'neutral',
                'confidence': 0.3,
                'signals': [],
                'summary': "No analysis available"
            }
            
            for line in lines:
                if line.startswith('SENTIMENT:'):
                    result['sentiment'] = line.split(':')[1].strip().lower()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        result['confidence'] = float(line.split(':')[1].strip())
                    except ValueError:
                        pass
                elif line.startswith('SIGNALS:'):
                    signals = line.split(':')[1].strip()
                    result['signals'] = [s.strip() for s in signals.split(',') if s.strip()]
                elif line.startswith('SUMMARY:'):
                    result['summary'] = line.split(':')[1].strip()
                    
            return result
            
        except Exception as e:
            print(f"Error parsing LLM analysis: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.3,
                'signals': [],
                'summary': "Error parsing analysis"
            }

    def _generate_summary(self, sentiment: Dict, onchain: Dict, whales: Dict, price_action: Dict, technical_indicators: Dict) -> str:
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
        
        # Add price action analysis
        if price_action.get('signals'):
            summary.append(f"Price action: {', '.join(price_action['signals'])}")
        
        # Add technical indicators analysis
        if technical_indicators.get('signals'):
            summary.append(f"Technical indicators: {', '.join(technical_indicators['signals'])}")
        
        return " | ".join(summary) if summary else "No significant market signals"
