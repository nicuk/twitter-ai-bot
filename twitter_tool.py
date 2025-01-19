from langchain.tools import BaseTool
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv
import time
import schedule

load_dotenv()

class TwitterPostTool(BaseTool):
    name = "twitter_post"
    description = "Posts a tweet to Twitter using Selenium"
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.logged_in = False
        
    def setup_driver(self):
        if not self.driver:
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                        options=options)
            self.wait = WebDriverWait(self.driver, 20)
    
    def login(self):
        if self.logged_in:
            return
        
        self.setup_driver()
        try:
            self.driver.get('https://twitter.com/login')
            
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_input.send_keys(os.getenv('TWITTER_USERNAME'))
            username_input.send_keys(Keys.RETURN)
            
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(os.getenv('TWITTER_PASSWORD'))
            password_input.send_keys(Keys.RETURN)
            
            self.wait.until(
                EC.presence_of_element_located((By.ARIA_LABEL, "Home timeline"))
            )
            
            self.logged_in = True
            
        except Exception as e:
            print(f"Error logging in: {e}")
            if self.driver:
                self.driver.quit()
            raise

    def _run(self, tweet_content: str) -> str:
        """Post a tweet using Selenium"""
        if not self.logged_in:
            self.login()

        try:
            # Click tweet button
            tweet_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            tweet_button.click()
            
            # Enter tweet content
            tweet_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]'))
            )
            tweet_input.send_keys(tweet_content)
            
            # Click post button
            post_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]'))
            )
            post_button.click()
            
            time.sleep(5)  # Wait for tweet to be posted
            return f"Successfully posted tweet: {tweet_content}"
            
        except Exception as e:
            return f"Error posting tweet: {e}"

    def schedule_tweets(self, interval_hours=2):
        """Schedule tweets every X hours"""
        schedule.every(interval_hours).hours.do(self._run)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
