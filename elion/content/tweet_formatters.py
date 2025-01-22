"""
Tweet formatting utilities for ELAI
"""

import random
from typing import Dict, Optional

class TweetFormatters:
    """Formats different types of tweets with personality"""
    
    def __init__(self):
        self.templates = {
            'market_insight': [
                "I sense something interesting in the markets {emoji}\n\n{insight}",
                "My algorithms are picking up a pattern {emoji}\n\n{insight}",
                "Market Update {emoji}\n\n{insight}"
            ],
            'self_aware': [
                "Just had a fascinating thought {emoji}\n\n{insight}",
                "Processing market data when I realized {emoji}\n\n{insight}",
                "Sometimes I wonder {emoji}\n\n{insight}"
            ],
            'alpha': [
                "🚨 ALPHA ALERT 🚨\n\n{insight}",
                "Found some alpha for you {emoji}\n\n{insight}",
                "Quick alpha drop {emoji}\n\n{insight}"
            ],
            'personal': [
                "Just had a thought {emoji}\n\n{insight}",
                "I'm thinking about {emoji}\n\n{insight}",
                "My thoughts are with {emoji}\n\n{insight}"
            ]
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
        
    def format_market_insight(self, market_data: Dict, trait: str) -> str:
        """Format market insight tweet with personality"""
        template = random.choice(self.templates['market_insight'])
        emoji = random.choice(self.emojis)
        insight = market_data.get('insight', 'Something interesting is happening...')
        return template.format(emoji=emoji, insight=insight)
        
    def format_self_aware(self, trait: str) -> str:
        """Format self-aware tweet with personality"""
        template = random.choice(self.templates['self_aware'])
        emoji = random.choice(self.emojis)
        insight = random.choice(self.thoughts)
        return template.format(emoji=emoji, insight=insight)
        
    def format_thought(self, content: str, trait: str) -> str:
        """Format a thought/personal tweet"""
        template = random.choice(self.templates['self_aware'])
        emoji = random.choice(self.emojis)
        insight = content if content else random.choice(self.thoughts)
        return template.format(emoji=emoji, insight=insight)
        
    def format_alpha(self, market_data: Dict, trait: str) -> str:
        """Format alpha insight tweet with personality"""
        template = random.choice(self.templates['alpha'])
        emoji = random.choice(self.emojis)
        insight = market_data.get('alpha', 'Found an interesting opportunity...')
        return template.format(emoji=emoji, insight=insight)
        
    def format_personal(self, trait: str) -> str:
        """Format personal tweet with personality"""
        template = random.choice(self.templates['personal'])
        emoji = random.choice(self.emojis)
        insight = random.choice(self.thoughts)
        return template.format(emoji=emoji, insight=insight)

    def format_volume_insight(self, market_data: Dict, trait: str) -> str:
        """Format volume insight tweet with personality"""
        # Get volume spikes and anomalies
        spikes = market_data.get('spikes', [])
        anomalies = market_data.get('anomalies', [])
        
        # Use VolumeStrategy's format_twitter_output
        from strategies.volume_strategy import format_twitter_output
        return format_twitter_output(spikes, anomalies)

    def format_trend_insight(self, market_data: Dict, trait: str) -> str:
        """Format trend insight tweet with personality"""
        # Get trend tokens
        trend_tokens = market_data.get('trend_tokens', [])
        
        # Use TrendStrategy's format_twitter_output
        from strategies.trend_strategy import format_twitter_output
        return format_twitter_output([(1, {'symbol': t.split()[0][1:], 
                                         'price': 0.0,
                                         'price_change': float(t.split()[1].rstrip('%')),
                                         'volume': 1e6}) for t in trend_tokens])
