"""
Tweet History Manager - Stores and manages Elion's tweet history for better variety and context
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class TweetHistoryManager:
    def __init__(self, history_file: str = "elion_tweet_history.json"):
        self.history_file = history_file
        self.max_history_size = 300 * 1024 * 1024  # 300MB in bytes
        self.history = self._load_history()
        
    def _load_history(self) -> Dict:
        """Load tweet history from file"""
        default_history = {
            'metadata': {
                'last_cleanup': datetime.now().isoformat(),
                'total_tweets': 0,
                'file_size': 0
            },
            'tweets': [],
            'personas': {},  # Track persona usage
            'topics': {},    # Track topic frequency
            'tokens': set()  # Track mentioned tokens
        }
        
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    # Convert tokens back to set
                    history['tokens'] = set(history.get('tokens', []))
                    return history
            return default_history
        except Exception as e:
            print(f"Error loading history: {e}")
            return default_history
    
    def _save_history(self):
        """Save tweet history to file"""
        try:
            # Convert set to list for JSON serialization
            history_to_save = self.history.copy()
            history_to_save['tokens'] = list(self.history['tokens'])
            
            with open(self.history_file, 'w') as f:
                json.dump(history_to_save, f, indent=2)
                
            # Update file size in metadata
            self.history['metadata']['file_size'] = os.path.getsize(self.history_file)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_tweet(self, tweet_content: str, persona: str, category: str):
        """Add a new tweet to history"""
        # Extract mentioned tokens
        tokens = set(word for word in tweet_content.split() if word.startswith('$'))
        
        tweet = {
            'content': tweet_content,
            'persona': persona,
            'category': category,
            'timestamp': datetime.now().isoformat(),
            'tokens': list(tokens)
        }
        
        # Update statistics
        self.history['tweets'].append(tweet)
        self.history['metadata']['total_tweets'] += 1
        self.history['personas'][persona] = self.history['personas'].get(persona, 0) + 1
        self.history['topics'][category] = self.history['topics'].get(category, 0) + 1
        self.history['tokens'].update(tokens)
        
        # Cleanup if needed
        self._cleanup_if_needed()
        self._save_history()
    
    def _cleanup_if_needed(self):
        """Cleanup old tweets if file size exceeds limit"""
        if os.path.exists(self.history_file):
            current_size = os.path.getsize(self.history_file)
            if current_size > self.max_history_size:
                # Keep last 1000 tweets
                self.history['tweets'] = self.history['tweets'][-1000:]
                # Reset statistics
                self._recalculate_statistics()
                self._save_history()
    
    def _recalculate_statistics(self):
        """Recalculate all statistics from current tweets"""
        self.history['personas'] = {}
        self.history['topics'] = {}
        self.history['tokens'] = set()
        
        for tweet in self.history['tweets']:
            self.history['personas'][tweet['persona']] = self.history['personas'].get(tweet['persona'], 0) + 1
            self.history['topics'][tweet['category']] = self.history['topics'].get(tweet['category'], 0) + 1
            self.history['tokens'].update(set(tweet.get('tokens', [])))
    
    def get_recent_tokens(self, days: int = 3) -> set:
        """Get tokens mentioned in last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_tokens = set()
        
        for tweet in self.history['tweets']:
            tweet_date = datetime.fromisoformat(tweet['timestamp'])
            if tweet_date > cutoff:
                recent_tokens.update(set(tweet.get('tokens', [])))
        
        return recent_tokens
    
    def get_persona_stats(self) -> Dict:
        """Get statistics about persona usage"""
        return self.history['personas']
    
    def get_topic_stats(self) -> Dict:
        """Get statistics about topic coverage"""
        return self.history['topics']
    
    def is_recent_duplicate(self, content: str, hours: int = 24) -> bool:
        """Check if similar content was tweeted recently"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Get recent tweets
        recent_tweets = [
            tweet['content'] for tweet in self.history['tweets']
            if datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]
        
        # Simple similarity check (can be improved)
        content_words = set(content.lower().split())
        for tweet in recent_tweets:
            tweet_words = set(tweet.lower().split())
            similarity = len(content_words.intersection(tweet_words)) / len(content_words.union(tweet_words))
            if similarity > 0.7:  # 70% similar words
                return True
        
        return False
    
    def suggest_persona(self, category: str) -> str:
        """Suggest a persona based on recent usage and category"""
        # Get persona usage in last 24h
        cutoff = datetime.now() - timedelta(hours=24)
        recent_personas = {}
        
        for tweet in self.history['tweets']:
            tweet_date = datetime.fromisoformat(tweet['timestamp'])
            if tweet_date > cutoff:
                persona = tweet['persona']
                recent_personas[persona] = recent_personas.get(persona, 0) + 1
        
        # Prefer less used personas
        all_personas = {'alpha_hunter', 'degen_trader', 'tech_analyst', 'meta_commentary', 'insider_ai'}
        unused_personas = all_personas - set(recent_personas.keys())
        
        if unused_personas:
            return random.choice(list(unused_personas))
        
        # If all used, pick least used
        return min(recent_personas.items(), key=lambda x: x[1])[0]
    
    def get_market_mood(self, hours: int = 24) -> str:
        """Analyze recent tweets to determine market mood"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_tweets = [
            tweet for tweet in self.history['tweets']
            if datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]
        
        if not recent_tweets:
            return 'neutral'
        
        # Simple sentiment analysis based on keywords
        bullish_words = {'moon', 'pump', 'breakout', 'accumulation', 'bullish', 'launch', 'integration'}
        bearish_words = {'dump', 'crash', 'bearish', 'correction', 'fear'}
        
        bull_count = 0
        bear_count = 0
        
        for tweet in recent_tweets:
            content = tweet['content'].lower()
            bull_count += sum(1 for word in bullish_words if word in content)
            bear_count += sum(1 for word in bearish_words if word in content)
        
        if bull_count > bear_count * 1.5:
            return 'bullish'
        elif bear_count > bull_count * 1.5:
            return 'bearish'
        return 'neutral'
