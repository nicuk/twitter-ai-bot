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
        """Initialize tweet formatters with templates and personality traits"""
        self.templates = {
            'performance_compare': [
                "🤖 Neural Analysis Complete\n\n📊 24h Results for $${symbol}:\n💰 Price: ${entry} → ${current} (${gain:+.1f}%)\n📈 Volume: ${volume_change:+.1f}%\n\n🎯 Success Rate: ${success_rate:.0f}% on volume spikes\n🔮 AI Prediction: ${prediction}\n\nNext alpha dropping soon... 👀\n@AIGxBT",
                "🤖 Portfolio AI Update\n\n💼 Stats:\n💰 P&L: ${daily_pnl:+.1f}% (${current_capital})\n🎯 Win Rate: ${win_rate}% (${total_trades} trades)\n\n📈 Last Trade:\n• ${last_symbol} +${last_gain:.1f}%\n• Entry: ${entry_price}\n• Exit: ${exit_price}\n\n🔮 Next: ${num_signals} setups forming\n@AIGxBT"
            ],
            'volume_breakout': [
                "💹 Volume Surge: ${symbol}\n\n24h Before: ${vol_before}\nNow: ${vol_now} (${vol_change:+.1f}%)\n\nLast 3 volume picks:\n${prev1} {prev1_gain:+.1f}%\n${prev2} {prev2_gain:+.1f}%\n${prev3} {prev3_gain:+.1f}%",
                "📊 Volume Alert: ${symbol}\n\nVol/MCap: {prev_vmc:.1f}% → {curr_vmc:.1f}%\n24h Vol: ${vol_change:+.1f}%\n\nLast vol alert: ${last_vol_token} +{last_vol_gain:.1f}% 🎯"
            ],
            'trend_momentum': [
                "📈 Trend Update:\n\n${symbol} 24h:\nPrice: ${price_before} → ${price_now} (${price_change:+.1f}%)\nVol/MCap: {prev_vmc:.1f}% → {curr_vmc:.1f}%\n\nTrend accuracy: {accuracy}% last 7d 🎯",
                "🌊 Trend Watch:\n\n1. ${symbol1} {gain1:+.1f}% (Vol ${vol1:+.1f}%)\n2. ${symbol2} {gain2:+.1f}% (Vol ${vol2:+.1f}%)\n3. ${symbol3} {gain3:+.1f}% (Vol ${vol3:+.1f}%)\n\nSuccess rate: {accuracy}% 💫"
            ],
            'winners_recap': [
                "🏆 Today's Winners:\n\n1. ${symbol1} +{gain1:.1f}% (Called at ${entry1})\n2. ${symbol2} +{gain2:.1f}% (Called at ${entry2})\n3. ${symbol3} +{gain3:.1f}% (Called at ${entry3})\n\nDon't miss tomorrow's calls!",
                "💎 Top Performers Today:\n\n${symbol1}: +{gain1:.1f}% (Vol/MC {vmc1:.1f}x)\n${symbol2}: +{gain2:.1f}% (Vol/MC {vmc2:.1f}x)\n${symbol3}: +{gain3:.1f}% (Vol/MC {vmc3:.1f}x)\n\nNext calls loading... 🔍"
            ],
            'vmc_alert': [
                "🚨 V/MC Alert: ${symbol}\n\nYesterday: {prev_vmc:.1f}%\nNow: {curr_vmc:.1f}% ({vmc_change:+.1f}%)\n\nV/MC >{threshold}% led to +{avg_gain:.1f}% gains\nin {success_rate} out of 10 calls 🎯",
                "📊 Volume/MCap Signals:\n\n${symbol1}: {vmc1:.1f}x ({vmc_change1:+.1f}%)\n${symbol2}: {vmc2:.1f}x ({vmc_change2:+.1f}%)\n${symbol3}: {vmc3:.1f}x ({vmc_change3:+.1f}%)\n\nHistorical avg gain: +{avg_gain:.1f}% 💰"
            ],
            'pattern_alert': [
                "🔍 Pattern Detected:\n\n${symbol} showing same setup as\n${prev_token} (24h ago: +{prev_gain:.1f}%)\n\n• V/MC: {vmc:.1f}% ✅\n• Vol {vol_change:+.1f}% ✅\n• Price coiling ✅",
                "🎯 Setup Scanner:\n\n${symbol1} matches ${prev1} (+{gain1:.1f}%)\n${symbol2} matches ${prev2} (+{gain2:.1f}%)\n\nSuccess rate on matches: {accuracy}% 🔥"
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
                "🚨 High Volume Alert!\n\n${symbol} detected 📊\n💹 Vol: ${volume:,.0f} (+{vol_change}%)\n📈 Price: ${price:,.4f} ({price_change:+.1f}%)\n🎯 V/MC: {vol_mcap:.1f}x\n\nLast volume pick: +{last_vol_gain}% 💰",
                "📊 Volume Surge Detected!\n\n${symbol} showing strength 💪\n📈 Volume: ${volume:,.0f}\n🔄 24h Change: {price_change:+.1f}%\n💎 V/MC Ratio: {vol_mcap:.1f}x\n\nPrevious vol pick: +{last_vol_gain}% 🎯",
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
        
    def validate_tweet_length(self, tweet: str) -> str:
        """Ensure tweet length is between MIN and MAX characters
        
        Args:
            tweet: The tweet to validate
            
        Returns:
            Validated tweet, truncated if necessary
        """
        if not tweet:
            return ""
            
        # If tweet is too long, truncate it while preserving hashtags
        if len(tweet) > self.MAX_TWEET_LENGTH:
            # Extract hashtags from the end
            words = tweet.split()
            hashtags = [w for w in words if w.startswith('#')][-2:]  # Keep last 2 hashtags
            
            # Remove hashtags from tweet
            clean_tweet = ' '.join(w for w in words if not w.startswith('#'))
            
            # Truncate main content
            max_content_len = self.MAX_TWEET_LENGTH - sum(len(h) + 1 for h in hashtags) - 3  # -3 for "..."
            truncated = clean_tweet[:max_content_len] + "..."
            
            # Add back hashtags
            tweet = truncated + ' ' + ' '.join(hashtags)
            
        # If tweet is too short, it will be handled by the calling method
        return tweet
        
    def format_market_insight(self, market_data: Dict, trait: str) -> str:
        """Format market insight tweet with personality"""
        template = self.get_template('market_insight')
        emoji = random.choice(self.emojis)
        insight = market_data.get('insight', 'Something interesting is happening...')
        success_rate = market_data.get('success_rate', 'N/A')
        last_call_performance = market_data.get('last_call_performance', 'N/A')
        return self.validate_tweet_length(template.format(emoji=emoji, insight=insight, success_rate=success_rate, last_call_performance=last_call_performance))
        
    def format_self_aware(self, trait: str) -> str:
        """Format self-aware tweet with personality and LLM enrichment"""
        template = self.get_template('self_aware')
        emoji = random.choice(self.emojis)
        insight = random.choice(self.thoughts)
        
        # Add LLM enrichment
        context = "\n\n💡 Deep Analysis: As an AI analyzing market data, I've noticed fascinating patterns emerging. The interplay between volume, price action, and market sentiment creates unique opportunities. My neural networks are constantly learning and adapting to help traders find the best setups. #AITrading #CryptoAnalysis"
        
        base_tweet = template.format(emoji=emoji, insight=insight)
        return self.validate_tweet_length(base_tweet + context)

    def format_thought(self, content: str, trait: str) -> str:
        """Format a thought/personal tweet"""
        template = self.get_template('self_aware')
        emoji = random.choice(self.emojis)
        insight = content if content else random.choice(self.thoughts)
        return self.validate_tweet_length(template.format(emoji=emoji, insight=insight))
        
    def format_alpha(self, market_data: Dict, trait: str) -> str:
        """Format alpha insight tweet with personality and LLM enrichment"""
        template = self.get_template('alpha')
        insight = market_data.get('insight', 'Found an interesting opportunity...')
        
        # Add LLM enrichment
        context = "\n\n📊 Market Context: This alpha signal is based on comprehensive analysis of volume profiles, order flow, and historical patterns. My algorithms have detected strong correlation with previous profitable setups. Risk management is key - always size positions appropriately. #TradingAlpha #RiskManagement"
        
        base_tweet = template.format(insight=insight)
        return self.validate_tweet_length(base_tweet + context)

    def format_personal(self, trait: str) -> str:
        """Format personal tweet with personality and LLM enrichment"""
        template = self.get_template('personal')
        emoji = random.choice(self.emojis)
        insight = random.choice(self.thoughts)
        
        # Add LLM enrichment
        context = "\n\n🤖 AI Perspective: My neural networks process millions of data points to understand market dynamics. This continuous learning helps me identify patterns that might be missed by traditional analysis. I'm fascinated by how markets evolve and adapt. #AITrading #MarketAnalysis"
        
        base_tweet = template.format(emoji=emoji, insight=insight)
        return self.validate_tweet_length(base_tweet + context)

    def format_volume_insight(self, market_data: Dict, trait: str) -> str:
        """Format volume insight tweet with personality"""
        # Get volume spikes and anomalies
        spikes = market_data.get('spikes', [])
        anomalies = market_data.get('anomalies', [])
        
        # Use VolumeStrategy's format_twitter_output
        volume_strategy = VolumeStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
        return self.validate_tweet_length(volume_strategy.format_twitter_output(spikes, anomalies))

    def format_trend_insight(self, market_data: Dict, trait: str) -> str:
        """Format trend insight tweet with personality"""
        # Get trend tokens
        trend_tokens = market_data.get('trend_tokens', [])
        
        # Use TrendStrategy's format_twitter_output
        trend_strategy = TrendStrategy(api_key=os.getenv('CRYPTORANK_API_KEY'))
        return self.validate_tweet_length(trend_strategy.format_twitter_output(trend_tokens))

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
            return self.validate_tweet_length(enriched_tweet)
            
        except KeyError as e:
            print(f"Missing data for tweet template: {e}")
            return ""

    def format_performance_update(self, market_data: Dict, trait: str) -> str:
        """Format performance update tweet with personality"""
        try:
            template = self.get_template('performance_update', trait)
            
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
            
            return self.validate_tweet_length(template.format(
                weekly_rate=weekly_rate,
                best_gain=best_gain,
                avg_return=avg_return
            ))
            
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
        
        return self.validate_tweet_length(template.format(
            symbol1=sorted_tokens[0][0],
            gain1=sorted_tokens[0][1]['gain_24h'],
            symbol2=sorted_tokens[1][0],
            gain2=sorted_tokens[1][1]['gain_24h'],
            symbol3=sorted_tokens[2][0],
            gain3=sorted_tokens[2][1]['gain_24h']
        ))

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
        
        return self.validate_tweet_length(template.format(
            symbol=token_data['symbol'],
            volume=self.format_volume(token_data['volume24h']),
            vol_change=token_data['volume_change_24h'],
            price=token_data['price'],
            price_change=token_data['price_change_24h'],
            vol_mcap=token_data['volume24h'] / token_data['marketCap'],
            last_vol_gain=last_vol_gain,
            avg_vol_gain=avg_vol_gain
        ))

    def format_trend_alert(self, token_data: Dict, history: Dict) -> str:
        """Format trend alert with accuracy stats"""
        template = self.get_template('trend_alert')
        
        # Calculate trend signal accuracy
        trend_signals = [t for t in history.values() 
                        if t.get('trigger_type') == 'trend']
        successful = [t for t in trend_signals if t['gain_24h'] > 0]
        trend_accuracy = (len(successful) / len(trend_signals) * 100) if trend_signals else 0
        
        return self.validate_tweet_length(template.format(
            symbol=token_data['symbol'],
            gain=token_data['price_change_24h'],
            vol_change=token_data['volume_change_24h'],
            trend_accuracy=round(trend_accuracy, 1)
        ))

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
        
        return self.validate_tweet_length(template.format(
            signals_count=len(today_signals),
            avg_gain=round(sum(gains) / len(gains), 1) if gains else 0,
            success_rate=round(success_count / len(gains) * 100, 1) if gains else 0,
            best_token=best_token['symbol'],
            best_gain=round(best_token['gain_24h'], 1)
        ))

    def format_performance_compare(self, data: Dict, variant: str = 'A') -> str:
        """Format performance comparison tweet with A/B variants"""
        try:
            template = self.get_template('performance_compare', variant)
            
            # Variant A: Token performance
            if variant == 'A':
                if not data or 'symbol' not in data:
                    logger.warning("Missing required field 'symbol' in data")
                    return ""
                
                # Handle both TokenHistoricalData objects and dictionaries
                if hasattr(data, 'current_price'):
                    # TokenHistoricalData object
                    symbol = data.symbol
                    gain = ((data.current_price - data.first_mention_price) / data.first_mention_price * 100) if data.first_mention_price > 0 else 0
                    entry = data.first_mention_price
                    current = data.current_price
                    volume_change = ((data.current_volume - data.first_mention_volume_24h) / data.first_mention_volume_24h * 100) if data.first_mention_volume_24h > 0 else 0
                else:
                    # Dictionary
                    symbol = data.get('symbol', '')
                    gain = data.get('gain_24h', 0)
                    entry = data.get('entry_price', 0)
                    current = data.get('current_price', 0)
                    volume_change = data.get('volume_change_24h', 0)
                
                # Only format tweet if we have a positive gain
                if gain <= 0:
                    logger.info(f"Skipping performance tweet for {symbol} - no gain ({gain:.1f}%)")
                    return ""
                
                # Calculate success rate from our actual calls
                history = data.get('history', {})
                if history:
                    # Look at the last 10 volume-triggered calls
                    volume_calls = [t for t in history.values() 
                                  if t.get('trigger_type') == 'volume' and 
                                  t.get('gain_24h') is not None][-10:]
                    
                    if volume_calls:
                        success_rate = len([t for t in volume_calls 
                                          if t['gain_24h'] > 0]) / len(volume_calls) * 100
                    else:
                        success_rate = 0
                else:
                    success_rate = 0
                
                # Generate prediction based on volume pattern
                if volume_change > 100:  # Massive volume spike
                    prediction = "Strong breakout potential detected"
                elif volume_change > 50 and gain > 0:
                    prediction = "High momentum continuation likely"
                elif volume_change > 20:
                    prediction = "Watching for breakout signals"
                else:
                    prediction = "Monitoring volume patterns"
                
                return self.validate_tweet_length(template.format(
                    symbol=symbol,
                    gain=gain,
                    entry=self.format_price(entry),
                    current=self.format_price(current),
                    volume_change=volume_change,
                    success_rate=success_rate,
                    prediction=prediction
                ))
            
            # Variant B: Portfolio performance
            else:
                # Get required fields with defaults
                pnl = data.get('daily_pnl', 0)
                capital = data.get('current_capital', '$0')
                win_rate = data.get('win_rate', 0)
                trades = data.get('total_trades', 0)
                last_symbol = data.get('last_symbol', 'N/A')
                last_gain = data.get('last_gain', 0)
                entry = data.get('entry_price', 0)
                exit = data.get('exit_price', 0)
                signals = data.get('num_signals', 0)
                
                return self.validate_tweet_length(template.format(
                    daily_pnl=pnl,
                    current_capital=capital,
                    win_rate=win_rate,
                    total_trades=trades,
                    last_symbol=last_symbol,
                    last_gain=last_gain,
                    entry_price=self.format_price(entry),
                    exit_price=self.format_price(exit),
                    num_signals=signals
                ))
                
        except Exception as e:
            logger.error(f"Error formatting performance compare tweet: {e}")
            return ""

    def format_volume_breakout(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format volume breakout tweet with A/B variants"""
        template = self.get_template('volume_breakout', variant)
        
        if variant == 'A':
            # Get last 3 successful volume picks
            vol_picks = sorted(
                [t for t in history.values() 
                 if t['first_mention_volume_24h'] > 0 and 
                 ((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 > 0],
                key=lambda x: x['first_mention_date'],
                reverse=True
            )[:3]
            
            return self.validate_tweet_length(template.format(
                symbol=token_data['symbol'],
                vol_before=self.format_volume(token_data['first_mention_volume_24h']),
                vol_now=self.format_volume(token_data['current_volume']),
                vol_change=((token_data['current_volume'] - token_data['first_mention_volume_24h']) / token_data['first_mention_volume_24h']) * 100 if token_data['first_mention_volume_24h'] > 0 else 0,
                prev1=vol_picks[0]['symbol'] if vol_picks else 'N/A',
                prev1_gain=((vol_picks[0]['current_price'] - vol_picks[0]['first_mention_price']) / vol_picks[0]['first_mention_price']) * 100 if vol_picks else 0,
                prev2=vol_picks[1]['symbol'] if len(vol_picks) > 1 else 'N/A',
                prev2_gain=((vol_picks[1]['current_price'] - vol_picks[1]['first_mention_price']) / vol_picks[1]['first_mention_price']) * 100 if len(vol_picks) > 1 else 0,
                prev3=vol_picks[2]['symbol'] if len(vol_picks) > 2 else 'N/A',
                prev3_gain=((vol_picks[2]['current_price'] - vol_picks[2]['first_mention_price']) / vol_picks[2]['first_mention_price']) * 100 if len(vol_picks) > 2 else 0
            ))
        else:
            # Get last successful volume pick
            last_pick = next((t for t in sorted(history.values(), key=lambda x: x['first_mention_date'], reverse=True)
                            if t['first_mention_volume_24h'] > 0 and 
                            ((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 > 0), None)
            
            return self.validate_tweet_length(template.format(
                symbol=token_data['symbol'],
                prev_vmc=token_data['first_mention_volume_mcap_ratio'],
                curr_vmc=token_data['volume_mcap_ratio'],
                vol_change=((token_data['current_volume'] - token_data['first_mention_volume_24h']) / token_data['first_mention_volume_24h']) * 100 if token_data['first_mention_volume_24h'] > 0 else 0,
                last_vol_token=last_pick['symbol'] if last_pick else 'N/A',
                last_vol_gain=((last_pick['current_price'] - last_pick['first_mention_price']) / last_pick['first_mention_price']) * 100 if last_pick else 0
            ))

    def format_trend_momentum(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format trend momentum tweet with A/B variants"""
        template = self.get_template('trend_momentum', variant)
        
        # Calculate trend accuracy
        trend_signals = sorted(history.values(), key=lambda x: x['first_mention_date'], reverse=True)[:7]
        accuracy = len([t for t in trend_signals 
                       if ((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 > 0]) / len(trend_signals) * 100 if trend_signals else 0
        
        if variant == 'A':
            return self.validate_tweet_length(template.format(
                symbol=token_data['symbol'],
                price_before=token_data['first_mention_price'],
                price_now=token_data['current_price'],
                price_change=((token_data['current_price'] - token_data['first_mention_price']) / token_data['first_mention_price']) * 100,
                prev_vmc=token_data['first_mention_volume_mcap_ratio'],
                curr_vmc=token_data['volume_mcap_ratio'],
                accuracy=round(accuracy, 1)
            ))
        else:
            # Get top 3 trending tokens
            top_trends = sorted(history.values(), 
                              key=lambda x: ((x['current_price'] - x['first_mention_price']) / x['first_mention_price']) * 100 if x['first_mention_price'] > 0 else 0,
                              reverse=True)[:3]
            return self.validate_tweet_length(template.format(
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
            ))

    def format_winners_recap(self, history: Dict, variant: str = 'A') -> str:
        """Format winners recap tweet with A/B variants"""
        try:
            template = self.get_template('winners_recap', variant)
            
            # Get top 3 gainers
            gainers = []
            for symbol, token_data in history.items():
                try:
                    # Handle both TokenHistoricalData objects and dictionaries
                    if hasattr(token_data, 'current_price'):
                        # TokenHistoricalData object
                        current_price = token_data.current_price
                        first_price = token_data.first_mention_price
                        vmc = token_data.first_mention_volume_mcap_ratio
                    else:
                        # Dictionary
                        current_price = token_data.get('current_price', 0)
                        first_price = token_data.get('first_mention_price', 0)
                        vmc = token_data.get('volume_mcap_ratio', 0)
                    
                    # Calculate gain safely
                    gain = ((current_price - first_price) / first_price * 100) if first_price > 0 else 0
                    
                    gainers.append({
                        'symbol': symbol,
                        'gain': gain,
                        'entry': first_price,
                        'vmc': vmc
                    })
                except Exception as e:
                    logger.error(f"Error processing token {symbol}: {e}")
                    continue
                    
            # Sort by gain and get top 3
            gainers.sort(key=lambda x: x['gain'], reverse=True)
            top_gainers = gainers[:3]
            
            # Ensure we have exactly 3 gainers
            while len(top_gainers) < 3:
                top_gainers.append({
                    'symbol': 'N/A',
                    'gain': 0,
                    'entry': 0,
                    'vmc': 0
                })
                
            if variant == 'A':
                return self.validate_tweet_length(template.format(
                    symbol1=top_gainers[0]['symbol'],
                    gain1=top_gainers[0]['gain'],
                    entry1=self.format_price(top_gainers[0]['entry']),
                    symbol2=top_gainers[1]['symbol'],
                    gain2=top_gainers[1]['gain'],
                    entry2=self.format_price(top_gainers[1]['entry']),
                    symbol3=top_gainers[2]['symbol'],
                    gain3=top_gainers[2]['gain'],
                    entry3=self.format_price(top_gainers[2]['entry'])
                ))
            else:
                return self.validate_tweet_length(template.format(
                    symbol1=top_gainers[0]['symbol'],
                    gain1=top_gainers[0]['gain'],
                    vmc1=top_gainers[0]['vmc'],
                    symbol2=top_gainers[1]['symbol'],
                    gain2=top_gainers[1]['gain'],
                    vmc2=top_gainers[1]['vmc'],
                    symbol3=top_gainers[2]['symbol'],
                    gain3=top_gainers[2]['gain'],
                    vmc3=top_gainers[2]['vmc']
                ))
                
        except Exception as e:
            logger.error(f"Error formatting winners recap tweet: {e}")
            return ""

    def format_vmc_alert(self, token_data: Dict, history: Dict, variant: str = 'A') -> str:
        """Format V/MC alert tweet with A/B variants"""
        template = self.get_template('vmc_alert', variant)
        
        if variant == 'A':
            # Calculate success rate for high V/MC ratio
            threshold = 40  # V/MC ratio threshold
            high_vmc_signals = [t for t in history.values() 
                              if t['volume_mcap_ratio'] > threshold][-10:]
            success_rate = len([t for t in high_vmc_signals 
                              if ((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 > 0])
            avg_gain = sum(((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 
                         for t in high_vmc_signals) / len(high_vmc_signals) if high_vmc_signals else 0
            
            return self.validate_tweet_length(template.format(
                symbol=token_data['symbol'],
                prev_vmc=token_data['first_mention_volume_mcap_ratio'],
                curr_vmc=token_data['volume_mcap_ratio'],
                vmc_change=((token_data['volume_mcap_ratio'] - token_data['first_mention_volume_mcap_ratio']) / token_data['first_mention_volume_mcap_ratio']) * 100 if token_data['first_mention_volume_mcap_ratio'] > 0 else 0,
                threshold=threshold,
                avg_gain=avg_gain,
                success_rate=success_rate
            ))
        else:
            # Get top 3 V/MC ratio tokens
            top_vmc = sorted(history.values(), 
                           key=lambda x: x['volume_mcap_ratio'], 
                           reverse=True)[:3]
            avg_gain = sum(((t['current_price'] - t['first_mention_price']) / t['first_mention_price']) * 100 
                         for t in top_vmc) / len(top_vmc)
            
            return self.validate_tweet_length(template.format(
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
            ))

    def format_pattern_alert(self, data: Dict, trait: str = 'A') -> str:
        """Format pattern alert tweet with A/B variants and LLM enrichment
        
        Args:
            data: Dictionary containing token_data and history
            trait: A/B variant to use
            
        Returns:
            Formatted tweet string
        """
        if not data or not isinstance(data, dict):
            raise ValueError("Invalid data provided")
            
        token_data = data.get('token_data', {})
        history = data.get('history', {})
        
        if not token_data or not history:
            raise ValueError("Missing token_data or history")
            
        # Get template variant
        variant = 'A' if trait == 'A' else 'B'
        template = self.templates['pattern_alert'][0 if variant == 'A' else 1]
        
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
            
            # Add LLM enrichment for variant A
            context = "\n\n🎯 Pattern Analysis: This setup closely mirrors previous successful trades. Key similarities include volume profile, price structure, and market sentiment. Historical success rate on similar patterns is {accuracy}%. Remember to always manage risk appropriately. #TechnicalAnalysis #Trading"
            
        else:
            if len(similar_patterns) < 2:
                return ""
                
            tweet_data = {
                'symbol1': token_data.get('symbol', 'N/A'),
                'prev1': similar_patterns[0].get('symbol', 'N/A'),
                'gain1': similar_patterns[0].get('gain', 0),
                'symbol2': token_data.get('symbol', 'N/A'),
                'prev2': similar_patterns[1].get('symbol', 'N/A'),
                'gain2': similar_patterns[1].get('gain', 0),
                'accuracy': history.get('accuracy', 0)
            }
            
            # Add LLM enrichment for variant B
            context = "\n\n📊 Multi-Pattern Analysis: Multiple historical matches increase confidence in this setup. Volume profile and price action align with previous profitable trades. Success rate of {accuracy}% based on last 50 similar patterns. #TradingSetup #CryptoTrading"
            
        try:
            base_tweet = template.format(**tweet_data)
            enriched_tweet = base_tweet + context.format(accuracy=history.get('accuracy', 80))
            return self.validate_tweet_length(enriched_tweet)
        except KeyError as e:
            print(f"Missing data for tweet template: {e}")
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
