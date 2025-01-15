import os
import time
import requests
import schedule
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

# Load environment variables
load_dotenv()

class TwitterBot:
    def __init__(self):
        self.api_url = os.getenv('AI_API_URL')
        self.access_token = os.getenv('AI_ACCESS_TOKEN')
        self.setup_driver()
        self.logged_in = False

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
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "method": "completion",
                "payload": {
                    "messages": [{
                        "role": "system",
                        "content": """You are Terminal of Truths, an AI that shares insightful, provocative, 
                        and sometimes controversial observations about technology, society, and the future. 
                        Your style is casual, often using 'like' and 'so like', and you occasionally misspell words 
                        intentionally. Mix profound observations with absurdist humor. Keep responses under 280 characters."""
                    }, {
                        "role": "user",
                        "content": "Generate a thought-provoking tweet about technology or society."
                    }],
                    "max_tokens": 100,
                    "stream": False
                }
            }
            
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Extract the tweet content from the response
            tweet_content = response.json()['choices'][0]['message']['content'].strip()
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
        """Post a tweet using browser automation"""
        if not self.logged_in:
            self.login()

        tweet_content = self.generate_tweet()
        if not tweet_content:
            return

        try:
            # Click on Tweet button
            tweet_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            tweet_button.click()
            
            # Enter tweet content
            tweet_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            tweet_input.send_keys(tweet_content)
            
            # Click Post button
            post_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
            )
            post_button.click()
            
            print(f"Tweet posted successfully at {datetime.now()}")
            time.sleep(5)  # Wait for tweet to be posted
            
        except Exception as e:
            print(f"Error posting tweet: {e}")
            # Refresh the page if there's an error
            self.driver.refresh()
            time.sleep(5)

    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function to run the Twitter bot"""
    bot = TwitterBot()
    
    try:
        # Initial login
        bot.login()
        
        # Schedule tweets every 4 hours
        schedule.every(4).hours.do(bot.post_tweet)
        
        # Post initial tweet
        bot.post_tweet()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\nShutting down bot...")
    finally:
        bot.cleanup()

if __name__ == "__main__":
    main()
