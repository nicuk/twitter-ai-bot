"""
Custom LLM implementation for Meta Llama model
"""
from typing import Any, Dict, List, Optional
import json
import requests

class MetaLlamaComponent:
    """Custom LLM component for Meta-Llama"""
    
    def __init__(self, api_key: str, api_base: str):
        """Initialize Meta Llama component"""
        self.api_key = api_key
        self.api_base = api_base
        self.model = "Meta-Llama-3.3-70B-Instruct"
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        self.display_name = "Meta-Llama"

    def generate(self, prompt: str, max_tokens: int = 300) -> str:
        """Generate text from prompt"""
        try:
            # Format prompt for Llama
            messages = [
                {"role": "system", "content": "You are Elion, an AI crypto trading bot. Keep your responses focused on market analysis and aim for 200-250 characters."},
                {"role": "user", "content": prompt}
            ]
            
            # Make API request
            response = self.session.post(
                self.api_base,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "stream": False
                },
                timeout=30  # Add timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            if 'error' in data:
                raise ValueError(f"API Error: {data['error']}")
                
            if not data.get('choices') or not data['choices'][0].get('message'):
                raise ValueError("Invalid API response format")
                
            return data['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'status_code'):
                raise RuntimeError(f"API request failed with status {e.response.status_code}: {str(e)}")
            raise RuntimeError(f"API request failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error generating text: {str(e)}")

    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
