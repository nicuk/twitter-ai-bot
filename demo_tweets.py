from elion.elion import Elion
from datetime import datetime
import sys
import os
import requests
from dotenv import load_dotenv

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
        pass
        
    def get_market_data(self, *args):
        return {
            'market_cap': 1000000,
            'volume': 500000,
            'price': 1.0,
            'price_change': 5.5
        }

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
        pass
        
    def generate(self, *args, **kwargs):
        return "Generated tweet content"
        
    def enhance_with_persona(self, content, persona=None):
        return f"{content} 🚀 #ElionAlpha"

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
    elion.portfolio = MockPortfolio()
    elion.data_sources = MockDataSources()
    elion.personality = MockPersonality()
    elion.engagement = MockEngagement()

    # Generate and record tweets
    tweets = []
    for i in range(4):
        if i == 0:
            # 1. Shill Review Tweet
            print("\n=== Shill Review Tweet ===")
            project = {
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
            }
            print(elion.format_shill_review([project]))
            tweets.append({'content': 'Shill Review', 'type': 'review', 'id': f'tweet_{i+1}'})
            
        elif i == 1:
            # 2. Market Analysis Tweet
            print("\n=== Market Analysis Tweet ===")
            market_data = {
                'sentiment': 'bullish',
                'btc_dominance': 41.5,
                'market_cap': 2750000000000,
                'volume_24h': 155000000000,
                'trends': ['DeFi 2.0 Season', 'L2 Narrative Strong', 'AI Tokens Pumping'],
                'key_events': ['Major Protocol Upgrade', 'Institutional Adoption News'],
                'btc_price': 68500,
                'btc_change_24h': 8.5,
                'eth_price': 4500,
                'eth_change_24h': 12.2
            }
            print(elion.format_market_response(market_data))
            tweets.append({'content': 'Market Analysis', 'type': 'analysis', 'id': f'tweet_{i+1}'})
            
        elif i == 2:
            # 3. Gem Alpha Tweet
            print("\n=== Gem Alpha Tweet ===")
            gem = {
                'name': 'Neural Finance',
                'symbol': 'NRAL',
                'market_cap': 15000000,
                'entry_price': 0.25,
                'target_price': 2.0,
                'metrics': {
                    'technical_score': 88,
                    'fundamental_score': 85,
                    'viral_potential': 'HIGH'
                },
                'analysis': 'AI-powered DeFi protocol with unique yield optimization. Early stage with massive growth potential.'
            }
            print(elion.format_gem_alpha([gem]))
            tweets.append({'content': 'Gem Alpha', 'type': 'alpha', 'id': f'tweet_{i+1}'})
            
        else:
            # 4. Portfolio Update Tweet
            print("\n=== Portfolio Update Tweet ===")
            # Add some positions for the portfolio update
            elion.portfolio.open_position('NRAL', 15000, 0.25, 88, 'EXTREMELY HIGH')
            elion.portfolio.open_position('QNTM', 10000, 0.85, 92, 'EXTREMELY HIGH')
            # Simulate some price changes
            elion.portfolio.positions['NRAL']['current_price'] = 0.45  # +80%
            elion.portfolio.positions['QNTM']['current_price'] = 1.15  # +35%
            print(elion.get_portfolio_update())
            tweets.append({'content': 'Portfolio Update', 'type': 'portfolio', 'id': f'tweet_{i+1}'})
            
        # Record engagement
        elion.engagement.record_tweet(tweets[-1])

    print(f"\nRecorded {len(elion.engagement.tweet_history)} tweets in history")

if __name__ == '__main__':
    demo_tweets()
