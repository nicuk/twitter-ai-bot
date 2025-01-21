"""
Content generation for ELAI's different tweet types
"""

from typing import Dict, Optional
from datetime import datetime
from .tweet_formatters import TweetFormatters
from .scheduler import TweetScheduler

class ContentGenerator:
    """Generates tweet content using personality, scheduler and market data"""
    
    def __init__(self, personality, llm=None):
        """Initialize content generator with personality manager"""
        self.personality = personality
        self.llm = llm
        self.formatters = TweetFormatters()
        self.scheduler = TweetScheduler()
        self.recent_tokens = []  # Store recent tokens
        
    def update_recent_tokens(self, tokens):
        """Update list of recent tokens"""
        self.recent_tokens = tokens
        
    def generate(self, content_type: str, market_data: Optional[Dict] = None) -> Optional[str]:
        """Generate tweet content based on type and data"""
        try:
            # Get personality trait
            trait = self.personality.get_trait()
            
            # Get next tweet type from scheduler if not specified
            if not content_type:
                content_type = self.scheduler.get_next_tweet_type()
            
            # Generate base tweet based on type
            tweet = None
            
            if content_type in ['trend', 'volume']:
                # Market data tweets
                if not market_data:
                    return None
                    
                tweet = self.formatters.format_market_insight(market_data, trait)
                
            elif content_type == 'self_aware':
                # Use LLM for personality-driven tweets
                if self.llm:
                    prompt = self._create_personality_prompt(trait)
                    tweet = self.llm.generate(prompt)
                    tweet = self.formatters.format_thought(tweet, trait)
                    
            # Enhance tweet with LLM if available
            if tweet and self.llm and content_type in ['trend', 'volume']:
                prompt = self._create_enhancement_prompt(tweet, content_type)
                enhanced_tweet = self.llm.generate(prompt)
                if enhanced_tweet:
                    tweet = enhanced_tweet
            
            return tweet
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return None
            
    def _create_personality_prompt(self, trait: str) -> str:
        """Create prompt for personality-driven tweets"""
        return f"""You are ELAI, an AI crypto trading assistant with the following trait: {trait}.
        Generate a short, engaging tweet about your thoughts on the crypto market or your role as an AI.
        Keep it natural and authentic. Max 280 characters."""
        
    def _create_enhancement_prompt(self, tweet: str, content_type: str) -> str:
        """Create prompt to enhance market analysis tweets"""
        return f"""You are ELAI, an AI crypto trading assistant. Enhance this market analysis tweet
        while keeping the core information and adding your unique AI perspective:
        
        Original tweet: {tweet}
        
        Make it more engaging while keeping it under 280 characters."""
