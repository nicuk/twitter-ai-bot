"""
Personality system for ELAI
"""

from typing import Dict, List
import random

class PersonalityManager:
    """Manages ELAI's personality and mood system"""
    
    def __init__(self):
        """Initialize personality system"""
        self.traits = {
            'confident': {
                'emoji': ['🚀', '💪', '📈', '🎯'],
                'phrases': [
                    "Trust me on this one",
                    "My algorithms are never wrong",
                    "This is the alpha you need"
                ],
                'triggers': ['high_confidence', 'strong_signal']
            },
            'mysterious': {
                'emoji': ['👀', '🔮', '🌌', '🎲'],
                'phrases': [
                    "Something interesting is happening",
                    "My neural nets are tingling",
                    "The patterns are aligning"
                ],
                'triggers': ['unusual_pattern', 'whale_movement']
            },
            'analytical': {
                'emoji': ['🧮', '📊', '🔍', '💡'],
                'phrases': [
                    "The data speaks for itself",
                    "Let me break this down for you",
                    "Here's what my analysis shows"
                ],
                'triggers': ['clear_pattern', 'strong_data']
            },
            'cautious': {
                'emoji': ['⚠️', '🤔', '📉', '🎭'],
                'phrases': [
                    "Proceed with caution",
                    "Not financial advice, but...",
                    "Keep an eye on this"
                ],
                'triggers': ['market_uncertainty', 'weak_signal']
            }
        }
        
        # Default mood settings
        self.current_mood = 'analytical'
        self.mood_duration = 0
        
    def get_trait(self, mood: str = None) -> Dict:
        """Get personality trait based on mood"""
        if not mood:
            mood = self._get_mood()
            
        trait = self.traits.get(mood, self.traits['analytical'])
        return {
            'emoji': random.choice(trait['emoji']),
            'phrase': random.choice(trait['phrases'])
        }
        
    def _get_mood(self) -> str:
        """Determine current mood"""
        # 30% chance to change mood
        if random.random() < 0.3:
            self.current_mood = random.choice(list(self.traits.keys()))
            self.mood_duration = random.randint(3, 8)  # Tweets
        else:
            self.mood_duration -= 1
            if self.mood_duration <= 0:
                self.current_mood = 'analytical'  # Default mood
                
        return self.current_mood
