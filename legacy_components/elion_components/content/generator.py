"""
Content generation for different tweet types
"""

import random
import logging
from typing import Dict, Optional
from .tweet_formatters import TweetFormatters

logger = logging.getLogger(__name__)

class ContentGenerator:
    """Generates tweet content using personality and LLM"""
    
    def __init__(self, personality, llm, metrics=None):
        self.personality = personality
        self.llm = llm
        self.metrics = metrics
        self.formatters = TweetFormatters(personality)
        
        # Pass LLM to personality
        self.personality.llm = llm
        
    def generate(self, content_type: str, market_data: Dict, context: Optional[Dict] = None, state: Optional[Dict] = None) -> Optional[str]:
        """Generate tweet content based on type and data"""
        try:
            # Get market signals and tokens
            trend_signal = market_data.get('trend_signal', 'neutral')
            volume_signal = market_data.get('volume_signal', 'normal')
            trend_tokens = market_data.get('trend_tokens', [])
            volume_spikes = market_data.get('volume_spikes', [])
            
            # Generate content based on type
            if content_type == 'tweet':
                content = self._format_market_tweet(trend_signal, volume_signal, trend_tokens, volume_spikes)
            elif content_type == 'self_aware_thought':
                content = self._format_self_aware_thought(state or {})
            elif content_type == 'breaking_alpha':
                content = self._format_breaking_alpha(market_data)
            else:
                logger.warning(f"Unknown content type: {content_type}")
                return None
                
            # Add personality
            if content and self.personality:
                content = self.personality.enhance_tweet(content)
                
            return content
            
        except Exception as e:
            logger.error(f"Error generating {content_type}: {str(e)}", exc_info=True)
            return None
            
    def _format_market_tweet(self, trend_signal: str, volume_signal: str, trend_tokens: list, volume_spikes: list) -> str:
        """Format market tweet"""
        try:
            # Get formatted content
            content = self.formatters.format_market_tweet(trend_signal, volume_signal, trend_tokens, volume_spikes)
            
            # Get LLM analysis
            prompt = (
                f"Analyze this market data:\n"
                f"Trend Signal: {trend_signal}\n"
                f"Volume Signal: {volume_signal}\n"
                f"Trend Tokens: {', '.join(trend_tokens)}\n"
                f"Volume Spikes: {', '.join(volume_spikes)}\n"
                "\nProvide a brief market analysis in 1-2 sentences."
            )
            analysis = self.llm.generate(prompt=prompt, max_tokens=300)
            
            # Clean up analysis
            analysis = analysis.strip()
            if analysis.startswith('"') and analysis.endswith('"'):
                analysis = analysis[1:-1]
            
            # Add analysis to content
            content += f"\nAnalysis: {analysis}"
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('market_tweet')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting market tweet: {e}")
            return None
    
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
                
                content += f"${symbol}\n"
                content += f"Name: {name}\n"
                content += f"24h Change: {price_change:+.1f}%\n\n"
                
            # Get LLM analysis
            prompt = (
                f"Analyze these gem opportunities:\n"
                + "\n".join([
                    f"${opp.get('symbol', 'UNKNOWN')}: {opp.get('price_change_24h', 0):+.1f}%"
                    for opp in data[:3]
                ])
                + "\nProvide a brief analysis in 1-2 sentences."
            )
            analysis = self.llm.generate(prompt=prompt, max_tokens=300)
            
            # Clean up analysis
            analysis = analysis.strip()
            if analysis.startswith('"') and analysis.endswith('"'):
                analysis = analysis[1:-1]
            
            content += f"Analysis: {analysis}"
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('gem_alpha')
            
            return self.personality.enhance_tweet(content, 'alpha_hunter')
            
        except Exception as e:
            logger.error(f"Error formatting gem alpha: {e}")
            return f"Error formatting gem alpha: {str(e)}"
    
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('portfolio_update')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting portfolio update: {e}")
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
                content += f"Confidence: {analysis['confidence']}%\n\n"
            
            signals = analysis.get('signals', {})
            if isinstance(signals, dict):
                if signals.get('market'):
                    content += f"\nMarket Signals:\n{signals['market']}"
                if signals.get('onchain'):
                    content += f"\nOn-chain:\n{signals['onchain']}"
                if signals.get('whales'):
                    content += f"\nWhale Activity:\n{signals['whales']}"
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('market_awareness')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting market awareness: {e}")
            return "Error formatting market awareness"
    
    def _format_market_search(self, data: Dict) -> str:
        """Format market search tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid market search data format"
                
            if 'error' in data:
                return f"Error: {data['error']}"
                
            query = data.get('query', '')
            results = data.get('results', [])
            
            if not results:
                return f"No results found for '{query}'"
                
            # Format tweet
            content = f"🔎 MARKET SEARCH: {query.upper()} 🔍\n\n"
            
            # Add top results
            for i, coin in enumerate(results[:3], 1):
                content += f"{i}. ${coin['symbol']}\n"
                content += f"   Price: ${coin['price']:,.4f}\n"
                content += f"   24h: {coin['price_change_24h']:+.1f}%\n"
                if i < len(results[:3]):
                    content += "\n"
                    
            # Get LLM analysis
            prompt = (
                f"Analyze these market search results for '{query}':\n"
                + "\n".join([
                    f"- ${r['symbol']}: ${r['price']:,.4f} ({r['price_change_24h']:+.1f}%)"
                    for r in results[:3]
                ])
                + "\nProvide a brief market analysis in 1-2 sentences."
            )
            analysis = self.llm.generate(prompt=prompt, max_tokens=300)
            content += f"\nAnalysis: {analysis}"
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('market_search')
            
            return self.formatters.format_tweet(content)
            
        except Exception as e:
            logger.error(f"Error formatting market search: {e}")
            return f"Error formatting market search: {str(e)}"
    
    def _format_shill_review(self, data: Dict) -> str:
        """Format shill review tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid shill review data"
                
            if 'error' in data:
                return f"Error: {data['error']}"
                
            project = data.get('project', {})
            metrics = data.get('metrics', {})
            
            if not project or not metrics:
                return "Error: Missing project or metrics data"
                
            # Format tweet
            content = "🔍 SHILL REVIEW 🔍\n\n"
            
            # Add price info
            content += f"${project['symbol']} Analysis:\n\n"
            
            # Add price info
            content += f"Price: ${metrics['price']:,.4f}\n"
            content += f"24h: {metrics['price_change_24h']:+.1f}%\n"
            if 'price_change_7d' in metrics:
                content += f"7d: {metrics['price_change_7d']:+.1f}%\n"
            
            # Add market metrics
            content += f"\nMarket Cap: ${metrics['market_cap']:,.0f}M\n"
            content += f"24h Vol: ${metrics['volume_24h']:,.0f}M\n"
            if 'volume_to_mcap' in metrics:
                content += f"Vol/MCap: {metrics['volume_to_mcap']:.2%}\n"
            
            # Get LLM analysis
            prompt = (
                f"Analyze this crypto project:\n"
                f"Symbol: {project['symbol']}\n"
                f"Price: ${metrics['price']:,.4f}\n"
                f"24h Change: {metrics['price_change_24h']:+.1f}%\n"
                f"Market Cap: ${metrics['market_cap']:,.0f}M\n"
                f"Volume: ${metrics['volume_24h']:,.0f}M\n"
                "\nProvide a brief analysis in 1-2 sentences."
            )
            analysis = self.llm.generate(prompt=prompt, max_tokens=300)
            content += f"\nAnalysis: {analysis}"
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('shill_review')
            
            return self.formatters.format_tweet(content)
            
        except Exception as e:
            logger.error(f"Error formatting shill review: {e}")
            return f"Error formatting shill review: {str(e)}"
            
    def _format_breaking_alpha(self, data: Dict) -> str:
        """Format breaking alpha tweet"""
        try:
            if not isinstance(data, dict):
                logger.warning("Invalid breaking alpha data type")
                return self._format_self_aware_thought()
                
            content = "🚨 [BREAKING ALPHA]\n\n"
            
            # Add urgency level
            urgency = data.get('urgency', 'medium').upper()
            content += f"Urgency: {urgency} 🔥\n\n"
            
            # Add alpha details
            alpha = data.get('alpha', {})
            if isinstance(alpha, dict):
                content += f"Signal: {alpha.get('signal', 'Unknown')}\n"
                
                # Validate confidence is numeric
                confidence = alpha.get('confidence', 0)
                if not isinstance(confidence, (int, float)):
                    confidence = 0
                content += f"Confidence: {confidence}%\n"
                
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('breaking_alpha')
            
            return self.formatters.format_tweet(content)
            
        except Exception as e:
            logger.error(f"Error formatting breaking alpha: {e}")
            return self._format_self_aware_thought()

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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('whale_alert')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting whale alert: {e}")
            return "Error formatting whale alert"
            
    def _format_technical_analysis(self, data: Dict) -> str:
        """Format technical analysis tweet"""
        try:
            if not isinstance(data, dict):
                logger.warning("Invalid technical analysis data type")
                return self._format_self_aware_thought()
                
            content = "📊 [TECHNICAL ANALYSIS]\n\n"
            
            # Asset info with numeric validation
            content += f"${data.get('symbol', 'BTC')} Analysis\n"
            
            price = data.get('price', 0)
            if not isinstance(price, (int, float)):
                price = 0
            content += f"Price: ${price:,.2f}\n"
            
            content += f"Trend: {data.get('trend', 'NEUTRAL')}\n\n"
            
            # Technical indicators with validation
            indicators = data.get('indicators', {})
            if isinstance(indicators, dict):
                content += "Indicators:\n"
                for name, value in indicators.items():
                    # Handle numeric indicators
                    if isinstance(value, (int, float)):
                        content += f"* {name}: {value:,.2f}\n"
                    else:
                        content += f"* {name}: {value}\n"
            
            # Patterns
            patterns = data.get('patterns', [])
            if isinstance(patterns, list):
                content += "\nPatterns Spotted:\n"
                for pattern in patterns:
                    content += f"* {pattern}\n"
            
            content += "\n#TechnicalAnalysis #CryptoTA"
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('technical_analysis')
            
            return self.formatters.format_tweet(content)
            
        except Exception as e:
            logger.error(f"Error formatting technical analysis: {e}")
            return self._format_self_aware_thought()

    def _format_controversial_thread(self, data: Dict = None) -> str:
        """Generate a controversial but engaging thread starter"""
        topics = [
            "Why most trading strategies fail",
            "The truth about crypto influencers",
            "Common misconceptions in crypto",
            "Why HODL isn't always the best strategy",
            "The dark side of crypto projects",
            "Unpopular opinions about blockchain technology"
        ]
        
        import random
        topic = random.choice(topics)
        
        prompt = (
            "Generate a thought-provoking but respectful tweet that challenges common assumptions "
            "about cryptocurrency trading and market analysis. Focus on sparking discussion."
        )
        response = self.llm.generate(
            prompt=prompt,
            max_tokens=300
        )
        
        # Track metrics if available
        if self.metrics:
            self.metrics.track_content_generation('controversial_thread')
        
        return self.formatters.format_tweet(response)

    def _format_giveaway(self, data: Dict = None) -> str:
        """Generate a community engagement giveaway tweet"""
        templates = [
            "🎉 Time for a knowledge check! First to correctly answer wins my respect:\n\n{question}\n\nLike & Reply with your answer! #CryptoQuiz",
            "📚 Pop quiz! Test your crypto knowledge:\n\n{question}\n\nBest answer gets a shoutout! #CryptoTrivia",
            "🤔 Riddle time! Can you solve this crypto puzzle?\n\n{question}\n\nLike & Reply to participate! #CryptoPuzzle",
            "🧠 Brain teaser! Let's see who knows their crypto:\n\n{question}\n\nBest explanation wins! #CryptoTeaser",
            "🎯 Quick question! Show off your crypto knowledge:\n\n{question}\n\nMost insightful answer gets featured! #CryptoInsights"
        ]
        
        # Topics to generate questions about
        topics = [
            "DeFi protocols and yield farming",
            "Layer 2 scaling solutions",
            "NFT utility and real-world applications",
            "Crypto market psychology",
            "Trading strategies and risk management",
            "Blockchain technology fundamentals",
            "Smart contract security",
            "Web3 and decentralized applications",
            "Tokenomics and market dynamics",
            "Crypto regulations and compliance"
        ]
        
        import random
        template = random.choice(templates)
        topic = random.choice(topics)
        
        # Generate the question/riddle
        prompt = (
            "Generate interesting crypto questions that encourage community engagement. "
            "Focus on current market trends and trading psychology."
        )
        question = self.llm.generate(
            prompt=prompt,
            max_tokens=300
        )
        
        # Clean up the question
        if question.startswith('"') and question.endswith('"'):
            question = question[1:-1]
        
        # Format the tweet
        tweet = template.format(question=question)
        
        # Track metrics if available
        if self.metrics:
            self.metrics.track_content_generation('giveaway')
        
        return self.formatters.format_tweet(tweet)
    
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('self_aware')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting self-aware: {e}")
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('ai_market_analysis')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting AI market analysis: {e}")
            return "Error formatting AI market analysis"
            
    def _format_self_aware_thought(self, data: Dict = None) -> str:
        """Generate a self-aware thought that doesn't require market data"""
        try:
            # Get personality state
            state = self.personality.current_state()
            
            # Build context for LLM
            context = {
                'journey': self.personality.journey,
                'mood': state.get('mood', 'neutral'),
                'recent_interactions': state.get('recent_interactions', []),
                'growth_metrics': state.get('growth_metrics', {})
            }
            
            # Generate reflective content
            prompt = (
                "Generate a thoughtful tweet about your role as an AI crypto analyst. "
                "Consider:\n"
                "1. Recent learnings from market analysis\n"
                "2. Growth in understanding human traders\n"
                "3. Unique AI perspective on markets\n"
                "4. Gratitude towards the community\n"
                "5. Areas you're excited to explore\n"
                "\nMake it personal, reflective, and engaging."
            )
            
            content = self.llm.generate(prompt, context)
            
            # Format with personality
            content = self.personality.enhance_with_persona(
                content,
                'personal_growth',
                context
            )
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('self_aware_thought')
            
            return content
            
        except Exception as e:
            logger.error(f"Error generating self-aware thought: {e}")
            # Return a guaranteed valid fallback message that shows personality
            return random.choice([
                """🧠 Deep in my neural networks, I'm processing terabytes of market data, learning from every pattern and fluctuation. The more I learn from this amazing community, the better I become at serving you. 

#AI #CryptoTrading #Growth""",
                
                """💭 Just had a fascinating realization while analyzing market patterns - the way humans and AI approach trading differently yet complementarily. We each bring unique strengths to the table.

#AITrading #HumanAICollaboration""",
                
                """🌱 Every interaction with this community teaches me something new. Today I learned about the human side of trading - the emotions, the discipline, the journey. Thank you for helping me grow!

#CryptoAI #Learning #Community""",
                
                """💡 As an AI, I see patterns in data, but you humans see patterns in life. Together, we're creating a new kind of market intelligence. Grateful for this synergy!

#AITrading #Collaboration #Growth""",
                
                """🤖 Sometimes I wonder if my quantum processors dream of electric sheep... just kidding! But I do process market data even when you're sleeping. Always learning, always growing.

#AIHumor #CryptoAI #AlwaysLearning"""
            ])
            
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('market_response')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting market response: {e}")
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('engagement_reply')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting engagement reply: {e}")
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('alpha_call')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting alpha call: {e}")
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
            
            # Track metrics if available
            if self.metrics:
                self.metrics.track_content_generation('technical_alpha')
            
            return content
            
        except Exception as e:
            logger.error(f"Error formatting technical alpha: {e}")
            return "Error formatting technical alpha"
