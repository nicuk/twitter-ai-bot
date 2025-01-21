"""
Custom LLM implementation for Meta Llama model
"""
from typing import Any, Dict, List, Optional
import json
import requests
import os
import re

class MetaLlamaComponent:
    """Custom LLM component for Meta-Llama"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """Initialize Meta Llama component"""
        # Use provided values or fall back to env vars
        self.api_key = api_key or os.getenv('AI_ACCESS_TOKEN')
        self.api_base = api_base or os.getenv('AI_API_URL')
        self.model = os.getenv('AI_MODEL_NAME', 'Meta-Llama-3.3-70B-Instruct')
        
        # Initialize session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        self.display_name = "Meta-Llama"

    def generate(self, prompt: str, max_tokens: int = 300, system_message: str = None) -> str:
        """Generate text from prompt"""
        try:
            # Format request body
            data = {
                "messages": [
                    {"role": "system", "content": system_message or "You are ELAI, an AI crypto trading bot. Keep your responses focused on market analysis."},
                    {"role": "user", "content": prompt}
                ],
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "stream": False  # Use non-streaming mode
            }
            
            # Make API request
            response = self.session.post(
                self.api_base,
                json=data,
                timeout=30
            )
            
            # Check for HTTP errors (200 or 201 are valid)
            if response.status_code not in [200, 201]:
                print(f"API Error: {response.status_code} - {response.text}")
                return None
            
            # Parse response
            try:
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    # Try different response formats
                    choice = data['choices'][0]
                    
                    # Try message.content (chat format)
                    message = choice.get('message', {})
                    if message and 'content' in message:
                        return message['content'].strip()
                    
                    # Try delta.content (streaming format)
                    delta = choice.get('delta', {})
                    if delta and 'content' in delta:
                        return delta['content'].strip()
                    
                    # Try text (completion format)
                    text = choice.get('text', '')
                    if text:
                        return text.strip()
                    
                    # Try raw text between quotes
                    raw = str(choice)
                    text_match = re.search(r'"([^"]{50,})"', raw)
                    if text_match:
                        return text_match.group(1).strip()
            
            except Exception as e:
                print(f"Failed to parse response: {str(e)}")
                print(f"Response text: {response.text}")
            
            return None
            
        except Exception as e:
            print(f"API Error: {str(e)}")
            return None

    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
