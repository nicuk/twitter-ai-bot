import os
import sys
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

def check_usage_limits(days=30):
    """Check current Twitter API usage limits"""
    try:
        # Load environment variables
        load_dotenv()
        
        # Get bearer token from environment
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        if not bearer_token:
            print("Error: TWITTER_BEARER_TOKEN not found in environment variables")
            return
            
        # Make request to usage endpoint
        url = "https://api.twitter.com/2/usage/tweets"
        # Properly format the Authorization header with 'Bearer' prefix
        headers = {"Authorization": f"Bearer {bearer_token.strip()}"}
        params = {"days": str(days)}
        
        print(f"\nChecking Twitter API usage for the last {days} days...")
        print(f"Using URL: {url}")
        print(f"Authorization Header: Bearer {'*' * len(bearer_token)}")  # Show masked token for verification
        
        response = requests.get(url, headers=headers, params=params)
        
        # Check rate limit headers
        rate_limit = response.headers.get('x-rate-limit-limit')
        rate_remaining = response.headers.get('x-rate-limit-remaining')
        rate_reset = response.headers.get('x-rate-limit-reset')
        
        print("\nRate Limit Information:")
        print(f"Rate Limit: {rate_limit if rate_limit else 'Not provided'}")
        print(f"Remaining: {rate_remaining if rate_remaining else 'Not provided'}")
        if rate_reset:
            reset_time = datetime.fromtimestamp(int(rate_reset))
            print(f"Reset Time: {reset_time} UTC")
        
        if response.status_code == 200:
            try:
                usage_data = response.json()
                print("\nTwitter API Usage Report")
                print(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
                print("-" * 50)
                print("\nRaw Response:")
                print(usage_data)  # Print raw response for debugging
                
                if isinstance(usage_data, dict) and 'data' in usage_data:
                    for usage in usage_data['data']:
                        if isinstance(usage, dict):
                            endpoint = usage.get('name', 'Unknown')
                            used = usage.get('used', 0)
                            cap = usage.get('cap', 'No cap')
                            
                            print(f"\nEndpoint: {endpoint}")
                            print(f"Used: {used}")
                            print(f"Cap: {cap}")
                            
                            if cap != 'No cap' and used > 0:
                                percentage = (used / cap) * 100
                                print(f"Usage: {percentage:.1f}%")
                                
                                # Show warning if usage is high
                                if percentage > 80:
                                    print("⚠️ Warning: High usage!")
                else:
                    print("\nUnexpected response format")
                    print("Response data:", usage_data)
            except Exception as e:
                print(f"\nError parsing response: {e}")
                print("Raw response:", response.text)
        elif response.status_code == 429:
            print("\nRate limit exceeded!")
            retry_after = response.headers.get('retry-after')
            if retry_after:
                retry_time = datetime.utcnow() + timedelta(seconds=int(retry_after))
                print(f"Please wait until: {retry_time} UTC")
                print(f"Time remaining: {int(retry_after)} seconds")
            else:
                print("No retry-after time provided. Please try again later.")
        else:
            print(f"\nError checking usage: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"\nError checking usage limits: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Get days from command line argument or use default
    days = 30
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
        except ValueError:
            print("Invalid days argument, using default 30 days")
    
    check_usage_limits(days)
