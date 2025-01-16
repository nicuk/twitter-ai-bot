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
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Load test environment variables
load_dotenv('.env.test')  # Load test environment first
load_dotenv(override=True)  # Then load production env if it exists

def check_environment_variables():
    """Check if all required environment variables are set"""
    required_vars = [
        'TWITTER_CLIENT_ID',
        'TWITTER_CLIENT_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN',
        'AI_API_URL',
        'AI_ACCESS_TOKEN',
        'AI_MODEL_NAME'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        return False
    
    print("✓ All required environment variables are set")
    return True

class AIGamingBot:
    def __init__(self):
        """Initialize the Twitter bot"""
        print("\nInitializing Twitter client...")
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
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
        
        # Initialize daily tweet count
        self.daily_tweet_count = 0
        self.daily_tweet_limit = 16  # Keep 1 buffer from 17 limit
        
        # Enhanced cache configuration
        self.cache_duration = timedelta(hours=12)  # Cache for longer since we can't query often
        self.cache_expiry = datetime.now()
        self.max_cache_size = 500  # Store up to 500 tweets
        self.market_intel = []
        
        # Track last search time and category
        self.last_search_time = datetime.now() - timedelta(minutes=15)  # Allow immediate first search
        self.current_category_index = 0
        
        # Initialize Elion's history manager
        self.history_manager = TweetHistoryManager()
        
        # Search queries for different types of market intelligence
        self.search_queries = {
            'ai_gaming': "(AI gaming OR GameFi) (launch OR partnership OR volume) ($10M OR $20M OR $50M) -is:retweet",
            'ai_tokens': "(AI token OR $MOG OR $BID) (mcap OR liquidity OR volume) ($500k OR $1M OR $5M) -is:retweet",
            'funding': "(AI gaming OR GameFi) (raise OR seed OR series) ($1M OR $5M OR $10M) (a16z OR binance OR USV) -is:retweet",
            'tech': "(Solana OR TON) (AI OR agents) (launch OR integration OR upgrade) -is:retweet"
        }

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

    def post_tweet(self):
        """Post tweet if within rate limits"""
        try:
            # Reset daily count if needed
            self._reset_daily_count()
            
            # Check if we've hit the daily limit
            if self.daily_tweet_count >= self.daily_tweet_limit:
                print(f"Daily tweet limit reached ({self.daily_tweet_count}/{self.daily_tweet_limit})")
                return False
            
            # Generate and post the tweet
            tweet_text = self.generate_tweet()
            if tweet_text:
                response = self.api.create_tweet(text=tweet_text)
                if response.data:
                    self.daily_tweet_count += 1
                    print(f"Tweet posted successfully at {datetime.now()}: {tweet_text}")
                    print(f"Tweet ID: {response.data['id']}")
                    print(f"Tweets today: {self.daily_tweet_count}/{self.daily_tweet_limit}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error posting tweet: {e}")
            return False

    def run(self):
        """Main bot loop - runs continuously"""
        print("\nStarting bot operations...")
        
        while True:
            try:
                current_time = datetime.now()
                
                # Reset daily tweet count at midnight
                if current_time.hour == 0 and current_time.minute < 5:
                    self.daily_tweet_count = 0
                    print("\nReset daily tweet count")
                
                # Try to gather market intelligence
                if self.gather_market_intel():
                    print("\nSuccessfully gathered market intelligence")
                else:
                    print("\nNo new market intelligence gathered")
                
                # Check if we can post a tweet
                if self.daily_tweet_count < self.daily_tweet_limit:
                    if self.post_tweet():
                        print("\nWaiting 90 minutes before next tweet...")
                        time.sleep(90 * 60)  # 90 minutes between tweets
                    else:
                        print("\nTweet failed, waiting 5 minutes before retry...")
                        time.sleep(5 * 60)
                else:
                    # Calculate time until midnight reset
                    seconds_until_midnight = (
                        ((24 - current_time.hour - 1) * 3600) +
                        ((60 - current_time.minute - 1) * 60) +
                        (60 - current_time.second)
                    )
                    print(f"\nDaily tweet limit reached. Waiting {seconds_until_midnight//3600} hours until reset")
                    time.sleep(min(3600, seconds_until_midnight))  # Sleep max 1 hour
                
            except Exception as e:
                print(f"\nError in main loop: {e}")
                print("Waiting 5 minutes before retry...")
                time.sleep(5 * 60)

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            try:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                }
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                print(f"Error in healthcheck: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress logging of requests"""
        return

def start_healthcheck_server(port=None):
    """Start the healthcheck server in a separate thread"""
    if port is None:
        port = int(os.getenv('PORT', 8080))
    
    host = os.getenv('HOST', '0.0.0.0')
    
    try:
        server = HTTPServer((host, port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        print(f"✓ Healthcheck server running on {host}:{port}")
        return server
    except Exception as e:
        print(f"Error starting healthcheck server: {e}")
        return None

def main():
    """Main function to run the Twitter bot"""
    print("\nInitializing Twitter AI Bot...")
    
    if not check_environment_variables():
        sys.exit(1)
    
    try:
        # Start healthcheck server first
        if not start_healthcheck_server():
            print("Failed to start healthcheck server")
            sys.exit(1)
        
        # Initialize and run the bot
        bot = AIGamingBot()
        bot.run()
    except Exception as e:
        print(f"Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
