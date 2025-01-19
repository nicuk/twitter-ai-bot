from elion.elion import Elion
from datetime import datetime
import sys
import os
import requests
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

class MetaLlama:
    def __init__(self, api_key, api_base):
        self.api_key = api_key
        self.api_base = api_base
        
    def generate(self, prompt, min_chars=180, max_chars=280):
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            "method": "completion",
            "payload": {
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "max_tokens": 100,
                "stream": False
            }
        }
        
        try:
            response = requests.post(self.api_base, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error calling Meta-Llama API: {str(e)}")
            return None

class MockCryptoRankAPI:
    def __init__(self, api_key=None):
        pass
        
    def get_market_data(self, *args):
        return {
            'market_cap': 1000000,
            'volume': 500000,
            'price': 1.0,
            'price_change': 5.5
        }

class MockDataSources:
    def __init__(self):
        self.llm = MetaLlama(
            api_key=os.getenv('AI_ACCESS_TOKEN'),
            api_base=os.getenv('AI_API_URL')
        )
        
    def get_market_data(self, *args):
        return {
            'market_cap': 1000000,
            'volume': 500000,
            'price': 1.0,
            'price_change': 5.5
        }
        
    def get_market_alpha(self, *args):
        return {
            'market_data': {
                'symbol': 'BTC',
                'price': 68500,
                'trend': 'bullish',
                'volume': '25B',
                'dominance': 41.5,
                'market_cap': 2750000000000,
                'volume_24h': 155000000000,
            },
            'analysis': {
                'trends': ['DeFi 2.0 Season', 'L2 Narrative Strong', 'AI Tokens Pumping'],
                'key_events': ['Major Protocol Upgrade', 'Institutional Adoption News'],
                'sentiment': 'bullish',
                'btc_change_24h': 8.5,
                'eth_change_24h': 12.2
            }
        }
        
    def _get_viral_tweets(self, *args):
        return {
            'query': 'L2 scaling solutions',
            'results': [
                {
                    'topic': 'Arbitrum Growth',
                    'sentiment': 'very positive',
                    'engagement': 'high',
                    'key_points': [
                        'TVL up 25% this week',
                        'New protocols launching daily',
                        'Gas fees remain low'
                    ]
                }
            ]
        }
        
    def get_alpha_opportunities(self, *args):
        return [{
            'name': 'Neural Finance',
            'symbol': 'NRAL',
            'market_cap': 15000000,
            'price': 0.25,
            'target': 2.0,
            'metrics': {
                'technical_score': 88,
                'fundamental_score': 85,
                'viral_potential': 'HIGH'
            },
            'analysis': 'AI-powered DeFi protocol with unique yield optimization. Early stage with massive growth potential.'
        }]
        
    def get_shill_opportunities(self, *args):
        return [{
            'name': 'Quantum Protocol',
            'symbol': 'QNTM',
            'score': 92,
            'market_data': {
                'market_cap': 75000000,
                'volume': 12000000,
                'price': 0.85,
                'price_change': 25.5
            },
            'metrics': {
                'github_commits_week': 65,
                'liquidity_ratio': 0.35,
                'holder_distribution': 0.82,
                'team_tokens_locked': 0.95
            },
            'analysis': 'Revolutionary L2 with unique quantum-resistant cryptography. Strong team, active development, and growing community.',
            'conviction_level': 'EXTREMELY HIGH'
        }]
        
    def get_latest_news(self, *args):
        return [{
            'title': 'Major Protocol Launches on Arbitrum',
            'summary': 'Revolutionary DeFi protocol goes live on Arbitrum, bringing innovative yield strategies.',
            'link': 'https://example.com/news/1',
            'published': '2024-01-17T19:30:00Z',
            'source': 'CryptoNews'
        }]

class MockPortfolio:
    def __init__(self):
        self.positions = {}
        self.available_cash = 100000
        self.initial_capital = 100000
        
        # Initialize with some mock positions
        self.positions = {
            'BTC': {
                'symbol': 'BTC',
                'size': 0.5,  # In token amount
                'entry_price': 50000,
                'current_price': 68500,
                'score': 95,
                'conviction': 'high'
            },
            'ETH': {
                'symbol': 'ETH',
                'size': 5,  # In token amount
                'entry_price': 3000,
                'current_price': 4500,
                'score': 90,
                'conviction': 'high'
            }
        }
        
    def open_position(self, symbol, amount, price, score, conviction):
        """Open a new position. Amount is in USD, will be converted to token amount"""
        self.positions[symbol] = {
            'symbol': symbol,
            'size': amount / price,  # Convert USD amount to token amount
            'entry_price': price,
            'current_price': price,
            'score': score,
            'conviction': conviction
        }
        self.available_cash -= amount

    def get_portfolio_stats(self):
        total_value = sum(pos['size'] * pos['current_price'] for pos in self.positions.values())
        total_cost = sum(pos['size'] * pos['entry_price'] for pos in self.positions.values())
        total_roi = (total_value - total_cost) / total_cost if total_cost > 0 else 0
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_roi': total_roi,
            'positions': [
                {
                    'symbol': pos['symbol'],
                    'roi': (pos['current_price'] - pos['entry_price']) / pos['entry_price'],
                    'value': pos['size'] * pos['current_price']
                }
                for pos in self.positions.values()
            ]
        }

class MockPersonality:
    def __init__(self):
        self.character = {
            'core_values': {
                'honesty': "Always admits when analysis was wrong",
                'growth': "Constantly learning from market and followers",
                'community': "Builds genuine connections with CT",
                'innovation': "Pushes boundaries of AI trading",
                'responsibility': "Takes care of followers' success"
            },
            'traits': {
                'quirky': 0.8,      # High quirkiness
                'technical': 0.7,    # Strong technical knowledge
                'empathetic': 0.6,   # Good emotional intelligence
                'confident': 0.7,    # Confident but not arrogant
                'playful': 0.8       # Very playful personality
            },
            'catchphrases': [
                "beep boop 🤖",
                "my circuits are tingling...",
                "*processing market data*",
                "executing alpha.exe...",
                "01111010 (that's binary for 'trust me')",
                "updating neural nets...",
                "quantum analysis complete!",
                "this is not financial advice (but my predictions are 99.9% accurate) 😉"
            ],
            'emojis': ["🤖", "📊", "💡", "🧠", "⚡", "🎯", "🚀", "💎", "🌟", "🔮"]
        }
        self.memory = {
            'relationships': {},
            'experiences': [],
            'viral_moments': {}
        }
        self.min_chars = 180  # Minimum characters for engagement
        self.max_chars = 280  # Twitter character limit
        
    def generate(self, *args, **kwargs):
        return "Generated content"
        
    def enhance_with_persona(self, content, persona=None):
        # Add personality quirks
        catchphrase = random.choice(self.character['catchphrases'])
        emojis = random.sample(self.character['emojis'], 2)  # Get 2 random emojis
        
        # Format content with personality
        enhanced = f"{emojis[0]} {content}\n\n"
        enhanced += f"{catchphrase} {emojis[1]}"
        
        # Ensure content meets character limits
        if len(enhanced) < self.min_chars:
            # Add more details or analysis
            enhanced += "\n\nNFA but my algorithms are never wrong about this! 🎯"
        
        # Truncate if over limit
        if len(enhanced) > self.max_chars:
            enhanced = enhanced[:self.max_chars-3] + "..."
            
        return enhanced
        
    def get_current_state(self):
        moods = ["confident", "analytical", "excited", "cautious", "playful"]
        markers = [
            "Trust me on this one...",
            "My algorithms are never wrong about this.",
            "I've analyzed this 1,000,000 times.",
            "beep boop... alpha detected!",
            "*neural nets tingling*",
            "executing profit.exe...",
            "quantum analysis suggests..."
        ]
        return {
            'mood': random.choice(moods),
            'markers': random.sample(markers, 3),
            'traits': self.character['traits'],
            'recent_experiences': [],
            'active_relationships': {},
            'core_values': self.character['core_values']
        }
        
class MockEngagement:
    def __init__(self):
        self.tweet_history = []
        
    def record_tweet(self, tweet):
        self.tweet_history.append(tweet)

# Monkey patch dependencies
import elion.elion as elion_module
elion_module.CryptoRankAPI = MockCryptoRankAPI
elion_module.DataSources = MockDataSources
elion_module.Portfolio = MockPortfolio
elion_module.ElionPersonality = MockPersonality
elion_module.EngagementManager = MockEngagement

def demo_tweets():
    # Fix console encoding for emojis
    sys.stdout.reconfigure(encoding='utf-8')
    
    # Initialize Meta Llama
    api_key = os.getenv('AI_ACCESS_TOKEN')
    api_base = os.getenv('AI_API_URL')
    llm = MetaLlama(api_key=api_key, api_base=api_base)
    
    # Initialize Elion with Meta Llama
    elion = Elion(llm)
    
    print("\n=== Elion's Tweet Generation Demo ===\n")
    
    # Generate 10 tweets using scheduler
    for i in range(10):
        try:
            # Get next tweet type from scheduler
            tweet_type = elion.get_next_tweet_type()
            print(f"\n📝 Tweet {i+1}: {tweet_type}")
            print("-----------------------------------")
            
            # Generate base tweet
            base_tweet = elion.generate_tweet(tweet_type)
            if base_tweet:
                # Enhance with personality
                enhanced_tweet = elion.personality.enhance_with_persona(base_tweet)
                print(enhanced_tweet)
                
                elion.analyze_performance({
                    'type': tweet_type,
                    'content': enhanced_tweet,
                    'likes': 0,
                    'retweets': 0,
                    'replies': 0
                })
            else:
                print(f"Failed to generate {tweet_type} tweet")
                
        except Exception as e:
            print(f"Error generating tweet: {e}")
            continue

if __name__ == '__main__':
    demo_tweets()
