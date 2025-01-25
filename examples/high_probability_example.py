"""Example usage of high probability strategy"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from strategies.high_probability_strategy import HighProbabilityStrategy

def main():
    # Load API key from environment
    load_dotenv()
    api_key = os.getenv('CRYPTORANK_API_KEY')
    
    # Initialize strategy
    strategy = HighProbabilityStrategy(api_key)
    
    # Run analysis
    results = strategy.analyze()
    
    print("\nHigh Probability Token Analysis")
    print("-" * 40)
    
    print("\nCurrently Monitoring:")
    for token in results['monitoring_tokens']:
        print(f"\n{token.symbol}:")
        print(f"  Current Price: ${token.current_price:.4f}")
        print(f"  Volume 24h: ${token.volume_24h:,.0f}")
        print(f"  Market Cap: ${token.market_cap:,.0f}")
        
    print("\nSuccessful Trades:")
    for trade in results['successful_trades']:
        print(f"\n{trade['symbol']}:")
        print(f"  Highest Price: ${trade['highest_price']:.4f}")
        print(f"  Gain: {trade['gain_percentage']:.1f}%")
        print(f"  Volume 24h: ${trade['volume_24h']:,.0f}")
        
    print("\nNew High-Probability Candidates:")
    for token in results['new_candidates']:
        print(f"\n{token['symbol']}:")
        print(f"  Price: ${float(token['price']):.4f}")
        print(f"  Trend Score: {token['trend_score']:.1f}")
        print(f"  Volume Score: {token['volume_score']:.1f}")
        print(f"  Combined Score: {token['combined_score']:.1f}")

if __name__ == "__main__":
    main()
