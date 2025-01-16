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
        
        # Rate limits for free tier
        self.rate_limits = {
            'search': {
                'requests_per_15min': 1,
                'buffer_minutes': 0.5  # Add 30 second buffer to be safe
            },
            'tweet': {'tweets_per_day': 16}  # Keep 1 buffer from 17 limit
        }
        
        # Enhanced cache configuration
        self.cache_duration = timedelta(hours=12)  # Cache for longer since we can't query often
        self.cache_expiry = datetime.now()
        self.max_cache_size = 500  # Store up to 500 tweets
        self.market_intel = []
        
        # Engagement thresholds for cache retention
        self.engagement_thresholds = {
            'high': {'retweets': 10, 'likes': 20},
            'medium': {'retweets': 5, 'likes': 10},
            'low': {'retweets': 2, 'likes': 5}
        }
        
        # Search categories - we'll rotate through these given our rate limits
        self.search_queries = {
            'ai_gaming': "(AI gaming OR GameFi) (launch OR partnership OR volume) ($10M OR $20M OR $50M) -is:retweet",
            'ai_tokens': "(AI token OR $MOG OR $BID) (mcap OR liquidity OR volume) ($500k OR $1M OR $5M) -is:retweet",
            'funding': "(AI gaming OR GameFi) (raise OR seed OR series) ($1M OR $5M OR $10M) (a16z OR binance OR USV) -is:retweet",
            'tech': "(Solana OR TON) (AI OR agents) (launch OR integration OR upgrade) -is:retweet"
        }
        
        # Track last search time and category
        self.last_search_time = datetime.now() - timedelta(minutes=15)  # Allow immediate first search
        self.current_category_index = 0
        
        # Initialize Elion's history manager
        self.history_manager = TweetHistoryManager()
        
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

    def _update_rate_limit(self, response, limit_type):
        """Update rate limit info from API response"""
        if hasattr(response, 'rate_limit_remaining'):
            self.rate_limits[limit_type]['remaining'] = int(response.rate_limit_remaining)
            self.rate_limits[limit_type]['reset_time'] = int(response.rate_limit_reset)

    def _get_engagement_level(self, metrics):
        """Calculate engagement level of a tweet"""
        if (metrics['retweet_count'] >= self.engagement_thresholds['high']['retweets'] or 
            metrics['like_count'] >= self.engagement_thresholds['high']['likes']):
            return 'high'
        elif (metrics['retweet_count'] >= self.engagement_thresholds['medium']['retweets'] or 
              metrics['like_count'] >= self.engagement_thresholds['medium']['likes']):
            return 'medium'
        return 'low'

    def _prune_cache(self):
        """Intelligently prune cache based on engagement and age"""
        if len(self.market_intel) <= self.max_cache_size:
            return
            
        # Sort by engagement level and age
        self.market_intel.sort(key=lambda x: (
            self._get_engagement_level(x['metrics']),
            datetime.fromisoformat(x['created_at'])
        ), reverse=True)
        
        # Keep top entries
        self.market_intel = self.market_intel[:self.max_cache_size]

    def gather_market_intel(self):
        """Gather market intelligence within rate limits"""
        try:
            current_time = datetime.now()
            
            # Check if we can make a new search request (15.5 minutes to be safe)
            wait_time = 15 + self.rate_limits['search']['buffer_minutes']
            time_since_last_search = (current_time - self.last_search_time).total_seconds() / 60
            
            if time_since_last_search < wait_time:
                minutes_remaining = wait_time - time_since_last_search
                print(f"Rate limit: Must wait {minutes_remaining:.1f} more minutes before next search")
                return bool(self.market_intel)
            
            # Rotate through categories
            categories = list(self.search_queries.keys())
            category = categories[self.current_category_index]
            self.current_category_index = (self.current_category_index + 1) % len(categories)
            
            query = self.search_queries[category]
            print(f"\nGathering intel for {category}...")
            
            try:
                response = self.api.search_recent_tweets(
                    query=query,
                    max_results=100,  # Get maximum results since we can only query rarely
                    tweet_fields=['created_at', 'public_metrics']
                )
                
                self.last_search_time = current_time
                
                if response.data:
                    fresh_intel = []
                    for tweet in response.data:
                        metrics = tweet.public_metrics
                        engagement_level = self._get_engagement_level(metrics)
                        
                        intel = {
                            'category': category,
                            'text': tweet.text,
                            'metrics': metrics,
                            'created_at': tweet.created_at.isoformat(),
                            'used': False,
                            'engagement_level': engagement_level
                        }
                        fresh_intel.append(intel)
                    
                    # Update market intel
                    self.market_intel.extend(fresh_intel)
                    self._prune_cache()
                    
                    print(f"Found {len(fresh_intel)} new items for {category}")
                    print(f"Next search available in {wait_time} minutes")
                    print(f"Next category will be: {categories[(self.current_category_index)]}")
                
            except Exception as e:
                print(f"Error in search: {str(e)}")
                return bool(self.market_intel)
            
            return bool(self.market_intel)
            
        except Exception as e:
            print(f"Error in market intelligence gathering: {e}")
            return bool(self.market_intel)

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

    def post_tweet(self, tweet_text):
        """Post tweet if within rate limits"""
        try:
            # Reset daily count if needed
            self._reset_daily_count()
            
            # Check if we've hit the daily limit
            if self.tweets_today >= self.daily_tweet_limit:
                print(f"Daily tweet limit reached ({self.tweets_today}/{self.daily_tweet_limit})")
                return False
            
            # Post the tweet
            response = self.api.create_tweet(text=tweet_text)
            if response.data:
                self.tweets_today += 1
                print(f"Tweet posted successfully at {datetime.now()}: {tweet_text}")
                print(f"Tweet ID: {response.data['id']}")
                print(f"Tweets today: {self.tweets_today}/{self.daily_tweet_limit}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return False
