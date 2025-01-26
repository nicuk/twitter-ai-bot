import importlib
from langchain.tools import StructuredTool
from langchain_core.tools import ToolException
from langchain_experimental.utilities import PythonREPL
from loguru import logger
from pydantic import BaseModel, Field
from langflow.base.langchain_utilities.model import LCToolComponent
from langflow.inputs import StrInput
from langflow.schema import Data
import os
from dotenv import load_dotenv
from twitter.api_client import TwitterAPI

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
            value="Posts tweets to Twitter using Twitter API.",
        ),
        StrInput(
            name="global_imports",
            display_name="Global Imports",
            info="Required imports for Twitter API",
            value="os,dotenv,twitter",
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
        """Post a tweet using the Twitter API"""
        try:
            # Get existing TwitterAPI instance from bot
            from twitter.bot import AIGamingBot
            bot = AIGamingBot()
            
            # Post tweet using bot's API instance
            response = bot.api.create_tweet(tweet_content)
            if response:
                logger.info("Successfully posted tweet")
                return "Tweet posted successfully"
            else:
                logger.error("Failed to post tweet")
                return "Failed to post tweet"
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            raise ToolException(f"Error posting tweet: {e}")

    def get_globals(self, global_imports: str | list[str]) -> dict:
        """Get global imports for the REPL environment"""
        global_dict = {}
        if isinstance(global_imports, str):
            modules = [imp.strip() for imp in global_imports.split(",")]
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
