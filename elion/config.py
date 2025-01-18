import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/elion.db')

# API Keys
CRYPTORANK_API_KEY = os.getenv('CRYPTORANK_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')

# Market Analysis Settings
MARKET_SETTINGS = {
    'gem_market_cap_min': 5_000_000,  # $5M minimum
    'gem_market_cap_max': 500_000_000,  # $500M maximum
    'significant_volume_ratio': 0.3,  # Volume/MCap ratio threshold
    'minimum_price_change': 5,  # Minimum 24h price change %
    'maximum_gems_per_call': 3,  # Max number of gems to mention
}

# Twitter Settings
TWEET_MIN_LENGTH = 180  # Minimum tweet length for substantial content
TWEET_MAX_LENGTH = 280  # Maximum tweet length
TWEET_THREAD_MAX = 4  # Maximum tweets in a thread

# Excluded Tokens
EXCLUDED_TOKENS = {
    'stablecoins': {'USDT', 'USDC', 'DAI', 'BUSD'},
    'mega_caps': {'BTC', 'ETH'}
}
