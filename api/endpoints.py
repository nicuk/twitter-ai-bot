"""FastAPI endpoints for the Twitter bot"""

from typing import Optional, List, Dict
from datetime import datetime
from fastapi import FastAPI, Query
from strategies.token_history_tracker import TokenHistoryTracker
from strategies.token_monitor import TokenMonitor
import os
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="ELAI Bot API")

def setup_routes(app: FastAPI):
    """Setup API routes"""
    
    # Initialize token monitor with API key
    monitor = TokenMonitor(api_key=os.getenv('CRYPTORANK_API_KEY'))
    
    @app.post("/test/tweet")
    async def test_tweet(text: str = Query(..., description="Tweet text to post")):
        """Test endpoint to post a tweet directly"""
        try:
            from twitter.api_client import TwitterAPI
            from twitter.bot import check_single_instance, cleanup_redis_lock
            
            # Check if another instance is running
            if not check_single_instance():
                return {
                    "status": "error",
                    "message": "Another bot instance is running"
                }
            
            # Initialize Twitter API
            api = TwitterAPI()
            
            # Try to post tweet
            logger.info(f"Test endpoint attempting to post tweet: {text}")
            response = api.create_tweet(text)
            
            # Clean up lock
            cleanup_redis_lock()
            
            if response:
                tweet_id = response.get('id')
                logger.info(f"Tweet posted successfully! ID: {tweet_id}")
                return {
                    "status": "success",
                    "tweet_id": tweet_id,
                    "message": "Tweet posted successfully"
                }
            else:
                logger.error("Failed to post tweet - no response")
                return {
                    "status": "error",
                    "message": "Failed to post tweet - no response"
                }
                
        except Exception as e:
            logger.error(f"Error posting test tweet: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
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
                "/analysis/performance",
                "/test/tweet"
            ]
        }
        
    @app.get("/token-history")
    async def get_token_history(
        days: Optional[int] = Query(None, description="Filter tokens by days since first mention"),
        min_gain: Optional[float] = Query(None, description="Filter tokens by minimum gain percentage"),
        max_tokens: Optional[int] = Query(100, description="Maximum number of tokens to return")
    ) -> Dict:
        """Get token history with optional filters"""
        try:
            tracker = TokenHistoryTracker()
            history = tracker.get_all_token_history()
            
            logger.info(f"Retrieved {len(history)} tokens from history")
            logger.info(f"Filters: days={days}, min_gain={min_gain}, max_tokens={max_tokens}")
            
            # Apply filters
            filtered_tokens = []
            for token_data in history.values():
                try:
                    if days and (datetime.now() - token_data.first_mention_date).days > days:
                        continue
                        
                    gain = ((token_data.current_price - token_data.first_mention_price) / token_data.first_mention_price) * 100 if token_data.first_mention_price > 0 else 0
                    if min_gain and gain < min_gain:
                        continue
                        
                    filtered_tokens.append({
                        'symbol': token_data.symbol,
                        'first_mention_date': token_data.first_mention_date.isoformat(),
                        'first_mention_price': token_data.first_mention_price,
                        'first_mention_mcap': token_data.first_mention_mcap,
                        'current_price': token_data.current_price,
                        'current_mcap': token_data.current_mcap,
                        'gain_percentage': gain,
                        'volume_24h': token_data.current_volume,
                        'max_gain_7d': token_data.max_gain_percentage_7d
                    })
                except Exception as e:
                    logger.error(f"Error processing token {token_data.symbol}: {e}")
                    continue
            
            # Sort by gain percentage and limit results
            filtered_tokens.sort(key=lambda x: x['gain_percentage'], reverse=True)
            filtered_tokens = filtered_tokens[:max_tokens]
            
            logger.info(f"Returning {len(filtered_tokens)} filtered tokens")
            return {
                'total': len(filtered_tokens),
                'tokens': filtered_tokens,
                'success': True,
                'message': f"Found {len(filtered_tokens)} tokens"
            }
            
        except Exception as e:
            logger.error(f"Error in get_token_history: {e}")
            logger.exception("Full traceback:")
            return {
                'total': 0,
                'tokens': [],
                'success': False,
                'message': str(e)
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
