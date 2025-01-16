import tweepy
import schedule
import time
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv
import os
import random
import json
from elion_personality import ElionPersonality, generate_elion_tweet, generate_elion_reply
from tweet_history_manager import TweetHistoryManager
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re
import uuid
from market_intel_gatherer import MarketIntelGatherer

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
    
    print("[OK] All required environment variables are set")
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
            wait_on_rate_limit=False  # Don't wait automatically
        )
        
        # Create client for searching (OAuth 2.0 App Only)
        self.search_api = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            wait_on_rate_limit=False  # Don't wait automatically
        )
        print("Twitter client initialized")
        
        # Track rate limit info for different endpoints
        self.rate_limits = {
            'search': {
                'remaining': None,
                'reset_time': None,
                'last_checked': None,
                'daily_searches': 0,
                'daily_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            },
            'timeline': {
                'remaining': None,
                'reset_time': None,
                'last_checked': None,
                'daily_engagement_posts': 0,
                'max_daily_engagement': 3  # Maximum engagement posts per day
            },
            'post': {
                'daily_count': 0,
                'monthly_count': 0,
                'last_reset': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0),
                'monthly_reset': datetime.utcnow().replace(day=15, hour=0, minute=0, second=0, microsecond=0),
                'daily_limit': 17,  # Keep 1 buffer from 18 limit
                'monthly_limit': 100  # Twitter's monthly post cap
            }
        }
        
        # Tweet tracking (use UTC for consistency)
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
        
        # Add new tracking for last search per category
        self.last_category_search = {
            'ai_gaming': None,
            'ai_tokens': None,
            'funding': None,
            'tech': None
        }
        
        # Add tracking for engagement tweets and responses
        self.engagement_tweets = {
            'last_question_id': None,
            'last_question_time': None,
            'pending_responses': [],  # Store high-engagement responses to feature
            'featured_projects': set()  # Track projects we've already featured
        }
        
        # Add engagement question templates
        self.engagement_questions = [
            "What's your favorite #GameFi project right now? Tell me why! ",
            "Shill me your best performing #crypto gaming token! What makes it special? ",
            "Which #P2E game has the most potential in 2025? Share your thoughts! ",
            "What's the most innovative #blockchain game you've played? Why did you love it? ",
            "Looking for the next big #NFTGame - what project should I check out? ",
            "Which gaming #memecoin has the strongest community? Convince me! ",
            "What's your favorite AI feature in a blockchain game? Share examples! ",
            "Which gaming guild is crushing it right now? Why do they stand out? ",
            "Searching for undervalued gaming tokens - what's flying under the radar? ",
            "What's the most fun P2E game you've played? Shill me your favorite! "
        ]
        
        # Expand engagement topics
        self.engagement_topics = {
            'memes': {
                'questions': [
                    "What's the most undervalued #memecoin right now? Shill me! ",
                    "Which meme community is the most active? Show me some proof! ",
                    "Shill me your favorite dog coin that isn't $DOGE! Why is it special? ",
                    "What's the next big meme trend in crypto? Share your predictions! ",
                    "Which meme token has the best utility? Convince me! "
                ],
                'featured': set()
            },
            'ai': {
                'questions': [
                    "What's the most innovative #AI project you've seen? Why? ",
                    "Which AI token has the strongest fundamentals? Share your analysis! ",
                    "Shill me your favorite AI x Crypto project! What makes it unique? ",
                    "What's the most practical use of AI in blockchain? Show examples! ",
                    "Which AI project is revolutionizing DeFi? Tell me more! "
                ],
                'featured': set()
            },
            'gamefi': {
                'questions': [
                    "What's your favorite #GameFi project right now? Tell me why! ",
                    "Shill me your best performing gaming token! What makes it special? ",
                    "Which #P2E game has the most potential? Share your thoughts! ",
                    "What's the most innovative blockchain game you've played? ",
                    "Which gaming guild is crushing it right now? Why? "
                ],
                'featured': set()
            }
        }
        
        # Initialize response cache
        self.response_cache_file = 'response_cache.json'
        self.response_cache = self._load_response_cache()
        
        # Try to initialize market intel gatherer
        try:
            self.intel_gatherer = MarketIntelGatherer()
            self.has_market_intel = True
            print("Market intel gatherer initialized successfully")
        except ImportError:
            print("Market intel not available, using backup content generation")
            self.has_market_intel = False
        
        # Initialize personality
        self.personality = ElionPersonality()
        
        # Track successful calls
        self.track_record = {
            'calls': [],  # List of project calls and their outcomes
            'success_rate': 0,
            'last_updated': None
        }
        
        # Engagement metrics
        self.engagement_metrics = {
            'replies': {},  # tweet_id -> reply count
            'likes': {},    # tweet_id -> like count
            'retweets': {}, # tweet_id -> retweet count
            'top_tweets': []  # List of most engaging tweets
        }
    
    def _should_reset_daily_count(self):
        """Check if we should reset the daily tweet count (using UTC)"""
        try:
            current_time = datetime.utcnow()
            
            current_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_day > self.rate_limits['post']['last_reset']:
                self.rate_limits['post']['daily_count'] = 0
                self.rate_limits['post']['last_reset'] = current_day
                self.retry_count = 0  # Reset retry counter on new day
                print(f"\nReset daily tweet count at {current_time} UTC")
                # Also clear old market intel on daily reset
                self._clear_old_market_intel()
                return True
            return False
        
        except Exception as e:
            print(f"Error in daily reset check: {e}")
            return False

    def _should_reset_monthly_count(self):
        """Check if we should reset the monthly tweet count (resets on 15th)"""
        try:
            current_time = datetime.utcnow()
            current_month_15th = current_time.replace(day=15, hour=0, minute=0, second=0, microsecond=0)
            
            # If we're past the 15th, use next month's 15th
            if current_time.day > 15:
                if current_time.month == 12:
                    current_month_15th = current_month_15th.replace(year=current_time.year + 1, month=1)
                else:
                    current_month_15th = current_month_15th.replace(month=current_time.month + 1)
            
            if current_time >= self.rate_limits['post']['monthly_reset']:
                self.rate_limits['post']['monthly_count'] = 0
                self.rate_limits['post']['monthly_reset'] = current_month_15th
                print(f"\nReset monthly tweet count at {current_time} UTC")
                return True
            return False
            
        except Exception as e:
            print(f"Error in monthly reset check: {e}")
            return False

    def _should_reset_search_count(self):
        """Check if we should reset the search count (daily reset)"""
        try:
            current_time = datetime.utcnow()
            current_day = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if current_time >= self.rate_limits['search']['daily_reset']:
                self.rate_limits['search']['daily_searches'] = 0
                self.rate_limits['search']['daily_reset'] = current_day + timedelta(days=1)
                print(f"\nReset daily search count at {current_time} UTC")
                return True
            return False
            
        except Exception as e:
            print(f"Error in search reset check: {e}")
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
        """Gather market intelligence using multiple methods"""
        try:
            if not self.has_market_intel:
                print("Market intel not available, using backup content")
                return False
            
            # Try API search first (if we have quota)
            api_success = self._gather_from_api()
            
            # Regardless of API success, try to scrape trending projects
            try:
                self.intel_gatherer.scrape_trending_projects()
                
                # Generate insight from gathered data
                insight = self.intel_gatherer.generate_market_insight()
                if insight:
                    self.market_intel.append({
                        'text': insight,
                        'category': 'market_insight',
                        'created_at': datetime.utcnow().isoformat(),
                        'used': False
                    })
            except Exception as e:
                print(f"Error scraping trending projects: {e}")
            
            # Always return True to continue posting
            return True
            
        except Exception as e:
            print(f"Error gathering market intel: {e}")
            return True  # Still return True to continue posting

    def _gather_from_api(self):
        """Gather intel using Twitter API (if quota available)"""
        try:
            # Check if we've hit daily search limit
            current_searches = self.rate_limits['search'].get('daily_searches', 0)
            daily_limit = 15  # Conservative daily limit
            
            if current_searches >= daily_limit:
                print("\nDaily search limit reached, using backup content generation")
                return False
            
            # Get next category to search
            categories = list(self.search_queries.keys())
            category = categories[self.current_category_index]
            
            # Check when we last searched this category
            last_search = self.last_category_search[category]
            if last_search:
                hours_since_search = (datetime.utcnow() - last_search).total_seconds() / 3600
                if hours_since_search < 32:  # Search each category every 32 hours instead of 24
                    print(f"\nCategory '{category}' was searched {hours_since_search:.1f} hours ago")
                    print("Using cached results - Next search in {:.1f} hours".format(32 - hours_since_search))
                    
                    # Move to next category for next time
                    self.current_category_index = (self.current_category_index + 1) % len(categories)
                    
                    return False
            
            # Check rate limits
            minutes_since_last = float('inf')
            if self.last_search_time:
                minutes_since_last = (datetime.utcnow() - self.last_search_time).total_seconds() / 60
            
            # Strict rate limit: 1 request per 15 minutes
            if minutes_since_last < 15:  # Twitter's actual limit
                wait_minutes = 15 - minutes_since_last
                print(f"\nRate limit hit, switching to backup content generation")
                return False
            
            query = self.search_queries[category]
            max_results = 25  # Get more results per search since we search less frequently
            
            # Update tracking
            self.current_category_index = (self.current_category_index + 1) % len(categories)
            self.last_search_time = datetime.utcnow()
            self.last_category_search[category] = datetime.utcnow()
            
            # Increment daily search count
            self.rate_limits['search']['daily_searches'] = current_searches + 1
            
            # Perform the search
            print(f"\nGathering intelligence for category: {category} ({self.current_category_index + 1}/4)")
            print(f"Search request {current_searches + 1}/{daily_limit} today")
            
            response = self._search_tweets(query, max_results)
            
            if response:
                fresh_intel = []
                for tweet in response:
                    # Skip if we already have this tweet cached
                    if any(x.get('id') == tweet['id'] for x in self.market_intel):
                        continue
                        
                    intel = {
                        'id': tweet['id'],
                        'category': category,
                        'text': tweet.get('text', ''),
                        'created_at': tweet.get('created_at', datetime.utcnow().isoformat()),
                        'metrics': tweet.get('metrics', {
                            'retweet_count': 0,
                            'like_count': 0
                        }),
                        'used': False
                    }
                    fresh_intel.append(intel)
                
                # Only add new unique intel
                self.market_intel.extend(fresh_intel)
                self._prune_cache()
                self._save_cached_intel()
                
                print(f"Found {len(fresh_intel)} new items for {category}")
                print(f"Cache size: {len(self.market_intel)}/{self.max_cache_size}")
                print(f"Next category: {categories[(self.current_category_index) % len(categories)]}")
                print(f"Next search available in 15 minutes")
                return True
            
            print(f"No new tweets found for {category}")
            return False
                
        except Exception as e:
            print(f"\nError gathering market intel from API: {e}")
            return False

    def _search_tweets(self, query, max_results=10):
        """Search for tweets matching query"""
        try:
            # Use the search_api client for searching
            response = self.search_api.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics']
            )
            
            # Update rate limits from response headers
            self._update_rate_limits(response, 'search')
            
            if not response.data:
                return []
                
            # Update post pull count
            self.rate_limits['search']['monthly_posts_pulled'] += len(response.data)
            current_pulled = self.rate_limits['search']['monthly_posts_pulled']
            post_limit = self.rate_limits['search']['monthly_post_limit']
            print(f"Monthly search posts pulled: {current_pulled}/{post_limit}")
                
            results = []
            for tweet in response.data:
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

    def _update_rate_limits(self, response, endpoint='search'):
        """Update rate limit info from response headers without extra API calls"""
        try:
            headers = response.response.headers
            
            # Extract rate limit info
            self.rate_limits[endpoint]['remaining'] = int(headers.get('x-rate-limit-remaining', 0))
            reset_time = headers.get('x-rate-limit-reset')
            
            if reset_time:
                self.rate_limits[endpoint]['reset_time'] = datetime.fromtimestamp(int(reset_time))
            self.rate_limits[endpoint]['last_checked'] = datetime.utcnow()
            
            # Only log rate limit status if very low (< 2 remaining)
            if self.rate_limits[endpoint]['remaining'] < 2:
                wait_time = (self.rate_limits[endpoint]['reset_time'] - datetime.utcnow()).total_seconds()
                wait_minutes = max(0, wait_time / 60)
                print(f"\nRate Limit Status for {endpoint}:")
                print(f"Remaining calls: {self.rate_limits[endpoint]['remaining']}")
                print(f"Reset in: {wait_minutes:.1f} minutes")
                
        except Exception as e:
            print(f"Error updating rate limits: {e}")

    def get_tweet_content(self):
        """Get content optimized for CT growth"""
        try:
            current_time = datetime.utcnow()
            
            # 1. Prime time alpha calls (13:00-22:00 UTC)
            is_prime_time = 13 <= current_time.hour <= 22
            if is_prime_time:
                # 40% chance of alpha call during prime time
                if random.random() < 0.4:
                    alpha = self._generate_alpha_call()
                    if alpha:
                        return alpha
                
                # 30% chance of whale alert
                elif random.random() < 0.3:
                    whale_alert = self._generate_whale_alert()
                    if whale_alert:
                        return whale_alert
                
                # 20% chance of controversy
                elif random.random() < 0.2:
                    controversy = self._generate_controversy()
                    if controversy:
                        return controversy
            
            # 2. Technical analysis (any time)
            if random.random() < 0.3:
                tech_alpha = self._generate_technical_alpha()
                if tech_alpha:
                    return tech_alpha
            
            # 3. Community engagement
            if self._should_post_question():
                return self._generate_ct_engagement()
            
            # 4. Market-aware backup
            return self._generate_market_aware_tweet()
            
        except Exception as e:
            print(f"Error getting tweet content: {e}")
            return self._generate_backup_tweet()
    
    def _generate_alpha_call(self):
        """Generate alpha call based on market data"""
        try:
            # Get trending data
            trending = self.intel_gatherer.get_trending_projects(limit=3)
            if not trending:
                return None
            
            project = trending[0]['name']
            
            # Compare to successful past projects
            comparison_projects = ['PEPE', 'WOJAK', 'BONK', 'WIF']
            
            signals = [
                "Unusual wallet accumulation",
                "Dev wallet activity spike",
                "Contract interactions +200%",
                "Insider accumulation pattern",
                "Whale wallet movement"
            ]
            
            features = [
                "Strong community growth",
                "Innovative tokenomics",
                "Unique use case",
                "Experienced team",
                "Strategic partnerships"
            ]
            
            template = random.choice(self.personality.content_strategies['alpha_calls']['templates'])
            return template.format(
                project=project,
                comparison_project=random.choice(comparison_projects),
                signal1=random.choice(signals),
                signal2=random.choice(signals),
                signal3=random.choice(signals),
                feature1=random.choice(features),
                feature2=random.choice(features),
                feature3=random.choice(features)
            )
            
        except Exception as e:
            print(f"Error generating alpha call: {e}")
            return None
    
    def _generate_whale_alert(self):
        """Generate whale movement alert"""
        try:
            # Get market data
            trending = self.intel_gatherer.get_trending_projects(limit=1)
            if not trending:
                return None
            
            project = trending[0]['name']
            
            amounts = [
                "500 ETH",
                "1.2M USDC",
                "3000 BNB",
                "2.5M tokens"
            ]
            
            destinations = [
                "CEX deposit address",
                "fresh deployment wallet",
                "staking contract",
                "LP pool"
            ]
            
            events = [
                "major partnership announcement",
                "CEX listing",
                "product launch",
                "token unlock"
            ]
            
            template = random.choice(self.personality.content_strategies['whale_tracking']['templates'])
            return template.format(
                project=project,
                amount=random.choice(amounts),
                destination=random.choice(destinations),
                event=random.choice(events),
                previous_event=random.choice(events)
            )
            
        except Exception as e:
            print(f"Error generating whale alert: {e}")
            return None
    
    def _generate_controversy(self):
        """Generate controversial take for engagement"""
        try:
            trending = self.intel_gatherer.get_trending_projects(limit=1)
            if not trending:
                return None
            
            project = trending[0]['name']
            
            takes = [
                "heavily undervalued",
                "a potential 100x",
                "better than competitors",
                "misunderstood by CT"
            ]
            
            proofs = [
                "Team's previous exits",
                "Unique tech advantage",
                "Market size potential",
                "Community metrics",
                "Partnership pipeline"
            ]
            
            template = random.choice(self.personality.content_strategies['controversy']['templates'])
            return template.format(
                project=project,
                controversial_take=random.choice(takes),
                proof1=random.choice(proofs),
                proof2=random.choice(proofs),
                secret_insight=f"{project} is about to change the game. Insiders accumulating."
            )
            
        except Exception as e:
            print(f"Error generating controversy: {e}")
            return None
    
    def _generate_technical_alpha(self):
        """Generate technical analysis"""
        try:
            trending = self.intel_gatherer.get_trending_projects(limit=1)
            if not trending:
                return None
            
            project = trending[0]['name']
            
            metrics = [
                "Gas optimization +40%",
                "Unique holders +150%",
                "Contract security 95/100",
                "Dev activity +300%",
                "TVL growth +80%"
            ]
            
            insights = [
                "Hidden mint function found",
                "Unusual proxy pattern",
                "New bridge integration",
                "Optimized fee structure",
                "Zero-knowledge proofs"
            ]
            
            template = random.choice(self.personality.content_strategies['technical_alpha']['templates'])
            return template.format(
                project=project,
                metric1=random.choice(metrics),
                metric2=random.choice(metrics),
                metric3=random.choice(metrics),
                tech_insight1=random.choice(insights),
                tech_insight2=random.choice(insights),
                tech_insight3=random.choice(insights)
            )
            
        except Exception as e:
            print(f"Error generating technical alpha: {e}")
            return None
    
    def _should_post_question(self):
        """Determine if we should post a new question"""
        try:
            current_time = datetime.utcnow()
            
            # Check last question time
            recent_questions = [
                q for q in self.response_cache['questions'].values()
                if (current_time - datetime.fromisoformat(q['time'])).total_seconds() <= 8 * 3600  # 8 hours
            ]
            
            # Post question if none in last 8 hours and 30% chance
            return len(recent_questions) == 0 and random.random() < 0.3
            
        except Exception as e:
            print(f"Error checking if should post question: {e}")
            return False
    
    def check_question_responses(self):
        """Check responses to recent questions and cache them"""
        try:
            current_time = datetime.utcnow()
            
            # Check unchecked questions from last 24 hours
            for qid, qdata in self.response_cache['questions'].items():
                if qdata['responses_checked']:
                    continue
                    
                question_time = datetime.fromisoformat(qdata['time'])
                if (current_time - question_time).total_seconds() > 24 * 3600:
                    continue
                
                # Get replies using API
                replies = self.api.get_tweet_replies(qid)
                
                for reply in replies:
                    reply_id = str(reply.id)
                    
                    # Skip if already processed
                    if reply_id in self.response_cache['responses']:
                        continue
                    
                    engagement_score = reply.public_metrics['like_count'] + reply.public_metrics['retweet_count']
                    
                    # Cache responses with good engagement
                    if engagement_score >= 5:
                        project = self._extract_project_from_reply(reply.text)
                        topic = qdata['topic']
                        
                        # Skip if project recently featured in this topic
                        if project in self.response_cache['featured_projects'][topic]:
                            continue
                        
                        self.response_cache['responses'][reply_id] = {
                            'project': project,
                            'topic': topic,
                            'username': f"@{reply.author_id}",
                            'highlight': self._extract_highlight_from_reply(reply.text),
                            'engagement_score': engagement_score,
                            'time': current_time.isoformat(),
                            'used': False
                        }
                
                # Mark question as checked
                qdata['responses_checked'] = True
            
            self._save_response_cache()
            
        except Exception as e:
            print(f"Error checking question responses: {e}")

    def _get_next_response_to_feature(self):
        """Get next high-engagement response to feature"""
        try:
            current_time = datetime.utcnow()
            
            # Get unused responses from last 48 hours
            valid_responses = [
                resp for resp in self.response_cache['responses'].values()
                if not resp['used']
                and (current_time - datetime.fromisoformat(resp['time'])).total_seconds() <= 48 * 3600
            ]
            
            if not valid_responses:
                return None
            
            # Sort by engagement score
            valid_responses.sort(key=lambda x: x['engagement_score'], reverse=True)
            response = valid_responses[0]
            
            # Mark as used and track featured project
            response['used'] = True
            self.response_cache['featured_projects'][response['topic']].add(response['project'])
            self._save_response_cache()
            
            return response
            
        except Exception as e:
            print(f"Error getting next response: {e}")
            return None
    
    def _format_feature_tweet(self, response):
        """Format a tweet featuring a high-engagement response"""
        topic = response['topic']
        templates = {
            'memes': [
                " {project} has an amazing {feature}! Thanks {username} for this gem! #Memecoin",
                "The {feature} of {project} is impressive! Great find {username}! ",
                "Love what {project} is doing with their {feature}! Shoutout to {username}! "
            ],
            'ai': [
                "Mind-blown by {project}'s {feature}! Thanks {username} for sharing! ",
                "The AI capabilities of {project} are next level! Great insight {username}! ",
                "{project} is revolutionizing {feature}! Credit to {username} for the tip! "
            ],
            'gamefi': [
                "Loving {project}'s {feature}! Thanks {username} for the recommendation! ",
                "{project} is crushing it with their {feature}! Hat tip to {username}! ",
                "Had to share: {project}'s {feature} is game-changing! Props to {username}! "
            ]
        }
        
        tweet = random.choice(templates[topic]).format(
            project=response['project'],
            feature=response['highlight'],
            username=response['username']
        )
        
        return tweet
    
    def _load_response_cache(self):
        """Load cached responses from file"""
        try:
            if os.path.exists(self.response_cache_file):
                with open(self.response_cache_file, 'r') as f:
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
            return {'questions': {}, 'responses': {}, 'featured_projects': {'memes': set(), 'ai': set(), 'gamefi': set()}}
    
    def _save_response_cache(self):
        """Save response cache to file"""
        try:
            # Convert sets to lists for JSON serialization
            cache_copy = {
                'questions': self.response_cache['questions'],
                'responses': self.response_cache['responses'],
                'featured_projects': {
                    topic: list(projects) 
                    for topic, projects in self.response_cache['featured_projects'].items()
                }
            }
            
            with open(self.response_cache_file, 'w') as f:
                json.dump(cache_copy, f, indent=2)
        except Exception as e:
            print(f"Error saving response cache: {e}")

    def post_tweet(self):
        """Post a tweet regardless of search status"""
        try:
            # Check posting rate limits
            if not self._can_post_tweet():
                print("\nCannot post tweet due to rate limits")
                return False
            
            # Get content (will work even if searches are limited)
            content = self.get_tweet_content()
            
            if not content:
                print("\nNo content available for tweet")
                return False
            
            # Try to post the tweet
            try:
                response = self.api.create_tweet(text=content)
                
                # Update rate limits
                self.rate_limits['post']['daily_count'] += 1
                self.rate_limits['post']['last_post_time'] = datetime.utcnow()
                
                print(f"\nSuccessfully posted tweet: {content[:50]}...")
                return True
                
            except Exception as e:
                print(f"\nError posting tweet: {e}")
                return False
                
        except Exception as e:
            print(f"\nError in post_tweet: {e}")
            return False

    def _can_post_tweet(self):
        """Check if we can post a tweet based on rate limits"""
        try:
            # Check monthly tweet limit first
            if not self._should_reset_monthly_count():
                if self.rate_limits['post']['monthly_count'] >= self.rate_limits['post']['monthly_limit']:
                    next_reset = self.rate_limits['post']['monthly_reset']
                    wait_time = (next_reset - datetime.utcnow()).total_seconds()
                    wait_minutes = max(0, wait_time / 60)
                    print(f"\nMonthly tweet limit reached ({self.rate_limits['post']['monthly_count']}/{self.rate_limits['post']['monthly_limit']})")
                    print(f"Next reset on: {next_reset.strftime('%Y-%m-%d %H:%M UTC')}")
                    print(f"Wait time: {wait_minutes/60:.1f} hours")
                    return False
            
            # Check daily tweet limit
            if not self._should_reset_daily_count():
                if self.rate_limits['post']['daily_count'] >= self.rate_limits['post']['daily_limit']:
                    wait_time = (self.rate_limits['post']['last_reset'] + timedelta(days=1) - datetime.utcnow()).total_seconds()
                    wait_minutes = max(0, wait_time / 60)
                    print(f"\nDaily tweet limit reached ({self.rate_limits['post']['daily_count']}/{self.rate_limits['post']['daily_limit']})")
                    print(f"Next reset in: {wait_minutes:.1f} minutes")
                    return False
            
            return True
        
        except Exception as e:
            print(f"Error checking post rate limits: {e}")
            return False

    def get_tweet_type_for_next_post(self):
        """Determine next tweet type based on position in cycle and engagement"""
        total_tweets = self.history_manager.history['metadata']['total_tweets']
        position_in_cycle = total_tweets % 50
        
        # Check remaining daily tweets
        remaining_tweets = self.rate_limits['post']['daily_limit'] - self.rate_limits['post']['daily_count']
        
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
            return self._generate_backup_tweet()
    
    def _generate_backup_tweet(self):
        """Generate engaging crypto content when API or data is unavailable"""
        try:
            # List of evergreen crypto topics and takes
            backup_content = {
                'crypto_wisdom': [
                    " Crypto Trading Alpha:\n\nBest traders don't chase pumps.\nThey accumulate in silence.\nThey sell into FOMO.\n\nLike for more wisdom ",
                    " Crypto Rules:\n\n- Research before APE\n- DCA > FOMO\n- Patience = Profit\n\nWho needs this reminder? ",
                    " 3 Rules of Crypto:\n\n1. Always DYOR\n2. Never FOMO at ATH\n3. Take profits\n\nSimple but effective "
                ],
                'crypto_psychology': [
                    " Crypto Truth:\n\nBear markets make you rich\nBull markets make you money\n\nAre you accumulating? ",
                    " Crypto Psychology 101:\n\nFear = Opportunity\nGreed = Risk\nPatience = Profit\n\nSave this ",
                    " Remember:\n\nWhen market is fearful = Buy\nWhen market is greedy = Sell\nWhen market is quiet = Research"
                ],
                'blockchain_tech': [
                    " Future of Crypto:\n\nL2s + AI integration\nZK privacy layers\nAI-powered DeFi\n\nThe future is clear ",
                    " Blockchain Alert:\n\nZK tech adoption growing\nL2 TVL increasing\nAI integration expanding\n\nConnect the dots ",
                    " Next Crypto Wave:\n\nAI-powered trading\nZK privacy\nL2 scaling\n\nPosition accordingly "
                ],
                'crypto_community': [
                    " Crypto Community Tips:\n\n- Add value daily\n- Network quietly\n- Share alpha freely\n\nWho's building? ",
                    " Your Crypto Strategy:\n\n1. Find your niche\n2. Share genuine alpha\n3. Network strategically\n\nSimple but effective ",
                    " Crypto Truth:\n\nValue providers win long-term\nNoise makers fade away\n\nChoose your path "
                ]
            }
            
            # Pick random category and content
            category = random.choice(list(backup_content.keys()))
            tweet = random.choice(backup_content[category])
            
            return tweet
            
        except Exception as e:
            print(f"Error generating backup tweet: {e}")
            return " Focus on crypto value. Not noise.\n\nWho agrees? "
            
    def _generate_market_aware_tweet(self):
        """Generate market-aware content without API dependency"""
        try:
            # Predefined high-value projects and sectors
            key_projects = ['BTC', 'ETH', 'SOL', 'MATIC', 'ARB', 'OP']
            key_sectors = ['L2s', 'AI', 'GameFi', 'DeFi', 'ZK', 'RWA']
            
            templates = [
                " {project} looking interesting here\n\nKey levels:\n Support: {support}\n Target: {target}\n\nThoughts? ",
                " {sector} sector heating up\n\nWatch for:\n Volume spikes\n Whale moves\n Accumulation\n\nReady? ",
                " {project} vs {project2}\n\nWhich wins Q1?\n\nLike = {project}\nRT = {project2}\n\nReason in replies ",
                " Building in {sector}?\n\nDM me if you need:\n- Tech review\n- Architecture feedback\n- Security check\n\nLets build "
            ]
            
            # Generate tweet with predefined data
            template = random.choice(templates)
            return template.format(
                project=random.choice(key_projects),
                project2=random.choice(key_projects),
                sector=random.choice(key_sectors),
                support=f"${random.randint(20, 100)}K",
                target=f"${random.randint(100, 500)}K"
            )
            
        except Exception as e:
            print(f"Error generating market-aware tweet: {e}")
            return self._generate_backup_tweet()
    
    def should_wait_for_rate_limit(self, endpoint='search'):
        """Check if we should wait for rate limit reset without making API calls"""
        if endpoint not in self.rate_limits:
            return False
            
        limits = self.rate_limits[endpoint]
        
        if endpoint == 'post':
            if limits['daily_count'] >= limits['daily_limit']:
                wait_time = (limits['last_reset'] + timedelta(days=1) - datetime.utcnow()).total_seconds()
                if wait_time > 0:
                    wait_minutes = wait_time / 60
                    print(f"\nDaily {endpoint} limit reached. Waiting {wait_minutes:.1f} minutes...")
                    return wait_minutes
        else:  # search endpoint
            if not limits['remaining'] or not limits['reset_time']:
                return False
                
            if limits['remaining'] < 2:
                wait_time = (limits['reset_time'] - datetime.utcnow()).total_seconds()
                if wait_time > 0:
                    wait_minutes = wait_time / 60
                    print(f"\n{endpoint.title()} rate limit almost exhausted. Waiting {wait_minutes:.1f} minutes...")
                    return wait_minutes
        return False

    def get_timeline_tweets(self, max_results=20):
        """Fetch recent tweets from followed accounts"""
        try:
            # Get tweets from followed accounts timeline
            response = self.search_api.get_home_timeline(
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                exclude=['retweets', 'replies']
            )
            
            if not response.data:
                return []
            
            # Update rate limits from response headers
            self._update_rate_limits(response, 'timeline')
            
            results = []
            for tweet in response.data:
                # Only include tweets from last 6 hours to keep engagement fresh
                tweet_time = tweet.created_at
                if (datetime.utcnow() - tweet_time).total_seconds() > 6 * 3600:
                    continue
                    
                results.append({
                    'id': tweet.id,
                    'author_id': tweet.author_id,
                    'text': tweet.text,
                    'created_at': tweet.created_at.isoformat(),
                    'metrics': {
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count']
                    }
                })
            
            return results
            
        except Exception as e:
            print(f"\nTimeline fetch failed: {e}")
            return []

    def generate_engagement_reply(self, tweet):
        """Generate a personality-driven reply to a tweet"""
        try:
            # Get tweet context
            tweet_text = tweet['text']
            metrics = tweet['metrics']
            
            # Determine engagement level
            engagement_level = self._get_engagement_level(metrics)
            
            # Generate reply using Elion's personality
            reply = generate_elion_reply(
                tweet_text,
                engagement_level=engagement_level,
                personality=self.personality
            )
            
            return reply
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None

    def post_engagement_reply(self):
        """Post a reply to a followed account's tweet"""
        try:
            # Check if we've hit daily engagement limit
            if self.rate_limits['timeline']['daily_engagement_posts'] >= self.rate_limits['timeline']['max_daily_engagement']:
                print("Daily engagement post limit reached")
                return False
            
            # Get recent timeline tweets
            timeline_tweets = self.get_timeline_tweets()
            if not timeline_tweets:
                return False
            
            # Sort by engagement potential (likes + retweets)
            timeline_tweets.sort(
                key=lambda x: x['metrics']['like_count'] + x['metrics']['retweet_count'],
                reverse=True
            )
            
            # Try to generate replies until we find a good one
            for tweet in timeline_tweets:
                reply = self.generate_engagement_reply(tweet)
                if reply:
                    # Post the reply
                    response = self.api.create_tweet(
                        text=reply,
                        in_reply_to_tweet_id=tweet['id']
                    )
                    
                    if response:
                        # Update engagement post count
                        self.rate_limits['timeline']['daily_engagement_posts'] += 1
                        print(f"\nPosted engagement reply ({self.rate_limits['timeline']['daily_engagement_posts']}/{self.rate_limits['timeline']['max_daily_engagement']} today)")
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error posting engagement reply: {e}")
            return False

    def _should_reset_engagement_count(self):
        """Check if we should reset the daily engagement post count"""
        current_time = datetime.utcnow()
        last_reset = self.rate_limits['timeline'].get('last_reset')
        
        if not last_reset or current_time.date() > last_reset.date():
            self.rate_limits['timeline']['daily_engagement_posts'] = 0
            self.rate_limits['timeline']['last_reset'] = current_time
            return True
        return False

    def run(self):
        """Main bot loop - runs continuously"""
        try:
            while True:
                # Reset counters if needed
                self._should_reset_daily_count()
                self._should_reset_monthly_count()
                self._should_reset_search_count()
                self._should_reset_engagement_count()
                
                # Try to post an engagement reply (20% chance when under daily limit)
                if (random.random() < 0.2 and 
                    self.rate_limits['timeline']['daily_engagement_posts'] < self.rate_limits['timeline']['max_daily_engagement']):
                    self.post_engagement_reply()
                
                # Regular posting logic
                if self._can_post_tweet():
                    self.post_tweet()
                
                # Sleep for a bit
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\nBot stopped by user")
        except Exception as e:
            print(f"\nError in main loop: {e}")

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
        print(f" Healthcheck server running on {host}:{port}")
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
