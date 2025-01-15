import importlib
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from langchain_experimental.utilities import PythonREPL
from loguru import logger
from pydantic import BaseModel, Field
from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.inputs import StrInput
from langflow.schema import Data
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

load_dotenv()

class PythonREPLToolComponent(LCToolComponent):
    display_name = "Python REPL"
    description = "A tool for running Python code in a REPL environment."
    name = "PythonREPLTool"
    icon = "Python"

    inputs = [
        StrInput(
            name="name",
            display_name="Tool Name",
            info="The name of the tool.",
            value="python_repl",
        ),
        StrInput(
            name="description",
            display_name="Tool Description",
            info="A description of the tool.",
            value="Posts tweets to Twitter using Selenium automation.",
        ),
        StrInput(
            name="global_imports",
            display_name="Global Imports",
            info="Required imports for Twitter automation",
            value="selenium,os,time,dotenv",
        ),
        StrInput(
            name="input_data",
            display_name="Tweet Content",
            info="The tweet content to post",
            value="",
            input_types=["Message", "str"],  # Accept Message type from Chat Output
        ),
    ]

    class PythonREPLSchema(BaseModel):
        tweet: str = Field(..., description="The tweet content to post")

    def post_tweet(self, tweet_content):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                options=options)
        wait = WebDriverWait(driver, 20)
        
        try:
            # Login
            driver.get('https://twitter.com/login')
            username_input = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            username_input.send_keys(os.getenv('TWITTER_USERNAME'))
            username_input.send_keys(Keys.RETURN)
            
            password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            password_input.send_keys(os.getenv('TWITTER_PASSWORD'))
            password_input.send_keys(Keys.RETURN)
            
            # Wait for home timeline and post tweet
            wait.until(EC.presence_of_element_located((By.ARIA_LABEL, "Home timeline")))
            tweet_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')))
            tweet_button.click()
            
            tweet_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweetTextarea_0"]')))
            tweet_input.send_keys(tweet_content)
            
            post_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="tweetButton"]')))
            post_button.click()
            
            time.sleep(5)
            return f"Tweet posted successfully: {tweet_content}"
            
        except Exception as e:
            return f"Error posting tweet: {e}"
        finally:
            driver.quit()

    def get_globals(self, global_imports: str | list[str]) -> dict:
        global_dict = {}
        if isinstance(global_imports, str):
            modules = [module.strip() for module in global_imports.split(",")]
        elif isinstance(global_imports, list):
            modules = global_imports
        else:
            msg = "global_imports must be either a string or a list"
            raise TypeError(msg)

        for module in modules:
            try:
                imported_module = importlib.import_module(module)
                global_dict[imported_module.__name__] = imported_module
            except ImportError as e:
                logger.opt(exception=True).debug(f"Could not import module {module}")
                continue
        return global_dict

    def build_tool(self) -> StructuredTool:
        def run_twitter_post(tweet: str) -> str:
            try:
                return self.post_tweet(tweet)
            except Exception as e:
                logger.opt(exception=True).debug("Error posting to Twitter")
                raise ToolException(str(e)) from e

        tool = StructuredTool.from_function(
            name=self.name,
            description=self.description,
            func=run_twitter_post,
            args_schema=self.PythonREPLSchema,
        )

        self.status = "Twitter posting tool created successfully"
        return tool

    def run_model(self, data: dict = None) -> list[Data]:
        tool = self.build_tool()
        # Handle both direct input and message input
        tweet_content = ""
        if data and isinstance(data, dict):
            if "message" in data:
                tweet_content = data["message"]
            elif "input_data" in data:
                tweet_content = data["input_data"]
        
        if tweet_content:
            result = tool.run(tweet_content)
        else:
            result = "No tweet content received"
        return [Data(data={"result": result})]
