"""
Custom LLM implementation for Meta Llama model
"""
from typing import Any, Dict, List, Optional
import json
import requests
import os
import re
import logging

logger = logging.getLogger(__name__)

class MetaLlamaComponent:
    """Custom LLM component for Meta-Llama"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """Initialize Meta Llama component"""
        # Use provided values or fall back to env vars
        self.api_key = api_key or os.getenv('AI_ACCESS_TOKEN')
        self.api_base = api_base or os.getenv('AI_API_URL')
        self.model = os.getenv('AI_MODEL_NAME', 'Meta-Llama-3.3-70B-Instruct')
        
        # Initialize session with longer timeouts
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        })
        
        # Set longer timeouts
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
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
            
            logger.info(f"Making API request to: {self.api_base}")
            
            # Make API request with longer timeout
            response = self.session.post(
                self.api_base,
                json=data,
                timeout=(10, 60)  # (connect timeout, read timeout)
            )
            
            # Check for HTTP errors (200 or 201 are valid)
            if response.status_code not in [200, 201]:
                logger.error(f"API Error: {response.status_code} - {response.text}")
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
                    if 'text' in choice:
                        return choice['text'].strip()
                        
                logger.error(f"Unexpected API response format: {data}")
                return None
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse API response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"API request timed out after 60 seconds")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
