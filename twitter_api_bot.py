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
        print("\nInitializing Twitter bot...")
        
        # Initialize retry settings
        self.max_retries = 3
        self.base_wait = 5  # Base wait time in minutes
        self.retry_count = 0
        
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
        
        print("\nInitializing Twitter client...")
        # Create client for posting tweets (OAuth 1.0a)
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            wait_on_rate_limit=True
        )
        
        # Create client for searching (OAuth 2.0 App Only)
        self.search_api = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=True
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
        
        # Tweet tracking (use UTC for consistency)
        self.daily_tweet_count = 0
        self.daily_tweet_limit = 16  # Keep 1 buffer from 17 limit
        self.last_reset = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        self.last_tweet_time = None
        
        # Engagement thresholds for cache retention
        self.engagement_thresholds = {
            'high': {'retweets': 10, 'likes': 20},
            'medium': {'retweets': 5, 'likes': 10},
            'low': {'retweets': 2, 'likes': 5}
        }
        
        # Enhanced cache configuration with size monitoring
        self.cache_duration = timedelta(hours=12)
        self.cache_expiry = datetime.utcnow()
        self.max_cache_size = 500
        self.market_intel = []
        self.last_cache_cleanup = datetime.utcnow()
        self.intel_cache_file = 'market_intel_cache.json'
        
        # Track last search time and category
        self.last_search_time = datetime.utcnow() - timedelta(minutes=15)
        self.current_category_index = 0
        
        # Initialize Elion's history manager
        self.history_manager = TweetHistoryManager()
        
        # Search queries for different types of market intelligence
        self.search_queries = {
            'ai_gaming': "(AI gaming OR GameFi OR P2E) (launch OR partnership OR volume OR gaming OR NFT) (million OR funding OR users) -is:retweet",
            'ai_tokens': "(AI token OR blockchain AI OR AI crypto) (mcap OR liquidity OR volume OR AI) (million OR launch OR integration) -is:retweet",
            'funding': "(AI gaming OR GameFi OR P2E OR AI crypto) (raise OR seed OR series) (million OR funding) (VC OR venture) -is:retweet",
            'tech': "(blockchain OR L1 OR L2) (AI OR agents OR gaming) (launch OR integration OR upgrade OR partnership) -is:retweet"
        }
        
        # Load cached data
        self._load_cached_intel()

    def _should_reset_daily_count(self):
        """Check if we should reset the daily tweet count (using UTC)"""
        try:
            current_time = datetime.utcnow()
            current_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_day > self.last_reset:
                self.daily_tweet_count = 0
                self.last_reset = current_day
                self.retry_count = 0  # Reset retry counter on new day
                print(f"\nReset daily tweet count at {current_time} UTC")
                # Also clear old market intel on daily reset
                self._clear_old_market_intel()
                return True
            return False
        except Exception as e:
            print(f"Error in daily reset check: {e}")
            return False

    def _clear_old_market_intel(self):
        """Clear old market intelligence to manage memory"""
        try:
            current_time = datetime.utcnow()
            
            # Only clean up if enough time has passed (every 6 hours)
            if (current_time - self.last_cache_cleanup).total_seconds() < 21600:  # 6 hours
                return
                
            initial_size = len(self.market_intel)
            
            # Keep only intel from the last 24 hours
            self.market_intel = [
                intel for intel in self.market_intel 
                if (current_time - datetime.fromisoformat(intel['created_at'])).total_seconds() < 86400
            ]
            
            # Trim to max size if still too large
            if len(self.market_intel) > self.max_cache_size:
                self.market_intel = self.market_intel[-self.max_cache_size:]
            
            cleaned_count = initial_size - len(self.market_intel)
            if cleaned_count > 0:
                print(f"\nCleared {cleaned_count} old market intel entries")
                print(f"Cache size: {len(self.market_intel)}/{self.max_cache_size}")
            
            # Update cleanup time
            self.last_cache_cleanup = current_time
            
            # Clear history manager periodically
            self.history_manager.clear_old_history()
            
        except Exception as e:
            print(f"Error clearing old market intel: {e}")

    def _handle_rate_limit(self, wait_minutes):
        """Handle rate limit with exponential backoff"""
        if self.retry_count >= self.max_retries:
            wait_minutes = min(wait_minutes * (2 ** self.retry_count), 60)  # Cap at 60 minutes
        print(f"\nRate limit: Waiting {wait_minutes:.1f} minutes before retry")
        time.sleep(wait_minutes * 60)
        self.retry_count += 1

    def gather_market_intel(self):
        """Gather market intelligence while respecting rate limits"""
        try:
            current_time = datetime.utcnow()
            
            # Check if we have cached intel we can use
            unused_intel = [x for x in self.market_intel if not x.get('used', False)]
            if unused_intel:
                print("\nUsing cached market intelligence")
                return True
                
            # Check rate limits
            minutes_since_last = float('inf')
            if self.last_search_time:
                minutes_since_last = (current_time - self.last_search_time).total_seconds() / 60
            
            # Strict rate limit: 1 request per 15 minutes
            if minutes_since_last < 15:  # Twitter's actual limit
                wait_minutes = 15 - minutes_since_last
                print(f"\nRate limit: Must wait {wait_minutes:.1f} minutes before next search")
                time.sleep(wait_minutes * 60)
            
            # Get next category to search
            categories = list(self.search_queries.keys())
            category = categories[self.current_category_index]
            query = self.search_queries[category]
            
            # Update for next time
            self.current_category_index = (self.current_category_index + 1) % len(categories)
            self.last_search_time = current_time
            
            # Perform the search
            print(f"\nGathering intelligence for category: {category}")
            response = self._search_tweets(query)
            
            if response:
                fresh_intel = []
                for tweet in response:
                    intel = {
                        'category': category,
                        'text': tweet.get('text', ''),
                        'created_at': tweet.get('created_at', current_time.isoformat()),
                        'metrics': {
                            'retweet_count': tweet.get('metrics', {}).get('retweet_count', 0),
                            'like_count': tweet.get('metrics', {}).get('like_count', 0)
                        },
                        'used': False
                    }
                    fresh_intel.append(intel)
                
                self.market_intel.extend(fresh_intel)
                self._prune_cache()
                self._save_cached_intel()
                
                print(f"Found {len(fresh_intel)} new items for {category}")
                print(f"Next search available in 15 minutes")
                return True
            
            print(f"No new tweets found for {category}")
            return False
                
        except Exception as e:
            print(f"\nError gathering market intel: {e}")
            return False

    def _search_tweets(self, query):
        """Search for tweets matching query"""
        try:
            # Use the search_api client for searching
            tweets = self.search_api.search_recent_tweets(
                query=query,
                max_results=100,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            if not tweets.data:
                return []
                
            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'metrics': {
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count']
                    }
                })
            return results
            
        except Exception as e:
            print(f"\nSearch attempt failed: {e}")
            return []

    def post_tweet(self, tweet_content, reply_to=None):
        """Post tweet if within rate limits"""
        try:
            if isinstance(tweet_content, list):  # It's a thread
                previous_tweet_id = None
                for tweet in tweet_content:
                    if self.daily_tweet_count >= self.daily_tweet_limit:
                        print("Daily tweet limit reached")
                        return None
                        
                    response = self.api.create_tweet(
                        text=tweet,
                        in_reply_to_tweet_id=previous_tweet_id
                    )
                    if response and response.data:
                        previous_tweet_id = response.data['id']
                        self.daily_tweet_count += 1
                        time.sleep(2)  # Small delay between thread tweets
                return previous_tweet_id
            else:  # Single tweet
                if self.daily_tweet_count >= self.daily_tweet_limit:
                    print("Daily tweet limit reached")
                    return None
                    
                response = self.api.create_tweet(
                    text=tweet_content,
                    in_reply_to_tweet_id=reply_to
                )
                if response and response.data:
                    self.daily_tweet_count += 1
                    return response.data['id']
                    
        except Exception as e:
            print(f"Error posting tweet: {e}")
            if "duplicate content" in str(e).lower():
                print("Duplicate tweet detected, will try again with different content")
                return None
            self._handle_rate_limit(self.base_wait)
        return None

    def get_tweet_type_for_next_post(self):
        """Determine next tweet type based on position in cycle and engagement"""
        total_tweets = self.history_manager.history['metadata']['total_tweets']
        position_in_cycle = total_tweets % 50
        
        # Check remaining daily tweets
        remaining_tweets = self.daily_tweet_limit - self.daily_tweet_count
        
        # Don't start threads if we're low on remaining tweets
        if remaining_tweets < 4:  # Need buffer for threads
            return 'regular'
        
        # Get engagement stats
        recent_engagement = self.history_manager.get_recent_engagement(hours=24)
        
        # If engagement is low and we have enough tweet quota, do a thread
        if recent_engagement < 10 and remaining_tweets >= 4:  # Low engagement threshold
            if position_in_cycle in [15, 35]:  # Reduced thread spots
                return 'controversial_thread'
        else:
            # Normal distribution with thread consideration
            if position_in_cycle == 25 and remaining_tweets >= 4:  # One prime thread spot
                return 'controversial_thread' if random.random() < 0.7 else 'controversial'
        
        # Rest of the logic
        if position_in_cycle in [45]:  # Reduced giveaway frequency
            return 'giveaway'
        elif position_in_cycle in [10, 30]:
            return 'ai_aware'
        return 'regular'

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

    def generate_tweet(self):
        """Generate market intelligence tweet using Meta Llama and gathered intel"""
        try:
            # Get unused market intel
            unused_intel = [x for x in self.market_intel if not x.get('used', False)]
            context = ""
            category = ""
            
            if unused_intel:
                # Use the most engaging piece of intel
                intel = max(unused_intel, 
                           key=lambda x: (x.get('metrics', {}).get('like_count', 0) + 
                                        x.get('metrics', {}).get('retweet_count', 0)))
                context = f"Category: {intel.get('category', 'ai_gaming')}\nTrend: {intel.get('text', '')}"
                category = intel.get('category', 'ai_gaming')
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
            
            return tweet_content
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return False

    def check_rate_limits(self):
        """Check current rate limit status"""
        try:
            # Get rate limit status for search endpoint
            response = self.search_api.get_recent_tweets_count("test")  # Lightweight query
            
            # Rate limits are in response headers
            headers = response.response.headers
            
            # Extract rate limit info
            remaining = headers.get('x-rate-limit-remaining', 'Unknown')
            reset_time = headers.get('x-rate-limit-reset', 'Unknown')
            limit = headers.get('x-rate-limit-limit', 'Unknown')
            
            if reset_time != 'Unknown':
                reset_time = datetime.fromtimestamp(int(reset_time))
                wait_time = (reset_time - datetime.utcnow()).total_seconds()
                wait_minutes = max(0, wait_time / 60)
            else:
                wait_minutes = 'Unknown'
            
            print(f"\nRate Limit Status:")
            print(f"Remaining calls: {remaining}")
            print(f"Total limit: {limit}")
            print(f"Reset in: {wait_minutes:.1f} minutes" if wait_minutes != 'Unknown' else "Reset time: Unknown")
            
            return {
                'remaining': remaining,
                'limit': limit,
                'reset_minutes': wait_minutes
            }
            
        except Exception as e:
            print(f"Error checking rate limits: {e}")
            return None

    def run(self):
        """Main bot loop - runs continuously"""
        print("\nStarting bot operations...")
        
        while True:
            try:
                # Check rate limits first
                limits = self.check_rate_limits()
                if limits and limits['remaining'] != 'Unknown' and int(limits['remaining']) < 2:
                    wait_mins = limits['reset_minutes']
                    if wait_mins != 'Unknown':
                        print(f"\nRate limit almost exhausted. Waiting {wait_mins:.1f} minutes...")
                        time.sleep(wait_mins * 60)
                        continue
                
                # Try to gather market intelligence with retry logic
                if self.gather_market_intel():
                    print("\nSuccessfully gathered market intelligence")
                else:
                    print("\nNo new market intelligence gathered")
                
                # Try to post a tweet with retry logic
                if self.post_tweet(self.generate_tweet()):
                    print("\nWaiting 90 minutes before next tweet...")
                    time.sleep(90 * 60)  # 90 minutes between tweets
                else:
                    print("\nWaiting 5 minutes before retry...")
                    time.sleep(5 * 60)
                
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
