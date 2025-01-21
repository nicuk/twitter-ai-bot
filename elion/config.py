import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/elai')

# API Keys and Tokens
CRYPTORANK_API_KEY = os.getenv('CRYPTORANK_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_CLIENT_ID')  # Changed from TWITTER_API_KEY
TWITTER_API_SECRET = os.getenv('TWITTER_CLIENT_SECRET')  # Changed from TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')  # Changed from TWITTER_ACCESS_SECRET

# Market Analysis Settings
MARKET_SETTINGS = {
    'gem_market_cap_min': 5_000_000,  # $5M minimum
    'gem_market_cap_max': 500_000_000,  # $500M maximum
    'significant_volume_ratio': 0.3,  # Volume/MCap ratio threshold
    'minimum_price_change': 5,  # Minimum 24h price change %
    'maximum_gems_per_call': 3,  # Max number of gems to mention
}

# Twitter Settings
TWEET_MAX_LENGTH = 280
TWEET_MIN_LENGTH = 240  # Minimum length for better engagement
TWEET_MAX_HASHTAGS = 3  # Maximum number of hashtags per tweet
TWEET_THREAD_MAX = 4  # Maximum tweets in a thread

# Excluded Tokens
EXCLUDED_TOKENS = {
    'stablecoins': {'USDT', 'USDC', 'DAI', 'BUSD'},
    'mega_caps': {'BTC', 'ETH'}
}

# ELAI Settings
ELAI_SETTINGS = {
    'name': 'ELAI',
    'description': 'Enhanced Learning AI for Crypto Trading',
    'version': '1.0.0',
    'personality': {
        'quirky': 0.8,
        'technical': 0.7,
        'empathetic': 0.6,
        'confident': 0.7,
        'playful': 0.8,
        'reflective': 0.9,
        'curious': 0.9,
        'humble': 0.8
    }
}
