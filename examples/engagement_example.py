"""Example of engagement-focused strategy"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from strategies.engagement_strategy import EngagementStrategy
from strategies.message_formatter import MessageFormatter

def main():
    # Load API key from environment
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    
    # Initialize strategy and formatter
    strategy = EngagementStrategy(api_key)
    formatter = MessageFormatter()
    
    # Run analysis
    results = strategy.analyze()
    
    print("\n🤖 AI Trading Signal Analysis")
    print("=" * 40)
    
    # Show performance stats
    if results['stats']:
        print("\n📊 Performance Metrics")
        print("-" * 20)
        stats = results['stats']
        print(formatter.format_performance(stats))
    
    # Show new announcements
    if results['announcements']:
        print("\n🎯 New Success Signals")
        print("-" * 20)
        for announcement in results['announcements']:
            tweets = formatter.format_success(announcement)
            print("\nTweet Thread:")
            for i, tweet in enumerate(tweets, 1):
                print(f"{i}. {tweet}")
    
    # Show currently monitoring
    if results['monitoring']:
        print("\n👀 Currently Monitoring")
        print("-" * 20)
        for record in results['monitoring']:
            gain = ((record.current_price - record.initial_price) / record.initial_price) * 100
            print(f"\n{formatter.format_monitoring_update(record.symbol, gain)}")
            print(f"Volume 24h: ${record.volume_24h:,.0f}")
            print(f"Market Cap: ${record.market_cap:,.0f}")
            print(f"Engagement Score: {record.engagement_score:.1f}/100")
    
    # Show new candidates
    if results['candidates']:
        print("\n💡 New Potential Targets")
        print("-" * 20)
        for token in results['candidates']:
            print(f"\n{formatter.format_detection(token['symbol'])}")
            print(f"Price: ${float(token['price']):.4f}")
            print(f"Trend Score: {token['trend_score']:.1f}/100")
            print(f"Volume Score: {token['volume_score']:.1f}/100")
            print(f"Engagement Potential: {token['engagement_score']:.1f}/100")

if __name__ == "__main__":
    main()
