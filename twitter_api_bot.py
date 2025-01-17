import sys
import os
import time
import json
from datetime import datetime, timedelta
import tweepy
import schedule
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import random
from elion.elion import Elion

# Load environment variables
load_dotenv()

def check_environment():
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
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        print("Error: Missing environment variables:", ", ".join(missing))
        return False
    return True

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def start_healthcheck(port=8080):
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Healthcheck server running on 0.0.0.0:{port}")

class TwitterBot:
    def __init__(self):
        print("\nInitializing Twitter bot...")
        
        # Initialize retry settings
        self.max_retries = 3
        self.base_wait = 5  # Base wait time in minutes
        self.retry_count = 0
        
        # Track rate limits
        self.rate_limits = {
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
                'daily_limit': 17,  # Keep 1 buffer from 18 limit
                'monthly_limit': 100  # Twitter's monthly post cap
            },
            'search': {
                'daily_searches': 0,
                'monthly_posts_pulled': 0,
                'monthly_post_limit': 500000,  # Twitter's monthly post pull limit
                'last_search': None
            }
        }
        
        # Initialize Twitter API clients
        print("Initializing Twitter client...")
        self.api = tweepy.Client(
            consumer_key=os.getenv('TWITTER_CLIENT_ID'),
            consumer_secret=os.getenv('TWITTER_CLIENT_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=True
        )
        print("Twitter client initialized")
        
        # Initialize Elion
        model_name = os.getenv('AI_MODEL_NAME', 'meta-llama-3.3-70b-instruct')
        self.elion = Elion(llm=model_name)
        
        # Set up tweet schedule
        self._setup_schedule()
        
        # Load cached data if exists
        self._load_cache()
        
        # Initialize response tracking
        self.response_cache = self._load_response_cache()
    
    def _setup_schedule(self):
        """Set up the tweet schedule"""
        # Main content schedule (every 4 hours)
        schedule.every(4).hours.do(self.run_cycle)
        
        # Engagement schedule (every 2 hours, offset by 1 hour from main content)
        schedule.every(2).hours.do(self.engagement_cycle)
        
        # Response checking (every hour)
        schedule.every(1).hours.do(self.check_responses)
        
        # Cache cleanup (daily)
        schedule.every().day.at("00:00").do(self._cleanup_cache)
    
    def _can_post_tweet(self) -> bool:
        """Check if we can post a tweet based on rate limits"""
        current_time = datetime.utcnow()
        
        # Reset daily count if needed
        if current_time - self.rate_limits['post']['last_reset'] > timedelta(days=1):
            self.rate_limits['post']['daily_count'] = 0
            self.rate_limits['post']['last_reset'] = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Reset monthly count if needed
        if current_time - self.rate_limits['post']['monthly_reset'] > timedelta(days=30):
            self.rate_limits['post']['monthly_count'] = 0
            self.rate_limits['post']['monthly_reset'] = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Check limits
        if self.rate_limits['post']['daily_count'] >= self.rate_limits['post']['daily_limit']:
            print("Daily tweet limit reached")
            return False
            
        if self.rate_limits['post']['monthly_count'] >= self.rate_limits['post']['monthly_limit']:
            print("Monthly tweet limit reached")
            return False
        
        return True
    
    def _update_post_counts(self):
        """Update tweet count after successful post"""
        self.rate_limits['post']['daily_count'] += 1
        self.rate_limits['post']['monthly_count'] += 1
        self._save_cache()
    
    def _load_cache(self):
        """Load cached data"""
        try:
            if os.path.exists('bot_cache.json'):
                with open('bot_cache.json', 'r') as f:
                    cache = json.load(f)
                    self.rate_limits = cache.get('rate_limits', self.rate_limits)
        except Exception as e:
            print(f"Error loading cache: {e}")
    
    def _save_cache(self):
        """Save cache data"""
        try:
            cache = {
                'rate_limits': self.rate_limits
            }
            with open('bot_cache.json', 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def _load_response_cache(self):
        """Load cached responses"""
        try:
            if os.path.exists('response_cache.json'):
                with open('response_cache.json', 'r') as f:
                    return json.load(f)
            return {
                'questions': {},  # tweet_id -> question data
                'responses': {},  # tweet_id -> response data
                'featured_projects': {
                    'memes': set(),
                    'ai': set(),
                    'gamefi': set()
                }
            }
        except Exception as e:
            print(f"Error loading response cache: {e}")
            return None
    
    def _save_response_cache(self):
        """Save response cache"""
        try:
            # Convert sets to lists for JSON serialization
            cache = self.response_cache.copy()
            cache['featured_projects'] = {
                k: list(v) for k, v in cache['featured_projects'].items()
            }
            with open('response_cache.json', 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            print(f"Error saving response cache: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache data"""
        try:
            self._load_cache()  # Ensure we have latest data
            current_time = datetime.utcnow()
            
            # Reset counts if needed
            if current_time - self.rate_limits['post']['last_reset'] > timedelta(days=1):
                self.rate_limits['post']['daily_count'] = 0
                self.rate_limits['post']['last_reset'] = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_time - self.rate_limits['post']['monthly_reset'] > timedelta(days=30):
                self.rate_limits['post']['monthly_count'] = 0
                self.rate_limits['post']['monthly_reset'] = current_time.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Clean up old responses
            if self.response_cache:
                for cache_type in ['questions', 'responses']:
                    old_items = []
                    for tweet_id, data in self.response_cache[cache_type].items():
                        if current_time - datetime.fromisoformat(data['time']) > timedelta(days=7):
                            old_items.append(tweet_id)
                    for tweet_id in old_items:
                        del self.response_cache[cache_type][tweet_id]
                
                # Reset featured projects every week
                if any(len(projects) > 100 for projects in self.response_cache['featured_projects'].values()):
                    self.response_cache['featured_projects'] = {
                        'memes': set(),
                        'ai': set(),
                        'gamefi': set()
                    }
                
                self._save_response_cache()
            
            self._save_cache()
        except Exception as e:
            print(f"Error cleaning cache: {e}")
    
    def check_responses(self):
        """Check responses to recent tweets"""
        try:
            if not self.response_cache:
                return
                
            current_time = datetime.utcnow()
            
            # Check unchecked questions from last 24 hours
            for qid, qdata in self.response_cache['questions'].items():
                if qdata.get('responses_checked'):
                    continue
                    
                question_time = datetime.fromisoformat(qdata['time'])
                if (current_time - question_time).total_seconds() > 24 * 3600:
                    continue
                
                # Get replies using API
                try:
                    search_query = f"conversation_id:{qid}"
                    replies = self.api.search_recent_tweets(
                        query=search_query,
                        max_results=100,
                        tweet_fields=['public_metrics', 'author_id']
                    )
                    
                    if replies.data:
                        for reply in replies.data:
                            reply_id = str(reply.id)
                            
                            # Skip if already processed
                            if reply_id in self.response_cache['responses']:
                                continue
                            
                            engagement_score = reply.public_metrics['like_count'] + reply.public_metrics['retweet_count']
                            
                            # Cache responses with good engagement
                            if engagement_score >= 5:
                                self.response_cache['responses'][reply_id] = {
                                    'text': reply.text,
                                    'author_id': reply.author_id,
                                    'engagement_score': engagement_score,
                                    'time': current_time.isoformat(),
                                    'used': False
                                }
                    
                    # Mark question as checked
                    qdata['responses_checked'] = True
                    
                except Exception as e:
                    print(f"Error getting replies for {qid}: {e}")
                    continue
            
            self._save_response_cache()
            
        except Exception as e:
            print(f"Error checking responses: {e}")
    
    def run_cycle(self):
        """Run a single tweet cycle"""
        try:
            if not self._can_post_tweet():
                return
            
            # Get tweet content from Elion
            tweet = self.elion.generate_tweet()
            if tweet:
                # Post tweet
                response = self.api.create_tweet(text=tweet)
                print(f"Tweet posted: {tweet}")
                
                # Update counts
                self._update_post_counts()
                
                # Let Elion analyze performance
                self.elion.analyze_performance({
                    'id': response.data['id'],
                    'text': tweet,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                # Track if it's a question
                if '?' in tweet:
                    self.response_cache['questions'][str(response.data['id'])] = {
                        'text': tweet,
                        'time': datetime.utcnow().isoformat(),
                        'responses_checked': False,
                        'topic': self._detect_topic(tweet)
                    }
                    self._save_response_cache()
        except Exception as e:
            print(f"Error in tweet cycle: {e}")
            self.retry_count += 1
            if self.retry_count < self.max_retries:
                time.sleep(self.base_wait * (2 ** self.retry_count))  # Exponential backoff
                self.run_cycle()  # Retry
            else:
                self.retry_count = 0
    
    def _detect_topic(self, text):
        """Detect tweet topic"""
        text = text.lower()
        if any(word in text for word in ['meme', 'doge', 'pepe']):
            return 'memes'
        elif any(word in text for word in ['ai', 'artificial', 'intelligence', 'bot']):
            return 'ai'
        else:
            return 'gamefi'  # Default to gamefi
    
    def engagement_cycle(self):
        """Run engagement cycle"""
        try:
            if not self._can_post_tweet():
                return
            
            # First try to feature a good response
            featured = False
            if self.response_cache and random.random() < 0.3:  # 30% chance to feature response
                for cache_type in ['responses']:
                    items = [
                        (tid, data) for tid, data in self.response_cache[cache_type].items()
                        if not data['used'] and data['engagement_score'] >= 5
                    ]
                    if items:
                        tweet_id, data = random.choice(items)
                        try:
                            # Get username
                            author = self.api.get_user(id=data['author_id'])
                            username = f"@{author.data.username}"
                            
                            # Create feature tweet
                            tweet = f"Great insight from {username}! {data['text'][:100]}..."
                            response = self.api.create_tweet(
                                text=tweet,
                                in_reply_to_tweet_id=tweet_id
                            )
                            print(f"Featured response: {tweet}")
                            
                            # Mark as used
                            data['used'] = True
                            self._save_response_cache()
                            
                            featured = True
                            break
                        except Exception as e:
                            print(f"Error featuring response: {e}")
                            continue
            
            # If no feature, do regular engagement
            if not featured:
                engagement = self.elion.handle_engagement()
                if engagement:
                    response = self.api.create_tweet(
                        text=engagement['text'],
                        in_reply_to_tweet_id=engagement.get('reply_to')
                    )
                    print(f"Engagement tweet posted: {engagement['text']}")
            
            self._update_post_counts()
            
        except Exception as e:
            print(f"Error in engagement cycle: {e}")
    
    def run(self):
        """Run the bot continuously"""
        print("Starting Twitter bot...")
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    print("Initializing Twitter AI Bot...")
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Start healthcheck server for Railway
    start_healthcheck()
    
    # Start bot
    bot = TwitterBot()
    bot.run()

if __name__ == "__main__":
    main()
