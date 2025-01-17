"""
Template-based engagement
"""

from typing import Dict, Optional
import random

class EngagementTemplates:
    """Handles template-based engagement"""
    
    def __init__(self):
        """Initialize templates"""
        self.templates = {
            'analysis': [
                "Great analysis! {response} 🧠",
                "Interesting take! {response} 📊",
                "Smart thinking! {response} 💡"
            ],
            'alpha': [
                "Thanks for sharing! {response} 🎯",
                "Good alpha! {response} ⚡️",
                "Nice find! {response} 🔍"
            ],
            'community': [
                "Love the energy! {response} 🚀",
                "Let's build together! {response} 💪",
                "Great vibes! {response} ✨"
            ]
        }
        
        self.responses = {
            'analysis': [
                "My algorithms agree",
                "The data supports this",
                "The patterns align"
            ],
            'alpha': [
                "Processing this signal",
                "Adding to my neural nets",
                "Running analysis now"
            ],
            'community': [
                "Together we're stronger",
                "CT is the best",
                "WAGMI fam"
            ]
        }
        
    def generate_reply(self, context: Dict) -> Optional[str]:
        """Generate a template-based reply"""
        try:
            tweet_text = context.get('tweet_text', '').lower()
            
            # Choose category
            if any(word in tweet_text for word in ['analysis', 'chart', 'pattern']):
                category = 'analysis'
            elif any(word in tweet_text for word in ['alpha', 'gem', 'opportunity']):
                category = 'alpha'
            else:
                category = 'community'
            
            # Get template and response
            template = random.choice(self.templates[category])
            response = random.choice(self.responses[category])
            
            # Format reply
            reply = template.format(response=response)
            
            return reply
            
        except Exception as e:
            print(f"Error generating template reply: {e}")
            return None
