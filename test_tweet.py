import tweepy
import os
from dotenv import load_dotenv
from twitter_api_bot import AIGamingBot

def test_tweet():
    """Test if we can still post tweets"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize the bot
        print("\nInitializing AI Gaming Bot...")
        bot = AIGamingBot()
        
        # Test backup content generation
        print("\nTesting backup content generation...")
        content = bot._generate_backup_tweet()
        print(f"\nGenerated content:\n{content}")
        
        # Get Twitter API credentials
        client_id = os.getenv('TWITTER_CLIENT_ID')
        client_secret = os.getenv('TWITTER_CLIENT_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # Verify credentials
        print("\nChecking API credentials...")
        if not all([client_id, client_secret, access_token, access_token_secret]):
            print("Error: Missing API credentials")
            print("Please check your .env file has these variables:")
            print("- TWITTER_CLIENT_ID")
            print("- TWITTER_CLIENT_SECRET")
            print("- TWITTER_ACCESS_TOKEN")
            print("- TWITTER_ACCESS_TOKEN_SECRET")
            return
            
        # Initialize Tweepy client (v2)
        client = tweepy.Client(
            consumer_key=client_id,
            consumer_secret=client_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        # Ask user if they want to post the generated tweet
        print("\nWould you like to post this tweet? (y/n)")
        choice = input().lower()
        
        if choice == 'y':
            print("\nAttempting to post the generated tweet...")
            response = client.create_tweet(text=content)
            
            if response.data:
                tweet_id = response.data['id']
                print("\nTweet posted successfully!")
                print(f"Tweet ID: {tweet_id}")
                print(f"View at: https://twitter.com/user/status/{tweet_id}")
        else:
            print("\nTest completed without posting.")
        
    except tweepy.TooManyRequests:
        print("\nError: Post limit reached")
        print("We've hit the posting rate limit")
        
    except tweepy.Forbidden as e:
        print(f"\nError: Forbidden - {str(e)}")
        print("This might mean we've hit the monthly tweet limit")
        print("If you see error 453, we need to ensure the app has write permissions")
        
    except Exception as e:
        print(f"\nError posting tweet: {str(e)}")

if __name__ == "__main__":
    test_tweet()
