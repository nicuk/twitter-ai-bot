"""
Core engagement functionality
Coordinates between metrics, viral patterns, and LLM components
"""

from typing import Dict, Optional
from datetime import datetime

class EngagementCore:
    """Core engagement functionality"""
    
    def __init__(self, llm=None):
        """Initialize engagement core with optional LLM"""
        self.llm = llm
        
        # Initialize components
        self.metrics = None  # Will be EngagementMetrics
        self.patterns = None  # Will be ViralPatterns
        self.segments = None  # Will be CommunitySegments
        self.templates = None  # Will be EngagementTemplates
        
    def setup_components(self, metrics, patterns, segments, templates):
        """Set up all engagement components"""
        self.metrics = metrics
        self.patterns = patterns
        self.segments = segments
        self.templates = templates
        
    def process_engagement(self, tweet_data: Dict) -> Dict:
        """Process engagement data and update metrics"""
        try:
            # Track metrics
            if self.metrics:
                self.metrics.track_engagement(tweet_data)
            
            # Analyze patterns
            if self.patterns:
                pattern_analysis = self.patterns.analyze_patterns(tweet_data)
            
            # Update segment data
            if self.segments:
                segment_data = self.segments.update_segments(tweet_data)
            
            return {
                'success': True,
                'patterns': pattern_analysis if 'pattern_analysis' in locals() else None,
                'segments': segment_data if 'segment_data' in locals() else None
            }
            
        except Exception as e:
            print(f"Error processing engagement: {e}")
            return {'success': False, 'error': str(e)}
            
    def generate_reply(self, context: Dict) -> Optional[str]:
        """Generate reply using available components"""
        try:
            # Try LLM first
            if self.llm:
                prompt = self._create_llm_prompt(context)
                reply = self.llm.generate(prompt)
                if reply:
                    return reply.strip()
            
            # Fall back to templates
            if self.templates:
                return self.templates.generate_reply(context)
            
            return None
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return None
            
    def _create_llm_prompt(self, context: Dict) -> str:
        """Create context-aware LLM prompt"""
        tweet = context.get('tweet_text', '')
        market = context.get('market_data', {})
        
        # Get optimal content category if patterns available
        category = self.patterns.get_optimal_category(tweet) if self.patterns else None
        
        # Get user segment if available
        segment = self.segments.get_user_segment(context) if self.segments else None
        
        prompt = f"""You are Elion, an AI crypto trading assistant.
        
        Tweet: {tweet}
        Market Context: {market}
        Category: {category if category else 'Not specified'}
        User Segment: {segment if segment else 'Not specified'}
        
        Generate a reply that:
        1. Matches the user's interests
        2. Uses appropriate content style
        3. Includes relevant market insights
        4. Shows your AI personality
        5. Uses emojis appropriately
        6. Is under 280 characters
        
        Reply:"""
        
        return prompt
