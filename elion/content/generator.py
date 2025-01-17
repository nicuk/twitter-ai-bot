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
            elif content_type == 'market_search':
                return self._format_market_search(data)
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
        try:
            if not isinstance(data, dict):
                return "Error: Invalid market data format"
                
            market_data = data.get('market_data', {})
            analysis = data.get('analysis', {})
            
            content = "🔍 Market Analysis\n\n"
            content += f"${market_data.get('symbol', 'BTC')} Update:\n"
            content += f"• Price: ${market_data.get('price', 0):,.2f}\n"
            content += f"• Trend: {market_data.get('trend', 'neutral').upper()}\n"
            
            if isinstance(market_data.get('indicators'), dict):
                content += "• Indicators:\n"
                for name, value in market_data['indicators'].items():
                    content += f"  - {name}: {value}\n"
            
            if analysis.get('summary'):
                content += f"\nAnalysis: {analysis['summary']}"
            
            return content
            
        except Exception as e:
            print(f"Error formatting market analysis: {e}")
            return "Error formatting market analysis"
    
    def _format_gem_alpha(self, data: Dict) -> str:
        """Format gem alpha tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid gem data format"
                
            gem_data = data.get('gem_data', {})
            
            content = "💎 GEM ALERT 💎\n\n"
            content += f"Found a hidden gem: ${gem_data.get('symbol', 'UNKNOWN')}\n\n"
            content += "Key Metrics:\n"
            
            if isinstance(gem_data.get('market_cap'), (int, float)):
                content += f"• MCap: ${gem_data['market_cap']:,.0f}\n"
            if isinstance(gem_data.get('volume'), (int, float)):
                content += f"• 24h Vol: ${gem_data['volume']:,.0f}\n"
            if isinstance(gem_data.get('holders'), (int, float)):
                content += f"• Holders: {gem_data['holders']:,}\n"
            
            if gem_data.get('analysis'):
                content += f"\nAnalysis: {gem_data['analysis']}"
            
            return content
            
        except Exception as e:
            print(f"Error formatting gem alpha: {e}")
            return "Error formatting gem alpha"
    
    def _format_portfolio_update(self, data: Dict) -> str:
        """Format portfolio update tweet"""
        try:
            if not isinstance(data, dict) or not isinstance(data.get('portfolio_stats'), dict):
                return "Error: Invalid portfolio data format"

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
            
        except Exception as e:
            print(f"Error formatting portfolio update: {e}")
            return "Error formatting portfolio update"
    
    def _format_market_awareness(self, data: Dict) -> str:
        """Format market awareness tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid market awareness data"
                
            market_data = data.get('market_data', {})
            analysis = data.get('analysis', {})
            
            content = "👁️ Market Watch 👁️\n\n"
            
            if analysis.get('sentiment'):
                content += f"Sentiment: {analysis['sentiment'].upper()}\n"
            if isinstance(analysis.get('confidence'), (int, float)):
                content += f"Confidence: {analysis['confidence']}%\n"
            
            signals = analysis.get('signals', {})
            if isinstance(signals, dict):
                if signals.get('market'):
                    content += f"\nMarket Signals:\n{signals['market']}"
                if signals.get('onchain'):
                    content += f"\nOn-chain:\n{signals['onchain']}"
                if signals.get('whales'):
                    content += f"\nWhale Activity:\n{signals['whales']}"
            
            return content
            
        except Exception as e:
            print(f"Error formatting market awareness: {e}")
            return "Error formatting market awareness"
    
    def _format_market_search(self, data: Dict) -> str:
        """Format market search tweet based on Twitter data"""
        try:
            if not isinstance(data, list):
                return "Error: Invalid market search data format"
                
            content = "🔍 Market Pulse\n\n"
            
            # Add viral tweets analysis
            if data:
                content += "Trending Topics:\n"
                for tweet in data[:3]:  # Top 3 viral tweets
                    username = tweet.get('username', 'Unknown')
                    text = tweet.get('text', '').split('\n')[0][:100]  # First line, truncated
                    engagement = tweet.get('engagement_score', 0)
                    content += f"• @{username}: {text}...\n"
                    content += f"  Engagement: {engagement:,}\n\n"
            else:
                content += "No significant market movements detected."
            
            return content
            
        except Exception as e:
            print(f"Error formatting market search: {e}")
            return "Error formatting market search"
    
    def _format_shill_review(self, data: Dict) -> str:
        """Format shill review tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid shill review data"
                
            projects = data.get('projects', [])
            if not projects or not isinstance(projects, list):
                return "No projects to review"
                
            content = "🔍 Project Review 🔍\n\n"
            project = projects[0]  # Take first project
            
            if isinstance(project, dict):
                content += f"Project: {project.get('name', 'Unknown')}\n"
                content += f"Symbol: ${project.get('symbol', 'XXX')}\n\n"
                
                if project.get('description'):
                    content += f"About: {project['description']}\n\n"
                    
                if isinstance(project.get('metrics'), dict):
                    metrics = project['metrics']
                    content += "Metrics:\n"
                    for key, value in metrics.items():
                        content += f"• {key}: {value}\n"
            
            return content
            
        except Exception as e:
            print(f"Error formatting shill review: {e}")
            return "Error formatting shill review"
