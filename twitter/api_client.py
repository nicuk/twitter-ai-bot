"""Twitter API client wrapper"""

import os
import tweepy
import logging
import asyncio
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class TwitterAPI:
    def __init__(self):
        """Initialize Twitter API client"""
        # Initialize Twitter API clients
        logger.info("Initializing Twitter client...")
        
        # Debug token loading
        token_keys = ['TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_TOKEN_SECRET', 'TWITTER_BEARER_TOKEN']
        for key in token_keys:
            if os.getenv(key):
                logger.info(f"✓ {key} is set")
            else:
                logger.warning(f"✗ {key} is not set")
        
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=True
        )
        logger.info("Twitter client initialized")
    
    def create_tweet(self, text: str, reply_to_id: str = None) -> Optional[Dict]:
        """Create a new tweet"""
        try:
            response = self.api.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_id
            )
            if response and hasattr(response, 'data'):
                logger.info(f"Tweet posted successfully! ID: {response.data['id']}")
                return response.data
            else:
                logger.error("Failed to post tweet - invalid response")
                return None
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None
    
    async def create_tweet_async(self, text: str, reply_to_id: str = None) -> Optional[Dict]:
        """Create a new tweet asynchronously"""
        try:
            # Run tweepy call in a thread pool since it's blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.api.create_tweet, text, in_reply_to_tweet_id=reply_to_id)
            if response and hasattr(response, 'data'):
                logger.info(f"Tweet posted successfully! ID: {response.data['id']}")
                return response.data
            else:
                logger.error("Failed to post tweet - invalid response")
                return None
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None
    
    def get_tweet(self, tweet_id: str, fields: list = None) -> Optional[Dict]:
        """Get tweet by ID with metrics"""
        try:
            return self.api.get_tweet(
                tweet_id,
                tweet_fields=fields or ['public_metrics', 'created_at']
            )
        except Exception as e:
            logger.error(f"Error getting tweet {tweet_id}: {e}")
            return None
            
    def get_tweet_responses(self, tweet_id: str) -> List[Dict]:
        """Get responses to a tweet"""
        try:
            responses = self.api.search_recent_tweets(
                query=f"conversation_id:{tweet_id}",
                tweet_fields=['public_metrics', 'created_at', 'author_id'],
                user_fields=['username', 'public_metrics'],
                expansions=['author_id']
            )
            
            if not responses or not hasattr(responses, 'data'):
                return []
                
            # Process responses with user data
            processed = []
            users = {u.id: u for u in responses.includes['users']} if 'users' in responses.includes else {}
            
            for tweet in responses.data:
                user = users.get(tweet.author_id, {})
                processed.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'username': user.username if user else None,
                    'metrics': tweet.public_metrics,
                    'created_at': tweet.created_at
                })
                
            return processed
            
        except Exception as e:
            logger.error(f"Error getting responses for tweet {tweet_id}: {e}")
            return []
            
    def verify_credentials(self) -> bool:
        """Verify Twitter API credentials"""
        try:
            # Try to get the authenticated user's info
            user = self.api.get_me()
            return user is not None
        except Exception as e:
            logger.error(f"Error verifying credentials: {e}")
            return False

    def calculate_engagement_score(self, metrics: Dict) -> float:
        """Calculate engagement score from tweet metrics"""
        if not metrics:
            return 0.0
            
        # Weights for different metrics
        weights = {
            'like_count': 1.0,
            'retweet_count': 2.0,
            'reply_count': 1.5,
            'quote_count': 2.0
        }
        
        score = 0.0
        for metric, weight in weights.items():
            score += metrics.get(metric, 0) * weight
            
        return score
