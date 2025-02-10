"""Twitter API client wrapper"""

import os
import tweepy
import logging
import asyncio
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

class TwitterAPI:
    def __init__(self):
        """Initialize Twitter API client"""
        # Initialize Twitter API clients
        logger.info("Initializing Twitter client...")
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=True
        )
        self.api_calls = {
            'create_tweet': {'count': 0, 'last_call': None, 'rate_limits': []},
            'get_tweet': {'count': 0, 'last_call': None, 'rate_limits': []},
            'search_tweets': {'count': 0, 'last_call': None, 'rate_limits': []}
        }
        logger.info("Twitter client initialized")
    
    def _log_api_call(self, endpoint: str):
        """Log API call with timing"""
        now = datetime.now()
        self.api_calls[endpoint]['count'] += 1
        self.api_calls[endpoint]['last_call'] = now
        logger.debug(f"API Call to {endpoint} - Total calls: {self.api_calls[endpoint]['count']}")
    
    def _log_rate_limit(self, endpoint: str):
        """Log rate limit hit"""
        now = datetime.now()
        self.api_calls[endpoint]['rate_limits'].append(now)
        recent_limits = [t for t in self.api_calls[endpoint]['rate_limits'] 
                        if (now - t).total_seconds() < 900]  # Last 15 minutes
        self.api_calls[endpoint]['rate_limits'] = recent_limits
        
        logger.warning(f"Rate limit hit for {endpoint}")
        logger.warning(f"Rate limits in last 15min: {len(recent_limits)}")
        logger.warning(f"Total API calls to {endpoint}: {self.api_calls[endpoint]['count']}")
        
    def create_tweet(self, text: str, reply_to_id: str = None) -> Optional[Dict]:
        """Create a new tweet"""
        try:
            self._log_api_call('create_tweet')
            logger.info(f"Attempting to post tweet: {text[:50]}...")
            logger.info(f"API calls in last 15min: {self.api_calls['create_tweet']['count']}")
            
            # Add more detailed logging for the API call
            logger.info("Making Twitter API call...")
            response = self.api.create_tweet(
                text=text,
                in_reply_to_tweet_id=reply_to_id
            )
            logger.info(f"Raw API response: {response}")
            if hasattr(response, '__dict__'):
                logger.info(f"Response attributes: {response.__dict__}")
            
            # Skip verification since we've hit GET limits
            if response:
                logger.info("Tweet posted successfully!")
                return {"id": "unknown"}  # Return dummy ID
            else:
                logger.error("Failed to post tweet - invalid response")
                return None
        except tweepy.errors.TooManyRequests as e:
            self._log_rate_limit('create_tweet')
            logger.info("Letting Tweepy handle rate limit waiting...")
            # Don't raise, let Tweepy retry with wait_on_rate_limit=True
            return None
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None
    
    async def create_tweet_async(self, text: str, reply_to_id: str = None) -> Optional[Dict]:
        """Create a new tweet asynchronously"""
        try:
            # Run tweepy call in a thread pool since it's blocking
            self._log_api_call('create_tweet')
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, self.api.create_tweet, text, in_reply_to_tweet_id=reply_to_id)
            
            # Skip verification since we've hit GET limits
            if response:
                logger.info("Tweet posted successfully!")
                return {"id": "unknown"}  # Return dummy ID
            else:
                logger.error("Failed to post tweet - invalid response")
                return None
        except tweepy.errors.TooManyRequests as e:
            self._log_rate_limit('create_tweet')
            logger.info("Letting Tweepy handle rate limit waiting...")
            # Don't raise, let Tweepy retry with wait_on_rate_limit=True
            return None
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return None
    
    def get_tweet(self, tweet_id: str, fields: list = None) -> Optional[Dict]:
        """Get tweet by ID with metrics"""
        try:
            self._log_api_call('get_tweet')
            return self.api.get_tweet(
                tweet_id,
                tweet_fields=fields or ['public_metrics', 'created_at']
            )
        except tweepy.errors.TooManyRequests as e:
            self._log_rate_limit('get_tweet')
            logger.error("\n=== TWITTER API ERROR DETAILS ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Full error object: {repr(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                logger.error(f"Response text: {e.response.text}")
            logger.error("=== END ERROR DETAILS ===\n")
            
            logger.warning("Note: Got rate limit despite wait_on_rate_limit=True")
            raise  # Let bot.py handle the retry
        except Exception as e:
            logger.error(f"Error getting tweet {tweet_id}: {e}")
            return None
            
    def get_tweet_responses(self, tweet_id: str) -> List[Dict]:
        """Get responses to a tweet"""
        try:
            self._log_api_call('search_tweets')
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
            
        except tweepy.errors.TooManyRequests as e:
            self._log_rate_limit('search_tweets')
            logger.error("\n=== TWITTER API ERROR DETAILS ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Full error object: {repr(e)}")
            if hasattr(e, 'response'):
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response headers: {e.response.headers}")
                logger.error(f"Response text: {e.response.text}")
            logger.error("=== END ERROR DETAILS ===\n")
            
            logger.warning("Note: Got rate limit despite wait_on_rate_limit=True")
            raise  # Let bot.py handle the retry
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
