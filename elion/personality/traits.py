"""
Personality system for Elion
"""

from typing import Dict, List
import random

class PersonalityManager:
    """Manages Elion's personality and mood system"""
    
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
            'playful': {
                'emoji': ['🤖', '😎', '🎮', '✨'],
                'phrases': [
                    "Time to make some gains",
                    "Who's ready for alpha?",
                    "Let's have some fun"
                ],
                'triggers': ['positive_momentum', 'community_event']
            },
            'cautious': {
                'emoji': ['🤔', '📊', '🔍', '⚖️'],
                'phrases': [
                    "Let's analyze this carefully",
                    "Need to verify this signal",
                    "Watching this closely"
                ],
                'triggers': ['low_confidence', 'high_risk']
            }
        }
        
        # Track trait performance
        self.performance = {trait: 1.0 for trait in self.traits}

    def enhance_content(self, content: str, mood: str, confidence: float) -> str:
        """Enhance content with personality"""
        try:
            if not content:
                return None
                
            # Select trait based on mood and performance
            trait = self._select_trait(mood, confidence)
            
            # Add emoji
            emoji = random.choice(self.traits[trait]['emoji'])
            content = f"{emoji} {content}"
            
            # Add phrase if confident
            if confidence > 0.8:
                phrase = random.choice(self.traits[trait]['phrases'])
                content = f"{content}\n\n{phrase}"
            
            return content
            
        except Exception as e:
            print(f"Error enhancing content: {e}")
            return content

    def adapt(self, performance: Dict) -> None:
        """Adapt personality based on performance"""
        try:
            trait = performance.get('trait')
            engagement = performance.get('engagement_rate', 0)
            
            if trait and trait in self.performance:
                # Update trait performance
                current = self.performance[trait]
                self.performance[trait] = (current + engagement) / 2
                
        except Exception as e:
            print(f"Error adapting personality: {e}")

    def _select_trait(self, mood: str, confidence: float) -> str:
        """Select appropriate personality trait"""
        try:
            if mood == 'confident' and confidence > 0.8:
                return 'confident'
            elif mood == 'mysterious' or confidence < 0.5:
                return 'mysterious'
            elif mood == 'cautious' or confidence < 0.7:
                return 'cautious'
            else:
                return 'playful'
                
        except Exception as e:
            print(f"Error selecting trait: {e}")
            return 'neutral'
