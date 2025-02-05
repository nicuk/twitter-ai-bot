"""Track and manage token price predictions using Redis"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis

class PredictionTracker:
    """Track and analyze token price predictions using Redis"""
    
    def __init__(self):
        """Initialize prediction tracker with Redis"""
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            raise ValueError("REDIS_URL environment variable not set")
        self.redis = redis.from_url(redis_url)
        self._init_stats()
    
    def _init_stats(self):
        """Initialize stats if they don't exist"""
        if not self.redis.exists('prediction_stats'):
            stats = {
                'total_predictions': 0,
                'successful_predictions': 0,
                'accuracy_24h': 0,
                'accuracy_7d': 0,
                'last_updated': datetime.now().isoformat()
            }
            self.redis.set('prediction_stats', json.dumps(stats))
    
    def add_prediction(self, symbol: str, predicted_gain: float) -> None:
        """Add a new prediction"""
        prediction = {
            'symbol': symbol,
            'predicted_gain': predicted_gain,
            'predicted_at': datetime.now().isoformat(),
            'actual_gain_24h': None,
            'actual_gain_7d': None,
            'success_24h': None,
            'success_7d': None,
            'validated': False
        }
        
        # Add to predictions list
        predictions = self._get_predictions()
        predictions.append(prediction)
        self.redis.set('predictions', json.dumps(predictions))
        
        # Update stats
        stats = json.loads(self.redis.get('prediction_stats'))
        stats['total_predictions'] += 1
        stats['last_updated'] = datetime.now().isoformat()
        self.redis.set('prediction_stats', json.dumps(stats))
    
    def _get_predictions(self) -> List[Dict]:
        """Get all predictions from Redis"""
        predictions = self.redis.get('predictions')
        return json.loads(predictions) if predictions else []
    
    def update_prediction_results(self, symbol: str, actual_gain: float) -> None:
        """Update prediction results after 24h/7d"""
        predictions = self._get_predictions()
        updated = False
        
        for pred in predictions:
            if pred['symbol'] == symbol and not pred['validated']:
                pred_time = datetime.fromisoformat(pred['predicted_at'])
                time_diff = datetime.now() - pred_time
                
                # Update 24h results
                if time_diff >= timedelta(hours=24) and pred['actual_gain_24h'] is None:
                    pred['actual_gain_24h'] = actual_gain
                    pred['success_24h'] = actual_gain > 0 and actual_gain >= pred['predicted_gain'] * 0.7
                    updated = True
                
                # Update 7d results
                if time_diff >= timedelta(days=7) and pred['actual_gain_7d'] is None:
                    pred['actual_gain_7d'] = actual_gain
                    pred['success_7d'] = actual_gain > 0 and actual_gain >= pred['predicted_gain'] * 0.7
                    pred['validated'] = True
                    updated = True
        
        if updated:
            self.redis.set('predictions', json.dumps(predictions))
            self._update_stats()
    
    def _update_stats(self):
        """Update overall prediction statistics"""
        predictions = self._get_predictions()
        predictions_24h = [p for p in predictions if p['success_24h'] is not None]
        predictions_7d = [p for p in predictions if p['success_7d'] is not None]
        
        stats = json.loads(self.redis.get('prediction_stats'))
        
        if predictions_24h:
            successful_24h = len([p for p in predictions_24h if p['success_24h']])
            stats['accuracy_24h'] = round(successful_24h / len(predictions_24h) * 100)
        
        if predictions_7d:
            successful_7d = len([p for p in predictions_7d if p['success_7d']])
            stats['accuracy_7d'] = round(successful_7d / len(predictions_7d) * 100)
        
        stats['successful_predictions'] = len([
            p for p in predictions 
            if p['success_24h'] or p['success_7d']
        ])
        
        stats['last_updated'] = datetime.now().isoformat()
        self.redis.set('prediction_stats', json.dumps(stats))
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """Get recent successful predictions"""
        predictions = self._get_predictions()
        successful = [
            p for p in predictions
            if p['success_24h'] or p['success_7d']
        ]
        return sorted(successful, key=lambda x: x['predicted_at'], reverse=True)[:limit]
    
    def get_stats(self) -> Dict:
        """Get current prediction statistics"""
        stats = self.redis.get('prediction_stats')
        return json.loads(stats) if stats else {}
