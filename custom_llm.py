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
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.display_name = "Meta-Llama"

    def generate(self, prompt: str, max_tokens: int = 150) -> str:
        """Generate text from prompt"""
        try:
            # Format prompt for Llama
            messages = [
                {"role": "system", "content": "You are Elion, an AI crypto trading bot. Keep your responses concise and focused on market analysis."},
                {"role": "user", "content": prompt}
            ]
            
            # Make API request
            response = requests.post(
                self.api_base,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                    "stream": False
                },
                timeout=30  # Add timeout
            )
            
            # Check response
            if response.status_code != 200:
                return f"Error: API returned status {response.status_code}"
                
            # Extract text from response
            try:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    return result['choices'][0]['message']['content'].strip()
                return "Error: No response generated"
            except Exception as e:
                return f"Error: Failed to parse response - {str(e)}"
                
        except requests.exceptions.Timeout:
            return "Error: API request timed out"
        except requests.exceptions.RequestException as e:
            return f"Error: API request failed - {str(e)}"
        except Exception as e:
            return f"Error: Unexpected error - {str(e)}"

    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
