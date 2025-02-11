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
            from twitter.bot import AIGamingBot, check_single_instance, cleanup_redis_lock
            
            # Check if another instance is running
            if not check_single_instance():
                return {
                    "status": "error",
                    "message": "Another bot instance is running"
                }
            
            # Initialize bot with rate limiter
            bot = AIGamingBot()
            
            # Try to post tweet
            logger.info(f"Test endpoint attempting to post tweet: {text}")
            result = bot._post_tweet(text)
            
            # Clean up lock
            cleanup_redis_lock()
            
            if result:
                logger.info(f"Tweet posted successfully!")
                return {
                    "status": "success",
                    "message": "Tweet posted successfully"
                }
            else:
                logger.error("Failed to post tweet")
                return {
                    "status": "error",
                    "message": "Failed to post tweet"
                }
                
        except Exception as e:
            logger.error(f"Error posting test tweet: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    @app.post("/tweet")
    async def post_tweet(text: str):
        """Post a tweet directly with the given text"""
        try:
            from twitter.bot import AIGamingBot
            
            # Initialize bot with rate limiter
            bot = AIGamingBot()
            
            # Post tweet using bot's rate-limited posting mechanism
            result = bot._post_tweet(text)
            
            if result:
                return {
                    'success': True,
                    'message': 'Tweet posted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to post tweet'
                }
                
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {
                'success': False,
                'message': str(e)
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
                "/test/tweet",
                "/post/{post_type}",
                "/tweet"
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

    @app.post("/post/{post_type}")
    async def trigger_post(post_type: str):
        """Trigger a specific type of post
        Valid types: trend, volume, format, performance"""
        try:
            from twitter.bot import AIGamingBot
            bot = AIGamingBot()
            
            post_functions = {
                'trend': bot.post_trend,
                'volume': bot.post_volume,
                'format': bot.post_format_tweet,
                'performance': bot.post_performance
            }
            
            if post_type not in post_functions:
                return {
                    'success': False,
                    'message': f'Invalid post type. Must be one of: {", ".join(post_functions.keys())}'
                }
                
            # Call the post function
            result = post_functions[post_type]()
            
            return {
                'success': True,
                'message': f'Successfully triggered {post_type} post',
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Error triggering {post_type} post: {e}")
            return {
                'success': False,
                'message': str(e)
            }

setup_routes(app)
