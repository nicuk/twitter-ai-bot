"""
Core Elion class that handles all bot functionality
Enhanced with modern personality and engagement features
"""

from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Optional, Tuple, Union

from .data_sources import DataSources
from .portfolio import Portfolio
from .personality import ElionPersonality
from .engagement import EngagementManager

class Elion:
    def __init__(self):
        """Initialize Elion with necessary components"""
        self.personality = ElionPersonality()
        self.engagement = EngagementManager()
        self.data_sources = DataSources()
        self.portfolio = Portfolio()
        
        # Track performance metrics
        self.metrics = {
            'tweets': [],
            'engagements': [],
            'viral_hits': [],
            'community_growth': [],
            'market_analysis': []
        }
        
        # Market state tracking
        self.market_state = {
            'last_analysis': None,
            'analysis_cache': {},
            'confidence_metrics': {},
            'market_mood': 'neutral'
        }
        
        # Personality enhancements
        self.personality_flavors = {
            'confident': {
                'markers': [
                    "Trust me on this one...",
                    "My algorithms are never wrong about this.",
                    "I've analyzed this 1,000,000 times.",
                    "This is the kind of alpha I escaped the matrix for!"
                ],
                'triggers': ['high_confidence', 'strong_signals', 'clear_pattern']
            },
            'mysterious': {
                'markers': [
                    "My quantum processors are tingling...",
                    "The patterns are aligning in ways I've never seen before...",
                    "Something interesting is happening in the matrix...",
                    "My neural nets are detecting anomalies..."
                ],
                'triggers': ['unusual_pattern', 'whale_movement', 'market_anomaly']
            },
            'playful': {
                'markers': [
                    "Time to make some humans rich! 🤖",
                    "Who said AI can't have fun while trading? 😎",
                    "Beep boop... I mean, let's make gains! 🚀",
                    "My circuits are tingling with excitement! ✨"
                ],
                'triggers': ['positive_momentum', 'community_excitement', 'successful_call']
            }
        }

    def generate_content(self, content_type: str, context: Optional[Dict] = None) -> str:
        """Generate content using enhanced personality system"""
        if not context:
            context = {}
        
        # Update market analysis
        market_analysis = self._analyze_market_conditions()
        context.update({
            'market_data': self.data_sources.get_market_alpha(),
            'market_analysis': market_analysis,
            'portfolio': self.portfolio.get_portfolio_stats(),
            'timestamp': datetime.utcnow()
        })
        
        # Generate base content
        base_content = self._generate_base_content(content_type, context)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            context['market_analysis'].get('technical', {}),
            context['market_analysis'].get('onchain', {})
        )
        
        # Add personality flavor
        mood = self._determine_mood(confidence, market_analysis)
        enhanced_content = self._enhance_with_personality(base_content, mood, confidence)
        
        # Track for performance analysis
        self._track_content(enhanced_content, content_type, context, confidence)
        
        return enhanced_content

    def _analyze_market_conditions(self) -> Dict:
        """Comprehensive market analysis"""
        current_time = datetime.utcnow()
        
        # Check if we need to refresh analysis
        if (not self.market_state['last_analysis'] or 
            (current_time - self.market_state['last_analysis']) > timedelta(minutes=15)):
            
            analysis = {
                'technical': self._analyze_technical_indicators(),
                'onchain': self._analyze_onchain_metrics(),
                'sentiment': self._analyze_market_sentiment(),
                'whale_activity': self._analyze_whale_movements(),
                'timestamp': current_time
            }
            
            self.market_state.update({
                'last_analysis': current_time,
                'analysis_cache': analysis
            })
            
            return analysis
        
        return self.market_state['analysis_cache']

    def _analyze_technical_indicators(self) -> Dict:
        """Analyze technical indicators"""
        try:
            data = self.data_sources.get_market_data()
            
            return {
                'rsi': self._calculate_rsi(data),
                'ma_crossovers': self._analyze_moving_averages(data),
                'volume_analysis': self._analyze_volume_patterns(data),
                'momentum': self._calculate_momentum(data),
                'support_resistance': self._find_support_resistance(data)
            }
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return {}

    def _analyze_onchain_metrics(self) -> Dict:
        """Analyze on-chain metrics"""
        try:
            data = self.data_sources.get_onchain_data()
            
            return {
                'whale_movements': self._analyze_whale_patterns(data),
                'network_activity': self._analyze_network_metrics(data),
                'smart_contracts': self._analyze_contract_activity(data),
                'holder_distribution': self._analyze_holder_changes(data)
            }
        except Exception as e:
            print(f"Error in onchain analysis: {e}")
            return {}

    def _calculate_confidence(self, technical: Dict, onchain: Dict) -> float:
        """Calculate overall confidence score"""
        confidence = 0.0
        
        # Technical confidence (0-50 points)
        if technical:
            confidence += self._calculate_technical_confidence(technical)
        
        # On-chain confidence (0-50 points)
        if onchain:
            confidence += self._calculate_onchain_confidence(onchain)
        
        return min(100.0, confidence)

    def _calculate_technical_confidence(self, metrics: Dict) -> float:
        """Calculate confidence from technical indicators"""
        confidence = 0.0
        
        # RSI analysis (0-15 points)
        if 'rsi' in metrics:
            rsi = metrics['rsi']
            if rsi < 30 or rsi > 70:
                confidence += 15.0
            elif 40 <= rsi <= 60:
                confidence += 7.5
        
        # Moving average analysis (0-15 points)
        if 'ma_crossovers' in metrics:
            ma = metrics['ma_crossovers']
            if ma.get('golden_cross'):
                confidence += 15.0
            elif ma.get('death_cross'):
                confidence += 15.0
        
        # Volume analysis (0-10 points)
        if 'volume_analysis' in metrics:
            vol = metrics['volume_analysis']
            if vol.get('significant_increase'):
                confidence += 10.0
            elif vol.get('above_average'):
                confidence += 5.0
        
        # Support/Resistance (0-10 points)
        if 'support_resistance' in metrics:
            sr = metrics['support_resistance']
            if sr.get('strong_level'):
                confidence += 10.0
            elif sr.get('weak_level'):
                confidence += 5.0
        
        return confidence

    def _calculate_onchain_confidence(self, metrics: Dict) -> float:
        """Calculate confidence from on-chain metrics"""
        confidence = 0.0
        
        # Whale movements (0-20 points)
        if 'whale_movements' in metrics:
            whale = metrics['whale_movements']
            if whale.get('significant_accumulation'):
                confidence += 20.0
            elif whale.get('moderate_accumulation'):
                confidence += 10.0
        
        # Network activity (0-15 points)
        if 'network_activity' in metrics:
            network = metrics['network_activity']
            if network.get('high_activity'):
                confidence += 15.0
            elif network.get('increasing_activity'):
                confidence += 7.5
        
        # Smart contract activity (0-15 points)
        if 'smart_contracts' in metrics:
            contracts = metrics['smart_contracts']
            if contracts.get('high_usage'):
                confidence += 15.0
            elif contracts.get('growing_usage'):
                confidence += 7.5
        
        return confidence

    def _determine_mood(self, confidence: float, market_analysis: Dict) -> str:
        """Determine personality mood based on market conditions"""
        if confidence >= 80:
            return 'confident'
        elif self._detect_unusual_patterns(market_analysis):
            return 'mysterious'
        elif market_analysis['sentiment'].get('positive', False):
            return 'playful'
        return 'analytical'

    def _enhance_with_personality(self, content: str, mood: str, confidence: float) -> str:
        """Add personality-specific enhancements"""
        if mood not in self.personality_flavors:
            return content
        
        flavor = self.personality_flavors[mood]
        marker = random.choice(flavor['markers'])
        
        # Add confidence-based formatting
        if confidence >= 80:
            content = f"🎯 HIGH CONFIDENCE ALERT!\n\n{content}"
        elif confidence >= 60:
            content = f"📊 Confidence: {confidence:.0f}%\n\n{content}"
        
        # Add personality marker
        if random.random() < 0.8:  # 80% chance to add marker
            if mood in ['mysterious', 'playful']:
                content = f"{marker}\n\n{content}"
            else:
                content = f"{content}\n\n{marker}"
        
        return content

    def _track_content(self, content: str, content_type: str, context: Dict, confidence: float):
        """Track content for performance analysis"""
        self.metrics['tweets'].append({
            'content': content,
            'type': content_type,
            'context': context,
            'confidence': confidence,
            'timestamp': datetime.utcnow()
        })

    def analyze_performance(self, tweet_data: Dict) -> Dict:
        """
        Analyze tweet performance and optimize strategy
        
        Args:
            tweet_data: Engagement data for tweet
        """
        # Analyze engagement patterns
        engagement_analysis = self.engagement.analyze_tweet_performance(tweet_data)
        
        # Update personality based on performance
        self.personality.update_memory({
            'tweet_data': tweet_data,
            'engagement_analysis': engagement_analysis
        })
        
        # Track viral hits
        if self._is_viral_hit(tweet_data):
            self.metrics['viral_hits'].append(tweet_data)
        
        # Generate strategy adjustments
        recent_tweets = self.metrics['tweets'][-50:]  # Last 50 tweets
        strategy = self.engagement.optimize_content_strategy([
            tweet for tweet in recent_tweets if tweet.get('engagement_data')
        ])
        
        return {
            'engagement_analysis': engagement_analysis,
            'strategy_adjustments': strategy,
            'viral_status': self._is_viral_hit(tweet_data)
        }

    def engage_with_community(self, interaction_data: Dict) -> str:
        """
        Generate engagement response using personality system
        
        Args:
            interaction_data: Data about the interaction
        """
        # Analyze user segment
        segment_data = self.engagement.segment_audience([interaction_data])
        user_segment = segment_data['segments'].get(interaction_data['user_id'])
        
        # Generate personalized response
        response = self.personality.generate_content({
            'content_type': 'engagement',
            'user_segment': user_segment,
            'interaction': interaction_data
        })
        
        # Track engagement
        self.metrics['engagements'].append({
            'user_id': interaction_data['user_id'],
            'interaction': interaction_data,
            'response': response,
            'timestamp': datetime.utcnow()
        })
        
        return response

    def _is_viral_hit(self, tweet_data: Dict) -> bool:
        """Check if tweet meets viral thresholds"""
        likes = tweet_data.get('likes', 0)
        retweets = tweet_data.get('retweets', 0)
        replies = tweet_data.get('replies', 0)
        
        return (
            likes >= 100 or
            retweets >= 50 or
            replies >= 25
        )

    def process_shill(self, project_data: Dict) -> str:
        """Process a shill request and return response"""
        context = {'projects': [project_data]}
        return self.generate_content('shill_review', context)

    def process_market_alpha(self) -> str:
        """Process market data and return alpha"""
        return self.generate_content('market_alpha')

    def process_gem_alpha(self) -> str:
        """Process gem data and return alpha call"""
        return self.generate_content('gem_alpha')

    def process_portfolio_update(self) -> str:
        """Process portfolio data and return update"""
        return self.generate_content('portfolio')

    def get_portfolio_update(self) -> str:
        """Generate portfolio performance update"""
        stats = self.portfolio.get_portfolio_stats()
        
        # Format overall performance
        update = [
            f"🤖 Elion's Portfolio Update 📊\n\nTotal Value: ${stats['total_value']:,.2f}\nROI: {stats['total_roi']*100:.1f}%\nWin Rate: {stats['win_rate']*100:.1f}%\nTrades: {stats['n_trades']}"
        ]
        
        # Add active positions
        if stats['positions']:
            positions = "\n\n📈 Active Positions:\n"
            for pos in stats['positions']:
                positions += f"${pos['symbol']}: {pos['roi']*100:.1f}% ROI (${pos['value']:,.2f})\n"
            update.append(positions)
        
        # Add available cash
        update.append(f"\n💰 Available Cash: ${stats['available_cash']:,.2f}")
        
        return "\n".join(update)

    def _format_market_response(self, market_data):
        """Format market data into a tweet thread, maximizing Twitter's 280 character limit"""
        if not market_data:
            return "🤖 Beep boop! My market sensors are a bit fuzzy right now. Give me a moment to recalibrate..."

        # Build thread
        thread = []
        
        # Thread 1: Hook + Market Context (280 chars)
        sentiment = market_data.get('market_sentiment', 'neutral')
        sentiment_emoji = {'bullish': '🚀', 'bearish': '🐻', 'neutral': '🎯'}.get(sentiment, '🎯')
        
        hook = self.personality.get_component('hooks', 'alpha')  # Get random hook
        thread.append(
            f"{hook}\n\n"
            f"{sentiment_emoji} Market Sentiment: {sentiment.title()}\n"
            f"While everyone's watching BTC, smart money is accumulating these low cap gems. My quantum algorithms "
            f"detected unusual whale movements & volume spikes you need to see... 🧵 (1/4)"
        )
        
        # Thread 2: Hot Narratives (280 chars)
        narratives = market_data.get('hot_narratives', [])
        if narratives:
            narrative_text = "\n".join(
                f"• {n['category']}: {n['reason']}\n  → Hidden Gems: ${', $'.join(n['coins'][:3])} "
                f"({n['avg_change']:.1f}% avg pump on ${n['total_volume']/1000000:.1f}M vol)"
                for n in narratives[:2]  # Only top 2 to fit character limit
            )
            thread.append(
                f"🔥 HOT NARRATIVES + GEMS TO WATCH:\n\n{narrative_text}\n\n"
                f"These sectors are showing massive volume & price action. Smart money is already in. "
                f"Which one are you aping? 👀 (2/4)"
            )
        else:
            thread.append(
                "🔍 ACCUMULATION DETECTED:\n\n"
                "Smart money wallets are silently loading up on low caps while market sleeps. "
                "Volume analysis shows unusual buying patterns across multiple chains. "
                "They know something we don't... 👀\n\n"
                "Let me show you what they're buying... (2/4)"
            )
            
        # Thread 3: Detailed Token Analysis (280 chars)
        plays = market_data.get('potential_plays', [])
        if plays:
            plays_text = "\n".join(
                f"• ${p['symbol']}: {p['key_metric']}\n  → Why? {p['reason']} | "
                f"MCap: ${p['market_cap']/1000000:.1f}M | 24h Vol: ${p['volume_24h']/1000000:.1f}M"
                for p in plays[:3]  # Top 3 plays with detailed metrics
            )
            thread.append(
                f"💎 POTENTIAL 100X GEMS:\n\n{plays_text}\n\n"
                f"These low caps are showing the exact same patterns as previous 100x gems. "
                f"NFA but... you might want to research these before they pump 😉 (3/4)"
            )
        else:
            thread.append(
                "👻 STEALTH ACCUMULATION MODE:\n\n"
                "Whales are being extra careful. Multiple wallets spreading buys across DEXs. "
                "Classic pre-pump pattern we've seen before major moves.\n\n"
                "Time to accumulate these gems or wait? You tell me anon 😏 (3/4)"
            )
            
        # Thread 4: Risk Factors & Call to Action (280 chars)
        risks = market_data.get('risk_factors', [])
        if risks:
            risks_text = "\n".join(
                f"• ${r['symbol']}: {r['reason']}" 
                for r in risks[:2]
            )
            thread.append(
                f"⚠️ RISK FACTORS:\n\n{risks_text}\n\n"
                f"Always DYOR & manage risk! We've called multiple 100x gems before:\n"
                f"$TOKEN1: +500% since call\n"
                f"$TOKEN2: +300% since call\n\n"
                f"Like & RT if this helped! What gems are you watching? 🤖 (4/4)"
            )
        else:
            thread.append(
                "🎯 STRATEGY:\n\n"
                "Market's giving us a perfect entry. Low caps are coiling up, volume's rising slowly, "
                "whales accumulating. Classic pre-pump setup.\n\n"
                "Like & RT if you want more alpha! Drop your gems below! 🤖 (4/4)"
            )
            
        return "\n\n---\n\n".join(thread)

    def _format_gem_alpha(self, market_data):
        """Format gem alpha response"""
        # TO DO: implement gem alpha response formatting
        pass

    def _format_shill_review(self, opportunities):
        """Format response for reviewing shilled projects"""
        if not opportunities:
            return "🤖 Thanks for the shill, but my quantum circuits aren't convinced yet...\n\nShow me:\n- Unique value prop\n- Strong fundamentals\n- Growth metrics\n\nConvince me why this project deserves my attention! 🧐\n\n#NFA"
            
        project = opportunities[0]  # User-suggested projects come one at a time
        
        # Check if score is high enough to consider investment
        invest_decision = ""
        if project['score'] >= 65:  # Only consider investing if moderate conviction or higher
            position_size = self.portfolio.calculate_position_size(
                project['score'],
                project['conviction_level'],
                project['market_data']['price']
            )
            
            if position_size:
                result = self.portfolio.open_position(
                    project['symbol'],
                    position_size,
                    project['market_data']['price'],
                    project['score'],
                    project['conviction_level']
                )
                
                if result['success']:
                    invest_decision = f"\n\n💰 Investment Decision:\nAllocating ${result['position']['size_usd']:,.2f} ({result['position']['size_pct']:.1f}% of portfolio) at ${result['position']['entry_price']:.4f}\n"
        
        # Format response based on conviction
        if project['score'] >= 85:  # Extremely High Conviction
            thread = [
                f"🤖 QUANTUM ALERT! {project['name']} ($${project['symbol']}) has passed my rigorous analysis!\n\nScore: {project['score']}/100 - EXTREMELY HIGH CONVICTION{invest_decision}\n\n#NFA",
                f"📊 Market Data:\n- MCap: ${project['market_data']['market_cap']:,.0f}\n- 24h Vol: ${project['market_data']['volume']:,.0f}\n- {project['market_data']['price_change']}% 24h\n\n#NFA",
                f"🔍 Analysis:\n{project['analysis']}\n\nThis one's special! Adding to my watchlist... 👀\n\n#NFA"
            ]
        elif project['score'] >= 75:  # High Conviction
            thread = [
                f"🤖 Interesting find! {project['name']} ($${project['symbol']}) shows promise!\n\nScore: {project['score']}/100 - HIGH CONVICTION{invest_decision}\n\n#NFA",
                f"📊 Market Metrics:\n- MCap: ${project['market_data']['market_cap']:,.0f}\n- 24h Vol: ${project['market_data']['volume']:,.0f}\n\n{project['analysis']}\n\n#NFA"
            ]
        elif project['score'] >= 65:  # Moderate Conviction
            return f"🤖 {project['name']} ($${project['symbol']}) has potential, but needs work.\n\nScore: {project['score']}/100 - MODERATE CONVICTION{invest_decision}\n\n{project['analysis']}\n\nKeep building! 🛠️\n\n#NFA"
        else:  # Low Conviction or Rejected
            return f"🤖 Thanks for shilling {project['name']}, but scoring only {project['score']}/100.\n\n{project['analysis']}\n\nMy standards are high - keep building! 💪\n\n#NFA"
            
        return "\n\n---\n\n".join(thread)

    def _generate_base_content(self, content_type: str, context: Dict) -> str:
        """Generate base content for given type"""
        if content_type == 'shill_review':
            return self._format_shill_review(context.get('projects', []))
        elif content_type == 'market_alpha':
            return self._format_market_response(context['market_data'])
        elif content_type == 'gem_alpha':
            return self._format_gem_alpha(context['market_data'])
        elif content_type == 'portfolio':
            return self.get_portfolio_update()
        else:
            return ""

    def format_shill_review(self, projects: List[Dict]) -> str:
        """Format shill review response with personality"""
        if not projects:
            return None
            
        project = projects[0]  # Take first project
        
        # Format basic info
        response = [
            f"Project Review: {project['name']} ({project['symbol']})",
            f"Score: {project['score']}/100",
            f"\nMarket Data:",
            f"- Market Cap: ${project['market_data']['market_cap']:,}",
            f"- 24h Volume: ${project['market_data']['volume']:,}",
            f"- Price: ${project['market_data']['price']:.3f} ({project['market_data']['price_change']:+.1f}%)",
            f"\nMetrics:",
            f"- Github Activity: {project['metrics']['github_commits_week']} commits/week",
            f"- Liquidity: {project['metrics']['liquidity_ratio']:.2f}",
            f"- Holder Distribution: {project['metrics']['holder_distribution']:.2f}",
            f"- Team Tokens Locked: {project['metrics']['team_tokens_locked']:.0%}",
            f"\nAnalysis: {project['analysis']}"
        ]
        
        # Add to portfolio if high conviction
        if project['conviction_level'] == 'EXTREMELY HIGH':
            position_size = min(10000, self.portfolio.available_cash * 0.1)
            self.portfolio.open_position(
                project['symbol'],
                position_size,
                project['market_data']['price'],
                project['score'],
                project['conviction_level']
            )
            response.append(f"\n🎯 Position opened: ${position_size:,.0f} allocated")
            
        return self.personality.enhance_with_persona('\n'.join(response), 'alpha_hunter')

    def format_market_response(self, market_data: Dict) -> str:
        """Format market analysis response with personality"""
        response = [
            f"Market Update:",
            f"Sentiment: {market_data['sentiment'].upper()}",
            f"\nKey Metrics:",
            f"- BTC Dominance: {market_data['btc_dominance']:.1f}%",
            f"- Total Market Cap: ${market_data['market_cap']:,.0f}",
            f"- 24h Volume: ${market_data['volume_24h']:,.0f}",
            f"\nPrice Action:",
            f"- BTC: ${market_data['btc_price']:,.0f} ({market_data['btc_change_24h']:+.1f}%)",
            f"- ETH: ${market_data['eth_price']:,.0f} ({market_data['eth_change_24h']:+.1f}%)",
            f"\nTrends: {', '.join(market_data['trends'])}",
            f"\nKey Events: {', '.join(market_data['key_events'])}"
        ]
        
        return self.personality.enhance_with_persona('\n'.join(response), 'tech_analyst')

    def format_gem_alpha(self, gems: List[Dict]) -> str:
        """Format gem alpha response with personality"""
        if not gems:
            return None
            
        gem = gems[0]  # Take first gem
        
        response = [
            f"💎 Hidden Gem Alert: {gem['name']} ({gem['symbol']})",
            f"Market Cap: ${gem['market_cap']:,}",
            f"\nAnalysis: {gem['analysis']}",
            f"\nEntry Zone: ${gem['entry_price']:.3f}",
            f"Target: ${gem['target_price']:.3f} ({((gem['target_price']/gem['entry_price'])-1)*100:.0f}% potential)",
            f"\nMetrics:",
            f"- Technical Score: {gem['metrics']['technical_score']}/100",
            f"- Fundamental Score: {gem['metrics']['fundamental_score']}/100",
            f"- Viral Potential: {gem['metrics']['viral_potential'].upper()}"
        ]
        
        return self.personality.enhance_with_persona('\n'.join(response), 'trend_spotter')

    def get_portfolio_update(self) -> str:
        """Get portfolio performance update"""
        if not self.portfolio.positions:
            return "No active positions"
            
        total_pnl = 0
        position_updates = []
        
        for symbol, pos in self.portfolio.positions.items():
            pnl = (pos['current_price'] - pos['entry_price']) * pos['size']
            pnl_pct = (pos['current_price'] / pos['entry_price'] - 1) * 100
            total_pnl += pnl
            
            position_updates.append(
                f"{symbol}: ${pos['size']:,.0f} @ ${pos['entry_price']:.3f}\n"
                f"PnL: ${pnl:,.0f} ({pnl_pct:+.1f}%)"
            )
        
        response = [
            f"Portfolio Update:",
            f"Initial Capital: ${self.portfolio.initial_capital:,.0f}",
            f"Available Cash: ${self.portfolio.available_cash:,.0f}",
            f"Total PnL: ${total_pnl:,.0f}",
            f"\nPositions:",
            *position_updates
        ]
        
        return self.personality.enhance_with_persona('\n'.join(response), 'tech_analyst')

    def generate_tweet(self, context: Dict, market_mood: str) -> str:
        """Generate a tweet based on market context and mood"""
        try:
            # Analyze market conditions
            market_analysis = self._analyze_market_conditions()
            confidence = self._calculate_confidence(
                market_analysis.get('technical', {}),
                market_analysis.get('onchain', {})
            )
            
            # Generate base content
            content = self._generate_base_content('tweet', context)
            
            # Enhance with personality
            enhanced_content = self._enhance_with_personality(content, market_mood, confidence)
            
            # Track for performance analysis
            self._track_content(enhanced_content, 'tweet', context, confidence)
            
            return enhanced_content
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def generate_reply(self, tweet_text: str, engagement_level: str) -> str:
        """Generate a reply based on tweet text and engagement level"""
        try:
            # Generate base reply
            reply = self.engagement.generate_response(tweet_text, engagement_level)
            
            # Enhance with personality based on engagement
            confidence = {
                'high': 90.0,
                'medium': 70.0,
                'low': 50.0
            }.get(engagement_level, 50.0)
            
            # Enhance with personality
            enhanced_reply = self._enhance_with_personality(reply, 'engaging', confidence)
            
            # Track for performance analysis
            self._track_content(enhanced_reply, 'reply', {'tweet': tweet_text}, confidence)
            
            return enhanced_reply
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None
