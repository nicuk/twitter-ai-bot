"""
Content generation for different tweet types
"""

from typing import Dict, Optional
from .tweet_formatters import TweetFormatters

class ContentGenerator:
    """Generates tweet content using personality and LLM"""
    
    def __init__(self, personality, llm):
        self.personality = personality
        self.llm = llm
        self.formatters = TweetFormatters(personality)
        
    def generate(self, content_type: str, data: Dict) -> Optional[str]:
        """Generate tweet content based on type and data"""
        try:
            if content_type == 'market_analysis':
                return self._format_market_analysis(data)
            elif content_type == 'gem_alpha':
                return self._format_gem_alpha(data)
            elif content_type == 'portfolio_update':
                return self._format_portfolio_update(data)
            elif content_type == 'market_aware':
                return self._format_market_awareness(data)
            elif content_type == 'shill_review':
                return self._format_shill_review(data)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
                
        except Exception as e:
            print(f"Error generating {content_type}: {e}")
            return "Error generating tweet"
            
    def _format_market_analysis(self, data: Dict) -> str:
        """Format market analysis tweet"""
        market_data = data.get('market_data', {})
        analysis = data.get('analysis', {})
        
        # Get market conditions
        symbol = market_data.get('symbol', 'BTC')
        price = market_data.get('price', 0)
        trend = market_data.get('trend', 'neutral')
        
        # Format indicators
        indicators = []
        if 'rsi' in market_data:
            indicators.append(f"RSI: {market_data['rsi']}")
        if 'macd' in market_data:
            indicators.append(f"MACD: {market_data['macd']}")
        if 'volume' in market_data:
            indicators.append(f"Volume: {market_data['volume']}")
            
        # Get AI analysis
        ai_analysis = self.llm.generate(
            f"Analyze {symbol} at ${price:,} with {trend} trend. "
            f"Keep it concise and engaging."
        )
        
        # Format tweet
        content = f" ${symbol} Technical Analysis\n\n"
        content += f"Price: ${price:,}\n"
        content += f"Trend: {trend.upper()}\n"
        if indicators:
            content += "\n" + "\n".join(indicators)
        content += f"\n\n{ai_analysis}"
        
        return self.personality.enhance_tweet(content)
        
    def _format_gem_alpha(self, data: Dict) -> str:
        """Format gem alpha tweet"""
        gem_data = data.get('gem_data', {})
        
        # Extract gem info
        name = gem_data.get('name', '')
        symbol = gem_data.get('symbol', '')
        score = gem_data.get('score', 0)
        market_data = gem_data.get('market_data', {})
        analysis = gem_data.get('analysis', '')
        conviction = gem_data.get('conviction_level', 'MEDIUM')
        
        # Get AI analysis
        ai_analysis = self.llm.generate(
            f"Analyze {name} (${symbol}) as a potential gem. "
            f"Score: {score}/100, Market Cap: ${market_data.get('market_cap', 0):,}. "
            f"Keep it concise and engaging."
        )
        
        # Format tweet
        content = f" GEM ALERT: ${symbol}\n\n"
        content += f"Score: {score}/100\n"
        content += f"Market Cap: ${market_data.get('market_cap', 0):,}\n"
        content += f"Volume: ${market_data.get('volume', 0):,}\n"
        content += f"Price: ${market_data.get('price', 0)}\n"
        content += f"\nConviction: {conviction}\n"
        content += f"\n{ai_analysis}"
        
        return self.personality.enhance_tweet(content)
        
    def _format_portfolio_update(self, data: Dict) -> str:
        """Format portfolio update tweet"""
        stats = data.get('portfolio_stats', {})
        
        # Extract portfolio stats
        total_value = stats.get('total_value', 0)
        total_roi = stats.get('total_roi', 0)
        win_rate = stats.get('win_rate', 0)
        positions = stats.get('positions', [])
        
        # Format positions
        position_text = []
        for pos in positions[:3]:  # Show top 3 positions
            symbol = pos.get('symbol', '')
            roi = pos.get('roi', 0)
            position_text.append(f"${symbol}: {roi*100:.1f}%")
            
        # Get AI analysis
        ai_analysis = self.llm.generate(
            f"Analyze portfolio performance with {total_roi*100:.1f}% ROI "
            f"and {win_rate*100:.1f}% win rate. Keep it concise and engaging."
        )
        
        # Format tweet
        content = f" Portfolio Update\n\n"
        content += f"Total Value: ${total_value:,}\n"
        content += f"Total ROI: {total_roi*100:.1f}%\n"
        content += f"Win Rate: {win_rate*100:.1f}%\n"
        if position_text:
            content += f"\nTop Positions:\n" + "\n".join(position_text)
        content += f"\n\n{ai_analysis}"
        
        return self.personality.enhance_tweet(content)
        
    def _format_market_awareness(self, data: Dict) -> str:
        """Format market awareness tweet"""
        market_data = data.get('market_data', {})
        analysis = data.get('analysis', {})
        
        # Get AI analysis
        ai_analysis = self.llm.generate(
            f"Analyze current market conditions and sentiment. "
            f"Keep it concise and engaging."
        )
        
        # Format tweet
        content = f" Market Update\n\n"
        content += f"BTC Dominance: {market_data.get('btc_dominance', 0)}%\n"
        content += f"Market Cap: ${market_data.get('market_cap', 0):,}\n"
        content += f"24h Volume: ${market_data.get('volume_24h', 0):,}\n"
        
        # Add trending coins
        trending = market_data.get('trending_coins', [])
        if trending:
            content += f"\nTrending: " + " ".join(f"${coin}" for coin in trending[:3])
            
        content += f"\n\n{ai_analysis}"
        
        return self.personality.enhance_tweet(content)
        
    def _format_shill_review(self, data: Dict) -> str:
        """Format shill review tweet"""
        projects = data.get('projects', [])
        if not projects:
            return None
            
        project = projects[0]  # Get first project
        
        # Extract project info
        name = project.get('name', '')
        symbol = project.get('symbol', '')
        score = project.get('score', 0)
        analysis = project.get('analysis', '')
        conviction = project.get('conviction_level', 'MEDIUM')
        
        # Get AI analysis
        ai_analysis = self.llm.generate(
            f"Review {name} (${symbol}) for potential investment. "
            f"Score: {score}/100, Analysis: {analysis}. "
            f"Keep it concise and engaging."
        )
        
        # Format tweet
        content = f" Project Review: ${symbol}\n\n"
        content += f"Score: {score}/100\n"
        content += f"Conviction: {conviction}\n"
        content += f"\n{ai_analysis}"
        
        return self.personality.enhance_tweet(content)
