"""
Content generation for ELAI's different tweet types
"""

from typing import Dict, Optional
from .tweet_formatters import TweetFormatters

class ContentGenerator:
    """Generates tweet content using personality and market data"""
    
    def __init__(self, personality, llm=None):
        """Initialize content generator with personality manager"""
        self.personality = personality
        self.llm = llm
        self.formatters = TweetFormatters()
        self.recent_tokens = []  # Store recent tokens
        
    def update_recent_tokens(self, tokens):
        """Update list of recent tokens"""
        self.recent_tokens = tokens
        
    def generate(self, content_type: str, market_data: Optional[Dict] = None) -> Optional[str]:
        """Generate tweet content based on type and data"""
        try:
            # Get personality trait
            trait = self.personality.get_trait()
            
            # Generate content based on type
            if content_type == 'self_aware':
                # Use LLM for personal tweets if available
                if self.llm:
                    # Format token list for prompt
                    token_str = ""
                    if self.recent_tokens:
                        token_str = "\nRecent notable tokens: " + ", ".join(self.recent_tokens)
                    
                    prompt = f"""As ELAI, an AI crypto analyst with trait: {trait}, share your thoughts about crypto markets, trading, or blockchain tech.{token_str}

Requirements:
1. Keep response between 240-280 characters (including emojis and spaces)
2. Include multiple crypto terms like: DeFi, DEX, AMM, liquidity pools, yield farming, staking, NFTs, etc.
3. Add 2-3 relevant emojis
4. Sound knowledgeable but approachable
5. If recent tokens are provided, mention at least one of them

Example: "Just analyzed the DeFi landscape 🔍 Seeing interesting MEV opportunities in AMM pools, while L2 rollups are making gas fees more bearable. Yield farmers might want to watch those TVL ratios - smart money's moving! Bullish on cross-chain liquidity 🌊 #DeFi #Crypto 🚀"
"""
                    
                    response = self.llm.generate(prompt, max_tokens=300)
                    if response:
                        # Clean response and enforce character limits
                        response = response.strip().replace('\n', ' ')
                        if len(response) < 240:
                            # Too short, try again
                            return self.generate(content_type, market_data)
                        elif len(response) > 280:
                            # Too long, truncate at last complete word before 280
                            response = response[:277] + "..."
                        return response
                
                # Fallback to template if no LLM
                return self.formatters.format_self_aware(trait)
                
            elif content_type == 'market_insight' and market_data:
                # Store tokens for future reference
                if 'trend_tokens' in market_data:
                    self.recent_tokens = market_data['trend_tokens']
                return self.formatters.format_market_insight(market_data, trait)
                
            elif content_type == 'alpha' and market_data:
                # Store tokens for future reference
                if 'volume_tokens' in market_data:
                    self.recent_tokens = market_data['volume_tokens']
                return self.formatters.format_alpha(market_data, trait)
            
            return None
            
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return None
