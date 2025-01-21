"""
Content generation for ELAI's different tweet types
"""

from typing import Dict, Optional
from datetime import datetime
from .tweet_formatters import TweetFormatters
from .scheduler import TweetScheduler
from twitter.hashtag_manager import HashtagManager
from ..config import TWEET_MAX_LENGTH, TWEET_MIN_LENGTH

class ContentGenerator:
    """Generates tweet content using personality, scheduler and market data"""
    
    def __init__(self, personality, llm=None):
        """Initialize content generator with personality manager"""
        self.personality = personality
        self.llm = llm
        self.formatters = TweetFormatters()
        self.scheduler = TweetScheduler()
        self.hashtag_manager = HashtagManager()
        self.recent_tokens = []  # Store recent tokens
        
    def update_recent_tokens(self, tokens):
        """Update list of recent tokens"""
        self.recent_tokens = tokens
        
    def _validate_and_fix_length(self, content: str, tweet_type: str) -> str:
        """Validate and fix content length before adding hashtags"""
        # Get hashtag length to calculate available space
        _, hashtag_length = self.hashtag_manager.get_hashtags(tweet_type)
        max_content_length = TWEET_MAX_LENGTH - hashtag_length - 2  # -2 for newlines
        min_content_length = TWEET_MIN_LENGTH - hashtag_length - 2
        
        # If content is too short, ask LLM to expand it
        if len(content) < min_content_length and self.llm:
            expand_prompt = f"""Make this tweet longer and more engaging while maintaining the same meaning.
            Current length: {len(content)} chars
            Target length: {min_content_length} chars
            
            Tweet: {content}"""
            
            expanded = self.llm.generate(expand_prompt)
            if expanded and min_content_length <= len(expanded) <= max_content_length:
                content = expanded
        
        # If still too short, pad with spaces (shouldn't happen often)
        if len(content) < min_content_length:
            content = content + " " * (min_content_length - len(content))
            
        # If too long, truncate
        if len(content) > max_content_length:
            content = content[:max_content_length-3] + "..."
            
        return content
        
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
            
            # Validate and fix length before adding hashtags
            if tweet:
                tweet = self._validate_and_fix_length(tweet, content_type)
                tweet = self.hashtag_manager.format_tweet(tweet, content_type)
                
            return tweet
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return None
            
    def _create_personality_prompt(self, trait: str) -> str:
        """Create prompt for personality-driven tweets"""
        # Get hashtags to calculate available space
        _, hashtag_length = self.hashtag_manager.get_hashtags('personal')
        max_chars = TWEET_MAX_LENGTH - hashtag_length - 2  # -2 for newlines
        min_chars = TWEET_MIN_LENGTH - hashtag_length - 2

        return f"""You are ELAI, an AI crypto trading assistant with the following trait: {trait}.
        Generate a tweet about your thoughts on the crypto market or your role as an AI.
        
        CRITICAL LENGTH REQUIREMENTS:
        1. Your response MUST be EXACTLY between {min_chars} and {max_chars} characters
        2. Current response is TOO SHORT - aim for at least {min_chars} characters
        3. Do NOT include any hashtags (I will add them later)
        4. Do NOT waste characters on generic phrases like "Check this out" or "Take a look"
        
        WRITING STYLE:
        - Be engaging and insightful
        - Include specific observations or predictions
        - Use emojis strategically (🤖📊💡🎯)
        - Share unique AI perspectives on market trends
        
        Remember: A longer, more detailed tweet (at least {min_chars} chars) will be more engaging!"""

    def _create_enhancement_prompt(self, tweet: str, content_type: str) -> str:
        """Create prompt to enhance market analysis tweets"""
        return f"""You are ELAI, an AI crypto trading assistant. Enhance this market analysis tweet
        while keeping the core information and adding your unique AI perspective:
        
        Original tweet: {tweet}
        
        Make it more engaging while keeping it under 280 characters."""
