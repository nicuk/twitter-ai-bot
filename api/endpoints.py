"""FastAPI endpoints for the Twitter bot"""

from typing import Optional, List, Dict
from datetime import datetime
from fastapi import FastAPI, Query
from strategies.token_history_tracker import TokenHistoryTracker
from strategies.token_monitor import TokenMonitor
import os

app = FastAPI(title="ELAI Bot API")

def setup_routes(app: FastAPI):
    """Setup API routes"""
    
    # Initialize token monitor with API key
    monitor = TokenMonitor(api_key=os.getenv('CRYPTORANK_API_KEY'))
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "status": "ok",
            "message": "ELAI Bot API is running",
            "endpoints": [
                "/token-history",
                "/token-history/{symbol}",
                "/analysis/current",
                "/analysis/performance"
            ]
        }
        
    @app.get("/token-history")
    async def get_token_history(
        days: Optional[int] = Query(None, description="Filter tokens by days since first mention"),
        min_gain: Optional[float] = Query(None, description="Filter tokens by minimum gain percentage"),
        max_tokens: Optional[int] = Query(100, description="Maximum number of tokens to return")
    ) -> Dict:
        """Get token history with optional filters"""
        tracker = TokenHistoryTracker()
        history = tracker.get_all_token_history()
        
        # Apply filters
        filtered_tokens = []
        for token in history:
            if days and (datetime.now() - token.first_mention_date).days > days:
                continue
                
            gain = ((token.current_price - token.first_mention_price) / token.first_mention_price) * 100
            if min_gain and gain < min_gain:
                continue
                
            filtered_tokens.append(token.to_dict())
            
            if len(filtered_tokens) >= max_tokens:
                break
                
        return {
            "total": len(filtered_tokens),
            "tokens": filtered_tokens
        }
        
    @app.get("/token-history/{symbol}")
    async def get_token_details(symbol: str) -> Dict:
        """Get detailed history for a specific token"""
        tracker = TokenHistoryTracker()
        token = tracker.get_token_history(symbol.upper())
        
        if not token:
            return {
                "error": "Token not found",
                "symbol": symbol
            }
            
        return token.to_dict()
        
    @app.get("/analysis/current")
    async def get_current_analysis() -> Dict:
        """Get real-time analysis from volume and trend strategies"""
        try:
            # Get real-time analysis
            analysis = monitor.run_analysis()
            volume_data = analysis.get('volume_data', {})
            trend_data = analysis.get('trend_data', {})
            volume_tokens = []
            
            if 'spikes' in volume_data:
                for score, token in volume_data['spikes']:
                    volume_tokens.append({
                        'symbol': token['symbol'],
                        'price': token['price'],
                        'volume_24h': token['volume'],
                        'market_cap': token['mcap'],
                        'volume_mcap_ratio': token['volume'] / token['mcap'] if token['mcap'] > 0 else 0,
                        'type': 'spike'
                    })
                    
            if 'anomalies' in volume_data:
                for score, token in volume_data['anomalies']:
                    volume_tokens.append({
                        'symbol': token['symbol'],
                        'price': token['price'],
                        'volume_24h': token['volume'],
                        'market_cap': token['mcap'],
                        'volume_mcap_ratio': token['volume'] / token['mcap'] if token['mcap'] > 0 else 0,
                        'type': 'anomaly'
                    })
            
            # Format trend data
            trend_tokens = []
            if 'trend_tokens' in trend_data:
                for token in trend_data['trend_tokens']:
                    trend_tokens.append({
                        'symbol': token['symbol'],
                        'price': token['price'],
                        'volume_24h': token['volume'],
                        'market_cap': token['mcap'],
                        'trend_score': token.get('trend_score', 0),
                        'momentum_score': token.get('momentum_score', 0)
                    })
                    
            return {
                'volume_analysis': {
                    'total_tokens': len(volume_tokens),
                    'tokens': volume_tokens
                },
                'trend_analysis': {
                    'total_tokens': len(trend_tokens),
                    'tokens': trend_tokens
                }
            }
        except Exception as e:
            import traceback
            print(f"Error in get_current_analysis: {str(e)}")
            print(traceback.format_exc())
            return {
                'volume_analysis': {'total_tokens': 0, 'tokens': []},
                'trend_analysis': {'total_tokens': 0, 'tokens': []},
                'error': str(e)
            }
        
    @app.get("/analysis/performance")
    async def get_performance_insights(
        days: Optional[int] = Query(30, description="Number of days to analyze")
    ) -> Dict:
        """Get performance insights about our token detection"""
        return monitor.get_performance_insights(days)

setup_routes(app)
