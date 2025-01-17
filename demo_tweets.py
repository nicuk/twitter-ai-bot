from elion.elion import Elion
from datetime import datetime
import sys

def demo_tweets():
    # Fix console encoding for emojis
    sys.stdout.reconfigure(encoding='utf-8')
    
    elion = Elion()
    
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
        'analysis': 'Revolutionary L2 with unique quantum-resistant cryptography. Strong team, active development, and growing community.',
        'conviction_level': 'EXTREMELY HIGH',
        'metrics': {
            'github_commits_week': 65,
            'liquidity_ratio': 0.35,
            'holder_distribution': 0.82,
            'team_tokens_locked': 0.95
        }
    }
    print(elion.format_shill_review([project]))

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

    # 3. Gem Alpha Tweet
    print("\n=== Gem Alpha Tweet ===")
    gem = {
        'name': 'Neural Finance',
        'symbol': 'NRAL',
        'market_cap': 15000000,
        'analysis': 'AI-powered DeFi protocol with unique yield optimization. Early stage with massive growth potential.',
        'conviction': 'EXTREMELY HIGH',
        'entry_price': 0.25,
        'target_price': 2.0,
        'metrics': {
            'technical_score': 88,
            'fundamental_score': 85,
            'viral_potential': 'high'
        }
    }
    print(elion.format_gem_alpha([gem]))

    # 4. Portfolio Update Tweet
    print("\n=== Portfolio Update Tweet ===")
    elion.portfolio.open_position('NRAL', 15000, 0.25, 88, 'EXTREMELY HIGH')
    elion.portfolio.open_position('QNTM', 10000, 0.85, 92, 'EXTREMELY HIGH')
    # Simulate some price changes
    elion.portfolio.positions['NRAL']['current_price'] = 0.45  # +80%
    elion.portfolio.positions['QNTM']['current_price'] = 1.15  # +35%
    print(elion.get_portfolio_update())

    # Record tweets in history
    for i, tweet in enumerate([
        {'content': 'Shill Review', 'type': 'review', 'id': f'tweet_{i+1}'},
        {'content': 'Market Analysis', 'type': 'analysis', 'id': f'tweet_{i+2}'},
        {'content': 'Gem Alpha', 'type': 'alpha', 'id': f'tweet_{i+3}'},
        {'content': 'Portfolio Update', 'type': 'portfolio', 'id': f'tweet_{i+4}'}
    ]):
        elion.engagement.record_tweet(tweet)
    
    print(f"\nRecorded {len(elion.engagement.tweet_history)} tweets in history")

if __name__ == '__main__':
    demo_tweets()
