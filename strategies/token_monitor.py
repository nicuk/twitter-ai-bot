"""Monitor tokens found by volume and trend strategies without modifying them"""

from typing import Dict, List, Optional
import os
from datetime import datetime
from strategies.token_history_tracker import TokenHistoryTracker
from strategies.volume_strategy import VolumeStrategy
from strategies.trend_strategy import TrendStrategy

class TokenMonitor:
    """Monitors tokens found by strategies without modifying their behavior"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.volume_strategy = VolumeStrategy(api_key)
        self.trend_strategy = TrendStrategy(api_key)
        self.history_tracker = TokenHistoryTracker()
        
    def run_analysis(self) -> Dict:
        """Run both strategies and track tokens they find"""
        # Get tokens from both strategies
        volume_data = self.volume_strategy.analyze()
        trend_data = self.trend_strategy.analyze()
        
        # Track tokens from volume strategy
        if volume_data and 'spikes' in volume_data:
            for score, token in volume_data['spikes']:
                formatted_token = {
                    'symbol': token['symbol'],
                    'price': token['price'],
                    'volume24h': token['volume'],  # Volume strategy uses 'volume'
                    'marketCap': token['mcap'],    # Volume strategy uses 'mcap'
                    'priceChange24h': token.get('price_change', 0)
                }
                self.history_tracker.update_token(formatted_token)
                
        if volume_data and 'anomalies' in volume_data:
            for score, token in volume_data['anomalies']:
                formatted_token = {
                    'symbol': token['symbol'],
                    'price': token['price'],
                    'volume24h': token['volume'],  # Volume strategy uses 'volume'
                    'marketCap': token['mcap'],    # Volume strategy uses 'mcap'
                    'priceChange24h': token.get('price_change', 0)
                }
                self.history_tracker.update_token(formatted_token)
        
        # Track tokens from trend strategy
        if trend_data and 'trend_tokens' in trend_data:
            for token in trend_data['trend_tokens']:
                # Handle trend strategy's reformatted structure
                formatted_token = {
                    'symbol': token['symbol'],
                    'price': token['price'],
                    'volume24h': token['volume'],  # Trend strategy uses 'volume'
                    'marketCap': token['mcap'],    # Trend strategy uses 'mcap'
                    'priceChange24h': token['price_change']  # Trend strategy uses 'price_change'
                }
                self.history_tracker.update_token(formatted_token)
        
        # Return original strategy data unchanged
        return {
            'volume_data': volume_data or {},
            'trend_data': trend_data or {}
        }
    
    def track_token(self, token: Dict) -> None:
        """Track a single token's data"""
        formatted_token = {
            'symbol': token['symbol'],
            'price': token.get('price', 0),
            'volume24h': token.get('volume24h', token.get('volume', 0)),  # Try API format first, fallback to strategy format
            'marketCap': token.get('marketCap', token.get('mcap', 0)),    # Try API format first, fallback to strategy format
            'priceChange24h': token.get('priceChange24h', token.get('price_change', 0))  # Try API format first, fallback to strategy format
        }
        self.history_tracker.update_token(formatted_token)
    
    def get_performance_insights(self, days: int = 30) -> Dict:
        """Get insights about how well our token detection is performing"""
        stats = self.history_tracker.get_performance_stats()
        recent = self.history_tracker.get_recent_opportunities(days)
        patterns = self.history_tracker.find_success_patterns()
        
        return {
            'summary': {
                'total_tokens_tracked': stats['total_tokens'],
                'tokens_with_gains': {
                    '24h': stats['tokens_24h_gain'],
                    '48h': stats['tokens_48h_gain'],
                    '7d': stats['tokens_7d_gain']
                },
                'average_gains': {
                    '24h': f"{stats['avg_24h_gain']:.1f}%",
                    '48h': f"{stats['avg_48h_gain']:.1f}%",
                    '7d': f"{stats['avg_7d_gain']:.1f}%"
                }
            },
            'recent_opportunities': recent[:10],  # Top 10 recent opportunities
            'success_patterns': patterns
        }
        
    def export_data(self, output_file: str = 'token_performance.json'):
        """Export token performance data to a file"""
        import json
        
        data = {
            'export_time': datetime.now().isoformat(),
            'performance_insights': self.get_performance_insights(),
            'token_history': {
                symbol: token.to_dict() 
                for symbol, token in self.history_tracker.get_all_token_history().items()
            }
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data exported to {output_file}")
        except Exception as e:
            print(f"Error exporting data: {e}")
