import tweepy
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import json
import random
from elion_personality import generate_elion_tweet
from tweet_history_manager import TweetHistoryManager

# Load test environment variables
load_dotenv('.env.test')

def test_tweet_generation():
    """Test tweet generation with Elion's personality"""
    print("\nTesting Elion's tweet generation...")
    
    # Initialize history manager
    history_manager = TweetHistoryManager()
    
    # Test categories
    categories = ['ai_gaming', 'ai_tokens', 'funding', 'tech']
    
    # Generate sample contexts
    contexts = [
        {
            'category': 'ai_gaming',
            'text': '$MOG just announced partnership with major gaming studio. Volume up 500% in last 24h. Multiple whales accumulating.'
        },
        {
            'category': 'ai_tokens',
            'text': 'New AI trading token $ELION launching with innovative tokenomics. Pre-sale filled in 2 minutes. Major VCs backing.'
        },
        {
            'category': 'funding',
            'text': 'Breaking: AI Gaming studio raises $50M from a16z and Binance Labs. Token launch imminent.'
        },
        {
            'category': 'tech',
            'text': 'Solana AI gaming infrastructure upgrade live. 50k TPS achieved in testnet. Major games migrating.'
        }
    ]
    
    print("\nTesting with different market conditions...")
    market_conditions = ['bullish', 'bearish', 'neutral']
    
    for condition in market_conditions:
        print(f"\nTesting {condition} market condition:")
        context = random.choice(contexts)
        category = context['category']
        
        # Generate tweet
        tweet_context = f"Category: {category}\nTrend: {context['text']}"
        tweet_content = generate_elion_tweet(tweet_context, condition)
        
        print(f"\nGenerated prompt:")
        print(tweet_content)
        
        # Make API request
        headers = {
            'Authorization': f'Bearer {os.getenv("AI_ACCESS_TOKEN")}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "messages": [{
                "role": "system",
                "content": tweet_content
            }],
            "model": os.getenv('AI_MODEL_NAME', 'meta-llama-3.3-70b-instruct'),
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        try:
            print("\nMaking request to AI API...")
            response = requests.post(
                os.getenv('AI_API_URL') + "/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            tweet = response.json()['choices'][0]['message']['content'].strip()
            print(f"\nGenerated tweet ({len(tweet)} chars):")
            print(tweet)
            
            # Check for duplicates
            if history_manager.is_recent_duplicate(tweet):
                print("Warning: Tweet is too similar to recent ones")
            else:
                # Add to history
                persona = history_manager.suggest_persona(category)
                history_manager.add_tweet(tweet, persona, category)
                print(f"Added to history with persona: {persona}")
            
            # Get some stats
            print("\nPersona usage stats:")
            print(history_manager.get_persona_stats())
            print("\nTopic coverage:")
            print(history_manager.get_topic_stats())
            print("\nCurrent market mood:")
            print(history_manager.get_market_mood())
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None
    
    return "Test completed successfully"

def test_single_tweet():
    """Test bot configuration and scheduling"""
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
    
    from twitter_api_bot import AIGamingBot
    import schedule
    
    bot = AIGamingBot()
    print("\nTesting bot configuration...")
    
    # Verify scheduling configuration
    print("\nVerifying scheduling configuration...")
    print("Daily tweet limit:", bot.daily_tweet_limit)
    print("\nCategory check intervals:")
    for category, interval in bot.category_intervals.items():
        checks_per_day = 24 * 60 / interval
        print(f"- {category}: Every {interval} minutes ({checks_per_day:.1f} checks/day)")
    
    total_checks = sum(24 * 60 / interval for interval in bot.category_intervals.values())
    print(f"\nTotal API usage per day:")
    print(f"- Market intelligence searches: {total_checks:.1f}")
    print(f"- Tweets: {bot.daily_tweet_limit}")
    
    # Test market intelligence structure
    print("\nTesting market intelligence structure...")
    test_intel = {
        'category': 'test',
        'text': 'Test market intelligence',
        'metrics': {'retweet_count': 5, 'like_count': 10},
        'created_at': datetime.now().isoformat(),
        'used': False
    }
    bot.market_intel = [test_intel]
    
    # Test tweet generation without API calls
    print("\nTesting tweet generation (with mock data)...")
    tweet = bot.generate_tweet()
    if tweet:
        print("Tweet generation successful!")
        print(f"Sample tweet: {tweet}")
    
    print("\nTest complete! Bot is configured correctly.")
    print("\nScheduled tasks would be:")
    print("- Market intelligence gathering: Every 2 hours")
    print("- Tweet posting: Every 90 minutes (16 tweets per day)")
    print(f"\nEstimated daily API calls: {total_checks:.1f} searches + {bot.daily_tweet_limit} tweets")

if __name__ == "__main__":
    print("Starting Elion Tweet Tests...")
    test_tweet_generation()
    print("\nStarting Bot Configuration Test...")
    test_single_tweet()
