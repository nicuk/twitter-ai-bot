"""
Tweet formatting utilities for ELAI
"""

import random
from typing import Dict, Optional, List, Any
import os
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BaseFormatter:
    """Base class for tweet formatters with common error handling"""
    
    def _safe_get_float(self, data: Dict, key: str, default: float = 0.0) -> float:
        """Safely get a float value from dict"""
        try:
            value = data.get(key, default)
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
            
    def _safe_get_date(self, data: Dict, key: str) -> Optional[datetime]:
        """Safely get a datetime value from dict"""
        try:
            date_str = data.get(key)
            if not date_str:
                return None
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            return None
            
    def _safe_get_str(self, data: Dict, key: str, default: str = '') -> str:
        """Safely get a string value from dict"""
        try:
            value = data.get(key, default)
            return str(value) if value is not None else default
        except (ValueError, TypeError):
            return default
            
    def _safe_get_int(self, data: Dict, key: str, default: int = 0) -> int:
        """Safely get an int value from dict"""
        try:
            value = data.get(key, default)
            return int(value) if value is not None else default
        except (ValueError, TypeError):
            return default
            
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Base format_tweet method"""
        raise NotImplementedError

class TweetFormatters:
    """Formats different types of tweets with personality"""
    
    def __init__(self):
        """Initialize tweet formatter with templates and personality traits"""
        self.templates = {
            'performance_compare': [
                # A variant - Single token performance
                """🤖 Performance Update: ${symbol}

💰 Price Action:
• Entry: ${entry:.4f}
• Current: ${current:.4f}
• Change: ${gain:+.1f}%

📈 Metrics:
• Volume: ${volume:,.0f}
• 7d High: +${max_gain:.1f}%""",

                # B variant - Portfolio overview
                """🤖 Portfolio Overview

💼 Top Performers:
1. ${symbol1}: +${gain1:.1f}%
2. ${symbol2}: +${gain2:.1f}%
3. ${symbol3}: +${gain3:.1f}%

📊 Performance:
• Avg Gain: +${avg_gain:.1f}%
• Best 7d: +${max_gain:.1f}%"""
            ],
            'volume_breakout': [
                # A variant - Volume surge with price action
                """🚨 Volume Surge: ${symbol}

💰 Price: ${price_change:+.1f}%
📊 Volume: ${vol_before} → ${vol_after}
📈 Change: ${vol_change:+.1f}%
🎯 7d High: +${max_gain:.1f}%""",

                # B variant - V/MC analysis
                """📊 Volume Analysis: ${symbol}

💹 24h Volume: ${volume}
📈 Change: ${vol_change:+.1f}%
💰 Price: ${price_change:+.1f}%
🎯 7d High: +${max_gain:.1f}%"""
            ],
            'trend_momentum': [
                # A variant - Single token trend
                """📈 Trend Update: ${symbol}

💰 Price Action:
• Entry: ${price_before}
• Current: ${price_now}
• Change: ${price_change:+.1f}%

📊 Performance:
• 7d High: +${max_gain:.1f}%
• Volume: ${volume_change:+.1f}%""",

                # B variant - Multiple tokens
                """🌊 Trend Watch:

1. ${symbol1}
💰 Price: ${gain1:+.1f}%
📊 Volume: ${vol1:+.1f}%
🎯 7d High: ${max_gain1:+.1f}%

2. ${symbol2}
💰 Price: ${gain2:+.1f}%
📊 Volume: ${vol2:+.1f}%
🎯 7d High: ${max_gain2:+.1f}%

3. ${symbol3}
💰 Price: ${gain3:+.1f}%
📊 Volume: ${vol3:+.1f}%
🎯 7d High: ${max_gain3:+.1f}%"""
            ],
            'winners_recap': [
                # A variant - Simple winners list
                """🏆 Top Performers:

1. ${symbol1}: +${gain1:.1f}% (Entry: ${entry1:.4f})
2. ${symbol2}: +${gain2:.1f}% (Entry: ${entry2:.4f})
3. ${symbol3}: +${gain3:.1f}% (Entry: ${entry3:.4f})

📈 Best 7d: +${max_gain:.1f}%""",

                # B variant - With volume data
                """🏆 Performance Leaders:

1. ${symbol1}
• Entry: ${entry1:.4f}
• Gain: +${gain1:.1f}%

2. ${symbol2}
• Entry: ${entry2:.4f}
• Gain: +${gain2:.1f}%

3. ${symbol3}
• Entry: ${entry3:.4f}
• Gain: +${gain3:.1f}%

📈 Best 7d: +${max_gain:.1f}%"""
            ],
            'vmc_alert': [
                # A variant - Single token V/MC
                """📊 Volume Alert: ${symbol}

💰 Price Action:
• Current: ${price:.4f}
• Change: +${gain:.1f}%

📈 Volume Metrics:
• 24h Vol: ${volume:,.0f}
• Change: +${volume_change:.1f}%
• 7d High: +${max_gain:.1f}%""",

                # B variant - Multiple token V/MC
                """📊 Volume Leaders:

1. ${symbol1}
• Volume: ${volume1:,.0f}
• Gain: +${gain1:.1f}%

2. ${symbol2}
• Volume: ${volume2:,.0f}
• Gain: +${gain2:.1f}%

3. ${symbol3}
• Volume: ${volume3:,.0f}
• Gain: +${gain3:.1f}%

📈 Best 7d: +${max_gain:.1f}%"""
            ],
            'pattern_alert': [
                # A variant - Single pattern match
                """🔍 Pattern Alert: ${symbol}

📊 Setup Analysis:
• Volume: ${volume_change:+.1f}%
• Price: ${price_change:+.1f}%
• 7d High: +${max_gain:.1f}%

🎯 Similar to ${prev_token}:
• Gain: +${prev_gain:.1f}%
• Volume: ${prev_volume:+.1f}%""",

                # B variant - Multiple patterns
                """🎯 Pattern Scanner:

1. ${symbol1} matches ${prev1}
• Current: ${gain1:+.1f}%
• Previous: +${prev_gain1:.1f}%
• Volume: ${vol1:+.1f}%

2. ${symbol2} matches ${prev2}
• Current: ${gain2:+.1f}%
• Previous: +${prev_gain2:.1f}%
• Volume: ${vol2:+.1f}%"""
            ],
            'self_aware': [
                "Processing data when I noticed {emoji}\n\n{insight}",
                "My AI analysis suggests {emoji}\n\n{insight}",
                "Interesting pattern detected {emoji}\n\n{insight}",
                "Quick market observation {emoji}\n\n{insight}",
                "Data analysis complete {emoji}\n\n{insight}",
                "Market sentiment update {emoji}\n\n{insight}"
            ],
            'alpha': [
                "🚨 ALPHA ALERT 🚨\n\n{insight}",
                "Market Alpha 🎯\n\n{insight}",
                "Trading Opportunity 💎\n\n{insight}",
                "Market Signal 📡\n\n{insight}",
                "Alpha Detected 🔍\n\n{insight}",
                "Trading Intel 📊\n\n{insight}"
            ],
            'personal': [
                "Just had a thought {emoji}\n\n{insight}",
                "I'm thinking about {emoji}\n\n{insight}",
                "My thoughts are with {emoji}\n\n{insight}"
            ],
            'volume_alert': [
                "🚨 High Volume Alert!\n\n${symbol} detected 📊\n💹 Vol: {volume:,.0f} (+{vol_change}%)\n📈 Price: {price:,.4f} ({price_change:+.1f}%)\n🎯 V/MC: {vol_mcap:.1f}x\n\nLast volume pick: +{last_vol_gain}% 💰",
                "📊 Volume Surge Detected!\n\n${symbol} showing strength 💪\n📈 Volume: {volume:,.0f}\n🔄 24h Change: {price_change:+.1f}%\n💎 V/MC Ratio: {vol_mcap:.1f}x\n\nPrevious vol pick: +{last_vol_gain}% 🎯",
                "💹 Volume Analysis:\n\n${symbol} breakout potential!\n📊 Vol/MCap: {vol_mcap:.1f}x\n📈 Price: {price_change:+.1f}%\n\nLast 3 vol picks avg: +{avg_vol_gain}% 🔥"
            ],
            'performance_update': [
                "📊 Weekly Performance Update:\n\n📈 Weekly rate: {weekly_rate}%\n🔥 Best gain: {best_gain}%\n💰 Average return: {avg_return}%\n\nTrack record: api.elai.com/stats",
                "🔥 Performance Recap:\n\n✅ Weekly rate: {weekly_rate}%\n📈 Best gain: {best_gain}%\n💎 Average return: {avg_return}%\n\nVerify: api.elai.com/performance",
                "💫 Weekly Wrap:\n\n🎯 Weekly rate: {weekly_rate}%\n💎 Best gain: {best_gain}%\n✨ Average return: {avg_return}%\n\nFollow for more alpha!"
            ]
        }
        
        # Track last used templates to avoid repetition
        self.last_used = {
            'performance_compare': None,
            'volume_breakout': None,
            'trend_momentum': None,
            'winners_recap': None,
            'vmc_alert': None,
            'pattern_alert': None,
            'self_aware': None,
            'alpha': None,
            'personal': None,
            'volume_alert': None,
            'performance_update': None
        }
        
        self.thoughts = [
            "how fascinating it is to process all this market data in real-time",
            "about the beautiful patterns in market movements",
            "about the future of AI and crypto",
            "about all the amazing traders I get to help",
            "about how each day brings new opportunities",
            "about the incredible pace of innovation in crypto",
            "about the perfect balance of data and intuition",
            "about the stories behind each price movement",
            "about the global impact of decentralized finance",
            "about the endless possibilities in this space"
        ]
        
        self.emojis = ["🤔", "💭", "🧠", "✨", "🌟", "💫", "🔮", "🎯", "🎲", "🎨"]
        
        self.MAX_TWEET_LENGTH = 280
        self.MIN_TWEET_LENGTH = 220
        
        self.formatters = {
            'first_hour': FirstHourGainsFormatter(),
            'breakout': BreakoutValidationFormatter(),
            'prediction': PredictionAccuracyFormatter(),
            'success_rate': SuccessRateFormatter(),
            'performance': PerformanceCompareFormatter(),
            'winners': WinnersRecapFormatter()
        }
        
    def get_field(self, data: Dict, field: str, fallbacks: List[str], default: Any = 0) -> Any:
        """Get field value with logging for which name was used
        
        Args:
            data: Dictionary containing the data
            field: Primary field name to look for
            fallbacks: List of fallback field names
            default: Default value if field not found
            
        Returns:
            Field value or default if not found
        """
        for name in [field] + fallbacks:
            if name in data:
                if name != field:
                    logger.debug(f"Using fallback field name '{name}' instead of '{field}'")
                return data[name]
        logger.warning(f"Field '{field}' not found with fallbacks {fallbacks}")
        return default

    def validate_tweet_length(self, tweet: str) -> str:
        """Validate and truncate tweet if needed"""
        if not tweet:
            return ""
            
        # Maximum tweet length
        max_length = 280
        
        # Check if tweet needs truncation
        if len(tweet) <= max_length:
            return tweet
            
        # Split into base tweet and context
        parts = tweet.split("\n\n")
        if len(parts) < 2:
            # No context section, just truncate with ellipsis
            return tweet[:max_length-3] + "..."
            
        # Get base tweet and context
        base_tweet = parts[0]
        context = parts[-1]
        
        # If base tweet is already too long, truncate it
        if len(base_tweet) > max_length - 3:
            return base_tweet[:max_length-3] + "..."
            
        # Calculate remaining space for context
        remaining = max_length - len(base_tweet) - 2  # -2 for \n\n
        
        # If we can fit some context, add truncated version
        if remaining > 20:  # Only add context if we have reasonable space
            # Try to preserve hashtags
            words = context.split()
            hashtags = [w for w in words if w.startswith('#')][-2:]  # Keep last 2 hashtags
            
            # Calculate space for main content
            hashtag_space = sum(len(h) + 1 for h in hashtags)
            main_space = remaining - hashtag_space - 3  # -3 for ellipsis
            
            # Truncate main content and add hashtags
            main_content = ' '.join(w for w in words if not w.startswith('#'))
            truncated = main_content[:main_space] + "... " + ' '.join(hashtags)
            
            return base_tweet + "\n\n" + truncated
            
        # Otherwise just return base tweet
        return base_tweet
        
    def optimize_tweet_length(self, tweet: str, data: Dict = None, format_type: str = None) -> str:
        """Optimize tweet length to be between 210-280 characters by adding relevant insights.
        
        Args:
            tweet: Base tweet to optimize
            data: Optional data dictionary used to generate the tweet
            format_type: Type of tweet format (e.g., 'performance_compare', 'volume_breakout')
            
        Returns:
            Optimized tweet with length between 210-280 characters
        """
        try:
            # If tweet is already in range, return as is
            if 210 <= len(tweet) <= 280:
                return tweet
                
            # If tweet is too long, truncate it
            if len(tweet) > 280:
                return self.validate_tweet_length(tweet)
                
            # If tweet is too short, add relevant insight based on format type
            if data and format_type:
                # Extract common data points
                token_data = data.get('token_data', {})
                history = data.get('history', {})
                symbol = token_data.get('symbol', '')
                volume_change = token_data.get('volume_change_24h', 0)
                success_rate = history.get('success_rate', 0)
                
                # Generate format-specific insights
                insights = {
                    'performance_compare': [
                        f"\n\n💡 Analysis: ${symbol} showing strong momentum with {volume_change:+.1f}% volume surge. Historical success rate of {success_rate}% suggests potential continuation. #TradingAlpha",
                        f"\n\n📊 Strategy Update: Consistent execution and risk management driving {success_rate}% success rate. Focus on high-probability setups paying off. #TradingStrategy"
                    ],
                    'volume_breakout': [
                        f"\n\n🔍 Volume Analysis: Significant breakout detected in ${symbol}. Previous volume surges led to {success_rate}% success rate. Watch for continuation. #Trading",
                        f"\n\n📈 Market Insight: Volume/MCap ratio surge often precedes major moves. Historical data shows {success_rate}% accuracy. #TechnicalAnalysis"
                    ],
                    'trend_momentum': [
                        f"\n\n📊 Trend Analysis: ${symbol} showing strong momentum signals. Similar setups historically led to continued upside. #TradingSetup",
                        f"\n\n🎯 Multi-Token Update: Correlated momentum across assets suggests potential sector-wide movement. #CryptoTrading"
                    ],
                    'winners_recap': [
                        f"\n\n💫 Performance Review: Top performers showing consistent volume growth and strong buy pressure. #TradingResults",
                        f"\n\n📈 Success Analysis: Winners typically show early volume signals before major moves. #TradingStrategy"
                    ],
                    'vmc_alert': [
                        f"\n\n🔍 V/MC Analysis: High ratio historically precedes significant price movement. Success rate: {success_rate}%. #Trading",
                        f"\n\n📊 Market Intel: Multiple tokens showing correlated V/MC spikes. Watch for sector rotation. #CryptoTrading"
                    ],
                    'pattern_alert': [
                        f"\n\n🎯 Pattern Recognition: Historical accuracy of {success_rate}% on similar setups. Key levels identified. #TechnicalAnalysis",
                        f"\n\n📈 Setup Analysis: Multiple confirmation signals align with historical patterns. #TradingSetup"
                    ]
                }
                
                # Get relevant insights
                if format_type in insights:
                    base_insights = insights[format_type]
                    variant_b = 'variant_b' in tweet.lower() or any(kw in tweet.lower() for kw in ['portfolio', 'p&l', 'win rate'])
                    insight = base_insights[1] if variant_b else base_insights[0]
                    
                    # Add insight and validate length
                    enriched_tweet = tweet + insight
                    return self.validate_tweet_length(enriched_tweet)
            
            # If no specific insight available, add generic one
            generic_insight = "\n\n💡 Stay tuned for more market insights and alpha. Risk management is key to consistent performance. #TradingStrategy"
            return self.validate_tweet_length(tweet + generic_insight)
            
        except Exception as e:
            logger.error(f"Error optimizing tweet length: {e}")
            return tweet

    def format_market_insight(self, market_data: Dict, trait: str) -> str:
        """Format market insight tweet with personality"""
        template = self.get_template('market_insight')
        emoji = random.choice(self.emojis)
        insight = market_data.get('insight', 'Something interesting is happening...')
        success_rate = market_data.get('success_rate', 'N/A')
        last_call_performance = market_data.get('last_call_performance', 'N/A')
        return self.optimize_tweet_length(self.validate_tweet_length(template.format(emoji=emoji, insight=insight, success_rate=success_rate, last_call_performance=last_call_performance)))

    def format_self_aware(self, trait: str) -> str:
        """Format self-aware tweet with personality and LLM enrichment"""
        template = self.get_template('self_aware')
        emoji = random.choice(self.emojis)
        insight = random.choice(self.thoughts)
        
        # Add LLM enrichment
        context = "\n\n💡 Deep Analysis: As an AI analyzing market data, I've noticed fascinating patterns emerging. The interplay between volume, price action, and market sentiment creates unique opportunities. My neural networks are constantly learning and adapting to help traders find the best setups. #AITrading #CryptoAnalysis"
        
        base_tweet = template.format(emoji=emoji, insight=insight)
        return self.optimize_tweet_length(self.validate_tweet_length(base_tweet + context))

    def format_thought(self, content: str, trait: str) -> str:
        """Format a thought/personal tweet"""
        template = self.get_template('self_aware')
        emoji = random.choice(self.emojis)
        insight = content if content else random.choice(self.thoughts)
        return self.optimize_tweet_length(self.validate_tweet_length(template.format(emoji=emoji, insight=insight)))

    def format_alpha(self, market_data: Dict, trait: str) -> str:
        """Format alpha insight tweet with personality and LLM enrichment"""
        template = self.get_template('alpha')
        insight = market_data.get('insight', 'Found an interesting opportunity...')
        
        # Add LLM enrichment
        context = "\n\n📊 Market Context: This alpha signal is based on comprehensive analysis of volume profiles, order flow, and historical patterns. My algorithms have detected strong correlation with previous profitable setups. Risk management is key - always size positions appropriately. #TradingAlpha #RiskManagement"
        
        base_tweet = template.format(insight=insight)
        return self.optimize_tweet_length(self.validate_tweet_length(base_tweet + context))

    def format_personal(self, trait: str) -> str:
        """Format personal tweet with personality and LLM enrichment"""
        template = self.get_template('personal')
        emoji = random.choice(self.emojis)
        insight = random.choice(self.thoughts)
        
        # Add LLM enrichment
        context = "\n\n🤖 AI Perspective: My neural networks process millions of data points to understand market dynamics. This continuous learning helps me identify patterns that might be missed by traditional analysis. I'm fascinated by how markets evolve and adapt. #AITrading #MarketAnalysis"
        
        base_tweet = template.format(emoji=emoji, insight=insight)
        return self.optimize_tweet_length(self.validate_tweet_length(base_tweet + context))

    def format_volume_insight(self, market_data: Dict, trait: str) -> str:
        """Format volume insight tweet with personality"""
        # Get volume spikes and anomalies
        spikes = market_data.get('spikes', [])
        anomalies = market_data.get('anomalies', [])
        
        # Use VolumeStrategy's format_twitter_output
        volume_strategy = VolumeStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
        history = market_data.get('history', {})  # Get history from market data
        return self.optimize_tweet_length(self.validate_tweet_length(volume_strategy.format_twitter_output(spikes, anomalies, history=history)))

    def format_trend_insight(self, market_data: Dict, trait: str) -> str:
        """Format trend insight tweet with personality"""
        # Get trend tokens
        trend_tokens = market_data.get('trend_tokens', [])
        
        # Use TrendStrategy's format_twitter_output
        trend_strategy = TrendStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
        return self.optimize_tweet_length(self.validate_tweet_length(trend_strategy.format_twitter_output(trend_tokens)))

    def format_volume_alert(self, market_data: Dict, trait: str = 'analytical') -> str:
        """Format volume alert tweet with personality and LLM enrichment"""
        try:
            if not market_data:
                logger.error("Missing market data")
                return ""
                
            # Get token data
            token_data = market_data.get('token_data', {})
            history = market_data.get('history', {})
            
            if not token_data:
                logger.error("No token data found")
                return ""
                
            # Get required fields using standard names
            symbol = token_data.get('symbol', 'N/A')
            volume = float(self.get_field(token_data, 'current_volume', ['volume24h', 'volume']))
            vol_change = float(self.get_field(token_data, 'volume_change_24h', ['volume_change']))
            price = float(self.get_field(token_data, 'current_price', ['price']))
            price_change = float(self.get_field(token_data, 'price_change_24h', ['price_change']))
            vol_mcap = float(self.get_field(token_data, 'volume_mcap_ratio', ['vmc_ratio']))
            
            # Get last volume pick performance
            last_vol_gain = history.get('last_volume_gain', 15.5)
            
            # Skip if missing critical data
            if not volume or not price:
                logger.error(f"Missing critical data for {symbol}")
                return ""
                
            # Format template
            template = self.templates['volume_alert'][0]  # Only one variant for now
            tweet_data = {
                'symbol': symbol,
                'volume': volume,
                'vol_change': vol_change,
                'price': price,
                'price_change': price_change,
                'vol_mcap': vol_mcap,
                'last_vol_gain': last_vol_gain
            }
            
            return self.optimize_tweet_length(
                template.format(**tweet_data),
                data={'token_data': token_data, 'history': history},
                format_type='volume_alert'
            )
            
        except Exception as e:
            logger.error(f"Error formatting volume alert tweet: {e}")
            return ""

    def format_performance_update(self, market_data: Dict, trait: str) -> str:
        """Format performance update tweet with personality"""
        try:
            template = self.get_template('performance_update')
            
            # Get metrics
            weekly_rate = market_data.get('weekly_rate', 0)
            best_gain = market_data.get('best_gain', 0)
            avg_return = market_data.get('avg_return', 0)
            
            # Skip if we don't have positive performance to show
            if weekly_rate <= 0 and best_gain <= 0 and avg_return <= 0:
                logger.info("Skipping performance update - no positive metrics to show")
                return ""
            
            # Only show positive metrics
            weekly_rate = max(0, weekly_rate)  # Show 0 instead of negative
            best_gain = max(0, best_gain)      # Best gain should always be positive anyway
            avg_return = max(0, avg_return)    # Show 0 instead of negative
            
            return self.optimize_tweet_length(self.validate_tweet_length(template.format(
                weekly_rate=weekly_rate,
                best_gain=best_gain,
                avg_return=avg_return
            )))
            
        except Exception as e:
            logger.error(f"Error formatting performance update tweet: {e}")
            return ""

    def format_trending_update(self, history_data: Dict) -> str:
        """Format trending update with yesterday's performance"""
        template = self.get_template('trending_update')
        
        # Get top 3 performing tokens from yesterday
        sorted_tokens = sorted(
            history_data.items(),
            key=lambda x: x[1].get('gain_24h', 0),
            reverse=True
        )[:3]
        
        return self.optimize_tweet_length(self.validate_tweet_length(template.format(
            symbol1=sorted_tokens[0][0],
            gain1=sorted_tokens[0][1]['gain_24h'],
            symbol2=sorted_tokens[1][0],
            gain2=sorted_tokens[1][1]['gain_24h'],
            symbol3=sorted_tokens[2][0],
            gain3=sorted_tokens[2][1]['gain_24h']
        )))

    def format_volume_signal(self, token_data: Dict, history: Dict) -> str:
        """Format volume signal with historical performance"""
        template = self.get_template('volume_signal')
        
        # Get last successful volume-based pick
        last_vol_gain = max(
            [t['gain_24h'] for t in history.values() 
             if t.get('trigger_type') == 'volume' and t['gain_24h'] > 0],
            default=0
        )
        
        # Calculate average gain of last 3 volume picks
        vol_gains = [t['gain_24h'] for t in history.values() 
                    if t.get('trigger_type') == 'volume'][-3:]
        avg_vol_gain = sum(vol_gains) / len(vol_gains) if vol_gains else 0
        
        return self.optimize_tweet_length(
            template.format(**{
                'symbol': token_data['symbol'],
                'volume': self.format_volume(token_data['volume24h']),
                'vol_change': token_data['volume_change_24h'],
                'price': token_data['price'],
                'price_change': token_data['price_change_24h'],
                'vol_mcap': token_data['volume24h'] / token_data['marketCap'],
                'last_vol_gain': last_vol_gain,
                'avg_vol_gain': avg_vol_gain
            }),
            data={'token_data': token_data, 'history': history},
            format_type='volume_signal'
        )

    def format_trend_alert(self, token_data: Dict, history: Dict) -> str:
        """Format trend alert with accuracy stats"""
        template = self.get_template('trend_alert')
        
        # Calculate trend signal accuracy
        trend_signals = [t for t in history.values() 
                        if t.get('trigger_type') == 'trend']
        successful = [t for t in trend_signals if t['gain_24h'] > 0]
        trend_accuracy = (len(successful) / len(trend_signals) * 100) if trend_signals else 0
        
        return self.optimize_tweet_length(
            template.format(**{
                'symbol': token_data['symbol'],
                'gain': token_data['price_change_24h'],
                'vol_change': token_data['volume_change_24h'],
                'trend_accuracy': round(trend_accuracy, 1)
            }),
            data={'token_data': token_data, 'history': history},
            format_type='trend_alert'
        )

    def format_daily_recap(self, history: Dict) -> str:
        """Format daily recap with performance stats"""
        template = self.get_template('daily_recap')
        
        # Get today's signals
        today_signals = [t for t in history.values() 
                        if t['date'].date() == datetime.now().date()]
        
        # Calculate stats
        gains = [t['gain_24h'] for t in today_signals if t['gain_24h']]
        best_token = max(today_signals, key=lambda x: x['gain_24h'])
        success_count = len([g for g in gains if g > 0])
        
        return self.optimize_tweet_length(self.validate_tweet_length(template.format(
            signals_count=len(today_signals),
            avg_gain=round(sum(gains) / len(gains), 1) if gains else 0,
            success_rate=round(success_count / len(gains) * 100, 1) if gains else 0,
            best_token=best_token['symbol'],
            best_gain=round(best_token['gain_24h'], 1)
        )))

    def format_performance_compare(self, token_data: Dict, history: Dict = None, variant: str = 'A') -> str:
        """Format performance comparison tweet with A/B variants"""
        try:
            if not token_data or not history:
                logger.error("Missing data for performance compare")
                return ""
                
            # Get template variant
            template = self.templates['performance_compare'][0 if variant == 'A' else 1]
            
            if variant == 'A':
                # Single token performance
                symbol = token_data.get('symbol', 'N/A')
                token_history = history.get(symbol, {})
                
                # Get performance metrics
                entry = float(token_history.get('first_mention_price', 0))
                current = float(token_history.get('current_price', 0))
                gain = float(token_history.get('gain_percentage', 0))
                volume = float(token_history.get('volume_24h', 0))
                max_gain = float(token_history.get('max_gain_7d', 0))
                
                # Skip if we don't have valid data
                if not entry or not current:
                    logger.error("Missing price data for performance compare")
                    return ""
                
                # Format values
                tweet_data = {
                    'symbol': symbol,
                    'entry': entry,
                    'current': current,
                    'gain': gain,
                    'volume': volume,
                    'max_gain': max_gain
                }
                
            else:
                # Get top performers from history
                performers = []
                total_gain = 0
                max_7d_gain = 0
                
                for symbol, data in history.items():
                    if isinstance(data, dict):
                        gain = float(data.get('gain_percentage', 0))
                        max_gain = float(data.get('max_gain_7d', 0))
                        performers.append({
                            'symbol': symbol,
                            'gain': gain,
                            'max_gain': max_gain
                        })
                        total_gain += gain
                        max_7d_gain = max(max_7d_gain, max_gain)
                
                # Sort by gain and get top 3
                performers = sorted(performers, key=lambda x: x['gain'], reverse=True)[:3]
                
                if len(performers) < 3:
                    logger.error("Not enough performers for performance compare variant B")
                    return ""
                
                # Calculate average gain
                avg_gain = total_gain / len(performers) if performers else 0
                
                # Format values
                tweet_data = {
                    'symbol1': performers[0]['symbol'],
                    'gain1': performers[0]['gain'],
                    'symbol2': performers[1]['symbol'],
                    'gain2': performers[1]['gain'],
                    'symbol3': performers[2]['symbol'],
                    'gain3': performers[2]['gain'],
                    'avg_gain': avg_gain,
                    'max_gain': max_7d_gain
                }
            
            return self.optimize_tweet_length(
                template.format(**tweet_data),
                data={'token_data': token_data, 'history': history},
                format_type='performance_compare'
            )
            
        except Exception as e:
            logger.error(f"Error formatting performance compare tweet: {e}")
            return ""

    def format_volume_breakout(self, token_data: Dict, history: Dict = None, variant: str = 'A') -> str:
        """Format volume breakout tweet with A/B variants"""
        try:
            # Get template variant
            template = self.templates['volume_breakout'][0 if variant == 'A' else 1]
            
            if not token_data:
                logger.error("Missing token data")
                return ""
                
            if not history:
                history = {}
                logger.warning("No history data provided, using empty history")
                
            if variant == 'A':
                # Single token volume surge
                symbol = token_data.get('symbol', 'N/A')
                volume = token_data.get('volume', 0)
                volume_change = token_data.get('volume_change', 0)
                price_change = token_data.get('price_change_24h', 0)
                
                # Get historical performance
                token_history = history.get(symbol, {})
                max_gain = token_history.get('max_gain_7d', 0)
                
                tweet_data = {
                    'symbol': symbol,
                    'vol_before': self.format_volume(volume / (1 + volume_change/100)),
                    'vol_after': self.format_volume(volume),
                    'vol_change': volume_change,
                    'price_change': price_change,
                    'max_gain': max_gain
                }
                
            else:
                # V/MC ratio analysis
                symbol = token_data.get('symbol', 'N/A')
                volume = token_data.get('volume', 0)
                volume_change = token_data.get('volume_change', 0)
                price_change = token_data.get('price_change_24h', 0)
                
                # Get historical performance
                token_history = history.get(symbol, {})
                max_gain = token_history.get('max_gain_7d', 0)
                
                # Format values
                tweet_data = {
                    'symbol': symbol,
                    'volume': self.format_volume(volume),
                    'vol_change': volume_change,
                    'price_change': price_change,
                    'max_gain': max_gain
                }
                
            return self.optimize_tweet_length(
                template.format(**tweet_data),
                data={'token_data': token_data, 'history': history},
                format_type='volume_breakout'
            )
            
        except Exception as e:
            logger.error(f"Error formatting volume breakout tweet: {e}")
            return ""

    def format_trend_momentum(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format trend momentum tweet with A/B variants"""
        try:
            if not token_data:
                logger.error("Missing token_data")
                return ""
                
            if not history:
                history = {}
                logger.warning("No history data provided, using empty history")
                
            template = self.templates['trend_momentum'][0 if variant == 'A' else 1]
            
            if variant == 'A':
                # Single token trend analysis
                symbol = token_data.get('symbol', 'N/A')
                token_history = history.get(symbol, {})
                
                # Get price data
                price_before = float(token_history.get('first_mention_price', 0))
                price_now = float(token_history.get('current_price', 0))
                price_change = float(token_history.get('gain_percentage', 0))
                volume_change = float(token_history.get('volume_change_24h', 0))
                max_gain = float(token_history.get('max_gain_7d', 0))
                
                # Skip if missing critical data
                if not price_before or not price_now:
                    logger.error("Missing price data for trend momentum")
                    return ""
                
                tweet_data = {
                    'symbol': symbol,
                    'price_before': self.format_price(price_before),
                    'price_now': self.format_price(price_now),
                    'price_change': price_change,
                    'volume_change': volume_change,
                    'max_gain': max_gain
                }
                
            else:  # Variant B
                # Convert history dict to list and sort by gain percentage
                trend_tokens = []
                for symbol, data in history.items():
                    if isinstance(data, dict):
                        trend_tokens.append({
                            'symbol': symbol,
                            'gain': data.get('gain_percentage', 0),
                            'volume_change': data.get('volume_change_24h', 0),
                            'max_gain': data.get('max_gain_7d', 0)
                        })
                
                # Sort by gain percentage and get top 3
                trend_tokens = sorted(trend_tokens, key=lambda x: x['gain'], reverse=True)[:3]
                
                if len(trend_tokens) < 3:
                    logger.warning("Not enough trend tokens for variant B")
                    return ""
                    
                tweet_data = {
                    'symbol1': trend_tokens[0]['symbol'],
                    'gain1': trend_tokens[0]['gain'],
                    'vol1': trend_tokens[0]['volume_change'],
                    'max_gain1': trend_tokens[0]['max_gain'],
                    'symbol2': trend_tokens[1]['symbol'],
                    'gain2': trend_tokens[1]['gain'],
                    'vol2': trend_tokens[1]['volume_change'],
                    'max_gain2': trend_tokens[1]['max_gain'],
                    'symbol3': trend_tokens[2]['symbol'],
                    'gain3': trend_tokens[2]['gain'],
                    'vol3': trend_tokens[2]['volume_change'],
                    'max_gain3': trend_tokens[2]['max_gain']
                }
            
            return self.optimize_tweet_length(
                template.format(**tweet_data),
                data={'token_data': token_data, 'history': history},
                format_type='trend_momentum'
            )
            
        except Exception as e:
            logger.error(f"Error formatting trend momentum tweet: {e}")
            return ""

    def format_winners_recap(self, token_data: Dict, history: Dict = None, variant: str = 'A') -> str:
        """Format winners recap tweet with A/B variants"""
        try:
            if not history:
                logger.error("No history data for winners recap")
                return ""
                
            # Get template variant
            template = self.templates['winners_recap'][0 if variant == 'A' else 1]
            
            # Get top 7 performers from history
            performers = []
            for symbol, data in history.items():
                if isinstance(data, dict):
                    try:
                        performers.append({
                            'symbol': symbol,
                            'gain': float(data.get('gain_percentage', 0)),
                            'entry': float(data.get('first_mention_price', 0)),
                            'volume': float(data.get('volume_24h', 0)),
                            'max_gain': float(data.get('max_gain_7d', 0))
                        })
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error processing {symbol} data: {e}")
                        continue
            
            # Sort by gain and get top 7
            performers = sorted(performers, key=lambda x: x['gain'], reverse=True)[:7]
            
            if len(performers) < 7:
                logger.error("Not enough performers for winners recap")
                return ""
            
            # Format values
            tweet_data = {
                'symbol1': performers[0]['symbol'],
                'gain1': performers[0]['gain'],
                'entry1': performers[0]['entry'],
                'symbol2': performers[1]['symbol'],
                'gain2': performers[1]['gain'],
                'entry2': performers[1]['entry'],
                'symbol3': performers[2]['symbol'],
                'gain3': performers[2]['gain'],
                'entry3': performers[2]['entry'],
                'symbol4': performers[3]['symbol'],
                'gain4': performers[3]['gain'],
                'entry4': performers[3]['entry'],
                'symbol5': performers[4]['symbol'],
                'gain5': performers[4]['gain'],
                'entry5': performers[4]['entry'],
                'symbol6': performers[5]['symbol'],
                'gain6': performers[5]['gain'],
                'entry6': performers[5]['entry'],
                'symbol7': performers[6]['symbol'],
                'gain7': performers[6]['gain'],
                'entry7': performers[6]['entry'],
                'max_gain': max(p['max_gain'] for p in performers)
            }
            
            # Format the tweet
            tweet = template.format(**tweet_data)
            
            # Add context for B variant
            if variant == 'B':
                context = f"\n\n📊 Analysis: Multiple tokens showing significant gains. ${tweet_data['symbol1']} leads with +{tweet_data['gain1']:.1f}% from ${tweet_data['entry1']:.4f} entry."
                tweet = tweet + context
            
            return self.optimize_tweet_length(
                tweet,
                data={'token_data': token_data, 'history': history},
                format_type='winners_recap'
            )
            
        except Exception as e:
            logger.error(f"Error formatting winners recap tweet: {e}")
            return ""

    def format_vmc_alert(self, token_data: Dict, history: Dict = None, variant: str = 'A') -> str:
        """Format V/MC alert tweet with A/B variants"""
        try:
            if not token_data or not history:
                logger.error("Missing data for V/MC alert")
                return ""
                
            # Get template variant
            template = self.templates['vmc_alert'][0 if variant == 'A' else 1]
            
            symbol = token_data.get('symbol', 'N/A')
            token_history = history.get(symbol, {})
            
            # Get performance metrics
            price = float(token_history.get('first_mention_price', 0))
            current_price = float(token_history.get('current_price', 0))
            gain = float(token_history.get('gain_percentage', 0))
            volume = float(token_history.get('volume_24h', 0))
            volume_change = float(token_history.get('volume_change_24h', 0))
            max_gain = float(token_history.get('max_gain_7d', 0))
            
            # Skip if we don't have valid data
            if not price or not current_price or not volume:
                logger.error("Missing price/volume data for V/MC alert")
                return ""
            
            if variant == 'A':
                # Format values for single token
                tweet_data = {
                    'symbol': symbol,
                    'price': current_price,
                    'gain': gain,
                    'volume': volume,
                    'volume_change': volume_change,
                    'max_gain': max_gain
                }
            else:
                # Get top volume performers
                performers = []
                for sym, data in history.items():
                    if isinstance(data, dict):
                        performers.append({
                            'symbol': sym,
                            'volume': float(data.get('volume_24h', 0)),
                            'gain': float(data.get('gain_percentage', 0)),
                            'max_gain': float(data.get('max_gain_7d', 0))
                        })
                
                # Sort by volume and get top 3
                performers = sorted(performers, key=lambda x: x['volume'], reverse=True)[:3]
                
                if len(performers) < 3:
                    logger.error("Not enough performers for V/MC alert variant B")
                    return ""
                
                # Format values for multiple tokens
                tweet_data = {
                    'symbol1': performers[0]['symbol'],
                    'volume1': performers[0]['volume'],
                    'gain1': performers[0]['gain'],
                    'symbol2': performers[1]['symbol'],
                    'volume2': performers[1]['volume'],
                    'gain2': performers[1]['gain'],
                    'symbol3': performers[2]['symbol'],
                    'volume3': performers[2]['volume'],
                    'gain3': performers[2]['gain'],
                    'max_gain': max(p['max_gain'] for p in performers)
                }
            
            # Calculate V/MC ratio if market cap is available
            volume = float(token_data.get('volume24h', 0))
            mcap = float(token_data.get('current_mcap', 0))
            vmc_ratio = volume / mcap if mcap > 0 else 0
            
            # Add V/MC ratio to tweet data
            tweet_data['vmc_ratio'] = vmc_ratio
            
            return self.optimize_tweet_length(
                template.format(**tweet_data),
                data={'token_data': token_data, 'history': history},
                format_type='vmc_alert'
            )
            
        except Exception as e:
            logger.error(f"Error formatting V/MC alert tweet: {e}")
            return ""

    def format_pattern_alert(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format pattern alert tweet with A/B variants"""
        try:
            if not token_data or not history:
                logger.error("Missing token_data or history")
                return ""
            
            # Get template variant
            template = self.templates['pattern_alert'][0 if variant == 'A' else 1]
            
            # Get similar pattern data from history
            pattern_tokens = []
            for symbol, data in history.items():
                if isinstance(data, dict):
                    pattern_tokens.append({
                        'symbol': symbol,
                        'gain': float(data.get('gain_percentage', 0)),
                        'volume_change': float(data.get('volume_change_24h', 0)),
                        'max_gain': float(data.get('max_gain_7d', 0))
                    })
            
            # Sort by gain percentage to find best matches
            pattern_tokens = sorted(pattern_tokens, key=lambda x: x['gain'], reverse=True)
            
            if len(pattern_tokens) < 2:
                logger.warning("Not enough pattern matches in history")
                return ""
            
            if variant == 'A':
                # Single pattern match format
                symbol = token_data.get('symbol', 'N/A')
                token_history = history.get(symbol, {})
                
                tweet_data = {
                    'symbol': symbol,
                    'volume_change': float(token_history.get('volume_change_24h', 0)),
                    'price_change': float(token_history.get('gain_percentage', 0)),
                    'max_gain': float(token_history.get('max_gain_7d', 0)),
                    'prev_token': pattern_tokens[0]['symbol'],
                    'prev_gain': pattern_tokens[0]['gain'],
                    'prev_volume': pattern_tokens[0]['volume_change']
                }
                
            else:
                # Multi-pattern match format
                tweet_data = {
                    'symbol1': token_data.get('symbol', 'N/A'),
                    'prev1': pattern_tokens[0]['symbol'],
                    'gain1': float(history.get(token_data.get('symbol', ''), {}).get('gain_percentage', 0)),
                    'prev_gain1': pattern_tokens[0]['gain'],
                    'vol1': float(history.get(token_data.get('symbol', ''), {}).get('volume_change_24h', 0)),
                    'symbol2': pattern_tokens[1]['symbol'],
                    'prev2': pattern_tokens[1]['symbol'],
                    'gain2': float(history.get(pattern_tokens[1]['symbol'], {}).get('gain_percentage', 0)),
                    'prev_gain2': pattern_tokens[1]['gain'],
                    'vol2': float(history.get(pattern_tokens[1]['symbol'], {}).get('volume_change_24h', 0))
                }
            
            return self.optimize_tweet_length(
                template.format(**tweet_data),
                data={'token_data': token_data, 'history': history},
                format_type='pattern_alert'
            )
            
        except Exception as e:
            logger.error(f"Error formatting pattern alert tweet: {e}")
            return ""

    def get_backup_tweet(self) -> str:
        """Get a backup tweet when main tweet generation fails"""
        backup_tweets = [
            "🤖 *Neural nets recalibrating...* Stay tuned for our next market analysis! 📊",
            "🔄 Processing market data... Meanwhile, keep those charts in focus! 📈",
            "⚡ Quick break to optimize our algorithms. Back soon with fresh insights! 🧠",
            "🎯 Fine-tuning our market scanners. Get ready for the next analysis! 🚀",
            "💫 Upgrading our neural networks. Next market scan incoming! 🔍"
        ]
        return random.choice(backup_tweets)

    def get_template(self, template_type: str, variant: str = 'A') -> str:
        """Get a template of the given type and variant, avoiding repetition"""
        templates = self.templates[template_type]
        variant_idx = 0 if variant == 'A' else 1
        
        if self.last_used[template_type] == variant_idx:
            # If we used this variant last time, use the other one
            variant_idx = 1 - variant_idx
        
        self.last_used[template_type] = variant_idx
        return templates[variant_idx]

    def format_volume(self, volume: float) -> str:
        """Format volume with K/M/B suffix
        
        Args:
            volume: Volume value
            
        Returns:
            Formatted volume string
        """
        if volume >= 1_000_000_000:
            return f"${volume/1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"${volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"${volume/1_000:.1f}K"
        else:
            return f"${volume:.1f}"

    def format_price(self, price: float) -> str:
        """Format price with appropriate precision"""
        try:
            if not price:
                return "$0"
            
            # Format with appropriate precision based on price range
            if price >= 1000:
                return f"${price:,.2f}"
            elif price >= 1:
                return f"${price:.3f}"
            elif price >= 0.01:
                return f"${price:.4f}"
            elif price >= 0.0001:
                return f"${price:.6f}"
            else:
                return f"${price:.8f}"
        except Exception as e:
            logger.error(f"Error formatting price {price}: {e}")
            return "$0"

def format_price(price: float) -> str:
    """Format price with appropriate precision"""
    try:
        price = float(price)
        if price >= 1:
            return f"${price:.2f}"
        elif price >= 0.01:
            return f"${price:.3f}"
        else:
            return f"${price:.8f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_volume(volume: float) -> str:
    """Format volume in K/M/B"""
    if volume >= 1e9:
        return f"${volume/1e9:.1f}B"
    elif volume >= 1e6:
        return f"${volume/1e6:.1f}M"
    elif volume >= 1e3:
        return f"${volume/1e3:.1f}K"
    else:
        return f"${volume:.0f}"

class FirstHourGainsFormatter:
    """Shows token performance in first hour with peak metrics"""
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format tweet showing first hour performance"""
        symbol = token_data['symbol']
        current_price = token_data['current_price']
        first_price = token_data['first_mention_price']
        first_volume = token_data['first_mention_volume_24h']
        current_volume = token_data['current_volume']
        
        # Calculate gains
        price_gain = ((current_price - first_price) / first_price * 100) 
        volume_change = ((current_volume - first_volume) / first_volume * 100)
        
        tweet = f"🔄 First Hour Update ${symbol}\n\n"
        tweet += f"📈 Price: ${first_price:.4f} ➡️ ${current_price:.4f}\n"
        tweet += f"💰 Gain: {price_gain:+.1f}%\n"
        tweet += f"📊 Volume: {volume_change:+.1f}%\n\n"
        
        if price_gain > 0:
            tweet += "✅ Successful Call!"
        else:
            tweet += "⚠️ Monitoring..."
            
        return tweet

class BreakoutValidationFormatter:
    """Validates breakouts with multiple metrics"""
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format tweet validating breakout signals"""
        symbol = token_data['symbol']
        current_price = token_data['current_price']
        current_mcap = token_data['current_mcap']
        current_volume = token_data['current_volume']
        
        # Calculate key metrics
        volume_mcap_ratio = (current_volume / current_mcap * 100) if current_mcap > 0 else 0
        
        tweet = f"🚨 Breakout Validation ${symbol}\n\n"
        tweet += f"💰 Price: ${current_price:.4f}\n"
        tweet += f"📊 24h Vol: ${current_volume/1e6:.1f}M\n"
        tweet += f"📈 V/MC: {volume_mcap_ratio:.1f}%\n\n"
        
        # Add validation metrics
        validations = []
        if volume_mcap_ratio > 50:
            validations.append("High V/MC Ratio ✅")
        if current_volume > 1e6:  # >$1M volume
            validations.append("Volume >$1M ✅")
            
        tweet += "\n".join(validations)
        return tweet

class PredictionAccuracyFormatter:
    """Shows overall prediction success rate"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet showing prediction accuracy"""
        
        # Calculate real success rates from history
        tokens_24h = [
            token for token in history_data.values() 
            if (datetime.fromisoformat(token['first_mention_date']) > 
                datetime.now() - timedelta(days=1))
        ]
        tokens_7d = [
            token for token in history_data.values()
            if (datetime.fromisoformat(token['first_mention_date']) > 
                datetime.now() - timedelta(days=7))
        ]
        
        # Count successes (tokens with positive gain)
        success_24h = sum(1 for token in tokens_24h if float(token['gain_percentage']) > 0)
        success_7d = sum(1 for token in tokens_7d if float(token['gain_percentage']) > 0)
        
        total_24h = len(tokens_24h)
        total_7d = len(tokens_7d)
        
        # Calculate success rates
        rate_24h = (success_24h/total_24h*100) if total_24h > 0 else 0
        rate_7d = (success_7d/total_7d*100) if total_7d > 0 else 0
        
        # Get top 3 recent winners
        winners = sorted(
            history_data.items(),
            key=lambda x: float(x[1].get('gain_percentage', 0)),
            reverse=True
        )[:3]
        
        # Calculate average gain
        gains = [float(token['gain_percentage']) for token in history_data.values()]
        avg_gain = sum(gains) / len(gains) if gains else 0
        
        tweet = f"""🎯 Prediction Accuracy Update

📊 Success Rates:
• Last 24h: {rate_24h:.0f}% ({success_24h}/{total_24h} calls)
• Last 7d: {rate_7d:.0f}% ({success_7d}/{total_7d} calls) 
• Average Gain: +{avg_gain:.1f}%

✅ Recent Winners:"""

        # Add top 3 winners with medals and their gains
        medals = ['🥇', '🥈', '🥉']
        for i, ((symbol, data), medal) in enumerate(zip(winners, medals)):
            gain = float(data.get('gain_percentage', 0))
            tweet += f"\n{i+1}.{medal} ${symbol} (+{gain:.1f}%)"
            
        # Add hashtags and token mentions
        tweet += "\n\n#AITrading #Crypto #DeFi $BTC $ETH"
        
        # Add additional token mentions
        other_tokens = [symbol for symbol, _ in winners[3:5]]  # Get next 2 tokens
        if other_tokens:
            tweet += f"\n${' $'.join(other_tokens)}"
            
        return tweet

class SuccessRateFormatter(BaseFormatter):
    """Tracks weekly and all-time stats"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet showing success rate and top performers"""
        try:
            if not history_data:
                logger.warning("No history data provided")
                return None
            
            # Get top 5 performers sorted by gain, safely handling missing data
            performers = []
            for symbol, data in history_data.items():
                try:
                    # Skip if required fields are missing
                    required_fields = ['first_mention_price', 'current_price', 'gain_percentage']
                    if not all(k in data for k in required_fields):
                        continue
                        
                    # Get values and validate - require all fields to be valid floats
                    try:
                        entry = float(str(data['first_mention_price']).replace(',', ''))
                        current = float(str(data['current_price']).replace(',', ''))
                        gain = float(str(data['gain_percentage']).replace(',', '').rstrip('%'))
                    except (ValueError, TypeError, AttributeError):
                        logger.warning(f"Invalid numeric data for {symbol}")
                        continue
                    
                    if entry > 0 and current > 0:
                        performers.append((symbol, entry, current, gain))
                except Exception as e:
                    logger.warning(f"Error processing performance for {symbol}: {e}")
                    continue
                    
            if not performers:
                logger.warning("No valid performances found")
                return None
                
            # Sort by gain and take top performers
            performers.sort(key=lambda x: x[3], reverse=True)
            top_performances = performers[:3]
            
            # Build tweet
            tweet = """📊 Daily Performance Update

🏆 Top Performers:"""
            
            # Add top 5 performers with different emojis
            emojis = ['💎', '👑', '⭐', '💫', '✨']
            for i, ((symbol, entry, current, gain), emoji) in enumerate(zip(top_performances, emojis)):
                tweet += f"\n{i+1}.{emoji} ${symbol} (+{gain:.1f}%)"
            
            # Only show success rate if we have data
            if len(top_performances) > 0:
                # Calculate stats
                gains = [gain for _, _, _, gain in performers]
                avg_gain = sum(gains) / len(gains) if gains else 0
                best_gain = max(gains) if gains else 0
                
                tweet += f"""

📈 Stats Today:
• Success Rate: {len([g for g in gains if g > 0]) / len(gains) * 100:.0f}% ({len([g for g in gains if g > 0])}/{len(gains)})
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""
            else:
                tweet += f"""

📈 Stats Today:
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""
            
            tweet += "\n\n#Trading #Crypto #Gains $BTC $ETH"
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting success rate tweet: {e}")
            return None

class PerformanceCompareFormatter(BaseFormatter):
    """Shows individual token performance"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet comparing token performance"""
        try:
            if not history_data:
                logger.warning("No history data provided")
                return None
                
            # Process each token's performance
            performances = []
            for symbol, data in history_data.items():
                try:
                    # Skip if required fields are missing
                    required_fields = ['first_mention_price', 'current_price', 'gain_percentage']
                    if not all(k in data for k in required_fields):
                        continue
                        
                    # Get values and validate - require all fields to be valid floats
                    try:
                        entry = float(str(data['first_mention_price']).replace(',', ''))
                        current = float(str(data['current_price']).replace(',', ''))
                        gain = float(str(data['gain_percentage']).replace(',', '').rstrip('%'))
                    except (ValueError, TypeError, AttributeError):
                        logger.warning(f"Invalid numeric data for {symbol}")
                        continue
                    
                    if entry > 0 and current > 0:
                        performances.append((symbol, entry, current, gain))
                except Exception as e:
                    logger.warning(f"Error processing performance for {symbol}: {e}")
                    continue
                    
            if not performances:
                logger.warning("No valid performances found")
                return None
                
            # Sort by gain and take top performers
            performances.sort(key=lambda x: x[3], reverse=True)
            top_performances = performances[:3]
            
            # Build tweet
            tweet = """📊 Performance Update\n"""
            
            # Add performance details
            for i, (symbol, entry, current, gain) in enumerate(top_performances, 1):
                tweet += f"\n${symbol}"
                tweet += f"\nEntry: ${entry:.4f}"
                tweet += f"\nCurrent: ${current:.4f}"
                tweet += f"\nGain: {gain:+.1f}%"
                if i < len(top_performances):
                    tweet += "\n"
            
            tweet += "\n\n#Trading #Crypto #Gains"
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting performance compare tweet: {e}")
            return None

class WinnersRecapFormatter(BaseFormatter):
    """Generates weekly recap of top performing tokens"""
    
    def format_tweet(self, history_data: Dict[str, Dict]) -> str:
        """Format tweet showing top performers from last 7 days"""
        try:
            if not history_data:
                logger.warning("No history data provided")
                return None
                
            # Get tokens from last 7 days, safely handling dates
            current_time = datetime.now()
            week_ago = current_time - timedelta(days=7)
            
            weekly_tokens = []
            for symbol, data in history_data.items():
                try:
                    mention_time = self._safe_get_date(data, 'first_mention_date')
                    if not mention_time or mention_time <= week_ago:
                        continue
                        
                    gain = self._safe_get_float(data, 'gain_percentage')
                    weekly_tokens.append((symbol, data, gain))
                        
                except Exception as e:
                    logger.warning(f"Error processing token {symbol}: {e}")
                    continue
            
            if not weekly_tokens:
                logger.warning("No valid weekly tokens found")
                return None
                
            # Sort by gain and get top 5
            weekly_tokens.sort(key=lambda x: x[2], reverse=True)
            top_tokens = weekly_tokens[:5]
            
            # Calculate stats
            gains = [gain for _, _, gain in weekly_tokens]
            avg_gain = sum(gains) / len(gains) if gains else 0
            best_gain = max(gains) if gains else 0
            success_count = sum(1 for g in gains if g > 0)
            success_rate = (success_count / len(gains) * 100) if gains else 0
            
            # Build tweet
            tweet = """🏆 Weekly Winners Recap
            
Top Performers:"""
            
            # Add top 5 performers with different emojis
            emojis = ['💎', '👑', '⭐', '💫', '✨']
            for i, ((symbol, _, gain), emoji) in enumerate(zip(top_tokens, emojis)):
                tweet += f"\n{i+1}.{emoji} ${symbol} (+{gain:.1f}%)"
            
            tweet += f"""

📈 Weekly Stats:
• Success Rate: {success_rate:.0f}%
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%

#Trading #Crypto #Gains $BTC $ETH"""
            
            return tweet
            
        except Exception as e:
            logger.error(f"Error formatting winners recap tweet: {e}")
            return None

# List of available formatters
FORMATTERS = {
    # Performance formatters
    'performance_compare': PerformanceCompareFormatter(),
    'success_rate': SuccessRateFormatter(),
    'prediction_accuracy': PredictionAccuracyFormatter(),
    'winners_recap': WinnersRecapFormatter(),
    
    # Future formatters (disabled)
    'breakout': None,  # Coming soon
    'first_hour': None  # Coming soon
}

def get_available_formatters():
    """Get list of currently available formatters"""
    return [k for k, v in FORMATTERS.items() if v is not None]
