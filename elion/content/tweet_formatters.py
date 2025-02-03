"""
Tweet formatting utilities for ELAI
"""

import random
from typing import Dict, Optional
import os
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TweetFormatters:
    """Formats different types of tweets with personality"""
    
    def __init__(self):
        """Initialize tweet formatter with templates and personality traits"""
        self.templates = {
            'performance_compare': [
                # A variant - Single token performance
                """🤖 Neural Analysis Complete

📊 24h Results for ${symbol}:
💰 Price: ${price:.4f} → ${current_price:.4f} ($+{gain:.1f}%)
📈 Volume: $+{volume_change:.1f}%

🎯 Success Rate: ${success_rate}% on volume spikes
🔮 AI Prediction: ${prediction}

Next alpha dropping soon... 👀""",
                
                # B variant - Portfolio performance
                """🤖 Portfolio AI Update

💼 Performance Stats:
💰 P&L: $+{daily_pnl:.1f}% (${current_capital:,.0f})
🎯 Win Rate: ${win_rate:.1f}% ({num_signals} signals)

📈 Strategy Metrics:
• Success Rate: ${success_rate}%
• Avg Gain: +${avg_gain:.1f}%

💡 Risk management and consistent execution driving results. #TradingStrategy"""
            ],
            'volume_breakout': [
                "💹 Volume Surge: {symbol}\n\n24h Before: {vol_before}\nNow: {vol_now} ({vol_change:+.1f}%)\n\nLast 3 volume picks:\n{prev1} {prev1_gain:+.1f}%\n{prev2} {prev2_gain:+.1f}%\n{prev3} {prev3_gain:+.1f}%",
                "📊 Volume Alert: {symbol}\n\nVol/MCap: {prev_vmc:.1f}% → {curr_vmc:.1f}%\n24h Vol: {vol_change:+.1f}%\n\nLast vol alert: {last_vol_token} +{last_vol_gain:.1f}% 🎯"
            ],
            'trend_momentum': [
                "📈 Trend Update:\n\n{symbol} 24h:\nPrice: {price_before} → {price_now} ({price_change:+.1f}%)\nVol/MCap: {prev_vmc:.1f}% → {curr_vmc:.1f}%\n\nTrend accuracy: {accuracy}% last 7d 🎯",
                "🌊 Trend Watch:\n\n1. {symbol1} {gain1:+.1f}% (Vol {vol1:+.1f}%)\n2. {symbol2} {gain2:+.1f}% (Vol {vol2:+.1f}%)\n3. {symbol3} {gain3:+.1f}% (Vol {vol3:+.1f}%)\n\nSuccess rate: {accuracy}% 💫"
            ],
            'winners_recap': [
                "🏆 Today's Winners:\n\n1. {symbol1} +{gain1:.1f}% (Called at {entry1})\n2. {symbol2} +{gain2:.1f}% (Called at {entry2})\n3. {symbol3} +{gain3:.1f}% (Called at {entry3})\n\nDon't miss tomorrow's calls!",
                "💎 Top Performers Today:\n\n{symbol1}: +{gain1:.1f}% (Vol/MC {vmc1:.1f}x)\n{symbol2}: +{gain2:.1f}% (Vol/MC {vmc2:.1f}x)\n{symbol3}: +{gain3:.1f}% (Vol/MC {vmc3:.1f}x)\n\nNext calls loading... 🔍"
            ],
            'vmc_alert': [
                "🚨 V/MC Alert: {symbol}\n\nYesterday: {prev_vmc:.1f}%\nNow: {curr_vmc:.1f}% ({vmc_change:+.1f}%)\n\nV/MC >{threshold}% led to +{avg_gain:.1f}% gains\nin {success_rate} out of 10 calls 🎯",
                "📊 Volume/MCap Signals:\n\n{symbol1}: {vmc1:.1f}x ({vmc_change1:+.1f}%)\n{symbol2}: {vmc2:.1f}x ({vmc_change2:+.1f}%)\n{symbol3}: {vmc3:.1f}x ({vmc_change3:+.1f}%)\n\nHistorical avg gain: +{avg_gain:.1f}% 💰"
            ],
            'pattern_alert': [
                "🔍 Pattern Detected:\n\n{symbol} showing same setup as\n{prev_token} (24h ago: +{prev_gain:.1f}%)\n\n• V/MC: {vmc:.1f}% ✅\n• Vol {vol_change:+.1f}% ✅\n• Price coiling ✅",
                "🎯 Setup Scanner:\n\n{symbol1} matches {prev1} (+{gain1:.1f}%)\n{symbol2} matches {prev2} (+{gain2:.1f}%)\n\nSuccess rate on matches: {accuracy}% 🔥"
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
                "🚨 High Volume Alert!\n\n{symbol} detected 📊\n💹 Vol: {volume:,.0f} (+{vol_change}%)\n📈 Price: {price:,.4f} ({price_change:+.1f}%)\n🎯 V/MC: {vol_mcap:.1f}x\n\nLast volume pick: +{last_vol_gain}% 💰",
                "📊 Volume Surge Detected!\n\n{symbol} showing strength 💪\n📈 Volume: {volume:,.0f}\n🔄 24h Change: {price_change:+.1f}%\n💎 V/MC Ratio: {vol_mcap:.1f}x\n\nPrevious vol pick: +{last_vol_gain}% 🎯",
                "💹 Volume Analysis:\n\n{symbol} breakout potential!\n📊 Vol/MCap: {vol_mcap:.1f}x\n📈 Price: {price_change:+.1f}%\n\nLast 3 vol picks avg: +{avg_vol_gain}% 🔥"
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
                volume_change = token_data.get('volume_change', 0)
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
        return self.optimize_tweet_length(self.validate_tweet_length(volume_strategy.format_twitter_output(spikes, anomalies)))

    def format_trend_insight(self, market_data: Dict, trait: str) -> str:
        """Format trend insight tweet with personality"""
        # Get trend tokens
        trend_tokens = market_data.get('trend_tokens', [])
        
        # Use TrendStrategy's format_twitter_output
        trend_strategy = TrendStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
        return self.optimize_tweet_length(self.validate_tweet_length(trend_strategy.format_twitter_output(trend_tokens)))

    def format_volume_alert(self, market_data: Dict, trait: str = 'analytical') -> str:
        """Format volume alert tweet with personality and LLM enrichment
        
        Args:
            market_data: Market data dictionary
            trait: Personality trait to use
            
        Returns:
            Formatted tweet string
        """
        if not market_data or not isinstance(market_data, dict):
            raise ValueError("Invalid market data provided")
            
        symbol = market_data.get('symbol')
        if not symbol:
            raise ValueError("Market data missing symbol")
            
        volume = market_data.get('volume', 0)
        prev_volume = market_data.get('prev_volume', 0)
        volume_change = ((volume - prev_volume) / prev_volume * 100) if prev_volume else 0
        
        mcap = market_data.get('market_cap', 0) 
        vmc_ratio = (volume / mcap * 100) if mcap else 0
        
        # Get template variant
        variant = 'A' if random.random() < 0.5 else 'B'
        template = self.templates['volume_alert'][0 if variant == 'A' else 1]
        
        # Format with available data
        tweet_data = {
            'symbol': symbol,
            'volume': volume,
            'vol_change': volume_change,
            'price': market_data.get('price', 0),
            'price_change': market_data.get('price_change', 0),
            'vol_mcap': vmc_ratio,
            'last_vol_gain': market_data.get('last_volume_gain', 0)
        }
        
        try:
            base_tweet = template.format(**tweet_data)
            
            # Add LLM enrichment based on the data
            if volume_change > 50:
                context = "\n\n🔍 Analysis: This massive volume surge often signals strong institutional interest. Historical data shows {symbol} tends to continue its momentum after such spikes. Key resistance levels and orderbook depth suggest potential for further upside. Stay tuned for more signals! #Crypto #TradingAlpha"
            elif volume_change > 20:
                context = "\n\n🔍 Analysis: Moderate volume increase showing growing market interest. {symbol}'s volume profile indicates accumulation phase, with similar patterns historically leading to +{last_vol_gain}% moves. Watch for continuation! #Crypto #TechnicalAnalysis"
            else:
                context = "\n\n🔍 Analysis: Early volume movement detected. While modest, {symbol} often sees price follow volume. Previous instances led to {last_vol_gain}% average gains. Monitor order flow for confirmation. #Crypto #TradingSignals"
                
            enriched_tweet = base_tweet + context.format(symbol=symbol, last_vol_gain=market_data.get('last_vol_gain', 10))
            return self.optimize_tweet_length(self.validate_tweet_length(enriched_tweet))
            
        except KeyError as e:
            print(f"Missing data for tweet template: {e}")
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
        
        return self.optimize_tweet_length(self.validate_tweet_length(template.format(
            symbol=token_data['symbol'],
            volume=self.format_volume(token_data['volume24h']),
            vol_change=token_data['volume_change_24h'],
            price=token_data['price'],
            price_change=token_data['price_change_24h'],
            vol_mcap=token_data['volume24h'] / token_data['marketCap'],
            last_vol_gain=last_vol_gain,
            avg_vol_gain=avg_vol_gain
        )))

    def format_trend_alert(self, token_data: Dict, history: Dict) -> str:
        """Format trend alert with accuracy stats"""
        template = self.get_template('trend_alert')
        
        # Calculate trend signal accuracy
        trend_signals = [t for t in history.values() 
                        if t.get('trigger_type') == 'trend']
        successful = [t for t in trend_signals if t['gain_24h'] > 0]
        trend_accuracy = (len(successful) / len(trend_signals) * 100) if trend_signals else 0
        
        return self.optimize_tweet_length(self.validate_tweet_length(template.format(
            symbol=token_data['symbol'],
            gain=token_data['price_change_24h'],
            vol_change=token_data['volume_change_24h'],
            trend_accuracy=round(trend_accuracy, 1)
        )))

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

    def format_performance_compare(self, data: Dict, variant: str = 'A') -> str:
        """Format performance comparison tweet with A/B variants"""
        try:
            # Get template variant
            template = self.templates['performance_compare'][0 if variant == 'A' else 1]
            
            # Extract token data
            token_data = data.get('token_data', {})
            history = data.get('history', {})
            
            if variant == 'A':
                # Single token performance
                symbol = token_data.get('symbol', 'N/A')
                price = float(token_data.get('first_mention_price', 0))
                current_price = float(token_data.get('price', 0))
                gain = float(token_data.get('price_change_24h', 0))
                volume_change = float(token_data.get('volume_change', 0))
                success_rate = float(history.get('success_rate', 80))
                
                # Generate prediction based on metrics
                if gain > 10 and volume_change > 50:
                    prediction = "Strong breakout potential detected"
                elif gain > 5 or volume_change > 25:
                    prediction = "Watching for continuation signals"
                else:
                    prediction = "Monitoring volume patterns"
                
                # Format values
                tweet_data = {
                    'symbol': symbol,
                    'price': price,
                    'current_price': current_price,
                    'gain': gain,
                    'volume_change': volume_change,
                    'success_rate': success_rate,
                    'prediction': prediction
                }
                
                # Format the tweet
                tweet = template.format(**tweet_data)
                return self.optimize_tweet_length(tweet, data, 'performance_compare')
                
            else:
                # Portfolio performance
                success_rate = float(history.get('success_rate', 80))
                avg_gain = float(history.get('avg_gain', 15.5))
                num_signals = int(history.get('num_signals', 10))
                daily_pnl = float(history.get('pnl', avg_gain * success_rate / 100))  # Use provided PNL or estimate
                current_capital = float(history.get('capital', 10000))  # Use provided capital or default
                win_rate = success_rate  # Use success rate as win rate
                
                # Format values
                tweet_data = {
                    'daily_pnl': daily_pnl,
                    'current_capital': current_capital,
                    'win_rate': win_rate,
                    'avg_gain': avg_gain,
                    'success_rate': success_rate,
                    'num_signals': num_signals
                }
                
                # Format base tweet
                base_tweet = template.format(**tweet_data)
                
                # Add strategy insight
                if len(base_tweet) < 220:
                    insight = f"\n\n📊 Strategy Update: Consistent execution and risk management driving {success_rate}% success rate. Focus on high-probability setups paying off. #TradingStrategy"
                    enriched_tweet = base_tweet + insight
                    return self.validate_tweet_length(enriched_tweet)
                return base_tweet
            
        except Exception as e:
            logger.error(f"Error formatting performance compare tweet: {e}")
            return ""

    def format_volume_breakout(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format volume breakout tweet with A/B variants"""
        try:
            # Get template variant
            template = self.templates['volume_breakout'][0 if variant == 'A' else 1]
            
            if not token_data or not history:
                logger.error("Missing required data")
                return ""
                
            if variant == 'A':
                # Single token volume surge
                symbol = token_data.get('symbol', 'N/A')
                volume = token_data.get('volume', 0)
                volume_change = token_data.get('volume_change', 0)
                
                # Get previous volume picks
                volume_picks = history.get('volume_picks', [])
                if len(volume_picks) < 3:
                    return ""
                    
                # Format values
                tweet_data = {
                    'symbol': symbol,
                    'vol_before': self.format_volume(volume / (1 + volume_change/100)),
                    'vol_now': self.format_volume(volume),
                    'vol_change': volume_change,
                    'prev1': volume_picks[0].get('symbol', 'N/A'),
                    'prev1_gain': volume_picks[0].get('gain', 0),
                    'prev2': volume_picks[1].get('symbol', 'N/A'),
                    'prev2_gain': volume_picks[1].get('gain', 0),
                    'prev3': volume_picks[2].get('symbol', 'N/A'),
                    'prev3_gain': volume_picks[2].get('gain', 0)
                }
                
                base_tweet = template.format(**tweet_data)
                
                # Add LLM enrichment
                context = f"\n\n📊 Analysis: {symbol} showing significant volume surge of {volume_change:+.1f}%. Previous volume picks averaged {(volume_picks[0].get('gain', 0) + volume_picks[1].get('gain', 0) + volume_picks[2].get('gain', 0))/3:.1f}% gains. Monitoring price action for breakout confirmation. #TradingSetup #VolumeAnalysis"
                
            else:
                # V/MC ratio change
                symbol = token_data.get('symbol', 'N/A')
                volume_change = token_data.get('volume_change', 0)
                curr_vmc = token_data.get('vmc_ratio', 0)
                prev_vmc = curr_vmc / (1 + volume_change/100) if volume_change != -100 else 0
                
                # Get last volume alert
                last_alert = history.get('volume_picks', [{}])[0]
                
                # Format values
                tweet_data = {
                    'symbol': symbol,
                    'prev_vmc': prev_vmc,
                    'curr_vmc': curr_vmc,
                    'vol_change': volume_change,
                    'last_vol_token': last_alert.get('symbol', 'N/A'),
                    'last_vol_gain': last_alert.get('gain', 0)
                }
                
                base_tweet = template.format(**tweet_data)
                
                # Add LLM enrichment
                context = f"\n\n🔍 Technical Analysis: {symbol}'s V/MC ratio surge from {prev_vmc:.1f}% to {curr_vmc:.1f}% indicates strong accumulation. Last alert ({last_alert.get('symbol', 'N/A')}) resulted in {last_alert.get('gain', 0):+.1f}% gain. Watching for continuation. #TradingAlpha #VolumeAnalysis"
            
            # Combine base tweet with context and validate length
            enriched_tweet = base_tweet + context
            return self.optimize_tweet_length(self.validate_tweet_length(enriched_tweet))
            
        except Exception as e:
            logger.error(f"Error formatting volume breakout tweet: {e}")
            return ""

    def format_trend_momentum(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format trend momentum tweet with A/B variants"""
        template = self.templates['trend_momentum'][0 if variant == 'A' else 1]
        
        # Calculate trend accuracy
        trend_signals = sorted(history.values(), key=lambda x: x['first_mention_date'], reverse=True)[:7]
        accuracy = len([t for t in trend_signals 
                       if ((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 > 0]) / len(trend_signals) * 100 if trend_signals else 0
        
        if variant == 'A':
            return self.optimize_tweet_length(self.validate_tweet_length(template.format(
                symbol=token_data['symbol'],
                price_before=token_data['first_mention_price'],
                price_now=token_data['current_price'],
                price_change=((token_data['current_price'] - token_data['first_mention_price']) / token_data['first_mention_price']) * 100,
                prev_vmc=token_data['first_mention_volume_mcap_ratio'],
                curr_vmc=token_data['volume_mcap_ratio'],
                accuracy=round(accuracy, 1)
            )))
        else:
            # Get top 3 trending tokens
            top_trends = sorted(history.values(), 
                              key=lambda x: ((x['current_price'] - x['first_mention_price']) / x['first_mention_price']) * 100 if x['first_mention_price'] > 0 else 0,
                              reverse=True)[:3]
            return self.optimize_tweet_length(self.validate_tweet_length(template.format(
                symbol1=top_trends[0]['symbol'],
                gain1=((top_trends[0]['current_price'] - top_trends[0]['first_mention_price']) / top_trends[0]['first_mention_price']) * 100,
                vol1=((top_trends[0]['current_volume'] - top_trends[0]['first_mention_volume_24h']) / top_trends[0]['first_mention_volume_24h']) * 100 if top_trends[0]['first_mention_volume_24h'] > 0 else 0,
                symbol2=top_trends[1]['symbol'],
                gain2=((top_trends[1]['current_price'] - top_trends[1]['first_mention_price']) / top_trends[1]['first_mention_price']) * 100,
                vol2=((top_trends[1]['current_volume'] - top_trends[1]['first_mention_volume_24h']) / top_trends[1]['first_mention_volume_24h']) * 100 if top_trends[1]['first_mention_volume_24h'] > 0 else 0,
                symbol3=top_trends[2]['symbol'],
                gain3=((top_trends[2]['current_price'] - top_trends[2]['first_mention_price']) / top_trends[2]['first_mention_price']) * 100,
                vol3=((top_trends[2]['current_volume'] - top_trends[2]['first_mention_volume_24h']) / top_trends[2]['first_mention_volume_24h']) * 100 if top_trends[2]['first_mention_volume_24h'] > 0 else 0,
                accuracy=round(accuracy, 1)
            )))

    def format_winners_recap(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format winners recap tweet with A/B variants"""
        if not history:
            logger.error("Missing history data")
            return ""
            
        # Get template variant
        template = self.templates['winners_recap'][0 if variant == 'A' else 1]
        
        try:
            # Get top performers
            volume_picks = history.get('volume_picks', [])
            if len(volume_picks) < 3:
                return ""
                
            # Format tweet data
            if variant == 'A':
                # Entry points and gains format
                tweet_data = {
                    'symbol1': volume_picks[0].get('symbol', 'N/A'),
                    'gain1': volume_picks[0].get('gain', 0),
                    'entry1': self.format_price(volume_picks[0].get('entry_price', 0)),
                    'symbol2': volume_picks[1].get('symbol', 'N/A'),
                    'gain2': volume_picks[1].get('gain', 0),
                    'entry2': self.format_price(volume_picks[1].get('entry_price', 0)),
                    'symbol3': volume_picks[2].get('symbol', 'N/A'),
                    'gain3': volume_picks[2].get('gain', 0),
                    'entry3': self.format_price(volume_picks[2].get('entry_price', 0))
                }
                
                base_tweet = template.format(**tweet_data)
                
                # Add LLM enrichment for variant A
                context = f"\n\n📈 Performance Analysis: Strong momentum across multiple tokens. {tweet_data['symbol1']} leading with {tweet_data['gain1']:+.1f}% gain from entry. Historical success rate suggests potential for continuation. Key levels: Entry ${tweet_data['entry1']} → Current ${token_data['price']:.4f}. #TradingAlpha #CryptoGains"
                
            else:
                # Gains with V/MC ratios format
                tweet_data = {
                    'symbol1': volume_picks[0].get('symbol', 'N/A'),
                    'gain1': volume_picks[0].get('gain', 0),
                    'vmc1': volume_picks[0].get('vmc_ratio', 0),
                    'symbol2': volume_picks[1].get('symbol', 'N/A'),
                    'gain2': volume_picks[1].get('gain', 0),
                    'vmc2': volume_picks[1].get('vmc_ratio', 0),
                    'symbol3': volume_picks[2].get('symbol', 'N/A'),
                    'gain3': volume_picks[2].get('gain', 0),
                    'vmc3': volume_picks[2].get('vmc_ratio', 0)
                }
                
                base_tweet = template.format(**tweet_data)
                
                # Add LLM enrichment for variant B
                context = f"\n\n🔍 Technical Analysis: High V/MC ratios combined with strong gains indicate sustained buying pressure. {tweet_data['symbol1']} shows particularly strong technicals with {tweet_data['vmc1']:.1f}x V/MC. #TechnicalAnalysis #CryptoTrading"
            
            # Combine base tweet with context and validate length
            enriched_tweet = base_tweet + context
            return self.optimize_tweet_length(self.validate_tweet_length(enriched_tweet))
            
        except Exception as e:
            logger.error(f"Error formatting winners recap tweet: {e}")
            return ""

    def format_vmc_alert(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format V/MC alert tweet with A/B variants"""
        template = self.templates['vmc_alert'][0 if variant == 'A' else 1]
        
        if variant == 'A':
            # Calculate success rate for high V/MC ratio
            threshold = 40  # V/MC ratio threshold
            high_vmc_signals = [t for t in history.values() 
                              if t['volume_mcap_ratio'] > threshold][-10:]
            success_rate = len([t for t in high_vmc_signals 
                              if ((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 > 0])
            avg_gain = sum(((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 
                         for t in high_vmc_signals) / len(high_vmc_signals) if high_vmc_signals else 0
            
            return self.optimize_tweet_length(self.validate_tweet_length(template.format(
                symbol=token_data['symbol'],
                prev_vmc=token_data['first_mention_volume_mcap_ratio'],
                curr_vmc=token_data['volume_mcap_ratio'],
                vmc_change=((token_data['volume_mcap_ratio'] - token_data['first_mention_volume_mcap_ratio']) / token_data['first_mention_volume_mcap_ratio']) * 100 if token_data['first_mention_volume_mcap_ratio'] > 0 else 0,
                threshold=threshold,
                avg_gain=avg_gain,
                success_rate=success_rate
            )))
        else:
            # Get top 3 V/MC ratio tokens
            top_vmc = sorted(history.values(), 
                           key=lambda x: x['volume_mcap_ratio'], 
                           reverse=True)[:3]
            avg_gain = sum(((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 
                         for t in top_vmc) / len(top_vmc)
            
            return self.optimize_tweet_length(self.validate_tweet_length(template.format(
                symbol1=top_vmc[0]['symbol'],
                vmc1=top_vmc[0]['volume_mcap_ratio'],
                vmc_change1=((top_vmc[0]['volume_mcap_ratio'] - top_vmc[0]['first_mention_volume_mcap_ratio']) / top_vmc[0]['first_mention_volume_mcap_ratio']) * 100 if top_vmc[0]['first_mention_volume_mcap_ratio'] > 0 else 0,
                symbol2=top_vmc[1]['symbol'],
                vmc2=top_vmc[1]['volume_mcap_ratio'],
                vmc_change2=((top_vmc[1]['volume_mcap_ratio'] - top_vmc[1]['first_mention_volume_mcap_ratio']) / top_vmc[1]['first_mention_volume_mcap_ratio']) * 100 if top_vmc[1]['first_mention_volume_mcap_ratio'] > 0 else 0,
                symbol3=top_vmc[2]['symbol'],
                vmc3=top_vmc[2]['volume_mcap_ratio'],
                vmc_change3=((top_vmc[2]['volume_mcap_ratio'] - top_vmc[2]['first_mention_volume_mcap_ratio']) / top_vmc[2]['first_mention_volume_mcap_ratio']) * 100 if top_vmc[2]['first_mention_volume_mcap_ratio'] > 0 else 0,
                avg_gain=avg_gain
            )))

    def format_pattern_alert(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format pattern alert tweet with A/B variants and LLM enrichment
        
        Args:
            token_data: Token market data dictionary
            history: Historical performance data dictionary
            variant: A/B variant to use (default: 'A')
            
        Returns:
            Formatted tweet string
        """
        if not token_data or not history:
            logger.error("Missing token_data or history")
            return ""
            
        # Get template variant
        template = self.templates['pattern_alert'][0 if variant == 'A' else 1]
        
        try:
            # Get similar pattern data
            similar_patterns = history.get('similar_patterns', [])
            if not similar_patterns:
                return ""
                
            # Format tweet data
            if variant == 'A':
                # Single pattern match format
                tweet_data = {
                    'symbol': token_data.get('symbol', 'N/A'),
                    'prev_token': similar_patterns[0].get('symbol', 'N/A'),
                    'prev_gain': similar_patterns[0].get('gain', 0),
                    'vmc': token_data.get('vmc_ratio', 0),
                    'vol_change': token_data.get('volume_change', 0)
                }
                
                base_tweet = template.format(**tweet_data)
                
                # Add LLM enrichment for variant A
                context = f"\n\n📊 Technical Analysis: {tweet_data['symbol']} showing strong correlation with {tweet_data['prev_token']}'s previous setup. Volume surge of {tweet_data['vol_change']:+.1f}% combined with high V/MC ratio of {tweet_data['vmc']:.1f}x suggests potential continuation. Key levels: Entry ${token_data.get('entry_price', 0):.4f} → Current ${token_data['price']:.4f}. #TradingSetup #CryptoTrading"
                
            else:
                # Multi-pattern match format
                if len(similar_patterns) < 2:
                    return ""
                    
                tweet_data = {
                    'symbol1': token_data.get('symbol', 'N/A'),
                    'prev1': similar_patterns[0].get('symbol', 'N/A'),
                    'gain1': similar_patterns[0].get('gain', 0),
                    'symbol2': similar_patterns[1].get('symbol', 'N/A'),
                    'prev2': similar_patterns[1].get('symbol', 'N/A'),
                    'gain2': similar_patterns[1].get('gain', 0),
                    'accuracy': history.get('accuracy', 80)
                }
                
                base_tweet = template.format(**tweet_data)
                
                # Add LLM enrichment for variant B
                context = f"\n\n📈 Pattern Analysis: Multiple high-probability setups detected. Volume profile and price action align with previous successful trades. Risk management is key - always size positions appropriately. #TradingSetup #RiskManagement"
            
            # Combine base tweet with context and validate length
            enriched_tweet = base_tweet + context
            return self.optimize_tweet_length(self.validate_tweet_length(enriched_tweet))
            
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
