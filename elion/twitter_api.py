"""
Twitter API integration for Elion
"""

import os
import logging
from typing import Optional
import tweepy

class TwitterAPI:
    """Handles Twitter API interactions"""
    
    def __init__(self):
        """Initialize Twitter API"""
        try:
            # Get credentials from environment
            self.client_id = os.getenv('TWITTER_CLIENT_ID')
            self.client_secret = os.getenv('TWITTER_CLIENT_SECRET')
            self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            # Check if we have credentials
            self.enabled = all([
                self.client_id,
                self.client_secret,
                self.access_token,
                self.access_token_secret,
                self.bearer_token
            ])
            
            if self.enabled:
                # Initialize client
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.client_id,
                    consumer_secret=self.client_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret
                )
                logging.info("Twitter API initialized")
            else:
                logging.warning("Twitter API disabled - missing credentials")
                
        except Exception as e:
            logging.error(f"Error initializing Twitter API: {e}")
            self.enabled = False
            
    def post_tweet(self, content: str) -> Optional[str]:
        """Post a tweet"""
        if not self.enabled:
            logging.warning("Twitter API not enabled")
            return None
            
        try:
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            logging.info(f"Tweet posted successfully: {tweet_id}")
            return tweet_id
        except Exception as e:
            logging.error(f"Error posting tweet: {e}")
            return None
            
    def reply_to_tweet(self, tweet_id: str, content: str) -> Optional[str]:
        """Reply to a tweet"""
        if not self.enabled:
            logging.warning("Twitter API not enabled")
            return None
            
        try:
            response = self.client.create_tweet(
                text=content,
                in_reply_to_tweet_id=tweet_id
            )
            reply_id = response.data['id']
            logging.info(f"Reply posted successfully: {reply_id}")
            return reply_id
        except Exception as e:
            logging.error(f"Error posting reply: {e}")
            return None
            
    def get_mentions(self, since_id: Optional[str] = None) -> list:
        """Get mentions timeline"""
        if not self.enabled:
            logging.warning("Twitter API not enabled")
            return []
            
        try:
            response = self.client.get_users_mentions(
                id=self.client.get_me().data.id,
                since_id=since_id
            )
            return response.data or []
        except Exception as e:
            logging.error(f"Error getting mentions: {e}")
            return []
            
    def get_tweet(self, tweet_id: str) -> Optional[dict]:
        """Get a specific tweet"""
        if not self.enabled:
            logging.warning("Twitter API not enabled")
            return None
            
        try:
            response = self.client.get_tweet(tweet_id)
            return response.data
        except Exception as e:
            logging.error(f"Error getting tweet: {e}")
            return None
