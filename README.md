# AI Twitter Bot

This is an automated Twitter bot that generates and posts tweets using GPT-4, similar to Terminal of Truths.

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API credentials:
   - Copy `.env.template` to a new file named `.env`
   - Get your Twitter API credentials from the Twitter Developer Portal
   - Get your OpenAI API key from OpenAI
   - Fill in your credentials in the `.env` file

3. Run the bot:
```bash
python twitter_bot.py
```

## Features

- Generates tweets using GPT-4
- Posts automatically every 4 hours
- Handles API rate limits and errors
- Configurable tweet generation prompt

## Customization

You can modify the system prompt in `twitter_bot.py` to change the bot's personality and the type of content it generates.

## Important Notes

- Make sure to follow Twitter's automation rules and guidelines
- Monitor your API usage to stay within limits
- Keep your API keys secure and never share them
