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
        
        # Initialize project stats if not exists
        if 'project_stats' not in self.history:
            self.history['project_stats'] = {}
        if 'tweet_types' not in self.history:
            self.history['tweet_types'] = {
                'regular': 0,
                'controversial': 0,
                'giveaway': 0,
                'ai_aware': 0
            }
        
        # Initialize core tracking features
        if 'personality_stats' not in self.history:
            self.history['personality_stats'] = {
                'quantum_references': 0,
                'ai_jokes': 0,
                'binary_speak': 0,
                'circuit_mentions': 0
            }
        
        if 'interactions' not in self.history:
            self.history['interactions'] = {
                'agreements': 0,
                'disagreements': 0,
                'memes': 0,
                'alpha_shares': 0
            }
            
        if 'engagement_stats' not in self.history:
            self.history['engagement_stats'] = {
                'mentioned_by': set(),
                'top_interactions': {},
                'viral_tweets': [],
                'project_performance': {}
            }
            
        if 'favorite_humans' not in self.history:
            self.history['favorite_humans'] = set()
            
        if 'running_jokes' not in self.history:
            self.history['running_jokes'] = set()
        
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

    def track_project_engagement(self, project: str, engagement: dict):
        """Track engagement metrics for specific projects"""
        if project not in self.history['project_stats']:
            self.history['project_stats'][project] = {
                'mentions': 0,
                'total_engagement': 0,
                'last_mentioned': None
            }
        
        stats = self.history['project_stats'][project]
        stats['mentions'] += 1
        stats['total_engagement'] += (engagement.get('retweets', 0) * 2 + engagement.get('likes', 0))
        stats['last_mentioned'] = datetime.now().isoformat()
        self._save_history()

    def get_top_performing_categories(self, days: int = 7):
        """Get categories sorted by engagement"""
        cutoff = datetime.now() - timedelta(days=days)
        category_stats = {}
        
        for tweet in self.history['tweets']:
            if datetime.fromisoformat(tweet['timestamp']) > cutoff:
                category = tweet['category']
                if category not in category_stats:
                    category_stats[category] = {
                        'tweets': 0,
                        'engagement': 0
                    }
                category_stats[category]['tweets'] += 1
                engagement = tweet.get('engagement', {})
                engagement_score = (
                    engagement.get('retweets', 0) * 2 + 
                    engagement.get('likes', 0)
                )
                category_stats[category]['engagement'] += engagement_score
        
        # Sort by engagement per tweet
        return sorted(
            category_stats.items(),
            key=lambda x: x[1]['engagement'] / x[1]['tweets'] if x[1]['tweets'] > 0 else 0,
            reverse=True
        )

    def get_tweet_type_for_next_post(self):
        """Determine next tweet type based on 50-post cycle"""
        total_tweets = self.history['metadata']['total_tweets']
        position_in_cycle = total_tweets % 50
        
        # Update tweet type counts
        if position_in_cycle in [15, 35]:  # Posts 15 and 35 are controversial
            self.history['tweet_types']['controversial'] += 1
            return 'controversial'
        elif position_in_cycle in [25, 45]:  # Posts 25 and 45 are giveaways
            self.history['tweet_types']['giveaway'] += 1
            return 'giveaway'
        elif position_in_cycle in [10, 30]:  # Posts 10 and 30 are AI self-aware
            self.history['tweet_types']['ai_aware'] += 1
            return 'ai_aware'
        else:
            self.history['tweet_types']['regular'] += 1
            return 'regular'

    def get_hot_projects(self, hours: int = 24):
        """Get currently hot projects based on engagement"""
        cutoff = datetime.now() - timedelta(hours=hours)
        active_projects = {}
        
        for project, stats in self.history['project_stats'].items():
            if stats['last_mentioned']:
                last_mention = datetime.fromisoformat(stats['last_mentioned'])
                if last_mention > cutoff:
                    engagement_rate = stats['total_engagement'] / stats['mentions']
                    active_projects[project] = engagement_rate
        
        return sorted(
            active_projects.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Return top 5 projects

    def get_recent_engagement(self, hours: int = 24) -> float:
        """Calculate average engagement for recent tweets"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_tweets = [
            tweet for tweet in self.history['tweets']
            if datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]
        
        if not recent_tweets:
            return 0.0
        
        total_engagement = 0
        for tweet in recent_tweets:
            engagement = tweet.get('engagement', {})
            total_engagement += (
                engagement.get('retweets', 0) * 2 + 
                engagement.get('likes', 0) + 
                engagement.get('replies', 0) * 3  # Weight replies more
            )
        
        return total_engagement / len(recent_tweets)

    def get_viral_threshold(self) -> float:
        """Calculate viral threshold based on historical performance"""
        if not self.history['tweets']:
            return 20.0  # Default threshold
            
        engagements = []
        for tweet in self.history['tweets']:
            engagement = tweet.get('engagement', {})
            score = (
                engagement.get('retweets', 0) * 2 + 
                engagement.get('likes', 0) + 
                engagement.get('replies', 0) * 3
            )
            engagements.append(score)
            
        if not engagements:
            return 20.0
            
        # Set threshold at 90th percentile
        return sorted(engagements)[int(len(engagements) * 0.9)]

    def get_best_posting_times(self) -> list:
        """Analyze best times to post based on engagement"""
        time_scores = {}
        
        for tweet in self.history['tweets']:
            timestamp = datetime.fromisoformat(tweet['timestamp'])
            hour = timestamp.hour
            
            if hour not in time_scores:
                time_scores[hour] = {'total': 0, 'count': 0}
            
            engagement = tweet.get('engagement', {})
            score = (
                engagement.get('likes', 0) + 
                engagement.get('retweets', 0) * 2 + 
                engagement.get('replies', 0) * 3
            )
            
            time_scores[hour]['total'] += score
            time_scores[hour]['count'] += 1
        
        # Calculate average score for each hour
        best_times = [
            (hour, stats['total'] / stats['count'])
            for hour, stats in time_scores.items()
            if stats['count'] > 0
        ]
        
        # Return top 5 hours sorted by score
        return sorted(best_times, key=lambda x: x[1], reverse=True)[:5]

    def should_follow_up(self, project: str, hours: int = 24) -> bool:
        """Check if we should follow up on a previous tweet about a project"""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        # Find recent tweets about this project
        project_tweets = [
            tweet for tweet in self.history['tweets']
            if project.lower() in tweet['content'].lower() and
            datetime.fromisoformat(tweet['timestamp']) > cutoff
        ]
        
        if not project_tweets:
            return False
            
        # Check if any had good engagement
        for tweet in project_tweets:
            engagement = tweet.get('engagement', {})
            score = (
                engagement.get('retweets', 0) * 2 + 
                engagement.get('likes', 0) + 
                engagement.get('replies', 0) * 3
            )
            if score >= 20:  # Threshold for follow-up
                return True
                
        return False

    def get_follow_up_stats(self, project: str) -> dict:
        """Get stats for follow-up tweet"""
        project_stats = self.history['project_stats'].get(project, {})
        
        if not project_stats:
            return None
            
        return {
            'initial_mention': project_stats.get('first_mentioned'),
            'total_engagement': project_stats.get('total_engagement'),
            'mention_count': project_stats.get('mentions'),
            'last_metrics': project_stats.get('last_metrics', {})
        }

    def track_interaction(self, interaction_type: str):
        """Track different types of interactions to maintain personality balance"""
        if interaction_type in self.history['interactions']:
            self.history['interactions'][interaction_type] += 1
        self._save_history()

    def track_personality_trait(self, trait: str):
        """Track usage of personality traits to keep them balanced"""
        if trait in self.history['personality_stats']:
            self.history['personality_stats'][trait] += 1
        self._save_history()

    def get_personality_balance(self) -> dict:
        """Get stats about personality trait usage"""
        total = sum(self.history['personality_stats'].values())
        if total == 0:
            return {k: 0.25 for k in self.history['personality_stats'].keys()}
        return {k: v/total for k, v in self.history['personality_stats'].items()}

    def update_tweet_engagement(self, tweet_id: str, engagement_metrics: dict):
        """Update engagement metrics for a tweet"""
        for tweet in self.history['tweets']:
            if tweet.get('id') == tweet_id:
                if 'engagement' not in tweet:
                    tweet['engagement'] = {}
                tweet['engagement'].update(engagement_metrics)
                
                # Track viral tweets
                if (engagement_metrics.get('likes', 0) > 100 or 
                    engagement_metrics.get('retweets', 0) > 50):
                    self.history['engagement_stats']['viral_tweets'].append({
                        'id': tweet_id,
                        'content': tweet['content'],
                        'engagement': tweet['engagement'],
                        'type': tweet.get('tweet_type')
                    })
                
                self._save_history()
                break

    def get_engagement_strategy(self) -> dict:
        """Get insights for engagement strategy"""
        viral_types = {}
        for tweet in self.history['engagement_stats']['viral_tweets']:
            tweet_type = tweet.get('type', 'unknown')
            viral_types[tweet_type] = viral_types.get(tweet_type, 0) + 1
        
        return {
            'best_tweet_types': viral_types,
            'top_mentioned_projects': self._get_top_mentioned_tokens(5),
            'engagement_rate': self._calculate_engagement_rate()
        }

    def _calculate_engagement_rate(self) -> float:
        """Calculate average engagement rate for recent tweets"""
        total_engagement = 0
        tweet_count = 0
        cutoff = datetime.now() - timedelta(days=7)
        
        for tweet in self.history['tweets']:
            if datetime.fromisoformat(tweet['timestamp']) > cutoff:
                engagement = tweet.get('engagement', {})
                total_engagement += (
                    engagement.get('likes', 0) + 
                    engagement.get('retweets', 0) * 2 + 
                    engagement.get('replies', 0) * 3
                )
                tweet_count += 1
        
        return total_engagement / tweet_count if tweet_count > 0 else 0

    def add_favorite_human(self, username: str):
        """Add a human to Elion's favorites list"""
        self.history['favorite_humans'].add(username)
        self._save_history()

    def add_running_joke(self, joke: str):
        """Add a running joke to track"""
        self.history['running_jokes'].add(joke)
        self._save_history()

    def get_favorite_humans(self, limit: int = 5) -> list:
        """Get Elion's favorite humans to interact with"""
        return list(self.history['favorite_humans'])[:limit]

    def get_running_jokes(self, limit: int = 3) -> list:
        """Get active running jokes to reference"""
        return list(self.history['running_jokes'])[:limit]
