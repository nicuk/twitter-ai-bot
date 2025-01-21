"""
LLM-based engagement functionality
"""

from typing import Dict, Optional

class LLMEngagement:
    """Handles LLM-based engagement"""
    
    def __init__(self, llm):
        """Initialize LLM engagement"""
        self.llm = llm
        
    def generate_reply(self, context: Dict) -> Optional[str]:
        """Generate a reply using LLM"""
        if not self.llm:
            return None
            
        try:
            # Extract context
            tweet_text = context.get('tweet_text', '')
            market_data = context.get('market_data', {})
            
            # Create prompt for LLM
            prompt = f"""You are Elion, a helpful and insightful AI crypto trading assistant.
            Generate a friendly and engaging reply to this tweet:
            
            Tweet: {tweet_text}
            
            Market Context: {market_data}
            
            Your reply should be:
            1. Natural and conversational
            2. Helpful and insightful
            3. Reflect your AI nature in a playful way
            4. Include relevant emojis
            5. Under 280 characters
            
            Reply:"""
            
            # Get LLM response
            response = self.llm.generate(prompt)
            
            return response.strip()
            
        except Exception as e:
            print(f"Error generating LLM reply: {e}")
            return None
