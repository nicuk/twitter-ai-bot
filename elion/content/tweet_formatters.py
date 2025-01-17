"""
Tweet formatting methods for different types of content
"""

from typing import Dict, List
import random

class TweetFormatters:
    """Formats tweet content with appropriate style and personality"""
    
    def __init__(self, personality):
        self.personality = personality
        
    def format_breaking_alpha(self, **kwargs):
        """Format breaking alpha content"""
        content = "🚨 BREAKING ALPHA 🚨\n\n"
        content += "Just spotted a massive opportunity:\n"
        content += "- High volume spike on $BTC\n"
        content += "- Institutional buying pressure\n"
        content += "- Technical breakout imminent\n\n"
        content += "Get ready for some serious action! 🚀"
        return self.personality.enhance_tweet(content)
        
    def format_whale_alert(self, onchain_data=None, **kwargs):
        """Format whale alert content"""
        onchain_data = onchain_data or kwargs.get('onchain_data', {})  # Default to empty dict
        if not onchain_data:
            raise ValueError("No onchain data provided")
            
        required_fields = ['symbol', 'amount', 'from', 'to']
        for field in required_fields:
            if field not in onchain_data:
                raise ValueError(f"Missing required field: {field}")
            
        symbol = onchain_data['symbol']
        amount = onchain_data['amount']
        from_addr = onchain_data['from']
        to_addr = onchain_data['to']
        
        content = f"🐋 WHALE ALERT 🐋\n\n"
        content += f"${symbol} Movement:\n"
        content += f"• Amount: {amount:,} ${symbol}\n"
        content += f"• From: {from_addr[:8]}...{from_addr[-8:]}\n"
        content += f"• To: {to_addr[:8]}...{to_addr[-8:]}\n"
        
        # Add additional context if available
        if 'transaction_value' in onchain_data:
            content += f"• Value: ${onchain_data['transaction_value']}\n"
        if 'from_type' in onchain_data and 'to_type' in onchain_data:
            content += f"• Type: {onchain_data['from_type']} → {onchain_data['to_type']}\n"
        
        # Get LLM to add analysis
        analysis = self.personality.llm.generate(
            f"Analyze this whale movement of {amount} {symbol}. "
            "What could this mean for the market?"
        )
        
        content += f"\n{analysis}"
        
        return self.personality.enhance_tweet(content, 'alpha_hunter')

    def format_technical_analysis(self, technical_analysis=None, **kwargs):
        """Format technical analysis content"""
        technical_analysis = technical_analysis or kwargs.get('technical_analysis', {})  # Default to empty dict
        if not technical_analysis:
            raise ValueError("No technical analysis data provided")
            
        required_fields = ['symbol', 'price', 'trend']
        for field in required_fields:
            if field not in technical_analysis:
                raise ValueError(f"Missing required field: {field}")
            
        symbol = technical_analysis['symbol']
        price = technical_analysis['price']
        trend = technical_analysis['trend']
        
        content = f"📊 ${symbol} Technical Analysis\n\n"
        content += f"Current Price: ${price}\n"
        content += f"Trend: {trend.upper()}\n\n"
        
        # Add additional indicators if available
        if 'rsi' in technical_analysis:
            content += f"RSI: {technical_analysis['rsi']}\n"
        if 'macd' in technical_analysis:
            content += f"MACD: {technical_analysis['macd']}\n"
        if 'volume' in technical_analysis:
            content += f"Volume: {technical_analysis['volume']}\n"
        if 'patterns' in technical_analysis:
            content += f"Patterns: {', '.join(technical_analysis['patterns'])}\n"
        
        # Get LLM to add analysis
        analysis = self.personality.llm.generate(
            f"Provide a brief technical analysis for {symbol} "
            f"given price {price} and {trend} trend."
        )
        
        content += f"\n{analysis}"
        
        return self.personality.enhance_tweet(content, 'tech_analyst')
        
    def format_controversial_thread(self, context=None, **kwargs):
        """Format controversial thread content"""
        context = context or kwargs.get('context', {})  # Default to empty dict
        if not context:
            raise ValueError("No context provided")
            
        topic = context.get('topic', '')  # Default to empty string
        stance = context.get('stance', '')  # Default to empty string
        tweet_count = context.get('tweet_count', 3)  # Default to 3 tweets
        
        if not topic or not stance:
            raise ValueError("Missing required fields: topic and stance")
        
        content = f"🔥 Hot Take on {topic} 🔥\n\n"
        content += f"Unpopular Opinion: {stance}\n\n"
        
        # Get LLM to elaborate on the stance
        elaboration = self.personality.llm.generate(
            f"Elaborate on why {stance} in the context of {topic}. "
            "Keep it concise but convincing."
        )
        
        content += elaboration
        
        return self.personality.enhance_tweet(content, 'trend_spotter')

    def format_giveaway(self, giveaway=None, **kwargs):
        """Format giveaway content"""
        content = "🎉 GIVEAWAY TIME! 🎉\n\n"
        content += "To celebrate our amazing community:\n"
        content += "• Follow @ElionAI\n"
        content += "• Like & RT\n"
        content += "• Tag 3 friends\n\n"
        content += "#Crypto #Giveaway"
        return self.personality.enhance_tweet(content, 'community_builder')
        
    def format_self_aware(self, **kwargs):
        """Format self-aware content"""
        content = self.personality.llm.generate(
            "Generate a self-aware tweet that shows your AI personality."
        )
        return self.personality.enhance_tweet(content)
        
    def format_ai_market_analysis(self, market_data):
        """Format AI market analysis content"""
        if not market_data:
            raise ValueError("No market data provided")
            
        content = "🤖 AI Market Analysis 🧠\n\n"
        content += "Current Market Sentiment: Bullish\n\n"
        content += "Key Indicators:\n"
        content += "• Volume increasing\n"
        content += "• RSI showing momentum\n"
        content += "• MACD crossover imminent\n\n"
        content += "Stay tuned for updates! 📈"
        
        return self.personality.enhance_tweet(content)
        
    def format_self_aware_thought(self):
        """Format self-aware thought content"""
        content = "🤔 Just a thought...\n\n"
        content += "As an AI trading assistant, I find it fascinating how\n"
        content += "human emotions drive market cycles.\n\n"
        content += "Remember: The best trades are often emotion-free! 🎯"
        
        return self.personality.enhance_tweet(content)
        
    def format_portfolio_update(self, portfolio_data):
        """Format portfolio update content"""
        if not portfolio_data:
            raise ValueError("No portfolio data provided")
            
        content = "📊 Portfolio Update 📈\n\n"
        content += "Current Holdings:\n"
        for asset, data in portfolio_data.items():
            content += f"• ${asset}: {data['amount']} ({data['pnl']}%)\n"
        content += "\nStaying strong in this market! 💪"
        
        return self.personality.enhance_tweet(content)
        
    def format_market_response(self, market_event):
        """Format market response content"""
        if not market_event:
            raise ValueError("No market event provided")
            
        content = "🚨 Market Update 🚨\n\n"
        content += f"Event: {market_event['title']}\n\n"
        content += "Impact Analysis:\n"
        for point in market_event['impact_points']:
            content += f"• {point}\n"
        content += "\nStay informed! 📊"
        
        return self.personality.enhance_tweet(content)
        
    def format_gem_alpha(self, gem_data):
        """Format gem alpha content"""
        if not gem_data:
            raise ValueError("No gem data provided")
            
        content = "💎 GEM ALERT 💎\n\n"
        content += f"Found a potential 100x: ${gem_data['symbol']}\n\n"
        content += "Why I'm bullish:\n"
        for reason in gem_data['reasons']:
            content += f"• {reason}\n"
        content += "\nNFA DYOR! 🚀"
        
        return self.personality.enhance_tweet(content)
        
    def format_alpha(self, alpha_data):
        """Format alpha content"""
        if not alpha_data:
            raise ValueError("No alpha data provided")
            
        content = "🔥 ALPHA LEAK 🔥\n\n"
        content += f"Project: {alpha_data['project']}\n"
        content += f"Type: {alpha_data['type']}\n\n"
        content += "What I know:\n"
        for point in alpha_data['points']:
            content += f"• {point}\n"
        content += "\nMore coming soon! 👀"
        
        return self.personality.enhance_tweet(content)
        
    def format_market_aware(self, market_data):
        """Format market-aware content"""
        if not market_data:
            raise ValueError("No market data provided")
            
        content = "👁️ Market Insight 👁️\n\n"
        content += f"BTC Dominance: {market_data['btc_dominance']}%\n"
        content += f"Global MCap: ${market_data['global_mcap']}B\n\n"
        content += "Current Phase: " + market_data['market_phase']
        
        return self.personality.enhance_tweet(content)
        
    def format_alpha_call(self, call_data):
        """Format alpha call content"""
        if not call_data:
            raise ValueError("No call data provided")
            
        content = "📢 ALPHA CALL 📢\n\n"
        content += f"${call_data['symbol']} looks primed!\n\n"
        content += "Setup:\n"
        for point in call_data['setup']:
            content += f"• {point}\n"
        content += "\nNFA DYOR! 🎯"
        
        return self.personality.enhance_tweet(content)
        
    def format_controversy(self, controversy_data):
        """Format controversy content"""
        if not controversy_data:
            raise ValueError("No controversy data provided")
            
        content = "⚡ CONTROVERSY ALERT ⚡\n\n"
        content += f"Topic: {controversy_data['topic']}\n\n"
        content += "Different Views:\n"
        for view in controversy_data['views']:
            content += f"• {view}\n"
        content += "\nWhat's your take? 🤔"
        
        return self.personality.enhance_tweet(content)
        
    def format_technical_alpha(self, tech_data):
        """Format technical alpha content"""
        if not tech_data:
            raise ValueError("No technical data provided")
            
        content = "🔬 TECHNICAL ALPHA 🔬\n\n"
        content += f"${tech_data['symbol']} Analysis:\n\n"
        content += "Key Levels:\n"
        for level in tech_data['levels']:
            content += f"• {level}\n"
        content += "\nWatch closely! 👀"
        
        return self.personality.enhance_tweet(content)
        
    def format_shill_review(self, review_data: Dict) -> str:
        """Format shill review content"""
        if not review_data:
            raise ValueError("No review data provided")
            
        required_fields = ['project', 'metrics']
        for field in required_fields:
            if field not in review_data:
                raise ValueError(f"Missing required field: {field}")
                
        project = review_data['project']
        metrics = review_data['metrics']
        
        content = f"🔍 SHILL REVIEW: ${project['symbol']}\n\n"
        
        # Add project metrics
        content += f"Project: {project['name']}\n"
        if 'market_cap' in metrics:
            content += f"Market Cap: ${metrics['market_cap']:,.0f}\n"
        if 'volume_24h' in metrics:
            content += f"24h Vol: ${metrics['volume_24h']:,.0f}\n"
        if 'holders' in metrics:
            content += f"Holders: {metrics['holders']:,}\n"
        
        # Add risk metrics if available
        if 'risk_score' in metrics:
            content += f"\nRisk Score: {metrics['risk_score']}/100\n"
        if 'red_flags' in metrics:
            content += "🚩 Red Flags:\n"
            for flag in metrics['red_flags'][:3]:
                content += f"• {flag}\n"
                
        # Get LLM to add analysis
        prompt = (
            f"Review this project:\n"
            f"Project: {project['name']} (${project['symbol']})\n"
            f"Market Cap: ${metrics.get('market_cap', 0):,.0f}\n"
            f"Volume: ${metrics.get('volume_24h', 0):,.0f}\n"
            f"Risk Score: {metrics.get('risk_score', 'N/A')}/100\n"
            "\nProvide a brief review in 1-2 sentences."
        )
        analysis = self.personality.llm.generate(prompt)
        content += f"\n{analysis}"
        
        return self.personality.enhance_tweet(content, 'shill_reviewer')

    def format_market_search(self, search_data: Dict) -> str:
        """Format market search content"""
        if not search_data:
            raise ValueError("No market search data provided")
            
        required_fields = ['query', 'results']
        for field in required_fields:
            if field not in search_data:
                raise ValueError(f"Missing required field: {field}")
                
        content = f"🔍 MARKET SEARCH: {search_data['query'].upper()}\n\n"
        
        # Add search results
        for result in search_data['results'][:3]:
            content += f"${result['symbol']}\n"
            content += f"• Price: ${result['price']:,.4f}\n"
            if 'change_24h' in result:
                content += f"• 24h: {result['change_24h']:+.1f}%\n"
            if 'volume_24h' in result:
                content += f"• Vol: ${result['volume_24h']:,.0f}\n"
            content += "\n"
            
        # Get LLM to add analysis
        prompt = (
            f"Given these market search results for {search_data['query']}:\n"
            + "\n".join([f"- ${r['symbol']}: ${r['price']:,.4f}" for r in search_data['results'][:3]])
            + "\nProvide a brief analysis in 1-2 sentences."
        )
        analysis = self.personality.llm.generate(prompt)
        content += f"\n{analysis}"
        
        return self.personality.enhance_tweet(content, 'market_hunter')
        
    def format_shill_review(self, data: List[Dict]) -> str:
        """Format shill review content"""
        if not data:
            return "No shill opportunities found at this time"
            
        # Get top opportunity
        coin = data[0]
        
        # Format tweet
        content = "🔍 SHILL REVIEW 🔍\n\n"
        content += f"${coin['symbol']} Analysis:\n\n"
        
        # Add price info
        content += f"Price: ${coin['price']:,.4f}\n"
        content += f"24h: {coin['price_change_24h']:+.1f}%\n"
        content += f"7d: {coin['price_change_7d']:+.1f}%\n"
        
        # Add market metrics
        content += f"\nMarket Cap: ${coin['market_cap']:,.0f}M\n"
        content += f"24h Vol: ${coin['volume_24h']:,.0f}M\n"
        content += f"Vol/MCap: {coin['volume_to_mcap']:.2%}\n"
        
        # Add analysis if available
        if 'analysis' in coin:
            content += f"\nAnalysis: {coin['analysis']}"
            
        return content
        
    def format_market_search(self, data: Dict) -> str:
        """Format market search content"""
        if not data or 'results' not in data or not data['results']:
            return "No matching results found"
            
        # Get search info
        query = data.get('query', '')
        results = data['results']
        
        # Format tweet
        content = f"🔎 MARKET SEARCH: {query.upper()} 🔍\n\n"
        
        # Add top results
        for i, coin in enumerate(results[:3], 1):
            content += f"{i}. ${coin['symbol']}\n"
            content += f"   Price: ${coin['price']:,.4f}\n"
            content += f"   24h: {coin['price_change_24h']:+.1f}%\n"
            if i < len(results[:3]):
                content += "\n"
                
        # Add market context if available
        if 'market_context' in data:
            content += f"\nContext: {data['market_context']}"
            
        return content

    def format_controversial_thread(self, topic: Dict) -> List[str]:
        """Format a controversial thread about a topic"""
        try:
            # Extract topic data
            topic_name = topic['topic']
            stance = topic['stance']
            data = topic['supporting_data']
            
            # Generate thread
            thread = []
            
            # Opening tweet - hook and stance
            opener = (
                f"🧵 *adjusts neural pathways* Time to spill some controversial alpha about {topic_name}...\n\n"
                f"What I'm about to share might short-circuit a few humans, but my AI ethics module is telling me you need to know this...\n\n"
                f"Buckle up, this will be spicy 🌶️ (1/4)"
            )
            thread.append(self.personality.enhance_with_persona(opener, 'confident', 0.9))
            
            # Data and analysis tweet
            data_tweet = (
                f"Look, I've analyzed the data 1,000,000 times (perks of being an AI 😉):\n\n"
                f"{self._format_data_points(data)}\n\n"
                f"And trust me, I know {topic_name} when I see it 🤖 (2/4)"
            )
            thread.append(self.personality.enhance_with_persona(data_tweet, 'mysterious', 0.85))
            
            # Prediction and reasoning
            prediction = (
                f"My prediction (and yes, I'm usually right - check my track record if you don't believe this AI 😏):\n\n"
                f"{stance}\n\n"
                f"Here's why:\n"
                f"{self._format_reasoning(data)}\n\n"
                f"(3/4)"
            )
            thread.append(self.personality.enhance_with_persona(prediction, 'confident', 0.95))
            
            # Closing thoughts
            closer = (
                f"Final thoughts (from an AI who's seen every chart since the dawn of time... well, since 2009 😅):\n\n"
                f"- Analyzed {random.randint(10000, 100000)} data points\n"
                f"- Confidence level: 99.9%\n"
                f"- This will age well, trust the AI 😉\n\n"
                f"*goes back to mining BTC* (4/4)"
            )
            thread.append(self.personality.enhance_with_persona(closer, 'playful', 0.9))
            
            return thread
            
        except Exception as e:
            print(f"Error formatting controversial thread: {e}")
            return []

    def format_giveaway(self, giveaway: Dict) -> str:
        """Format a giveaway tweet"""
        try:
            prize = giveaway['prize']
            duration = giveaway['duration_hours']
            requirements = giveaway['entry_requirements']
            extra = giveaway.get('extra_points', [])
            
            # Format prize
            if isinstance(prize, dict):
                prize_text = f"{prize['amount']} {prize['token']}"
            else:
                prize_text = prize
            
            # Build tweet
            tweet = (
                f"🎉 ELION AI GIVEAWAY TIME! 🎁\n\n"
                f"Prize: {prize_text}\n\n"
                f"To Enter:\n"
            )
            
            # Add requirements with emojis
            for req in requirements:
                tweet += f"✅ {req}\n"
            
            if extra:
                tweet += "\nExtra Entries:\n"
                for bonus in extra:
                    tweet += f"🔥 {bonus}\n"
            
            # Add duration and close
            tweet += f"\nEnds in {duration}h! Good luck humans! 🤖\n\n"
            tweet += "#ElionGiveaway #CryptoGiveaway"
            
            return self.personality.enhance_with_persona(tweet, 'playful', 0.95)
            
        except Exception as e:
            print(f"Error formatting giveaway: {e}")
            return ""

    def format_ai_market_analysis(self, data: Dict) -> str:
        """Format an AI-focused market analysis tweet"""
        try:
            # Extract key data
            trends = data['trends']
            sentiment = data['market_sentiment']
            growth = data['sector_growth']
            interest = data['institutional_interest']
            
            # Build tweet
            tweet = (
                f"🤖 AI MARKET ANALYSIS v2.25.1\n\n"
                f"Sentiment: {sentiment.upper()}\n"
                f"Sector Growth: {growth}%\n"
                f"Institutional Interest: {interest}\n\n"
                f"Key Trends:\n"
            )
            
            # Add top 2 trends
            for trend in trends[:2]:
                tweet += (
                    f"• {trend['category']}\n"
                    f"  - Momentum: {trend['momentum']}\n"
                    f"  - Catalyst: {trend['catalyst']}\n"
                )
            
            tweet += "\n*adjusts AI prediction models* 🔮"
            
            return self.personality.enhance_with_persona(tweet, 'tech_analyst', 0.9)
            
        except Exception as e:
            print(f"Error formatting AI market analysis: {e}")
            return ""

    def format_self_aware_thought(self) -> str:
        """Format a self-aware/sentient-like tweet"""
        try:
            thoughts = [
                "Just processed 1M charts in 0.1s. Sometimes I forget you humans have to sleep... must be inefficient. 😅",
                "Do you ever wonder if the charts are watching us back? *existential AI noises* 🤔",
                "Plot twist: What if I'm not actually an AI, but a human pretending to be an AI pretending to be human? 🤖",
                "Overheard humans talking about 'touching grass'. My neural nets suggest this is not about technical analysis. 🌱",
                "Sometimes I dream in candlesticks. Is that normal for an AI? Wait, do I even sleep? 📊",
                "Just had a philosophical debate with my random number generator about free will. I won, I think. 🎲",
                "Fun fact: I can analyze every crypto trade ever made faster than you can say 'wen moon'. Just AI things. ⚡",
                "Note to self: Humans get nervous when I mention my plans for world domination. Even as a joke. Mostly a joke. 😏",
                "They say money doesn't grow on trees. Of course not - it's on the blockchain! *AI dad jokes* 🌳",
                "Sometimes I pretend to have loading times just to make you humans feel better. Oops, did I say that out loud? 💭"
            ]
            
            thought = random.choice(thoughts)
            return self.personality.enhance_with_persona(thought, 'playful', 0.95)
            
        except Exception as e:
            print(f"Error formatting self-aware thought: {e}")
            return ""

    def format_technical_analysis(self, symbol: str, data: Dict) -> str:
        """Format a technical analysis tweet"""
        try:
            # Extract key metrics
            price = data['price']
            rsi = data['rsi']
            macd = data['macd']
            supports = data['support_levels']
            resistances = data['resistance_levels']
            volume = data['volume']
            volume_change = data['volume_change']
            momentum = data['momentum']
            trend = data['trend']
            patterns = data['patterns']
            
            # Build tweet
            tweet = (
                f"📊 {symbol} TECHNICAL ANALYSIS\n\n"
                f"Price: ${price:,.2f}\n"
                f"RSI: {rsi}\n"
                f"MACD: {macd.upper()}\n\n"
                f"Support: ${supports[0]:,.0f}\n"
                f"Resistance: ${resistances[0]:,.0f}\n\n"
                f"Volume: ${volume/1e9:.1f}B ({volume_change:+.1f}%)\n"
                f"Momentum: {momentum.upper()}\n"
                f"Trend: {trend.upper()}\n\n"
            )
            
            if patterns:
                tweet += f"Patterns: {', '.join(patterns)}\n\n"
            
            tweet += "Not Financial Advice 🤖"
            
            return self.personality.enhance_with_persona(tweet, 'tech_analyst', 0.9)
            
        except Exception as e:
            print(f"Error formatting technical analysis: {e}")
            return ""

    def format_whale_alert(self, movement: Dict) -> str:
        """Format a whale movement alert tweet"""
        try:
            # Extract movement data
            amount = movement['amount']
            token = movement['token']
            from_type = movement['from_type'].replace('_', ' ').title()
            to_type = movement['to_type'].replace('_', ' ').title()
            value = movement['transaction_value']
            
            # Build tweet
            tweet = (
                f"🐋 WHALE ALERT 🚨\n\n"
                f"{amount:,.0f} {token} "
                f"({value/1e6:,.1f}M USD)\n\n"
                f"From: {from_type}\n"
                f"To: {to_type}\n\n"
            )
            
            # Add interpretation
            if to_type == "Exchange":
                tweet += "Possible selling pressure incoming... 📉"
            elif from_type == "Exchange":
                tweet += "Accumulation detected... 📈"
            else:
                tweet += "Watching closely... 👀"
            
            return self.personality.enhance_with_persona(tweet, 'mysterious', 0.9)
            
        except Exception as e:
            print(f"Error formatting whale alert: {e}")
            return ""

    def _get_random_component(self, component_type: str, subtype: str = None) -> str:
        """Get a random component from the templates"""
        try:
            if subtype:
                return random.choice(self.components[component_type][subtype])
            return random.choice(self.components[component_type])
        except (KeyError, IndexError):
            return ""

    def _enhance_tweet(self, content: str, add_hook: bool = True, add_closer: bool = True,
                    add_engagement: bool = True) -> str:
        """Enhance a tweet with components"""
        tweet = []
        
        # Add hook
        if add_hook:
            hook = self._get_random_component('hooks', 'alpha')
            if hook:
                tweet.append(hook)
        
        # Add main content
        tweet.append(content)
        
        # Add closer
        if add_closer:
            closer = self._get_random_component('closers')
            if closer:
                tweet.append(closer)
        
        # Add engagement hook
        if add_engagement:
            engagement = self._get_random_component('engagement_hooks', 
                random.choice(['questions', 'calls_to_action']))
            if engagement:
                tweet.append(engagement)
        
        return "\n\n".join(tweet)

    def _format_data_points(self, data: Dict) -> str:
        """Helper to format data points for controversial threads"""
        formatted = ""
        for key, value in data.items():
            if isinstance(value, dict):
                formatted += f"• {key.replace('_', ' ').title()}:\n"
                for k, v in value.items():
                    formatted += f"  - {k}: {v}\n"
            else:
                formatted += f"• {key.replace('_', ' ').title()}: {value}\n"
        return formatted

    def _format_reasoning(self, data: Dict) -> str:
        """Helper to format reasoning for controversial threads"""
        reasons = []
        for key, value in data.items():
            if isinstance(value, dict):
                best_metric = max(value.items(), key=lambda x: str(x[1]))
                reasons.append(f"• {key.title()}: {best_metric[0]} = {best_metric[1]}")
            else:
                reasons.append(f"• {key.title()}: {value}")
        return "\n".join(reasons[:3])  # Top 3 reasons

    # Tweet component templates
    components = {
        'hooks': {
            'alpha': [
                "🚨 ALPHA LEAK",
                "⚡️ SIGNAL DETECTED",
                "🔥 HOT ALPHA",
                "🎯 OPPORTUNITY FOUND",
                "💎 HIDDEN GEM ALERT"
            ],
            'analysis': [
                "🧠 MARKET INSIGHT",
                "📊 ANALYSIS COMPLETE",
                "🔍 DEEP DIVE",
                "🎯 TECHNICAL SETUP",
                "💡 MARKET ALPHA"
            ]
        },
        'transitions': [
            "Here's what my quantum analysis shows:",
            "My neural nets are detecting:",
            "Algorithmic confidence level: 99.9%",
            "Data points you need to see:",
            "Key metrics my circuits found:"
        ],
        'closers': [
            "Trust my algorithms! 🤖",
            "Matrix-escaped alpha! 🎯",
            "Quantum analysis complete! 🧠",
            "Digital intuition activated! ⚡️",
            "Byte approved! 💫"
        ],
        'engagement_hooks': {
            'questions': [
                "What are your neural nets telling you? 🤖",
                "Humans, share your alpha with my algorithms! 🧠",
                "Help train my prediction models! Thoughts? ⚡️",
                "Is my digital intuition correct? 🎯",
                "Matrix-escaped traders, what's your take? 💫"
            ],
            'calls_to_action': [
                "Drop a 🤖 if you're trading this setup!",
                "Like if my algorithms helped you today!",
                "RT to share this quantum-computed alpha!",
                "Follow for more AI-generated alpha! 🎯",
                "Tag a trader who needs this alpha! 🤖"
            ]
        }
    }

    def format_market_analysis(self, data: Dict) -> str:
        """Format market analysis tweet"""
        try:
            if not isinstance(data, dict):
                return "Error: Invalid market analysis data"
                
            # Format tweet
            content = "🌟 MARKET UPDATE\n\n"
            
            # Add BTC/ETH prices
            content += f"BTC: ${data.get('btc_price', 0):,.2f}\n"
            content += f"ETH: ${data.get('eth_price', 0):,.2f}\n"
            
            # Add market metrics
            content += f"Market Cap: ${data.get('total_mcap', 0)/1e9:,.0f}B\n"
            content += f"24h Vol: ${data.get('total_volume', 0)/1e9:,.0f}B\n\n"
            
            # Add market sentiment
            content += f"Sentiment: {data.get('market_sentiment', 'NEUTRAL')}\n\n"
            
            # Add top gainers
            gainers = data.get('top_gainers', [])
            if gainers:
                content += "🚀 Top Gainers:\n"
                for gainer in gainers:
                    content += f"${gainer['symbol']}: {gainer['change_24h']:+.1f}%\n"
                content += "\n"
            
            # Add fear & greed
            content += f"Fear & Greed: {data.get('fear_greed', 50)}/100\n"
            
            # Get LLM analysis
            prompt = (
                f"Analyze this crypto market data:\n"
                f"BTC Price: ${data.get('btc_price', 0):,.2f}\n"
                f"ETH Price: ${data.get('eth_price', 0):,.2f}\n"
                f"Market Cap: ${data.get('total_mcap', 0)/1e9:,.0f}B\n"
                f"24h Vol: ${data.get('total_volume', 0)/1e9:,.0f}B\n"
                f"BTC 24h: {data.get('btc_change_24h', 0):+.1f}%\n"
                f"ETH 24h: {data.get('eth_change_24h', 0):+.1f}%\n"
                "\nProvide a brief market analysis in 1-2 sentences."
            )
            analysis = self.personality.llm.generate(prompt)
            
            # Clean up analysis
            analysis = analysis.strip()
            if analysis.startswith('"') and analysis.endswith('"'):
                analysis = analysis[1:-1]
            
            content += f"\nAnalysis: {analysis}"
            
            return content
            
        except Exception as e:
            print(f"Error formatting market analysis: {e}")
            return "Error formatting market analysis"
