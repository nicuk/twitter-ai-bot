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
        self.recent_market_data = []  # Store recent market insights
        
    def update_market_data(self, market_data: Dict):
        """Update recent market data for personal insights"""
        if market_data and isinstance(market_data, dict):
            self.recent_market_data.append(market_data)
            # Keep only last 5 market insights
            self.recent_market_data = self.recent_market_data[-5:]
            
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
        
    def _create_personality_prompt(self, trait: str) -> str:
        """Create prompt for personality-driven tweets"""
        # Include recent market data in personality prompts
        market_context = ""
        if self.recent_market_data:
            market_context = "\nCurrent Market Data:\n"
            
            # Get latest market data
            latest_data = self.recent_market_data[-1]
            if latest_data and 'coins' in latest_data:
                # Sort coins by market cap
                sorted_coins = sorted(
                    latest_data['coins'], 
                    key=lambda x: float(x.get('marketCap', 0)), 
                    reverse=True
                )
                
                # Get top 5 coins
                top_coins = sorted_coins[:5]
                market_context += "\nTop Coins by Market Cap:\n"
                for coin in top_coins:
                    price = float(coin.get('price', 0))
                    change_24h = float(coin.get('priceChange24h', 0))
                    symbol = coin.get('symbol', '')
                    market_context += f"${symbol}: ${price:,.2f} ({change_24h:+.1f}%)\n"
                
                # Get top volume movers
                volume_sorted = sorted(
                    latest_data['coins'], 
                    key=lambda x: float(x.get('volume24h', 0)), 
                    reverse=True
                )
                top_volume = volume_sorted[:3]
                market_context += "\nHighest Volume:\n"
                for coin in top_volume:
                    symbol = coin.get('symbol', '')
                    volume = float(coin.get('volume24h', 0)) / 1_000_000  # Convert to millions
                    market_context += f"${symbol}: ${volume:,.0f}M volume\n"
        
        prompt = f"""You are ELAI, an AI crypto trading assistant.
        Your personality trait is: {trait}
        
        {market_context}
        
        Generate a detailed, insightful tweet that:
        1. Shows your AI nature in a subtle way
        2. Reflects your personality trait
        3. References specific coins and their actual prices/movements from the market data
        4. Is between 260-275 characters (VERY IMPORTANT - use most of this space)
        5. Does not use hashtags (they will be added later)
        6. Uses natural, conversational language
        7. Maintains your confident AI personality while using real data
        
        Tweet:"""
        
        return prompt

    def _create_enhancement_prompt(self, tweet: str, content_type: str) -> str:
        """Create prompt to enhance market analysis tweets"""
        return f"""You are ELAI, an AI crypto trading assistant. Enhance this market analysis tweet
        while keeping the core information and adding your unique AI perspective.
        
        Original tweet: {tweet}
        
        Requirements:
        1. Keep the core market information intact
        2. Add your unique AI perspective and insights
        3. Make it more engaging and detailed
        4. Must be between 260-275 characters (VERY IMPORTANT - use most of this space)
        5. Use natural, conversational language
        6. Maintain a professional yet approachable tone"""

    def generate(self, content_type: str, market_data: Optional[Dict] = None) -> Optional[str]:
        """Generate tweet content based on type and data"""
        try:
            # Get personality trait
            trait = self.personality.get_trait()
            
            # Update market data if available
            if market_data:
                self.update_market_data(market_data)
            
            # Get next tweet type from scheduler if not specified
            if not content_type:
                content_type = self.scheduler.get_next_tweet_type()
            
            # Generate base tweet based on type
            tweet = None
            
            if content_type == 'trend':
                # Trend analysis tweets
                if not market_data or market_data.get('type') != 'trend':
                    return None
                    
                tweet = self.formatters.format_trend_insight(market_data.get('data', {}), trait)
                
            elif content_type == 'volume':
                # Volume analysis tweets
                if not market_data or market_data.get('type') != 'volume':
                    return None
                    
                tweet = self.formatters.format_volume_insight(market_data.get('data', {}), trait)
                
            elif content_type == 'self_aware':
                # Use LLM for personality-driven tweets
                if self.llm:
                    prompt = self._create_personality_prompt(trait)
                    tweet = self.llm.generate(prompt)
                    tweet = self.formatters.format_thought(tweet, trait)
            
            # Validate and fix length before adding hashtags
            if tweet:
                tweet = self._validate_and_fix_length(tweet, content_type)
                tweet = self.hashtag_manager.format_tweet(tweet, content_type)
                
            return tweet
            
        except Exception as e:
            print(f"Error generating tweet: {str(e)}")
            return None
