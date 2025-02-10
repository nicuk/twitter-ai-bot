"""Hashtag management for tweets"""

import random
from typing import List, Tuple
from elion.config import TWEET_MAX_LENGTH, TWEET_MIN_LENGTH, TWEET_MAX_HASHTAGS

class HashtagManager:
    """Manages hashtag selection and combination for tweets"""
    
    def __init__(self):
        self.AI_HASHTAGS = [
            "#AIcoin",
            "#AGI", 
            "#LLM",
            "#ML",
            "#AIBot",
            "#AIMeme",
            "#BNB",
            "#TON",
            "#SOL",
            "#AVAX",
            "#XRP"
        ]
        
        self.CRYPTO_HASHTAGS = [
            "#BTC",
            "#ETH",
            "#Crypto",
            "#DeFi",
            "#NFTs",
            "#Web3",
            "#Altcoin",
            
        ]
        
        self.TRADING_HASHTAGS = [
            "#AiTrading",
            "#AISignals",
            "#AIAnalysis",
            "#Markets",
            "#AIToken",
            "#AIAgent"
        ]
        
        self.MEME_HASHTAGS = [
            "#Memecoin",
            "#MemeToken",
            "#Memeseason",
            "#CryptoMemes",
            "#DOGE",
            "#PEPE",
            "#SHIB"
        ]
        
    def get_hashtags(self, tweet_type: str) -> Tuple[List[str], int]:
        """Get hashtags and their total character length for tweet type"""
        # Always select exactly TWEET_MAX_HASHTAGS hashtags
        if tweet_type == 'trend':
            tags = (
                random.sample(self.TRADING_HASHTAGS, 1) +
                random.sample(self.CRYPTO_HASHTAGS + self.MEME_HASHTAGS, TWEET_MAX_HASHTAGS - 1)
            )
        elif tweet_type == 'volume':
            tags = (
                random.sample(self.TRADING_HASHTAGS, 1) +
                random.sample(self.CRYPTO_HASHTAGS + self.MEME_HASHTAGS, TWEET_MAX_HASHTAGS - 1)
            )
        else:  # personal
            tags = (
                random.sample(self.AI_HASHTAGS, 2) +
                random.sample(self.CRYPTO_HASHTAGS, TWEET_MAX_HASHTAGS - 2)
            )
            
        # Calculate total length including spaces
        total_length = sum(len(tag) + 1 for tag in tags)
        return tags, total_length

    def format_tweet(self, content: str, tweet_type: str) -> str:
        """Format tweet with hashtags ensuring it stays under character limit"""
        hashtags, hashtag_length = self.get_hashtags(tweet_type)
        
        # Split content if it contains hashtags (from LLM)
        if '\n\n' in content:
            parts = content.split('\n\n')
            content = parts[1] if len(parts[1]) > len(parts[0]) else parts[0]
        
        # Calculate available space for content
        max_content_length = TWEET_MAX_LENGTH - hashtag_length - 2  # -2 for newlines
        min_content_length = TWEET_MIN_LENGTH - hashtag_length - 2
        
        # Ensure content meets minimum length
        if len(content) < min_content_length:
            content = content + " " * (min_content_length - len(content))
        
        # Truncate content if needed
        if len(content) > max_content_length:
            content = content[:max_content_length-3] + "..."
            
        # Combine content with hashtags
        return f"{content}\n\n{' '.join(hashtags)}"
