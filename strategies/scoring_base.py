"""Base scoring utilities for all strategies"""
import datetime
from typing import Dict, Tuple

class BaseScoring:
    @staticmethod
    def get_confidence_label(score: float) -> Tuple[str, str]:
        """Get confidence label and emoji based on score"""
        if score >= 75:
            return "High Confidence Signal", "💪"
        elif score >= 60:
            return "Moderate Confidence Signal", "🔍"
        else:
            return "Watching Closely", "👀"
    
    @staticmethod
    def get_market_hours_score(max_points: int = 10) -> float:
        """Calculate score bonus for market hours (UTC)"""
        current_hour = datetime.datetime.now().hour
        return max_points if 13 <= current_hour <= 21 else max_points/2
        
    @staticmethod
    def get_stability_score(token: Dict, max_points: int = 20) -> float:
        """Calculate basic stability score based on market cap"""
        mcap_billions = token['marketCap'] / 1e9
        if mcap_billions < 0.1:  # Less than 100M
            return max_points * 0.25
        elif mcap_billions < 0.5:  # 100M-500M
            return max_points * 0.5
        elif mcap_billions < 1:  # 500M-1B
            return max_points * 0.75
        else:  # >1B
            return max_points
            
    @staticmethod
    def apply_volatility_penalty(score: float, price_change: float, threshold: float = 40) -> float:
        """Apply penalty for extreme volatility"""
        return score * 0.7 if abs(price_change) > threshold else score
        
    @staticmethod
    def format_score(score: float) -> str:
        """Format score for display"""
        return f"Signal Strength: {score:.1f}/100"
