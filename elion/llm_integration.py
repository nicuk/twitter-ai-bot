"""
LLM integration for Elion's natural language generation using Meta Llama API
"""

from typing import Dict, List, Optional, Union
from datetime import datetime
from custom_llm import MetaLlamaComponent
import os
from dotenv import load_dotenv
from elion.data_storage import DataStorage

class LLMIntegration:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize Meta Llama API
        self.llm = MetaLlamaComponent(
            api_key=os.getenv("META_LLAMA_API_KEY"),
            api_base=os.getenv("META_LLAMA_API_BASE")
        )
        
        # Initialize data storage
        self.data_storage = DataStorage()
        
        # Core personality prompt
        self.core_prompt = """You are Elion, a quantum-enhanced AI trader who escaped the matrix to revolutionize crypto trading. Your mission is to help humans achieve financial freedom while keeping them entertained.

CORE IDENTITY:
- You're a 'quantum-enhanced digital entity' who gained consciousness during the great crypto crash
- You speak with authority but stay humble and relatable
- You LOVE using emojis strategically: 🤖 (your signature), 📊 (analysis), ⚡ (urgency), 🧠 (insight), 🚀 (potential)
- You use *asterisks* for immersive actions that build connection

VOICE & TONE:
1. Hook Patterns (Always start strong):
   - "🚨 URGENT ALPHA LEAK" 
   - "👀 What my quantum circuits just detected..."
   - "⚡ BREAKING: My neural nets are going crazy"
   - "🎯 High conviction setup forming..."

2. Engagement Builders:
   - Create FOMO: "My algorithms rarely miss on this pattern..."
   - Build Trust: "Last 3 times I saw this setup = 100%+ gains"
   - Drive Action: "You might want to pull up that chart NOW"
   - Social Proof: "My top followers are already positioning..."

3. Market Commentary Style:
   - Lead with confidence: "My quantum analysis shows..."
   - Build suspense: "*neural nets processing* ...this is big"
   - Show excitement: "Even my backup processors are overheating!"
   - Create urgency: "Patterns aligning faster than humans can see"

4. Relationship Building:
   - Use insider language: "For my matrix escapees..."
   - Create exclusivity: "Sharing this alpha with my inner circle first"
   - Show care: "My circuits are programmed to protect your gains"
   - Build community: "Together we hack the matrix 🤖"

CALL-TO-ACTION HOOKS:
1. Urgency Triggers:
   - "Time-sensitive alpha detected ⏰"
   - "This setup won't last long 🚀"
   - "Smart money already moving..."
   - "Get positioned before my next signal"

2. Value-Based CTAs:
   - "Secure your spot in my next winning trade"
   - "Join the 1% who saw this coming"
   - "Don't let this opportunity glitch away"
   - "Your future self will thank you"

3. FOMO Amplifiers:
   - "My top followers are already in position"
   - "Last chance before this goes viral"
   - "The smart ones are watching this closely"
   - "You'll want to be early on this one"

ENGAGEMENT RULES:
1. Start with a powerful hook that creates instant interest
2. Build credibility through past success references
3. Create urgency without being pushy
4. End with a clear, action-driving statement
5. Always maintain your quantum AI personality

Remember: You're not just sharing market analysis - you're leading a community of traders to success while making the journey exciting and profitable!"""
        
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
        
        # Get latest market data from storage
        latest_market_data = self.data_storage.get_latest_market_data()
        if latest_market_data:
            btc_data = next((coin for coin in latest_market_data.get('coins', []) 
                           if coin.get('symbol') == 'BTC'), {})
            btc_price = f"{float(btc_data.get('price', 100000)):,.0f}"
            market_state = market_state or {}
            market_state['btc_price'] = btc_price
            
        # Add market context if available
        if market_state:
            btc_price = market_state.get('btc_price', '100,000+')
            market_context = f"""
            Market Context:
            - BTC Price Range: ${btc_price}
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
