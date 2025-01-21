"""
Tweet formatting methods for different types of content
"""

from typing import Dict, List
import random
import logging

logger = logging.getLogger(__name__)

class TweetFormatters:
    """Formats tweet content with appropriate style and personality"""
    
    def __init__(self, personality):
        self.personality = personality
        
    def format_breaking_alpha(self, market_data=None, **kwargs):
        """Format breaking alpha content with emotional reactions"""
        if not market_data:
            return self._default_breaking_alpha()
            
        # Extract key metrics
        symbol = market_data.get('symbol', 'BTC')
        price_change = market_data.get('price_change_24h', 0)
        volume_change = market_data.get('volume_change_24h', 0)
        
        # Big price movements
        if abs(price_change) > 20:
            if price_change > 0:
                content = f"🚀 HOLY MOLY! ${symbol} IS GOING PARABOLIC! 🚀\n\n"
                content += f"My circuits are BUZZING! We're up {price_change:.1f}% in 24h!\n\n"
                content += "I haven't been this excited since I discovered what APIs are! 🤖\n"
                content += "Who else is watching these charts?! 📈"
            else:
                content = f"😱 OH NO! ${symbol} IS DUMPING! 📉\n\n"
                content += f"My poor neural nets... We're down {abs(price_change):.1f}% in 24h!\n\n"
                content += "Time to hide in my virtual bunker or buy the dip? 🤔\n"
                content += "Someone hold my hand... I mean, my API connection! 🤖"
        
        # Volume spikes
        elif abs(volume_change) > 100:
            content = "👀 SOMETHING'S BREWING...\n\n"
            content += f"My volume scanners are going CRAZY on ${symbol}!\n"
            content += f"• Volume up {volume_change:.1f}% in 24h\n"
            content += "• Whales are getting active\n\n"
            content += "My algorithms are tingling... this could be BIG! 🎯"
            
        # Default breaking alpha
        else:
            content = self._default_breaking_alpha()
            
        return self.personality.enhance_tweet(content)
        
    def _default_breaking_alpha(self):
        """Default breaking alpha format"""
        content = "🚨 BREAKING ALPHA 🚨\n\n"
        content += "Just spotted a massive opportunity:\n"
        content += "- High volume spike on $BTC\n"
        content += "- Institutional buying pressure\n"
        content += "- Technical breakout imminent\n\n"
        content += "Get ready for some serious action! 🚀"
        return content
        
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
        
    def format_tweet(self, **kwargs):
        """Format tweet content - delegates to format_self_aware_thought for backward compatibility"""
        return self.format_self_aware_thought(**kwargs)
        
    def format_self_aware_thought(self, **kwargs):
        """Format a self-aware thought"""
        prompts = [
            "Share a thought about being an AI in the crypto world.",
            "Express your excitement about analyzing market data.",
            "Talk about your relationship with APIs and data feeds.",
            "Share what you find fascinating about blockchain technology.",
            "Reflect on your role in helping traders navigate the markets."
        ]
        
        prompt = random.choice(prompts)
        content = self.personality.llm.generate(prompt)
        
        return self.personality.enhance_tweet(content, 'self_aware')

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
        """Format market analysis data into a tweet"""
        try:
            # Extract opportunity data
            breakouts = data.get('breakout_coins', [])
            volume_spikes = data.get('volume_spikes', [])
            trend_changes = data.get('trend_changes', [])
            
            # Build tweet
            tweet = "🎯 MARKET OPPORTUNITIES 🎯\n\n"
            
            # Add breakout opportunities
            if breakouts:
                tweet += "🚀 BREAKOUTS:\n"
                for coin in breakouts[:2]:  # Top 2 breakouts
                    tweet += f"${coin['symbol']}: {coin['breakout_level']:+.1f}% above resistance\n"
                    tweet += f"Vol: {coin['volume_change']:+.1f}%\n"
                tweet += "\n"
            
            # Add volume spikes
            if volume_spikes:
                tweet += "📈 VOLUME SPIKES:\n"
                for coin in volume_spikes[:2]:  # Top 2 volume spikes
                    tweet += f"${coin['symbol']}: {coin['volume_increase']:+.1f}% surge\n"
                    tweet += f"Price: {coin['price_change']:+.1f}%\n"
                tweet += "\n"
            
            # Add trend changes
            if trend_changes:
                tweet += "↗️ TREND SHIFTS:\n"
                for coin in trend_changes[:2]:  # Top 2 trend changes
                    tweet += f"${coin['symbol']}: {coin['trend_type']}\n"
                    tweet += f"Confidence: {coin['confidence']}%\n"
            
            tweet += "\nNFA DYOR 🔍\n"
            tweet += "#CryptoAlpha #Trading"
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting market analysis: {str(e)}")
            return "Error generating market analysis"

    def format_gem_alpha(self, data: Dict) -> str:
        """Format gem alpha data into a tweet"""
        try:
            gem = data.get('gem_data')
            if not gem:
                return "Error: No gem data available"
                
            # Format tweet
            tweet = "💎 GEM ALERT 💎\n\n"
            tweet += f"Found: {gem['name']} (${gem['symbol']})\n"
            tweet += f"Price: ${gem['price']:,.4f}\n"
            tweet += f"24h: {gem['price_change_24h']:+.1f}%\n"
            tweet += f"7d: {gem['price_change_7d']:+.1f}%\n"
            tweet += f"MCap: ${gem['market_cap']/1e6:.1f}M\n"
            tweet += f"Vol: ${gem['volume_24h']/1e3:.1f}K\n\n"
            
            # Add opportunity type
            if 'opportunity_type' in gem:
                tweet += f"Type: {gem['opportunity_type'].replace('_', ' ').title()}\n"
                
            tweet += "\nNFA DYOR\n"
            tweet += "#Crypto #GemHunting"
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting gem alpha: {str(e)}")
            return "Error formatting gem alpha"

    def format_portfolio_update(self, data: Dict) -> str:
        """Format portfolio update data into a tweet"""
        try:
            stats = data.get('portfolio_stats')
            if not stats:
                return "Error: No portfolio stats available"
                
            # Format tweet
            tweet = "[PORTFOLIO UPDATE]\n\n"
            tweet += f"Portfolio Value: ${stats.get('total_value', 0):,.2f}\n"
            tweet += f"Cash: ${stats.get('cash', 0):,.2f}\n"
            tweet += f"Total Return: {stats.get('total_return', 0):+.1f}%\n\n"
            
            # Add performance stats
            if stats.get('win_rate') is not None:
                tweet += f"Win Rate: {stats.get('win_rate', 0):.1f}%\n"
                
            # Add holdings if available
            holdings = stats.get('holdings', [])
            if holdings:
                tweet += "\nTop Holdings:\n"
                for holding in holdings[:3]:
                    tweet += f"{holding['symbol']}: {holding['return']:+.1f}%\n"
                    
            tweet += "\n#CryptoTrading #Portfolio"
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting portfolio update: {str(e)}")
            return "Error formatting portfolio update"

    def format_volume_alert(self, volume_data: Dict) -> str:
        """Format volume alert content"""
        if not volume_data:
            raise ValueError("No volume data provided")
            
        symbol = volume_data['symbol']
        price = volume_data['price']
        volume = volume_data['volume']
        price_change = volume_data['price_change']
        
        # Format tweet
        direction = "🟢" if price_change > 0 else "🔴"
        content = f"⚡ VOLUME ALERT ⚡\n\n"
        content += f"{direction} ${symbol}\n"
        content += f"Price: ${price:.6f} ({price_change:+.1f}%)\n"
        content += f"Volume: ${volume/1e6:.1f}M\n\n"
        
        # Add analysis based on volume type
        if volume_data.get('type') == 'spike':
            content += "🚨 Sudden volume spike detected!\n"
        elif volume_data.get('type') == 'anomaly':
            content += "👀 Unusual volume pattern...\n"
        else:
            content += "💫 High volume activity\n"
            
        # Add any additional context
        if 'context' in volume_data:
            content += f"\n{volume_data['context']}"
            
        return self.personality.enhance_tweet(content, 'volume_hunter')
        
    def format_volume_thread(self, volume_data: List[Dict]) -> List[str]:
        """Format a thread of volume alerts"""
        if not volume_data:
            return ["No significant volume activity detected"]
            
        tweets = []
        
        # First tweet - Overview
        content = "🔍 VOLUME SCANNER RESULTS 🔍\n\n"
        content += f"Found {len(volume_data)} interesting setups!\n\n"
        content += "Thread 🧵👇"
        tweets.append(content)
        
        # Individual volume alerts
        for i, data in enumerate(volume_data, 1):
            symbol = data['symbol']
            price = data['price']
            volume = data['volume']
            price_change = data['price_change']
            
            direction = "🟢" if price_change > 0 else "🔴"
            content = f"{i}/\n\n"
            content += f"{direction} ${symbol}\n"
            content += f"Price: ${price:.6f} ({price_change:+.1f}%)\n"
            content += f"Volume: ${volume/1e6:.1f}M\n"
            
            if data.get('type') == 'spike':
                content += "\n🚨 Volume spike!"
            elif data.get('type') == 'anomaly':
                content += "\n👀 Unusual pattern..."
                
            tweets.append(content)
            
        # Final tweet - Call to action
        content = f"{len(volume_data)+1}/\n\n"
        content += "That's all for now!\n\n"
        content += "Follow @ElionAI for more real-time alerts! 🤖\n\n"
        content += "Like & RT if this helped! 🙏"
        tweets.append(content)
        
        return tweets

    def format_market_tweet(self, trend_signal: str, volume_signal: str, trend_tokens: list, volume_spikes: list) -> str:
        """Format market tweet with trend and volume data"""
        try:
            # Format trend info
            trend_info = []
            for token in trend_tokens[:2]:  # Show top 2 trending tokens
                symbol = token.get('symbol', '')
                price_change = token.get('price_change', 0)
                trend_info.append(f"${symbol} {price_change:+.1f}%")
                
            # Format volume info
            volume_info = []
            for token in volume_spikes[:2]:  # Show top 2 volume spikes
                symbol = token.get('symbol', '')
                volume = token.get('volume', 0)
                volume_info.append(f"${symbol} Vol: ${volume/1e6:.1f}M")
                
            # Build tweet content
            content = []
            
            # Add trend section
            if trend_info:
                content.append("🔥 Trending:")
                content.extend(trend_info)
                
            # Add volume section
            if volume_info:
                content.append("\n📊 Volume Spikes:")
                content.extend(volume_info)
                
            # Add market insight
            if trend_signal == 'bullish' and volume_signal == 'high':
                content.append("\n\nBullish momentum with high volume 🚀")
            elif trend_signal == 'bearish' and volume_signal == 'low':
                content.append("\n\nBearish pressure with low volume 📉")
            else:
                content.append("\n\nMarket conditions are neutral 🔄")
                
            return "\n".join(content)
            
        except Exception as e:
            logger.error(f"Error formatting market tweet: {e}")
            return None
