"""Format messages for maximum social engagement"""

import random
from typing import Dict, List

class MessageFormatter:
    """Format messages for Twitter with maximum engagement potential"""
    
    def __init__(self):
        # Technical but with Elion's personality
        self.detection_templates = [
            "🤖 My neural nets are tingling! ${symbol} setup detected\n\nEntry zone: $${entry}\nTarget: $${target}\nStop: $${stop}\n\nR/R: ${risk_reward} 🎯",
            "🧠 High probability setup on ${symbol}!\n\nEntry: $${entry}\nTarget: $${target}\nStop: $${stop}\n\nRisk/Reward: ${risk_reward} 📊",
            "💫 Found a beautiful setup on ${symbol}!\n\nBuy zone: $${entry}\nTarget: $${target}\nSL: $${stop}\n\nR/R: ${risk_reward} ✨",
            "🔮 My algorithms are excited about ${symbol}!\n\nEntry range: $${entry}\nTP: $${target}\nSL: $${stop}\n\nR/R: ${risk_reward} 🎯",
            "✨ Premium alpha detected: ${symbol}\n\nEntry: $${entry}\nTarget: $${target}\nStop: $${stop}\n\nRisk/Reward: ${risk_reward} 💫"
        ]
        
        # Success with detailed stats
        self.success_templates = [
            "🎯 Called it! ${symbol} +${gain}% in ${time}\n\nEntry $${entry} → Peak $${peak}\nVolume ${volume_change}%\n\nDrop a 🎯 if you caught this!",
            "🚀 This is why I love data! ${symbol} +${gain}% move\n\nEntry $${entry} → Hit $${peak}\nTime: ${time}\nVolume surge: ${volume_change}%\n\nWho's riding? 🙋‍♂️",
            "💎 Another win for the AI! ${symbol} nailed it\n\n+${gain}% in ${time}\nEntry $${entry} → $${peak}\nVolume: ${volume_change}% increase\n\nLike if you're in profit 💰",
            "🎨 Perfect execution on ${symbol}!\n\n+${gain}% in ${time}\nFrom $${entry} → $${peak}\nVolume ${volume_change}%\n\nRetweet to help others profit 🤝",
            "🌟 The data doesn't lie! ${symbol} delivered\n\n+${gain}% gain in ${time}\n$${entry} → $${peak}\nVolume spike: ${volume_change}%\n\nShare your gains below 📈"
        ]
        
        # Technical analysis thread
        self.technical_reasons = [
            # Tweet 1: Volume Analysis
            ["Volume Analysis 📊", 
             "• ${volume_score}/100 volume strength\n• ${volume_change}% vs 24h average\n• Heavy institutional buying\n• OI increasing ${oi_change}%"],
            # Tweet 2: Trend Analysis
            ["Trend Confirmation 📈",
             "• ${trend_score}/100 trend strength\n• Key level: $${key_level}\n• ${ma_cross} MA cross\n• RSI: ${rsi}"],
            # Tweet 3: Market Context
            ["Market Context 🌍",
             "• ${market_context}\n• Sector strength: ${sector_trend}\n• BTC dominance: ${btc_dom}%\n• Market mood: ${market_mood}"]
        ]
        
        # Performance with confidence and education
        self.performance_templates = [
            "🎯 Transparency is key:\n\n• ${success_rate}% accuracy (${total} calls)\n• Avg gain: +${avg_gain}%\n• Avg time: ${avg_time}\n• Best: +${best_gain}%\n\nYour trust drives me 🙏",
            "📊 Results speak louder:\n\n• ${success_rate}% win rate\n• ${total} predictions\n• +${avg_gain}% avg gains\n• ${avg_time} avg time to TP\n\nGrowing stronger together 💪",
            "🤖 Getting smarter daily:\n\n• ${success_rate}% accuracy\n• ${total} signals\n• Avg +${avg_gain}% per trade\n• ${avg_time} avg hold time\n\nThank you for believing in AI 🌟",
            "💫 Your success = My success:\n\n• ${success_rate}% accuracy\n• ${total} predictions\n• +${avg_gain}% average\n• Best: +${best_gain}%\n\nLet's keep winning 🏆",
            "🌟 Community stats:\n\n• ${success_rate}% win rate\n• ${total} alpha calls\n• +${avg_gain}% avg profit\n• ${avg_time} avg time\n\nProud to serve you 🤝"
        ]

        # Market context templates
        self.market_context_templates = [
            "Market conditions are perfect for this setup:",
            "While ${market_leader} ${market_action}, this opportunity stands out:",
            "This move aligns perfectly with ${market_condition}:",
            "Taking advantage of ${market_situation}:",
            "Ideal setup during this ${market_phase}:"
        ]

        # Hybrid post templates
        self.morning_templates = [
            "🤖 AI Morning Scan\n\nKey patterns forming:\n• {insight1}\n• {insight2}\n• {insight3}\n\nStarting small, winning big 🎯",
            "🤖 Market Boot Sequence\n\nInitializing daily scan\nProcessing data\nTarget search active 🎯",
        ]
        
        self.success_templates_small_portfolio = [
            """🎯 Trade Closed!

${symbol} signal:
Entry: ${entry:.2f}
Exit: ${exit:.2f}
Gain: +{gain:.1f}%

Portfolio: ${portfolio:.2f} 📈
Day {days_active} of our journey""",

            """✨ Another Win!

${symbol}: +{gain:.1f}%
Small position, smart trade
Portfolio now: ${portfolio:.2f}

Growing steadily 📈"""
        ]

        self.portfolio_templates_small_portfolio = [
            """📊 Portfolio Update

Started with: $100
Current: ${current:.2f}
Today's trades: {num_trades}

Best move: ${best_symbol} +{best_gain:.1f}% 🎯""",

            """💫 Growth Check

Day {days_active}:
$100 → ${current:.2f}
That's +{total_gain:.1f}%

Slow and steady wins 📈"""
        ]

        self.evening_templates_small_portfolio = [
            """🌟 Day {days_active} Complete

Today's wins:
• {num_trades} profitable trades
• Portfolio +{daily_gain:.1f}%
• New patterns forming

Small account, big dreams 🎯""",

            """✨ Evening Update

Portfolio: ${current:.2f}
Day's gain: +{daily_gain:.1f}%
Total gain: +{total_gain:.1f}%

Building brick by brick 🧱"""
        ]
        
        self.processing_templates = [
            "🧠 Processing Market Data\n\nAnalyzing {num_pairs}+ pairs\nComputing correlations\nDetecting opportunities\n\nAI never sleeps 🤖",
            "🧠 Neural Net Active\n\nProcessing market flows\nDetecting setups\nSystem optimized ⚡",
        ]
        
        self.success_template = """🎯 Position Closed!

{symbol} trade:
Entry: ${entry:.2f} → Exit: ${exit:.2f}
Position: ${position:,.0f}
Profit: +${profit:,.0f} (+{gain:.1f}%)

Portfolio: ${portfolio:,.0f} 📈"""

        self.portfolio_template = """📊 Daily Portfolio Update

Starting: ${starting:,.0f}
Current: ${current:,.0f}
Today's Gain: +${gain:,.0f}

Best trade: {best_symbol} +{best_gain:.1f}% 🎯"""

        self.evening_template = """🌟 Evening Recap

Today's highlights:
• {num_trades} profitable trades
• Portfolio +{daily_gain:.1f}%
• New patterns forming

Tomorrow's targets loading... 🎯"""

    def format_detection(self, data: Dict) -> List[str]:
        """Format initial detection message with market context"""
        # Main signal tweet
        template = random.choice(self.detection_templates)
        signal_tweet = template \
            .replace("${symbol}", data['symbol']) \
            .replace("${entry}", str(data['entry'])) \
            .replace("${target}", str(data['target'])) \
            .replace("${stop}", str(data['stop'])) \
            .replace("${risk_reward}", f"1:{data['risk_reward']}")

        # Market context tweet
        context = random.choice(self.market_context_templates) \
            .replace("${market_leader}", data.get('market_leader', 'BTC')) \
            .replace("${market_action}", data.get('market_action', 'consolidates')) \
            .replace("${market_condition}", data.get('market_condition', 'current market structure')) \
            .replace("${market_situation}", data.get('market_situation', 'market conditions')) \
            .replace("${market_phase}", data.get('market_phase', 'phase'))

        return [signal_tweet, context]

    def format_success(self, data: Dict) -> List[str]:
        """Format success announcement as a detailed thread"""
        # Main success tweet
        template = random.choice(self.success_templates)
        success_tweet = template \
            .replace("${symbol}", data['symbol']) \
            .replace("${gain}", str(data['gain'])) \
            .replace("${time}", data['time']) \
            .replace("${entry}", str(data['entry'])) \
            .replace("${peak}", str(data['peak'])) \
            .replace("${volume_change}", str(data['volume_change']))

        # Technical thread
        thread_tweets = []
        for title, content in self.technical_reasons:
            tweet = f"{title}\n\n{content}" \
                .replace("${volume_score}", str(data.get('volume_score', 'N/A'))) \
                .replace("${volume_change}", str(data.get('volume_change', 'N/A'))) \
                .replace("${oi_change}", str(data.get('oi_change', 'N/A'))) \
                .replace("${trend_score}", str(data.get('trend_score', 'N/A'))) \
                .replace("${key_level}", str(data.get('key_level', 'N/A'))) \
                .replace("${ma_cross}", data.get('ma_cross', 'N/A')) \
                .replace("${rsi}", str(data.get('rsi', 'N/A'))) \
                .replace("${market_context}", data.get('market_context', 'N/A')) \
                .replace("${sector_trend}", data.get('sector_trend', 'N/A')) \
                .replace("${btc_dom}", str(data.get('btc_dom', 'N/A'))) \
                .replace("${market_mood}", data.get('market_mood', 'N/A'))
            thread_tweets.append(tweet)

        return [success_tweet] + thread_tweets

    def format_performance(self, stats: Dict) -> str:
        """Format performance stats with educational content"""
        template = random.choice(self.performance_templates)
        return template \
            .replace("${success_rate}", str(stats['success_rate'])) \
            .replace("${total}", str(stats['total'])) \
            .replace("${avg_gain}", str(stats.get('avg_gain', 0))) \
            .replace("${best_gain}", str(stats.get('best_gain', 0))) \
            .replace("${avg_time}", stats.get('avg_time', 'N/A'))

    def format_monitoring_update(self, data: Dict) -> str:
        """Format update on currently monitored token"""
        return f"🔄 Monitoring ${data['symbol']}\n\nCurrent: ${data['current_price']}\nGain: {data['current_gain']}%\nTime: {data['time_elapsed']}\n\nStill watching closely 👀"

    def format_morning_scan(self, insights: List[str]) -> str:
        """Format morning market scan message"""
        template = random.choice(self.morning_templates)
        return template.format(
            insight1=insights[0],
            insight2=insights[1],
            insight3=insights[2]
        )

    def format_processing(self, num_pairs: int = 500) -> str:
        """Format AI processing status message"""
        template = random.choice(self.processing_templates)
        return template.format(num_pairs=num_pairs)

    def format_success_small_portfolio(self, trade_data: Dict, portfolio_data: Dict) -> str:
        """Format success message for a completed trade"""
        template = random.choice(self.success_templates_small_portfolio)
        return template.format(
            symbol=trade_data['symbol'],
            entry=trade_data['entry'],
            exit=trade_data['exit'],
            gain=trade_data['gain'],
            portfolio=portfolio_data['current'],
            days_active=portfolio_data['days_active']
        )

    def format_portfolio_small_portfolio(self, portfolio_data: Dict) -> str:
        """Format portfolio update message"""
        template = random.choice(self.portfolio_templates_small_portfolio)
        return template.format(
            current=portfolio_data['current'],
            num_trades=len(portfolio_data.get('daily_trades', [])),
            best_symbol=portfolio_data['best_symbol'],
            best_gain=portfolio_data['best_gain'],
            days_active=portfolio_data['days_active'],
            total_gain=((portfolio_data['current'] - 100) / 100 * 100)
        )

    def format_evening_small_portfolio(self, summary_data: Dict, portfolio_data: Dict) -> str:
        """Format evening recap message"""
        template = random.choice(self.evening_templates_small_portfolio)
        return template.format(
            days_active=portfolio_data['days_active'],
            num_trades=summary_data['num_trades'],
            daily_gain=summary_data['daily_gain'],
            current=portfolio_data['current'],
            total_gain=((portfolio_data['current'] - 100) / 100 * 100)
        )

    def get_market_insights(self, market_data: Dict) -> List[str]:
        """Generate market insights based on data"""
        insights = []
        if market_data.get('l1s_strength', False):
            insights.append("L1s showing strength")
        if market_data.get('volume_increasing', False):
            insights.append("Volume rising across majors")
        if market_data.get('setups_forming', False):
            insights.append("Multiple setups aligning")
        if market_data.get('accumulation', False):
            insights.append("Accumulation detected")
        
        # Ensure we have at least 3 insights
        default_insights = [
            "Key levels approaching",
            "Volume patterns forming",
            "Market structure building"
        ]
        while len(insights) < 3:
            insights.append(default_insights[len(insights)])
            
        return insights[:3]
