import tweepy
import schedule
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os
import random
import json
from elion_personality import ELION_PROFILE, generate_elion_tweet, generate_elion_reply
from tweet_history_manager import TweetHistoryManager

# Load test environment variables
load_dotenv('.env.test')  # Load test environment first
load_dotenv(override=True)  # Then load production env if it exists

# Add debug logging
print("\nChecking environment variables...")
for var in ['TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET', 'TWITTER_ACCESS_TOKEN', 
            'TWITTER_ACCESS_TOKEN_SECRET', 'TWITTER_BEARER_TOKEN', 'AI_API_URL', 
            'AI_ACCESS_TOKEN', 'AI_MODEL_NAME']:
    print(f"{var} exists: {os.getenv(var) is not None}")

print("\nAfter loading .env:")
for var in ['TWITTER_CLIENT_ID', 'TWITTER_CLIENT_SECRET', 'TWITTER_ACCESS_TOKEN', 
            'TWITTER_ACCESS_TOKEN_SECRET', 'TWITTER_BEARER_TOKEN', 'AI_API_URL', 
            'AI_ACCESS_TOKEN', 'AI_MODEL_NAME']:
    print(f"{var} exists: {os.getenv(var) is not None}")

class AIGamingBot:
    def __init__(self):
        # Meta Llama setup
        base_url = os.getenv('AI_API_URL')
        if not base_url:
            raise ValueError("AI_API_URL environment variable is not set")
        self.ai_url = base_url.rstrip('/')  # Just use the base URL as is
        print(f"Using AI API URL: {self.ai_url}")
        
        self.ai_token = os.getenv('AI_ACCESS_TOKEN')
        if not self.ai_token:
            raise ValueError("AI_ACCESS_TOKEN environment variable is not set")
            
        self.model_name = os.getenv('AI_MODEL_NAME', 'meta-llama-3.3-70b-instruct')
        
        # Twitter API setup
        print("\nInitializing Twitter client...")
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN')
        )
        print("Twitter client initialized")
        
        # Rate limiting setup
        self.daily_tweet_limit = 16  # Keep 1 tweet buffer for errors
        self.tweets_today = 0
        self.last_reset = datetime.now()
        
        # Market intelligence storage
        self.market_intel = []
        
        # Search queries for different types of market intelligence
        self.search_queries = {
            'ai_gaming': "(AI gaming OR GameFi) (launch OR partnership OR volume) ($10M OR $20M OR $50M) -is:retweet",
            'ai_tokens': "(AI token OR $MOG OR $BID) (mcap OR liquidity OR volume) ($500k OR $1M OR $5M) -is:retweet",
            'funding': "(AI gaming OR GameFi) (raise OR seed OR series) ($1M OR $5M OR $10M) (a16z OR binance OR USV) -is:retweet",
            'tech': "(Solana OR TON) (AI OR agents) (launch OR integration OR upgrade) -is:retweet"
        }
        
        # Different intervals for each category (in minutes)
        self.category_intervals = {
            'ai_gaming': 180,    # Check AI gaming news every 3 hours
            'ai_tokens': 120,    # Check AI token metrics every 2 hours
            'funding': 240,      # Check funding news every 4 hours
            'tech': 180         # Check tech updates every 3 hours
        }
        
        # Initialize Elion's history manager
        self.history_manager = TweetHistoryManager()
        
        # Track last check time for each category
        self.last_checked = {category: 0 for category in self.search_queries}
        
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
            current_time = time.time()
            
            # Find categories that need checking based on intervals
            categories_to_check = []
            for category, interval in self.category_intervals.items():
                if current_time - self.last_checked[category] >= interval * 60:
                    categories_to_check.append(category)
            
            if not categories_to_check:
                print("\nNo categories need checking yet...")
                return True
            
            # Pick one random category from those that need checking
            category = random.choice(categories_to_check)
            self.last_checked[category] = current_time
            
            # First check if we have any unused cached intel
            unused_cached = [x for x in self.market_intel if not x['used']]
            if unused_cached:
                print("\nUsing cached market intelligence...")
                return True

            time.sleep(5)  # Wait before making request
            
            fresh_intel = []
            query = self.search_queries[category]
            
            print(f"\nSearching {category}...")
            try:
                tweets = self.api.search_recent_tweets(
                    query=query,
                    max_results=10,
                    tweet_fields=['created_at', 'public_metrics']
                )
                
                if tweets.data:
                    for tweet in tweets.data:
                        metrics = tweet.public_metrics
                        if (metrics['retweet_count'] > 2 or 
                            metrics['like_count'] > 5):
                            intel = {
                                'category': category,
                                'text': tweet.text,
                                'metrics': metrics,
                                'created_at': tweet.created_at.isoformat(),
                                'used': False
                            }
                            fresh_intel.append(intel)
                
                print(f"Found {len(fresh_intel)} items for {category}")
                
            except Exception as e:
                print(f"Error searching {category}: {str(e)}")
                if self.market_intel:
                    print("Falling back to cached intelligence...")
                    return True
                return False
            
            # Update market intel with new findings
            self.market_intel = ([x for x in self.market_intel if not x['used']] 
                               + fresh_intel)
            self._save_cached_intel()
            
            print(f"\nGathered total of {len(fresh_intel)} new market intel items")
            
            return len(fresh_intel) > 0 or len(self.market_intel) > 0
            
        except Exception as e:
            print(f"Error gathering market intel: {e}")
            # On error, try to use cached intel if available
            if self.market_intel:
                print("Falling back to cached intelligence...")
                return True
            return False

    def generate_tweet(self):
        """Generate market intelligence tweet using Meta Llama and gathered intel"""
        try:
            # Get unused market intel
            unused_intel = [x for x in self.market_intel if not x['used']]
            context = ""
            category = ""
            
            if unused_intel:
                # Use the most engaging piece of intel
                intel = max(unused_intel, 
                           key=lambda x: x['metrics']['like_count'] + x['metrics']['retweet_count'])
                context = f"Category: {intel['category']}\nTrend: {intel['text']}"
                category = intel['category']
                intel['used'] = True
                self._save_cached_intel()
            else:
                # Fallback to random category if no intel available
                category = random.choice(list(self.search_queries.keys()))
                context = f"Category: {category}\nGenerate a viral tweet about recent developments in {category}."
            
            print(f"\nGenerating tweet with context:\n{context}")
            
            # Get market mood from history
            market_mood = self.history_manager.get_market_mood()
            
            # Generate tweet with Elion's personality
            headers = {
                'Authorization': f'Bearer {self.ai_token}',
                'Content-Type': 'application/json'
            }
            
            # Get tweet content from Elion
            prompt = generate_elion_tweet(context, market_mood)
            
            data = {
                "messages": [{
                    "role": "system",
                    "content": prompt
                }],
                "model": self.model_name,
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            print("Making request to AI API...")
            response = requests.post(self.ai_url + "/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            
            tweet_content = response.json()['choices'][0]['message']['content'].strip()
            print(f"\nGenerated tweet ({len(tweet_content)} chars):")
            print(tweet_content)
            
            # Check for similarity with recent tweets
            if self.history_manager.is_recent_duplicate(tweet_content):
                print("[WARNING] Too similar to recent tweet, will try again")
                return False
            
            if len(tweet_content) > 280:
                print("[WARNING] Tweet too long, will try again")
                return False
            
            # Add to history before posting
            persona = self.history_manager.suggest_persona(category)
            self.history_manager.add_tweet(tweet_content, persona, category)
            
            # Post the tweet if ENABLE_POSTING is true
            if os.getenv('ENABLE_POSTING', 'false').lower() == 'true':
                print("\nPosting tweet...")
                tweet = self.api.create_tweet(text=tweet_content)
                print(f"Tweet posted successfully! ID: {tweet.data['id']}")
            else:
                print("\nSkipping tweet posting (ENABLE_POSTING is not true)")
            
            return tweet_content
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return False

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

def test_single_tweet():
    """Quick test of tweet generation"""
    # Check environment variables
    required_vars = [
        'TWITTER_BEARER_TOKEN',
        'TWITTER_CLIENT_ID',
        'TWITTER_CLIENT_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'AI_API_URL',
        'AI_ACCESS_TOKEN',
        'AI_MODEL_NAME'
    ]
    
    print("\nChecking environment variables...")
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return
    
    print("All required environment variables present!")
    
    bot = AIGamingBot()
    print("\nTesting single tweet generation...")
    bot.gather_market_intel()
    bot.generate_tweet()

if __name__ == "__main__":
    test_single_tweet()
