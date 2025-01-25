"""Test Elion's hybrid messaging approach"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from elion.content.generator import ContentGenerator
from elion.personality import PersonalityManager
from strategies.message_formatter import MessageFormatter

def test_hybrid_responses():
    """Test different types of Elion responses"""
    
    # Initialize components
    personality = PersonalityManager()
    personality.current_trait = "analytical"  # Set initial trait
    elion = ContentGenerator(personality)
    
    print("🤖 Testing Elion's Enhanced Hybrid Messaging System\n")
    
    # Test 1: Technical Signal with Risk Management
    print("Test 1: Technical Signal Detection")
    technical_data = {
        'type': 'technical',
        'symbol': 'BTC',
        'entry': 42150,
        'target': 45300,
        'stop': 41200,
        'risk_reward': 3.2,
        'volume_score': 85,
        'trend_score': 92,
        'market_leader': 'ETH',
        'market_action': 'shows strength',
        'market_condition': 'bullish market structure'
    }
    response = elion.generate_market_insight(technical_data)
    print("Technical Setup + Market Context:")
    for tweet in response:
        print(f"{tweet}\n")
    
    # Test 2: Success Announcement with Details
    print("\nTest 2: Detailed Success Thread")
    trade_data = {
        'symbol': 'ETH',
        'gain': 12.5,
        'time_to_gain': '2.5 hours',
        'entry': 2450,
        'peak': 2756,
        'volume_score': 88,
        'volume_change': 312,
        'trend_score': 90,
        'oi_change': 45,
        'key_level': 2700,
        'ma_cross': '20/50 EMA',
        'rsi': 65,
        'market_context': 'Layer 1s showing momentum',
        'sector_trend': 'Very Bullish',
        'btc_dom': 48,
        'market_mood': 'Risk-on'
    }
    success_thread = elion.generate_success_announcement(trade_data)
    print("Success Announcement Thread:")
    for tweet in success_thread:
        print(f"{tweet}\n")
    
    # Test 3: Performance Stats with Education
    print("\nTest 3: Enhanced Performance Stats")
    stats = {
        'success_rate': 82,
        'total': 50,
        'avg_gain': 8.5,
        'best_gain': 25.3,
        'avg_time': '3.2 hours'
    }
    performance = elion.generate_performance_update(stats)
    print(f"Performance Update:\n{performance}\n")
    
    # Test 4: Personal Market Commentary
    print("\nTest 4: Market Commentary with Context")
    market_data = {
        'type': 'market',
        'insight': 'Bitcoin dominance dropping as L1s and AI tokens show exceptional strength. Market structure remains bullish with increasing volume across major altcoins.',
        'sentiment': 'bullish'
    }
    commentary = elion.generate_market_insight(market_data)
    print(f"Market Commentary:\n{commentary}\n")
    
    # Test 5: Monitoring Update
    print("\nTest 5: Active Monitoring Update")
    monitoring_data = {
        'symbol': 'MATIC',
        'current_price': 0.95,
        'current_gain': 8.3,
        'time_elapsed': '1.5 hours',
    }
    monitoring = elion.message_formatter.format_monitoring_update(monitoring_data)
    print(f"Monitoring Update:\n{monitoring}\n")

if __name__ == "__main__":
    test_hybrid_responses()
