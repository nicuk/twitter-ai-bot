"""
ELAI - Advanced AI Trading Bot
"""

from .elion import Elion
from .personality.traits import PersonalityManager
from .content.generator import ContentGenerator
from .content.tweet_formatters import TweetFormatters

__version__ = "1.0.0"

__all__ = [
    'Elion',
    'PersonalityManager',
    'ContentGenerator',
    'TweetFormatters'
]
