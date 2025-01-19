import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time
import random

class MarketIntelGatherer:
    def __init__(self):
        self.data_dir = 'market_data'
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data files
        self.files = {
            'trending': os.path.join(self.data_dir, 'trending_projects.json'),
            'interactions': os.path.join(self.data_dir, 'user_interactions.json'),
            'mentions': os.path.join(self.data_dir, 'project_mentions.json')
        }
        
        # Load existing data
        self.trending_projects = self._load_json(self.files['trending'])
        self.user_interactions = self._load_json(self.files['interactions'])
        self.project_mentions = self._load_json(self.files['mentions'])
        
        # Initialize headers for web requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def _load_json(self, filepath):
        """Load JSON data from file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
            return {'items': [], 'last_updated': None}
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {'items': [], 'last_updated': None}
    
    def _save_json(self, data, filepath):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving to {filepath}: {e}")
    
    def scrape_trending_projects(self):
        """Scrape trending projects from various sources"""
        try:
            # CoinGecko Gainers/Losers
            response = requests.get('https://www.coingecko.com/en/crypto-gainers-losers', headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Find gainers table
                gainers = soup.find('table', {'data-target': 'gecko-table.table'})
                if gainers:
                    rows = gainers.find_all('tr')
                    for row in rows[1:]:  # Skip header
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            name_col = cols[1].text.strip()
                            if name_col:
                                project = {
                                    'name': name_col,
                                    'source': 'coingecko_gainers',
                                    'time': datetime.utcnow().isoformat()
                                }
                                self.trending_projects['items'].append(project)
            
            # DEXScreener Trending
            response = requests.get('https://dexscreener.com/trending', headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                trending_items = soup.find_all('div', {'class': 'chakra-card'})
                for item in trending_items:
                    name = item.find('span', {'class': 'chakra-text'})
                    if name:
                        project = {
                            'name': name.text.strip(),
                            'source': 'dexscreener',
                            'time': datetime.utcnow().isoformat()
                        }
                        self.trending_projects['items'].append(project)
            
            # Keep only recent items (last 24 hours)
            current_time = datetime.utcnow()
            self.trending_projects['items'] = [
                item for item in self.trending_projects['items']
                if (current_time - datetime.fromisoformat(item['time'])).total_seconds() <= 24 * 3600
            ]
            
            # Remove duplicates (keep most recent)
            seen = set()
            unique_items = []
            for item in sorted(self.trending_projects['items'], key=lambda x: x['time'], reverse=True):
                if item['name'].lower() not in seen:
                    seen.add(item['name'].lower())
                    unique_items.append(item)
            
            self.trending_projects['items'] = unique_items
            self.trending_projects['last_updated'] = datetime.utcnow().isoformat()
            self._save_json(self.trending_projects, self.files['trending'])
            
            print(f"Found {len(unique_items)} trending projects")
            
        except Exception as e:
            print(f"Error scraping trending projects: {e}")
    
    def track_interaction(self, username, project, interaction_type):
        """Track user interactions with projects"""
        try:
            interaction = {
                'username': username,
                'project': project,
                'type': interaction_type,
                'time': datetime.utcnow().isoformat()
            }
            
            self.user_interactions['items'].append(interaction)
            self._save_json(self.user_interactions, self.files['interactions'])
            
            # Also update project mentions
            self._update_project_mentions(project)
            
        except Exception as e:
            print(f"Error tracking interaction: {e}")
    
    def _update_project_mentions(self, project):
        """Update project mention counts"""
        try:
            # Find existing project or create new entry
            found = False
            for item in self.project_mentions['items']:
                if item['project'].lower() == project.lower():
                    item['mentions'] += 1
                    item['last_mentioned'] = datetime.utcnow().isoformat()
                    found = True
                    break
            
            if not found:
                self.project_mentions['items'].append({
                    'project': project,
                    'mentions': 1,
                    'first_mentioned': datetime.utcnow().isoformat(),
                    'last_mentioned': datetime.utcnow().isoformat()
                })
            
            self._save_json(self.project_mentions, self.files['mentions'])
            
        except Exception as e:
            print(f"Error updating project mentions: {e}")
    
    def get_trending_projects(self, category=None, limit=10):
        """Get trending projects, optionally filtered by category"""
        try:
            # Sort by recency
            sorted_projects = sorted(
                self.trending_projects['items'],
                key=lambda x: x['time'],
                reverse=True
            )
            
            if category:
                sorted_projects = [p for p in sorted_projects if p.get('category') == category]
            
            return sorted_projects[:limit]
            
        except Exception as e:
            print(f"Error getting trending projects: {e}")
            return []
    
    def get_most_mentioned_projects(self, hours=24, limit=10):
        """Get most mentioned projects in the last X hours"""
        try:
            current_time = datetime.utcnow()
            recent_projects = []
            
            for project in self.project_mentions['items']:
                last_mentioned = datetime.fromisoformat(project['last_mentioned'])
                hours_ago = (current_time - last_mentioned).total_seconds() / 3600
                
                if hours_ago <= hours:
                    recent_projects.append(project)
            
            # Sort by mention count
            sorted_projects = sorted(
                recent_projects,
                key=lambda x: x['mentions'],
                reverse=True
            )
            
            return sorted_projects[:limit]
            
        except Exception as e:
            print(f"Error getting most mentioned projects: {e}")
            return []
    
    def get_user_favorites(self, username):
        """Get projects a user has interacted with"""
        try:
            user_projects = {}
            
            for interaction in self.user_interactions['items']:
                if interaction['username'] == username:
                    project = interaction['project']
                    user_projects[project] = user_projects.get(project, 0) + 1
            
            # Sort by interaction count
            sorted_projects = sorted(
                user_projects.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return [{'project': p[0], 'interactions': p[1]} for p in sorted_projects]
            
        except Exception as e:
            print(f"Error getting user favorites: {e}")
            return []

    def generate_market_insight(self):
        """Generate market insight based on collected data"""
        try:
            insights = []
            current_time = datetime.utcnow()
            
            # Get recent trending projects (last 6 hours)
            recent_trending = [
                item for item in self.trending_projects['items']
                if (current_time - datetime.fromisoformat(item['time'])).total_seconds() <= 6 * 3600
            ]
            
            if recent_trending:
                # Group by source
                by_source = {}
                for item in recent_trending:
                    source = item['source']
                    if source not in by_source:
                        by_source[source] = []
                    by_source[source].append(item)
                
                # Generate insights for each source
                for source, items in by_source.items():
                    if source == 'coingecko_gainers':
                        project = random.choice(items)
                        insights.append(f"🚀 {project['name']} is among top gainers on CoinGecko! Worth checking out? #Crypto")
                    elif source == 'dexscreener':
                        project = random.choice(items)
                        insights.append(f"📈 {project['name']} is trending on DEXScreener! What's the story? #DeFi")
            
            # Get most mentioned projects in last 12 hours
            mentioned = self.get_most_mentioned_projects(hours=12, limit=5)
            if mentioned:
                project = random.choice(mentioned)
                mentions = project['mentions']
                insights.append(f"👀 {project['project']} is getting attention with {mentions} mentions in the last 12 hours! #Crypto")
            
            # Return random insight or None if no insights
            return random.choice(insights) if insights else None
            
        except Exception as e:
            print(f"Error generating market insight: {e}")
            return None
