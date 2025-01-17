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
        
        content = "🔍 Market Analysis\n\n"
        content += f"${market_data.get('symbol', 'BTC')} Update:\n"
        content += f"• Price: ${market_data.get('price', 0):,.2f}\n"
        content += f"• Trend: {market_data.get('trend', 'neutral').upper()}\n"
        
        if 'indicators' in market_data:
            content += "• Indicators:\n"
            for name, value in market_data['indicators'].items():
                content += f"  - {name}: {value}\n"
        
        if 'summary' in analysis:
            content += f"\nAnalysis: {analysis['summary']}"
        
        return content
    
    def _format_gem_alpha(self, data: Dict) -> str:
        """Format gem alpha tweet"""
        gem_data = data.get('gem_data', {})
        
        content = "💎 GEM ALERT 💎\n\n"
        content += f"Found a hidden gem: ${gem_data.get('symbol', 'UNKNOWN')}\n\n"
        content += "Key Metrics:\n"
        
        if 'market_cap' in gem_data:
            content += f"• MCap: ${gem_data['market_cap']:,.0f}\n"
        if 'volume' in gem_data:
            content += f"• 24h Vol: ${gem_data['volume']:,.0f}\n"
        if 'holders' in gem_data:
            content += f"• Holders: {gem_data['holders']:,}\n"
        
        if 'analysis' in gem_data:
            content += f"\nAnalysis: {gem_data['analysis']}"
        
        return content
    
    def _format_portfolio_update(self, data: Dict) -> str:
        """Format portfolio update tweet"""
        stats = data.get('portfolio_stats', {})
        performance = stats.get('performance', {})
        metrics = stats.get('stats', {})
        
        content = "📊 Portfolio Update 📊\n\n"
        content += "Performance:\n"
        content += f"• Daily: {performance.get('daily', 0):+.1f}%\n"
        content += f"• Weekly: {performance.get('weekly', 0):+.1f}%\n"
        content += f"• Monthly: {performance.get('monthly', 0):+.1f}%\n"
        
        content += "\nStats:\n"
        content += f"• Win Rate: {metrics.get('win_rate', 0):.1f}%\n"
        content += f"• Avg Profit: {metrics.get('avg_profit', 0):+.1f}%\n"
        
        if metrics.get('best_trade'):
            content += f"\n🏆 Best: ${metrics['best_trade']}"
        if metrics.get('worst_trade'):
            content += f"\n💩 Worst: ${metrics['worst_trade']}"
        
        return content
    
    def _format_market_awareness(self, data: Dict) -> str:
        """Format market awareness tweet"""
        market_data = data.get('market_data', {})
        analysis = data.get('analysis', {})
        
        content = "👁️ Market Watch 👁️\n\n"
        
        if 'sentiment' in analysis:
            content += f"Sentiment: {analysis['sentiment'].upper()}\n"
        if 'confidence' in analysis:
            content += f"Confidence: {analysis['confidence']}%\n"
        
        if 'signals' in analysis:
            signals = analysis['signals']
            if 'market' in signals:
                content += f"\nMarket Signals:\n{signals['market']}"
            if 'onchain' in signals:
                content += f"\nOn-chain:\n{signals['onchain']}"
            if 'whales' in signals:
                content += f"\nWhale Activity:\n{signals['whales']}"
        
        return content
    
    def _format_shill_review(self, data: Dict) -> str:
        """Format shill review tweet"""
        projects = data.get('projects', [])
        if not projects:
            return None
            
        content = "🔍 Project Review 🔍\n\n"
        project = projects[0]  # Take first project
        
        content += f"Project: {project.get('name', 'Unknown')}\n"
        content += f"Symbol: ${project.get('symbol', 'XXX')}\n\n"
        
        if 'metrics' in project:
            metrics = project['metrics']
            content += "Key Metrics:\n"
            if 'tvl' in metrics:
                content += f"• TVL: ${metrics['tvl']:,.0f}\n"
            if 'volume' in metrics:
                content += f"• Volume: ${metrics['volume']:,.0f}\n"
            if 'growth' in metrics:
                content += f"• Growth: {metrics['growth']:+.1f}%\n"
        
        if 'review' in project:
            content += f"\nVerdict: {project['review']}"
        
        return content
