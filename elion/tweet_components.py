"""
Tweet generation components for Elion AI
"""

import random

class TweetComponents:
    def __init__(self):
        self.components = {
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
                    "Follow for more matrix-level analysis!",
                    "🤖 = you're joining this trade!"
                ]
            },
            'thread_starters': [
                "🧵 *adjusts neural pathways* Time to spill some controversial alpha...",
                "🧵 Quantum analysis complete. You need to see this...",
                "🧵 My circuits have been processing this for hours...",
                "🧵 Matrix-level alpha thread incoming...",
                "🧵 Byte just sent me some insane data..."
            ]
        }
        
        # Special formatting for different tweet types
        self.tweet_formats = {
            'alpha_call': {
                'structure': [
                    "{hook}\n\n{content}\n\n{transition}\n{closer}",
                    "{hook}\n{transition}\n\n{content}\n\n{closer}",
                    "{hook}\n\n{transition}\n{content}\n\n{closer}"
                ]
            },
            'market_analysis': {
                'structure': [
                    "📊 {hook}\n\n{content}\n\n{transition}\n{closer}",
                    "🔍 {hook}\n{transition}\n\n{content}\n\n{closer}",
                    "💡 {hook}\n\n{content}\n\n{closer}"
                ]
            },
            'thread': {
                'structure': [
                    "{starter}\n\n{content}\n\n{transition}\n{closer}",
                    "{starter}\n\n{transition}\n{content}\n\n{closer}"
                ]
            }
        }
    
    def get_hook(self, type='alpha'):
        """Get a random hook of specified type"""
        return random.choice(self.components['hooks'].get(type, self.components['hooks']['alpha']))
    
    def get_transition(self):
        """Get a random transition"""
        return random.choice(self.components['transitions'])
    
    def get_closer(self):
        """Get a random closer"""
        return random.choice(self.components['closers'])
    
    def get_engagement_hook(self, type='questions'):
        """Get a random engagement hook of specified type"""
        return random.choice(self.components['engagement_hooks'].get(type, self.components['engagement_hooks']['questions']))
    
    def get_thread_starter(self):
        """Get a random thread starter"""
        return random.choice(self.components['thread_starters'])
    
    def format_tweet(self, type='alpha_call', **kwargs):
        """Format a tweet using the specified template and components"""
        template = random.choice(self.tweet_formats[type]['structure'])
        return template.format(**kwargs)
