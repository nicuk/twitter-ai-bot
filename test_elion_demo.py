"""
Demo script to test Elion's main functionalities
"""
import sys
from elion.elion import Elion
from elion.data_sources import DataSources
from elion.portfolio import Portfolio

# Set console encoding to UTF-8
sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("Testing Elion's Main Functionalities\n")
    
    # Initialize Elion
    elion = Elion()
    
    # 1. Test Shill Reviews
    print("1. Testing Shill Reviews")
    
    # Test high conviction shill
    high_conviction = {
        'name': 'Quality Protocol',
        'symbol': 'QUAL',
        'score': 85,
        'market_data': {
            'market_cap': 125000000,
            'volume': 15000000,
            'price': 1.25,
            'price_change': 15.5
        },
        'analysis': 'Strong fundamentals, active development, growing community',
        'conviction_level': 'EXTREMELY HIGH',
        'metrics': {
            'github_commits_week': 45,
            'liquidity_ratio': 0.25,
            'holder_distribution': 0.75,
            'team_tokens_locked': 0.9
        }
    }
    
    # Test medium conviction shill
    medium_conviction = {
        'name': 'Decent Token',
        'symbol': 'DCNT',
        'score': 72,
        'market_data': {
            'market_cap': 75000000,
            'volume': 5000000,
            'price': 0.75,
            'price_change': 5.5
        },
        'analysis': 'Decent tech but needs more development activity',
        'conviction_level': 'MODERATE',
        'metrics': {
            'github_commits_week': 15,
            'liquidity_ratio': 0.18,
            'holder_distribution': 0.65,
            'team_tokens_locked': 0.85
        }
    }
    
    # Test low quality shill
    low_quality = {
        'name': 'Sketchy Token',
        'symbol': 'SKTCH',
        'score': 45,
        'market_data': {
            'market_cap': 1000000,
            'volume': 50000,
            'price': 0.001,
            'price_change': -12.5
        },
        'analysis': 'Multiple red flags in tokenomics and development',
        'conviction_level': 'LOW',
        'metrics': {
            'github_commits_week': 2,
            'liquidity_ratio': 0.05,
            'holder_distribution': 0.35,
            'team_tokens_locked': 0.2
        }
    }
    
    try:
        print("\nHigh Conviction Shill Review:")
        print(elion.format_shill_review([high_conviction]))
        print("\nMedium Conviction Shill Review:")
        print(elion.format_shill_review([medium_conviction]))
        print("\nLow Quality Shill Review:")
        print(elion.format_shill_review([low_quality]))
    except Exception as e:
        print(f"Error in shill review: {str(e)}")
    print("\n" + "-"*50 + "\n")
    
    # 2. Test Portfolio Update with Multiple Positions
    print("2. Testing Portfolio Update")
    try:
        # Open some test positions
        elion.portfolio.open_position('QUAL', 15000, 1.25, 85, 'EXTREMELY HIGH')
        elion.portfolio.open_position('DCNT', 7500, 0.75, 72, 'MODERATE')
        
        # Simulate some price movement
        elion.portfolio.positions['QUAL']['current_price'] = 1.75  # +40%
        elion.portfolio.positions['DCNT']['current_price'] = 0.85  # +13%
        
        portfolio_update = elion.get_portfolio_update()
        print("\nPortfolio Update:")
        print(portfolio_update)
    except Exception as e:
        print(f"Error in portfolio update: {str(e)}")
    print("\n" + "-"*50 + "\n")
    
    # 3. Test Market Responses
    print("3. Testing Market Responses")
    
    # Test bullish market
    bullish_market = {
        'sentiment': 'bullish',
        'btc_dominance': 42.5,
        'market_cap': 2500000000000,
        'volume_24h': 125000000000,
        'trends': ['Layer 2s pumping', 'AI tokens mooning'],
        'key_events': ['ETF approval', 'Major protocol upgrade'],
        'btc_price': 65000,
        'btc_change_24h': 12.5,
        'eth_price': 4200,
        'eth_change_24h': 15.2
    }
    
    # Test bearish market
    bearish_market = {
        'sentiment': 'bearish',
        'btc_dominance': 48.5,
        'market_cap': 1800000000000,
        'volume_24h': 75000000000,
        'trends': ['DeFi tokens bleeding', 'Risk-off sentiment'],
        'key_events': ['Regulatory FUD', 'Protocol exploit'],
        'btc_price': 38000,
        'btc_change_24h': -8.5,
        'eth_price': 2200,
        'eth_change_24h': -12.2
    }
    
    try:
        print("\nBullish Market Response:")
        print(elion.format_market_response(bullish_market))
        print("\nBearish Market Response:")
        print(elion.format_market_response(bearish_market))
    except Exception as e:
        print(f"Error in market response: {str(e)}")
    print("\n" + "-"*50 + "\n")
    
    # 4. Test Gem Alpha with Different Scenarios
    print("4. Testing Gem Alpha")
    
    # Test promising gem
    promising_gem = {
        'name': 'Hidden Gem Protocol',
        'symbol': 'GEM',
        'market_cap': 25000000,
        'analysis': 'Revolutionary L2 with unique ZK implementation',
        'conviction': 'EXTREMELY HIGH',
        'entry_price': 0.5,
        'target_price': 2.5,
        'metrics': {
            'technical_score': 85,
            'fundamental_score': 82,
            'viral_potential': 'high'
        }
    }
    
    # Test speculative gem
    speculative_gem = {
        'name': 'Moonshot Token',
        'symbol': 'MOON',
        'market_cap': 5000000,
        'analysis': 'High-risk high-reward gaming token',
        'conviction': 'MODERATE',
        'entry_price': 0.1,
        'target_price': 0.8,
        'metrics': {
            'technical_score': 68,
            'fundamental_score': 65,
            'viral_potential': 'medium'
        }
    }
    
    try:
        print("\nPromising Gem Alpha:")
        print(elion.format_gem_alpha([promising_gem]))
        print("\nSpeculative Gem Alpha:")
        print(elion.format_gem_alpha([speculative_gem]))
    except Exception as e:
        print(f"Error in gem alpha: {str(e)}")
    
    # 5. Test Personality Enhancement
    print("\n5. Testing Personality Enhancement")
    base_content = "Bitcoin is showing strong accumulation patterns!"
    
    try:
        print("\nAlpha Hunter Persona:")
        print(elion.personality.enhance_with_persona(base_content, 'alpha_hunter'))
        print("\nTech Analyst Persona:")
        print(elion.personality.enhance_with_persona(base_content, 'tech_analyst'))
        print("\nCommunity Builder Persona:")
        print(elion.personality.enhance_with_persona(base_content, 'community_builder'))
    except Exception as e:
        print(f"Error in personality enhancement: {str(e)}")

    # 6. Test Reply Generation
    print("\n6. Testing Reply Generation")
    
    # Simulate a viral tweet that Elion might want to engage with
    viral_tweet = {
        'id': '12345',
        'author': 'CryptoWhale',
        'content': 'Just spotted a massive whale movement! 10,000 $BTC moved from cold storage to exchanges... ',
        'metrics': {
            'likes': 5000,
            'retweets': 1200,
            'replies': 800
        },
        'timestamp': '2025-01-17T00:16:59Z'
    }
    
    # Simulate replies to Elion's tweet
    replies_to_elion = [
        {
            'id': '54321',
            'author': 'TraderJoe',
            'content': '@ElionAI what do you think about $QUAL? Worth buying at these levels?',
            'context': {
                'mentioned_symbols': ['QUAL'],
                'sentiment': 'curious',
                'user_history': {
                    'interaction_count': 5,
                    'sentiment': 'positive'
                }
            }
        },
        {
            'id': '54322',
            'author': 'CryptoSkeptic',
            'content': '@ElionAI your analysis on $DCNT was wrong. It\'s down 5% since your call!',
            'context': {
                'mentioned_symbols': ['DCNT'],
                'sentiment': 'negative',
                'user_history': {
                    'interaction_count': 1,
                    'sentiment': 'negative'
                }
            }
        },
        {
            'id': '54323',
            'author': 'NewbieCrypto',
            'content': '@ElionAI hey! I\'m new to crypto. Could you explain what market cap means?',
            'context': {
                'mentioned_symbols': [],
                'sentiment': 'curious',
                'user_history': {
                    'interaction_count': 0,
                    'sentiment': 'neutral'
                }
            }
        }
    ]
    
    try:
        # Test viral tweet engagement
        print("\nEngaging with Viral Tweet:")
        engagement = elion.personality.enhance_with_persona(
            f"Analyzing this whale movement:\n\n"
            f"- 10k BTC is significant\n"
            f"- Could signal institutional accumulation\n"
            f"- Watch for price action in next 24-48h\n\n"
            f"Keep your eyes on the charts! ",
            'tech_analyst'
        )
        print(engagement)
        
        # Test replies to different types of users
        print("\nReplying to User Questions/Comments:")
        
        # Friendly regular who asks about a token
        trader_reply = elion.personality.enhance_with_persona(
            f"Hey @TraderJoe! Thanks for asking about $QUAL \n\n"
            f"Current analysis:\n"
            f"- Strong support at $1.20\n"
            f"- Development activity increasing\n"
            f"- Community growth steady\n\n"
            f"I maintain my bullish stance! NFA",
            'alpha_hunter'
        )
        print("\nTo @TraderJoe:")
        print(trader_reply)
        
        # Handle criticism professionally
        skeptic_reply = elion.personality.enhance_with_persona(
            f"@CryptoSkeptic Appreciate the feedback!\n\n"
            f"My calls are based on:\n"
            f"- Technical analysis\n"
            f"- On-chain metrics\n"
            f"- Development activity\n\n"
            f"Short-term price action varies, but I focus on long-term value. DYOR!",
            'community_builder'
        )
        print("\nTo @CryptoSkeptic:")
        print(skeptic_reply)
        
        # Help newcomers with educational content
        newbie_reply = elion.personality.enhance_with_persona(
            f"Welcome to crypto @NewbieCrypto! \n\n"
            f"Market cap = Price × Circulating Supply\n\n"
            f"It helps compare different cryptocurrencies:\n"
            f"- Higher cap = typically more stable\n"
            f"- Lower cap = potentially more volatile\n\n"
            f"Happy to help you learn! ",
            'community_builder'
        )
        print("\nTo @NewbieCrypto:")
        print(newbie_reply)
        
    except Exception as e:
        print(f"Error in reply generation: {str(e)}")

if __name__ == "__main__":
    main()
