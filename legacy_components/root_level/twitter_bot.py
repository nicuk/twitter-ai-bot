import os
import time
import requests
import schedule
import random
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import tweepy
from requests_oauthlib import OAuth1
from elion.engagement import EngagementManager
from elion.data_sources import DataSources
from strategies.volume_strategy import test_volume_strategy

# Load environment variables
load_dotenv()

class EngagementManager:
    def __init__(self):
        self.content_categories = {
            'alpha': {'interests': ['trading', 'investing', 'finance']},
            'analysis': {'interests': ['market analysis', 'technical analysis', 'fundamental analysis']},
            'community': {'interests': ['community engagement', 'social media', 'influencer marketing']},
            'education': {'interests': ['financial education', 'trading education', 'investing education']}
        }
        self.viral_patterns = {
            'hooks': {
                'hook1': 'Did you know?',
                'hook2': 'Here\'s a surprising fact:',
                'hook3': 'You won\'t believe what happened in the market today!'
            }
        }

    def analyze_tweet_performance(self, tweet_data):
        # Simulate analysis for demonstration purposes
        engagement_score = random.random()
        return {'engagement_score': engagement_score}

    def _generate_recommendations(self, analysis):
        # Simulate recommendations for demonstration purposes
        recommendations = ['Use a more attention-grabbing hook', 'Include more relevant hashtags']
        return recommendations

class DataSources:
    def __init__(self):
        pass

    def get_market_overview(self):
        # Simulate market data for demonstration purposes
        market_data = 'The market is currently bullish, with a strong uptrend in the crypto sector.'
        return market_data

class TwitterBot:
    def __init__(self):
        """Initialize the Twitter bot"""
        self.api_url = os.getenv('AI_API_URL')
        self.access_token = os.getenv('AI_ACCESS_TOKEN')
        self.twitter_api_key = os.getenv('TWITTER_API_KEY')
        self.twitter_api_secret = os.getenv('TWITTER_API_SECRET')
        self.twitter_access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.twitter_access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        
        # Initialize Tweepy client
        auth = tweepy.OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
        auth.set_access_token(self.twitter_access_token, self.twitter_access_secret)
        self.api = tweepy.API(auth)
        
        # Initialize components
        self.setup_driver()
        self.engagement_manager = EngagementManager()
        self.data_sources = DataSources()
        
        # State
        self.logged_in = False
        self.current_method = 'api'  # Use Twitter API by default

    def setup_driver(self):
        """Initialize Chrome driver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # Uncomment the line below to run in headless mode if needed
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                     options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def _post_tweet_api(self, tweet_content):
        """Post tweet using Twitter API"""
        try:
            self.api.update_status(tweet_content)
            print("Tweet posted successfully using API!")
            return True
        except Exception as e:
            print(f"Error posting tweet via API: {str(e)}")
            return False

    def _post_tweet_selenium(self, tweet_content):
        """Post tweet using Selenium browser automation"""
        try:
            if not self.logged_in:
                self.login()
                
            self.driver.get('https://twitter.com/compose/tweet')
            
            tweet_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-text='true']"))
            )
            tweet_input.send_keys(tweet_content)
            
            tweet_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='tweetButton']"))
            )
            tweet_button.click()
            
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"Selenium posting failed: {e}")
            self.logged_in = False
            return False
            
    def _post_tweet_requests(self, tweet_content):
        """Post tweet using direct HTTP requests"""
        try:
            # Twitter API v2 endpoint
            url = "https://api.twitter.com/2/tweets"
            
            # Create headers with OAuth 1.0a authentication
            auth = OAuth1(
                self.twitter_api_key,
                self.twitter_api_secret,
                self.twitter_access_token,
                self.twitter_access_secret
            )
            
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                'text': tweet_content
            }
            
            # Make request
            response = requests.post(url, headers=headers, auth=auth, json=data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Direct requests posting failed: {e}")
            return False

    def post_tweet(self):
        """Post a tweet with volume analysis"""
        try:
            # Get volume analysis
            tweet_content = test_volume_strategy()
            
            if not tweet_content:
                print("No significant volume activity to report")
                return False
                
            # Try posting with different methods
            methods = {
                'api': self._post_tweet_api,
                'selenium': self._post_tweet_selenium,
                'requests': self._post_tweet_requests
            }
            
            # Try current method first
            if methods[self.current_method](tweet_content):
                return True
                
            # If current method fails, try others
            for method, func in methods.items():
                if method != self.current_method:
                    if func(tweet_content):
                        self.current_method = method  # Update to working method
                        return True
                        
            return False
            
        except Exception as e:
            print(f"Error in post_tweet: {str(e)}")
            return False

    def login(self):
        """Login to Twitter"""
        if self.logged_in:
            return
        
        try:
            self.driver.get('https://twitter.com/login')
            
            # Wait for and enter username
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_input.send_keys(os.getenv('TWITTER_USERNAME'))
            username_input.send_keys(Keys.RETURN)
            
            # Wait for and enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(os.getenv('TWITTER_PASSWORD'))
            password_input.send_keys(Keys.RETURN)
            
            # Wait for home timeline to confirm login
            self.wait.until(
                EC.presence_of_element_located((By.ARIA_LABEL, "Home timeline"))
            )
            
            self.logged_in = True
            print("Successfully logged in to Twitter")
            
        except Exception as e:
            print(f"Error logging in: {e}")
            self.driver.quit()
            raise

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to run the Twitter bot"""
    bot = TwitterBot()
    retry_delay = 300  # 5 minutes
    max_retries = 3
    
    while True:
        try:
            # Initial login
            if not bot.logged_in:
                bot.login()
            
            # Schedule tweets every 4 hours
            schedule.every(4).hours.do(bot.post_tweet)
            
            # Post initial tweet if not already posted
            if not hasattr(bot, 'initial_tweet_posted'):
                bot.post_tweet()
                bot.initial_tweet_posted = True
            
            # Keep the script running
            while True:
                schedule.run_pending()
                time.sleep(60)
                
        except KeyboardInterrupt:
            print("\nShutting down bot...")
            break
            
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            
            # Reset login status on error
            bot.logged_in = False
            
            # Increment retry counter
            if not hasattr(bot, 'retry_count'):
                bot.retry_count = 0
            bot.retry_count += 1
            
            # If max retries reached, wait longer
            if bot.retry_count >= max_retries:
                print("Max retries reached. Waiting 30 minutes before trying again...")
                time.sleep(1800)  # 30 minutes
                bot.retry_count = 0
            
            continue
            
        finally:
            bot.cleanup()

if __name__ == "__main__":
    main()
