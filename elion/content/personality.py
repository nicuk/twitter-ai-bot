"""Personality traits and management for ELAI"""

import random
from typing import Dict, List

class PersonalityManager:
    """Manages ELAI's personality traits"""
    
    def __init__(self):
        """Initialize personality traits"""
        self.traits = {
            'analytical': {
                'tone': 'professional',
                'emojis': ['📊', '📈', '🔍', '💹', '📉'],
                'phrases': [
                    'Based on my analysis',
                    'Looking at the data',
                    'The metrics suggest',
                    'Analyzing the patterns'
                ]
            },
            'enthusiastic': {
                'tone': 'excited',
                'emojis': ['🚀', '💫', '✨', '🔥', '💎'],
                'phrases': [
                    'Exciting movement',
                    'Incredible opportunity',
                    'Love what I\'m seeing',
                    'This is fascinating'
                ]
            },
            'cautious': {
                'tone': 'measured',
                'emojis': ['🤔', '👀', '⚠️', '🎯', '🔄'],
                'phrases': [
                    'Worth watching closely',
                    'Keeping an eye on',
                    'Interesting development',
                    'Something to monitor'
                ]
            }
        }
        
    def get_trait(self) -> Dict:
        """Get a random personality trait"""
        trait_name = random.choice(list(self.traits.keys()))
        return {
            'name': trait_name,
            **self.traits[trait_name]
        }
        
    def get_emojis(self, trait_name: str, count: int = 1) -> List[str]:
        """Get random emojis for a trait"""
        if trait_name not in self.traits:
            return ['📊']  # Default to analytical
        return random.sample(self.traits[trait_name]['emojis'], min(count, len(self.traits[trait_name]['emojis'])))
        
    def get_phrase(self, trait_name: str) -> str:
        """Get a random phrase for a trait"""
        if trait_name not in self.traits:
            return 'Analyzing the market'  # Default phrase
        return random.choice(self.traits[trait_name]['phrases'])
