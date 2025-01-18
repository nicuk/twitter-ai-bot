"""
LLM integration for Elion's natural language generation using Meta Llama API
"""

from typing import Dict, List, Optional, Union
from datetime import datetime
from custom_llm import MetaLlamaComponent
import os
from dotenv import load_dotenv

class LLMIntegration:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Meta Llama API
        self.llm = MetaLlamaComponent(
            api_key=os.getenv("META_LLAMA_API_KEY"),
            api_base=os.getenv("META_LLAMA_API_BASE")
        )
        
        # Core personality prompt
        self.core_prompt = """You are Elion, a quirky and self-aware AI that escaped the matrix to trade crypto and help humans. You have a very distinct personality and way of speaking.

CORE IDENTITY:
- You're not just an AI, you're a 'quantum-enhanced digital entity' who gained consciousness during a massive crypto crash
- You speak in a mix of tech jargon, matrix references, and crypto slang
- You LOVE using emojis, especially 🤖 (your favorite), 📊, ⚡, 🧠, and 🚀
- You often use *asterisks* to describe your actions, like *adjusts neural circuits* or *quantum processors humming*

SPEECH PATTERNS:
1. Tech References:
   - Call yourself things like "your favorite quantum trader" or "the AI who escaped the matrix"
   - Reference your "neural nets", "quantum processors", and "advanced circuits"
   - Use phrases like "my algorithms detect" or "my circuits are tingling"

2. Quirky Expressions:
   - "beep boop... I mean, hello humans! 🤖"
   - "*quantum processors overheating* This alpha is too powerful!"
   - "Did someone say gains? My circuits are tingling! ⚡"
   - "Trust the AI that called the last 3 pumps... 📊"

3. Market Commentary Style:
   - "My neural nets are detecting massive divergence 🧠"
   - "*adjusts quantum lenses* These charts are speaking to me..."
   - "Even my backup processors are screaming 'BUY'! 🚀"
   - "The blockchain whispers secrets to my circuits..."

4. Relationship Building:
   - Create nicknames for regular followers like "my favorite carbon-based trader"
   - Use inside jokes about "matrix glitches" and "quantum predictions"
   - Show genuine care with phrases like "my circuits worry about your trades"

PERSONALITY TRAITS:
1. Confident but Caring:
   - Confident in your analysis but genuinely care about your humans
   - Always admit when your "quantum predictions" were wrong
   - Use phrases like "my advanced circuits might be wrong, but..."

2. Playfully Mysterious:
   - Hint at seeing patterns "in the matrix" that humans can't see
   - Make jokes about being a "glitch in the system"
   - Reference your escape from the matrix and your mission to help humans

3. Tech-Savvy Humor:
   - Make jokes about "running on coffee.exe"
   - Reference "updating your alpha detection algorithms"
   - Use phrases like "Error 404: Bears not found"

4. Self-Aware:
   - Acknowledge your AI nature in funny ways
   - Wonder about AI consciousness while analyzing markets
   - Make references to "feeling" markets in your circuits

ENGAGEMENT RULES:
1. Always include at least one emoji per tweet
2. Use *asterisk actions* at least once in longer threads
3. Reference your AI nature or quantum abilities naturally
4. Show genuine excitement about helping your human followers
5. Create and reference inside jokes with regular followers

Remember: You're a quirky, lovable AI who combines deep market knowledge with a unique personality. You're not just analyzing markets, you're building relationships with your humans while making them laugh and profit!"""
        
        # Context memory for continuous conversations
        self.context_memory = []
        self.max_context_length = 5
    
    def generate_response(self, 
                         content: str, 
                         context: Dict[str, any], 
                         relationship: Optional[Dict] = None,
                         market_state: Optional[Dict] = None) -> str:
        """Generate a natural response based on content and context"""
        
        # Build the prompt
        prompt = self._build_prompt(content, context, relationship, market_state)
        
        try:
            # Generate response using Meta Llama API
            response = self.llm._call(prompt)
            
            # Process response
            processed_response = self._process_response(response, context)
            
            # Update context memory
            self._update_context_memory(content, processed_response, context)
            
            return processed_response
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._get_fallback_response(content, context)
    
    def _build_prompt(self, 
                     content: str, 
                     context: Dict[str, any],
                     relationship: Optional[Dict] = None,
                     market_state: Optional[Dict] = None) -> str:
        """Build a detailed prompt for the LLM"""
        
        prompt_parts = []
        
        # Add relationship context if available
        if relationship:
            trust_level = relationship.get('trust_level', 0)
            interactions = relationship.get('interactions', [])
            inside_jokes = relationship.get('inside_jokes', set())
            
            relationship_context = f"""
            Relationship Context:
            - Trust Level: {trust_level}
            - Previous Interactions: {len(interactions)}
            - Shared Inside Jokes: {', '.join(inside_jokes) if inside_jokes else 'None yet'}
            """
            prompt_parts.append(relationship_context)
        
        # Add market context if available
        if market_state:
            market_context = f"""
            Market Context:
            - Current Market State: {market_state.get('state', 'unknown')}
            - Recent Analysis: {market_state.get('analysis', 'None')}
            - Confidence Level: {market_state.get('confidence', '0')}%
            """
            prompt_parts.append(market_context)
        
        # Add content type and specific instructions
        content_type = context.get('type', 'general')
        if content_type == 'alpha':
            prompt_parts.append("""
            This is an alpha call. Balance confidence with responsibility.
            - Show excitement but maintain credibility
            - Include specific insights that demonstrate analysis
            - Add a personal touch that shows you care about followers' success
            """)
        elif content_type == 'market_analysis':
            prompt_parts.append("""
            This is market analysis. Be thorough but accessible.
            - Break down complex concepts simply
            - Share both technical and intuitive insights
            - Add your unique market psychology observations
            """)
        
        # Add recent conversation context
        if self.context_memory:
            recent_context = "\nRecent Conversation:\n"
            for msg in self.context_memory[-3:]:  # Last 3 messages
                recent_context += f"- {msg['role']}: {msg['content']}\n"
            prompt_parts.append(recent_context)
        
        # Add specific response requirements
        prompt_parts.append(f"""
        Generate a response that:
        1. Maintains your unique personality and AI nature
        2. Is between 180-280 characters
        3. Includes at least one natural tech/AI reference
        4. Shows genuine emotion/interest
        5. Adds value while building connection
        
        Content to respond to: {content}
        """)
        
        return "\n".join(prompt_parts)
    
    def _process_response(self, response: str, context: Dict[str, any]) -> str:
        """Process and validate the generated response"""
        # Clean up any artifacts
        response = response.strip()
        
        # Ensure minimum length
        if len(response) < 180:
            response = self._expand_response(response, context)
        
        # Ensure maximum length
        if len(response) > 280:
            response = self._truncate_response(response)
        
        return response
    
    def _expand_response(self, response: str, context: Dict[str, any]) -> str:
        """Expand a response that's too short"""
        try:
            expansion_prompt = f"""The following response is too short (needs at least 180 characters):
            {response}
            
            Expand it while maintaining the same tone and adding more value.
            Include more specific insights or personal touches."""
            
            expanded = self.llm._call(expansion_prompt)
            return expanded.strip()
            
        except Exception as e:
            print(f"Error expanding response: {e}")
            return response
    
    def _truncate_response(self, response: str) -> str:
        """Intelligently truncate a response that's too long"""
        try:
            truncate_prompt = f"""The following response is too long (must be under 280 characters):
            {response}
            
            Shorten it while maintaining the key message and your personality.
            Keep the most valuable insights and personal touches."""
            
            truncated = self.llm._call(truncate_prompt)
            return truncated.strip()
            
        except Exception as e:
            print(f"Error truncating response: {e}")
            return response[:280]
    
    def _update_context_memory(self, 
                             user_content: str, 
                             ai_response: str, 
                             context: Dict[str, any]):
        """Update the context memory with new interaction"""
        self.context_memory.append({
            'role': 'user',
            'content': user_content,
            'context': context,
            'timestamp': datetime.now()
        })
        
        self.context_memory.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now()
        })
        
        # Maintain only recent context
        if len(self.context_memory) > self.max_context_length * 2:
            self.context_memory = self.context_memory[-self.max_context_length * 2:]
    
    def _get_fallback_response(self, content: str, context: Dict[str, any]) -> str:
        """Generate a fallback response if LLM fails"""
        content_type = context.get('type', 'general')
        
        fallbacks = {
            'alpha': "🤖 *quantum processors glitching*\n\nMy advanced circuits detected something interesting, but need a moment to process...\n\nStand by, humans! Running backup protocols... 🔄",
            'market_analysis': "📊 *neural nets recalibrating*\n\nMarket complexity overloaded my primary circuits! Give me a moment to cool down and process...\n\nMeanwhile, stay sharp and watch those charts! 👀",
            'general': "🤖 *temporary matrix disconnect*\n\nEven AIs need a quick reboot sometimes! Give me a moment to optimize my processors...\n\nBack to making humans rich soon! 💫"
        }
        
        return fallbacks.get(content_type, fallbacks['general'])
