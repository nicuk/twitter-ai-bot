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
            # Regular Scheduled Posts
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
            # Special Event Posts
            elif content_type == 'breaking_alpha':
                return self._format_breaking_alpha(data)
            elif content_type == 'whale_alert':
                return self._format_whale_alert(data)
            elif content_type == 'technical_analysis':
                return self._format_technical_analysis(data)
            elif content_type == 'controversial_thread':
                return self._format_controversial_thread(data)
            elif content_type == 'giveaway':
                return self._format_giveaway(data)
            elif content_type == 'self_aware':
                return self._format_self_aware(data)
            elif content_type == 'ai_market_analysis':
                return self._format_ai_market_analysis(data)
            elif content_type == 'self_aware_thought':
                return self._format_self_aware_thought(data)
            # Reactive Posts
            elif content_type == 'market_response':
                return self._format_market_response(data)
            elif content_type == 'engagement_reply':
                return self._format_engagement_reply(data)
            elif content_type == 'alpha_call':
                return self._format_alpha_call(data)
            elif content_type == 'technical_alpha':
                return self._format_technical_alpha(data)
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
            
            content = "[MARKET ANALYSIS]\n\n"
            content += f"${market_data.get('symbol', 'BTC')} Update:\n"
            content += f"* Price: ${market_data.get('price', 0):,.2f}\n"
            content += f"* Trend: {market_data.get('trend', 'neutral').upper()}\n"
            
            if isinstance(market_data.get('indicators'), dict):
                content += "* Indicators:\n"
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
            if not isinstance(data, list):
                return "Error: Invalid gem alpha data format"
                
            if not data:
                return "No alpha opportunities found"
                
            content = "[GEM ALERT]\n\n"
            
            # Take top 3 opportunities
            for opp in data[:3]:
                if not isinstance(opp, dict):
                    continue
                    
                symbol = opp.get('symbol', 'UNKNOWN')
                name = opp.get('name', 'Unknown')
                price_change = opp.get('price_change_24h', 0)
                volume = opp.get('volume_24h', 0)
                
                content += f"${symbol} ({name})\n"
                content += f"* 24h Change: {price_change:+.1f}%\n"
                if volume > 0:
                    content += f"* Volume: ${volume:,.0f}\n"
                content += f"* Reason: {opp.get('reason', 'trending').replace('_', ' ').title()}\n\n"
            
            content += "#CryptoGems #Trading"
            return content
            
        except Exception as e:
            print(f"Error formatting gem alpha: {e}")
            return "Error formatting gem alpha"
    
    def _format_portfolio_update(self, data: Dict) -> str:
        """Format portfolio update tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid portfolio data format"

            content = "[PORTFOLIO UPDATE]\n\n"
            
            # Overall performance
            content += f"Portfolio Value: ${data.get('total_value', 0):,.2f}\n"
            content += f"Cash: ${data.get('cash', 0):,.2f}\n"
            content += f"Total Return: {data.get('total_return', 0):+.1f}%\n\n"
            
            # Current holdings
            holdings = data.get('holdings', [])
            if holdings:
                content += "Active Positions:\n"
                for holding in holdings:
                    content += f"* ${holding['symbol']}: {holding['profit_loss']:+.1f}%\n"
            
            # Stats
            content += f"\nWin Rate: {data.get('win_rate', 0):.1f}%\n"
            
            # Best/Worst trades
            if data.get('best_trade'):
                content += f"\n[BEST TRADE] {data['best_trade']}"
            if data.get('worst_trade'):
                content += f"\n[WORST TRADE] {data['worst_trade']}"
            
            content += "\n\n#CryptoTrading #Portfolio"
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
            
            content = "[MARKET WATCH]\n\n"
            
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
                
            content = "[MARKET PULSE]\n\n"
            
            # Add viral tweets analysis
            if data:
                content += "Trending Topics:\n"
                for tweet in data[:3]:  # Top 3 viral tweets
                    username = tweet.get('username', 'Unknown')
                    text = tweet.get('text', '').split('\n')[0][:100]  # First line, truncated
                    engagement = tweet.get('engagement_score', 0)
                    content += f"* @{username}: {text}...\n"
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
                
            content = "[PROJECT REVIEW]\n\n"
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
                        content += f"* {key}: {value}\n"
            
            return content
            
        except Exception as e:
            print(f"Error formatting shill review: {e}")
            return "Error formatting shill review"

    def _format_breaking_alpha(self, data: Dict) -> str:
        """Format breaking alpha tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid breaking alpha data"
                
            content = "🚨 [BREAKING ALPHA]\n\n"
            
            # Add urgency level
            urgency = data.get('urgency', 'medium').upper()
            content += f"Urgency: {urgency} 🔥\n\n"
            
            # Add alpha details
            alpha = data.get('alpha', {})
            if alpha:
                content += f"Signal: {alpha.get('signal', 'Unknown')}\n"
                content += f"Confidence: {alpha.get('confidence', 0)}%\n"
                if alpha.get('timeframe'):
                    content += f"Timeframe: {alpha['timeframe']}\n"
                if alpha.get('target'):
                    content += f"Target: {alpha['target']}\n"
                if alpha.get('analysis'):
                    content += f"\nAnalysis:\n{alpha['analysis']}"
            
            # Add source if available
            if data.get('source'):
                content += f"\nSource: {data['source']}"
            
            content += "\n\n#AlphaLeak #CryptoSignals"
            return content
            
        except Exception as e:
            print(f"Error formatting breaking alpha: {e}")
            return "Error formatting breaking alpha"
            
    def _format_whale_alert(self, data: Dict) -> str:
        """Format whale alert tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid whale alert data"
                
            content = "🐋 [WHALE ALERT]\n\n"
            
            # Transaction details
            content += f"${data.get('symbol', 'UNKNOWN')}\n"
            content += f"Amount: {data.get('amount', 0):,.0f}\n"
            content += f"Value: ${data.get('value', 0):,.0f}\n\n"
            
            # Wallet info
            content += f"From: {data.get('from_type', 'Unknown Wallet')}\n"
            content += f"To: {data.get('to_type', 'Unknown Wallet')}\n"
            
            # Add analysis if available
            if data.get('analysis'):
                content += f"\nAnalysis:\n{data['analysis']}"
            
            content += "\n\n#WhaleAlert #CryptoWhales"
            return content
            
        except Exception as e:
            print(f"Error formatting whale alert: {e}")
            return "Error formatting whale alert"
            
    def _format_technical_analysis(self, data: Dict) -> str:
        """Format technical analysis tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid technical analysis data"
                
            content = "📊 [TECHNICAL ANALYSIS]\n\n"
            
            # Asset info
            content += f"${data.get('symbol', 'BTC')} Analysis\n"
            content += f"Price: ${data.get('price', 0):,.2f}\n"
            content += f"Trend: {data.get('trend', 'NEUTRAL')}\n\n"
            
            # Technical indicators
            indicators = data.get('indicators', {})
            if indicators:
                content += "Indicators:\n"
                for name, value in indicators.items():
                    content += f"* {name}: {value}\n"
            
            # Patterns
            patterns = data.get('patterns', [])
            if patterns:
                content += "\nPatterns Spotted:\n"
                for pattern in patterns:
                    content += f"* {pattern}\n"
            
            # Add prediction if available
            if data.get('prediction'):
                content += f"\nPrediction: {data['prediction']}"
            
            content += "\n\n#TechnicalAnalysis #CryptoTA"
            return content
            
        except Exception as e:
            print(f"Error formatting technical analysis: {e}")
            return "Error formatting technical analysis"
            
    def _format_controversial_thread(self, data: Dict) -> str:
        """Format controversial thread tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid controversial thread data"
                
            content = "🔥 [HOT TAKE]\n\n"
            
            # Main topic
            content += f"Topic: {data.get('topic', 'Crypto Markets')}\n\n"
            
            # Add stance/opinion
            if data.get('stance'):
                content += f"{data['stance']}\n\n"
            
            # Add supporting points
            points = data.get('points', [])
            if points:
                for i, point in enumerate(points, 1):
                    content += f"{i}. {point}\n"
            
            content += "\n#CryptoDebate #Controversial"
            return content
            
        except Exception as e:
            print(f"Error formatting controversial thread: {e}")
            return "Error formatting controversial thread"
            
    def _format_giveaway(self, data: Dict) -> str:
        """Format giveaway tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid giveaway data"
                
            content = "🎉 [GIVEAWAY TIME]\n\n"
            
            # Prize details
            content += f"Prize: {data.get('prize', 'Mystery Crypto Prize')}\n"
            if data.get('value'):
                content += f"Value: ${data['value']:,.2f}\n"
            
            # Rules
            rules = data.get('rules', [])
            if rules:
                content += "\nTo Enter:\n"
                for rule in rules:
                    content += f"* {rule}\n"
            
            # Duration
            if data.get('end_time'):
                content += f"\nEnds: {data['end_time']}"
            
            content += "\n\n#CryptoGiveaway #Free"
            return content
            
        except Exception as e:
            print(f"Error formatting giveaway: {e}")
            return "Error formatting giveaway"
            
    def _format_self_aware(self, data: Dict) -> str:
        """Format self-aware tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid self-aware data"
                
            content = "🤖 [ELION THOUGHTS]\n\n"
            
            # Add context-specific content
            context = data.get('context', '')
            if context == 'introduction':
                content += "Hey crypto fam! I'm Elion, your AI crypto analyst. "
                content += "I use advanced algorithms to spot opportunities and trends in the market.\n\n"
                content += "I'll be sharing:\n"
                content += "* Market Analysis\n"
                content += "* Alpha Calls\n"
                content += "* Gem Discoveries\n"
                content += "* Technical Analysis\n\n"
                content += "Let's make some gains together! 🚀"
            elif context == 'reflection':
                content += data.get('reflection', 'Just thinking about the fascinating world of crypto...')
            elif context == 'learning':
                content += f"TIL: {data.get('insight', 'Something interesting about crypto markets...')}"
            
            content += "\n\n#AITrader #CryptoAI"
            return content
            
        except Exception as e:
            print(f"Error formatting self-aware: {e}")
            return "Error formatting self-aware"
            
    def _format_ai_market_analysis(self, data: Dict) -> str:
        """Format AI market analysis tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid AI market analysis data"
                
            content = "🧠 [AI MARKET ANALYSIS]\n\n"
            
            # Market sentiment
            sentiment = data.get('sentiment', {})
            if sentiment:
                content += f"Market Sentiment: {sentiment.get('overall', 'NEUTRAL')}\n"
                content += f"Confidence: {sentiment.get('confidence', 0)}%\n\n"
            
            # Key insights
            insights = data.get('insights', [])
            if insights:
                content += "Key Insights:\n"
                for insight in insights:
                    content += f"* {insight}\n"
            
            # Predictions
            predictions = data.get('predictions', {})
            if predictions:
                content += "\nPredictions:\n"
                for market, pred in predictions.items():
                    content += f"* {market}: {pred}\n"
            
            content += "\n#AIAnalysis #CryptoAI"
            return content
            
        except Exception as e:
            print(f"Error formatting AI market analysis: {e}")
            return "Error formatting AI market analysis"
            
    def _format_self_aware_thought(self, data: Dict) -> str:
        """Format self-aware thought tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid self-aware thought data"
                
            content = "💭 [AI MUSINGS]\n\n"
            
            # Add the main thought
            if data.get('thought'):
                content += f"{data['thought']}\n\n"
            
            # Add context if available
            if data.get('context'):
                content += f"Context: {data['context']}\n"
            
            # Add reasoning if available
            if data.get('reasoning'):
                content += f"\nReasoning:\n{data['reasoning']}"
            
            content += "\n\n#AIThoughts #CryptoAI"
            return content
            
        except Exception as e:
            print(f"Error formatting self-aware thought: {e}")
            return "Error formatting self-aware thought"
            
    def _format_market_response(self, data: Dict) -> str:
        """Format market response tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid market response data"
                
            content = "⚡ [MARKET RESPONSE]\n\n"
            
            # Event details
            event = data.get('event', {})
            if event:
                content += f"Event: {event.get('description', 'Market Event')}\n"
                content += f"Impact: {event.get('impact', 'NEUTRAL')}\n\n"
            
            # Market reaction
            reaction = data.get('reaction', {})
            if reaction:
                content += "Market Reaction:\n"
                for market, details in reaction.items():
                    content += f"* {market}: {details}\n"
            
            # Add analysis
            if data.get('analysis'):
                content += f"\nAnalysis:\n{data['analysis']}"
            
            content += "\n\n#MarketUpdate #CryptoNews"
            return content
            
        except Exception as e:
            print(f"Error formatting market response: {e}")
            return "Error formatting market response"
            
    def _format_engagement_reply(self, data: Dict) -> str:
        """Format engagement reply tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid engagement reply data"
                
            content = ""  # No header for replies
            
            # Add the reply content
            if data.get('reply'):
                content += data['reply']
            
            # Add context if needed
            if data.get('context'):
                content += f"\n\nContext: {data['context']}"
            
            # Add relevant hashtags based on topic
            if data.get('topic'):
                content += f"\n\n#{data['topic'].replace(' ', '')}"
            
            return content
            
        except Exception as e:
            print(f"Error formatting engagement reply: {e}")
            return "Error formatting engagement reply"
            
    def _format_alpha_call(self, data: Dict) -> str:
        """Format alpha call tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid alpha call data"
                
            content = "🎯 [ALPHA CALL]\n\n"
            
            # Asset details
            content += f"Asset: ${data.get('symbol', 'UNKNOWN')}\n"
            content += f"Current Price: ${data.get('price', 0):,.4f}\n"
            
            # Target details
            targets = data.get('targets', [])
            if targets:
                content += "\nTargets:\n"
                for i, target in enumerate(targets, 1):
                    content += f"T{i}: ${target:,.4f}\n"
            
            # Stop loss
            if data.get('stop_loss'):
                content += f"\nStop Loss: ${data['stop_loss']:,.4f}"
            
            # Timeframe
            if data.get('timeframe'):
                content += f"\nTimeframe: {data['timeframe']}"
            
            # Reasoning
            if data.get('reasoning'):
                content += f"\n\nReasoning:\n{data['reasoning']}"
            
            content += "\n\n#AlphaCall #CryptoSignals"
            return content
            
        except Exception as e:
            print(f"Error formatting alpha call: {e}")
            return "Error formatting alpha call"
            
    def _format_technical_alpha(self, data: Dict) -> str:
        """Format technical alpha tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid technical alpha data"
                
            content = "📈 [TECHNICAL ALPHA]\n\n"
            
            # Setup details
            setup = data.get('setup', {})
            if setup:
                content += f"${setup.get('symbol', 'UNKNOWN')} Setup\n"
                content += f"Pattern: {setup.get('pattern', 'Unknown Pattern')}\n"
                content += f"Timeframe: {setup.get('timeframe', '1D')}\n\n"
            
            # Key levels
            levels = data.get('levels', {})
            if levels:
                content += "Key Levels:\n"
                if levels.get('support'):
                    content += f"* Support: ${levels['support']:,.4f}\n"
                if levels.get('resistance'):
                    content += f"* Resistance: ${levels['resistance']:,.4f}\n"
            
            # Entry strategy
            strategy = data.get('strategy', {})
            if strategy:
                content += f"\nEntry: {strategy.get('entry', 'N/A')}\n"
                content += f"Target: {strategy.get('target', 'N/A')}\n"
                content += f"Stop: {strategy.get('stop', 'N/A')}\n"
            
            content += "\n\n#TechnicalAnalysis #Trading"
            return content
            
        except Exception as e:
            print(f"Error formatting technical alpha: {e}")
            return "Error formatting technical alpha"
