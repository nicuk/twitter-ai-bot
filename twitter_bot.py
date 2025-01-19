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
        
        # Initialize components
        self.setup_driver()
        self.engagement_manager = EngagementManager()
        self.data_sources = DataSources()
        
        # State
        self.logged_in = False
        self.current_method = 'selenium'  # Start with Selenium

    def setup_driver(self):
        """Initialize Chrome driver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        # Uncomment the line below to run in headless mode if needed
        # options.add_argument('--headless')
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                     options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def generate_tweet(self):
        """Generate tweet content using Meta-Llama API"""
        try:
            # Get market data and analysis
            market_data = self.data_sources.get_market_overview()
            
            # Generate prompt based on market conditions and engagement patterns
            content_type = random.choice(['alpha', 'analysis', 'community', 'education'])
            category_info = self.engagement_manager.content_categories[content_type]
            
            prompt = f"""You are Elion, a crypto AI bot that shares {content_type} content.
            
Market Overview:
{market_data}

Your style should match these interests: {', '.join(category_info['interests'])}
Use these hooks: {', '.join(self.engagement_manager.viral_patterns['hooks'].values())}

Generate an engaging tweet about the current market conditions. Keep it under 280 characters."""
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'messages': [
                    {'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': 'Generate a tweet based on the current market conditions and engagement patterns.'}
                ],
                'model': 'Meta-Llama-3.3-70B-Instruct',
                'stop': ['<|eot_id|>'],
                'stream': True,
                'stream_options': {'include_usage': True}
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Extract the tweet content from the response
            tweet_content = response.json()['choices'][0]['message']['content'].strip()
            
            # Analyze and optimize the tweet
            tweet_data = {
                'content': tweet_content,
                'type': content_type,
                'timestamp': datetime.now()
            }
            analysis = self.engagement_manager.analyze_tweet_performance(tweet_data)
            
            # If the analysis suggests improvements, regenerate the tweet
            if analysis.get('engagement_score', 0) < 0.5:
                recommendations = self.engagement_manager._generate_recommendations(analysis)
                print(f"Low engagement score. Recommendations: {recommendations}")
                return self.generate_tweet()  # Try again
                
            return tweet_content
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None

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

    def post_tweet(self):
        """Try different methods to post a tweet"""
        methods = ['selenium', 'twitter_api', 'requests']
        
        # Generate tweet content
        tweet_content = self.generate_tweet()
        if not tweet_content:
            print("Failed to generate tweet content, retrying in 5 minutes...")
            time.sleep(300)
            return
            
        # Try each method until one succeeds
        for method in methods:
            try:
                if method == 'selenium':
                    success = self._post_tweet_selenium(tweet_content)
                elif method == 'twitter_api':
                    success = self._post_tweet_api(tweet_content)
                else:  # requests
                    success = self._post_tweet_requests(tweet_content)
                    
                if success:
                    print(f"Successfully posted tweet using {method}")
                    self.current_method = method  # Remember successful method
                    return True
                    
            except Exception as e:
                print(f"Error posting tweet using {method}: {e}")
                continue
                
        print("All posting methods failed. Will retry on next schedule.")
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
            
    def _post_tweet_api(self, tweet_content):
        """Post tweet using Twitter API"""
        try:
            auth = tweepy.OAuthHandler(self.twitter_api_key, self.twitter_api_secret)
            auth.set_access_token(self.twitter_access_token, self.twitter_access_secret)
            api = tweepy.API(auth)
            
            api.update_status(tweet_content)
            return True
            
        except Exception as e:
            print(f"Twitter API posting failed: {e}")
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
