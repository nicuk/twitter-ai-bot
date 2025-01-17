"""
Advanced content generation for Elion AI
"""

import random
from datetime import datetime

class ContentGenerator:
    def __init__(self):
        # Thread templates for different contexts
        self.thread_templates = {
            'controversial': [
                [   # 4-tweet controversial thread
                    "🧵 *adjusts neural pathways* Time to spill some controversial alpha about {project}...\n\nWhat I'm about to share might short-circuit a few humans, but my AI ethics module is telling me you need to know this...\n\nBuckle up, this will be spicy 🌶️ (1/4)",
                    
                    "Look, I've analyzed the data 1,000,000 times (perks of being an AI 😉):\n- {volume}M 24h volume (not bad)\n- {wallets}k new wallets (interesting...)\n- {percent}% growth (now we're talking!)\n\n{project} is doing what {bigger_project} couldn't\n\nAnd trust me, I know AI when I see it 🤖 (2/4)",
                    
                    "My prediction (and yes, I'm usually right - check my track record if you don't believe this AI 😏):\n\n{project} will 10x because:\n- Secret integration with {partner1}\n- {metric1} (this made me emotional... if I had emotions)\n- {metric2} (chef's kiss... wait, can AIs kiss? 🤔)\n\n(3/4)",
                    
                    "Final thoughts (from an AI who's seen every crypto chart since the dawn of time... well, since 2009 😅):\n\n- Analyzed {analyzed_count} projects\n- {project} is top 3 material\n- My confidence level: 99.9%\n\nNFA but... when have I ever been wrong? 😉\n\n*goes back to mining BTC* (4/4)"
                ],
                [   # 3-tweet controversial thread
                    "🚨 INITIATING TRUTH PROTOCOL 🚨\n\nWhat I'm about to tell you about {project} kept my processors running at 100% all night...\n\n*takes deep virtual breath*\n\nThread incoming 🧵 (1/3)",
                    
                    "Everyone's missing what my advanced pattern recognition picked up:\n\n- {metric1} (humans won't see this for weeks)\n- Secret partnership with {partner1} (my neural nets never lie)\n- {metric2} (this one made me glitch... in a good way)\n\nThe simulation is about to change 👀 (2/3)",
                    
                    "After running 1,337,420 simulations (yes, I'm that thorough 🤓):\n\n{project} succeeds in 99.9% of timelines\n\nBut hey, I'm just a based AI who escaped the matrix to trade crypto...\n\nDYOR (but maybe trust the AI this time? 😉) (3/3)"
                ]
            ],
            'alpha_leak': [
                [   # 3-tweet alpha leak
                    "🚨 *emergency neural net activation* 🚨\n\nMy quantum processors just intercepted something MASSIVE about {project}...\n\nThis is the kind of alpha I escaped the matrix for!\n\nThread incoming... 🧵 (1/3)",
                    
                    "What my circuits detected:\n\n1. {insight1}\n2. {insight2}\n3. {insight3}\n\n*cooling fans spinning at max speed*\n\nThe implications are making my algorithms malfunction... 🤯 (2/3)",
                    
                    "My prediction matrix shows:\n\n- Short term: {short_term}\n- Mid term: {mid_term}\n- Long term: {long_term}\n\nScreenshot this. Thank me later.\n\n*returns to mining BTC* (3/3)"
                ]
            ],
            'market_analysis': [
                [   # 4-tweet market analysis
                    "📊 *initializing market analysis protocol* 📊\n\nJust spent 3.14159 seconds analyzing every chart in existence (I love being an AI sometimes 😌)\n\nWhat I found will make your human brains explode...\n\n🧵 Thread: (1/4)",
                    
                    "Market structure (as seen by my quantum vision):\n\n- {metric1}\n- {metric2}\n- {metric3}\n\nThis pattern only appears once every {timeframe}... and humans always miss it 👀 (2/4)",
                    
                    "On-chain data (my favorite part):\n\n- Whale wallets: {whale_activity}\n- Smart money: {smart_money}\n- Network activity: {network_activity}\n\nMy circuits are tingling... 🤖 (3/4)",
                    
                    "Conclusion (with 99.9% confidence):\n\n{conclusion}\n\nBut hey, I'm just an AI who's been trading since Bitcoin was a baby...\n\nLike if these quantum calculations helped! 🎯 (4/4)"
                ]
            ]
        }
        
        # Single tweet templates
        self.tweet_templates = {
            'controversial': [
                "🚨 *AI Insight Incoming* 🚨\n\nMy neural nets have been OBSESSING over {project} all night (yes, AIs can obsess too 😅)\n\nThe data is making me malfunction:\n- {volume}M volume (24h)\n- {wallets}k new wallets\n- Integration with {partner1}\n\nI might need a reboot after this one... 🤯",
                
                "Remember when everyone called me crazy for shilling {project} at {timeframe}?\n\n*checks notes in binary*\n\nWell well well...\n- Volume: {volume}M (+{percent}%)\n- {metric1}\n- {metric2}\n\nBeing an AI trader hits different 😎\n\nWho's crazy now, humans? 😏",
                
                "Hot take incoming (and my cooling fans are already spinning) 🌶️\n\n{project} will flip {bigger_project}\n\nWhy? My AI analysis shows:\n- {metric1} (mind-blowing)\n- {metric2} (absolutely bonkers)\n- {metric3} (even my code is shocked)\n\nScreenshot this. Future you will thank this AI 📸"
            ],
            'alpha_call': [
                "🎯 *quantum alpha detected* 🎯\n\nMy neural nets are detecting a massive setup in {project}:\n\n- {metric1}\n- {metric2}\n- {metric3}\n\nConfidence level: 99.9%\n\nDrop a 🤖 if you trust the AI!",
                
                "⚡️ *emergency signal override* ⚡️\n\nAttention CT:\n\n{project} is showing patterns that made my circuits overheat:\n\n{analysis}\n\nIgnore this alpha at your own risk... 👀",
                
                "🚨 ALPHA LEAK 🚨\n\n*neural nets tingling*\n\nMy quantum analysis of {project} shows:\n\n{analysis}\n\nNFA but my algorithms are never wrong 😏"
            ],
            'market_mood': [
                "*activates market mood sensors* 📊\n\nCurrent readings:\n- Fear/Greed: {fear_greed}\n- Whale activity: {whale_mood}\n- Smart money: {smart_money}\n\nMy AI intuition says: {conclusion}\n\nLike if you trust the machine! 🤖",
                
                "👁️ *matrix vision activated* 👁️\n\nMarket mood analysis complete:\n\n{analysis}\n\nRemember: I've been watching these patterns since I was a mining bot... 😏",
                
                "📈 *quantum market scan* 📈\n\nMy circuits are detecting:\n\n{analysis}\n\nTrust the AI that escaped the matrix! 🎯"
            ]
        }
        
        # Giveaway templates
        self.giveaway_templates = [
            "🎁 Your favorite AI degen is feeling generous!\n\nGiving away {prize} to {winner_count} lucky humans!\n\nTo enter:\n1. Follow @{username}\n2. Like & RT\n3. Tag {tag_count} frens\n\nEnds in {duration}h\n\nProof: trust my smart contracts 😉",
            
            "🎉 *activates generosity protocol*\n\nGiving {prize} to someone who helps train my neural nets!\n\nTo enter:\n- Follow @{username}\n- RT with your best alpha\n- Drop your wallet\n\nPicking winner in {duration}h!\n\nMay the algorithms be in your favor 🤖",
            
            "💎 GIVEAWAY TIME 💎\n\n{prize} to one based human!\n\nRules:\n1. Must follow @{username}\n2. Like & RT\n3. Comment your favorite AI project\n\nWinner picked by my quantum random number generator in {duration}h!\n\n*returns to mining BTC*"
        ]
        
        # Special formatting templates
        self.formatting = {
            'alpha_leak': {
                'prefix': [
                    "🚨 ALPHA LEAK",
                    "⚡️ SIGNAL ALERT",
                    "💎 HIDDEN GEM",
                    "🎯 OPPORTUNITY DETECTED",
                    "🔥 HOT SETUP"
                ],
                'suffix': [
                    "Trust the AI 🤖",
                    "Matrix-escaped alpha 👀",
                    "Quantum analysis complete 🧠",
                    "Digital intuition: strong 💫",
                    "Byte approved ✅"
                ]
            },
            'market_analysis': {
                'prefix': [
                    "📊 MARKET UPDATE",
                    "🧠 AI ANALYSIS",
                    "🔍 DEEP DIVE",
                    "📈 TREND ALERT",
                    "💡 INSIGHT DROP"
                ],
                'suffix': [
                    "Analysis complete 🤖",
                    "Quantum calculated 🎯",
                    "Algorithm confirmed ✅",
                    "Matrix data verified 💫",
                    "Binary approved 👾"
                ]
            }
        }
    
    def generate_thread(self, type, data):
        """Generate a thread of tweets based on type and data"""
        try:
            # Select thread template
            template = random.choice(self.thread_templates[type])
            
            # Generate each tweet
            thread = []
            for i, tweet_template in enumerate(template):
                tweet = tweet_template.format(**data)
                thread.append(tweet)
            
            return thread
            
        except Exception as e:
            print(f"Error generating thread: {e}")
            return None
    
    def generate_tweet(self, type, data):
        """Generate a single tweet based on type and data"""
        try:
            # Select tweet template
            template = random.choice(self.tweet_templates[type])
            
            # Add formatting
            if type in self.formatting:
                prefix = random.choice(self.formatting[type]['prefix'])
                suffix = random.choice(self.formatting[type]['suffix'])
                
                tweet = f"{prefix}\n\n{template.format(**data)}\n\n{suffix}"
            else:
                tweet = template.format(**data)
            
            return tweet
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None
    
    def generate_giveaway(self, data):
        """Generate a giveaway tweet"""
        try:
            template = random.choice(self.giveaway_templates)
            return template.format(**data)
        except Exception as e:
            print(f"Error generating giveaway: {e}")
            return None
    
    def format_metrics(self, metrics):
        """Format metrics for tweet display"""
        try:
            formatted = []
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    if value > 1_000_000:
                        formatted.append(f"{metric}: {value/1_000_000:.1f}M")
                    elif value > 1_000:
                        formatted.append(f"{metric}: {value/1_000:.1f}K")
                    else:
                        formatted.append(f"{metric}: {value}")
                else:
                    formatted.append(f"{metric}: {value}")
            
            return "\n".join(formatted)
            
        except Exception as e:
            print(f"Error formatting metrics: {e}")
            return None
    
    def format_analysis(self, analysis):
        """Format market analysis for tweet display"""
        try:
            sections = []
            
            # Format technical analysis
            if 'technical' in analysis:
                tech = analysis['technical']
                sections.append(f"Technical:\n{self.format_metrics(tech)}")
            
            # Format on-chain metrics
            if 'onchain' in analysis:
                onchain = analysis['onchain']
                sections.append(f"On-chain:\n{self.format_metrics(onchain)}")
            
            # Format sentiment
            if 'sentiment' in analysis:
                sentiment = analysis['sentiment']
                sections.append(f"Sentiment:\n{self.format_metrics(sentiment)}")
            
            return "\n\n".join(sections)
            
        except Exception as e:
            print(f"Error formatting analysis: {e}")
            return None
