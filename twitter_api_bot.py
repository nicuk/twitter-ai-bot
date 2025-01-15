import tweepy
import schedule
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os
import random
import json

load_dotenv()

class AIGamingBot:
    def __init__(self):
        # Meta Llama setup
        self.ai_url = os.getenv('AI_API_URL')
        self.ai_token = os.getenv('AI_ACCESS_TOKEN')
        
        # Twitter API setup
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        )
        
        # Rate limiting setup
        self.daily_tweet_limit = 16  # Keep 1 tweet buffer for errors
        self.tweets_today = 0
        self.last_reset = datetime.now()
        
        # Market intelligence storage
        self.market_intel = []
        
        # Search queries
        self.search_queries = {
            "ai_gaming": "AI gaming (NFT OR P2E OR GameFi) -is:retweet",
            "tokens": "(AGAME OR ATLAS OR AXS OR IMX OR GALA OR GOAT OR AO OR SAI OR TAO) (launch OR partnership OR announcement) -is:retweet",
            "funding": "(gaming OR GameFi OR P2E) (raise OR funding OR investment) -is:retweet",
            "tech": "(AI OR gaming) (infrastructure OR SDK OR engine) (launch OR update) -is:retweet"
        }
        
        # Load cached intel if exists
        self.intel_cache_file = "market_intel_cache.json"
        self._load_cached_intel()

    def _load_cached_intel(self):
        """Load cached market intelligence"""
        try:
            if os.path.exists(self.intel_cache_file):
                with open(self.intel_cache_file, 'r') as f:
                    self.market_intel = json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}")

    def _save_cached_intel(self):
        """Save market intelligence to cache"""
        try:
            with open(self.intel_cache_file, 'w') as f:
                json.dump(self.market_intel, f)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _reset_daily_count(self):
        """Reset daily tweet count if 24 hours have passed"""
        now = datetime.now()
        if (now - self.last_reset) >= timedelta(hours=24):
            self.tweets_today = 0
            self.last_reset = now
            print(f"Daily tweet count reset at {now}")

    def gather_market_intel(self):
        """Gather market intelligence from Twitter searches"""
        try:
            fresh_intel = []
            for category, query in self.search_queries.items():
                tweets = self.api.search_recent_tweets(
                    query=query,
                    max_results=10,
                    tweet_fields=['created_at', 'public_metrics']
                )
                
                if tweets.data:
                    for tweet in tweets.data:
                        # Filter for high engagement tweets
                        metrics = tweet.public_metrics
                        if (metrics['retweet_count'] > 5 or 
                            metrics['like_count'] > 10):
                            intel = {
                                'category': category,
                                'text': tweet.text,
                                'metrics': metrics,
                                'created_at': tweet.created_at.isoformat(),
                                'used': False
                            }
                            fresh_intel.append(intel)
            
            # Update market intel with new findings
            self.market_intel = ([x for x in self.market_intel if not x['used']] 
                               + fresh_intel)
            self._save_cached_intel()
            
            print(f"Gathered {len(fresh_intel)} new market intel items")
            
        except Exception as e:
            print(f"Error gathering market intel: {e}")

    def generate_tweet(self):
        """Generate market intelligence tweet using Meta Llama and gathered intel"""
        # Get unused market intel
        unused_intel = [x for x in self.market_intel if not x['used']]
        context = ""
        
        if unused_intel:
            # Use the most engaging piece of intel
            intel = max(unused_intel, 
                       key=lambda x: x['metrics']['like_count'] + x['metrics']['retweet_count'])
            context = f"Category: {intel['category']}\nTrend: {intel['text']}"
            intel['used'] = True
            self._save_cached_intel()
        else:
            # Fallback to random context if no intel available
            category = random.choice(list(self.search_queries.keys()))
            context = f"Category: {category}"
        
        headers = {
            'Authorization': f'Bearer {self.ai_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "method": "completion",
            "payload": {
                "messages": [{
                    "role": "system",
                    "content": """You are an AI market intelligence bot focused on AI Gaming and Web3 projects.
                    Format tweets as:
                    [PROJECT NEWS]
                    - Key metric or announcement
                    - Supporting data point
                    - Insider insight or edge
                    
                    Keep it factual, focus on metrics, and provide insider perspective.
                    IMPORTANT: Keep tweets under 280 characters."""
                }, {
                    "role": "user",
                    "content": f"Generate a market intelligence tweet about this trend:\n{context}"
                }],
                "max_tokens": 100,
                "stream": False
            }
        }
        
        try:
            response = requests.post(self.ai_url, headers=headers, json=data)
            response.raise_for_status()
            tweet = response.json()['choices'][0]['message']['content'].strip()
            return tweet[:280]  # Ensure tweet length compliance
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

    def post_tweet(self):
        """Post tweet if within rate limits"""
        self._reset_daily_count()
        
        if self.tweets_today >= self.daily_tweet_limit:
            print(f"Daily tweet limit reached ({self.tweets_today}/{self.daily_tweet_limit})")
            return

        tweet = self.generate_tweet()
        if tweet:
            try:
                self.api.create_tweet(text=tweet)
                self.tweets_today += 1
                print(f"Tweet posted successfully at {datetime.now()}: {tweet}")
                print(f"Tweets today: {self.tweets_today}/{self.daily_tweet_limit}")
            except Exception as e:
                print(f"Error posting tweet: {e}")

def main():
    bot = AIGamingBot()
    
    # Schedule tweets every 90 minutes
    schedule.every(90).minutes.do(bot.post_tweet)
    
    # Initial tweet
    bot.post_tweet()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
