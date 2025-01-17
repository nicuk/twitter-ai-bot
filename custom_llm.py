"""
Custom LLM implementation for Meta Llama model
"""
from typing import Any, Dict, List, Optional
import requests

class MetaLlamaComponent:
    """Custom LLM component for Meta Llama model"""
    
    def __init__(self, api_key: str, api_base: str):
        """Initialize Meta Llama component"""
        self.api_key = api_key
        self.api_base = api_base
        self.model_name = "Meta-Llama-3.2-7B-Instruct"
        self.display_name = "Meta-Llama"

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "frequency_penalty": kwargs.get("frequency_penalty", 0),
                "presence_penalty": kwargs.get("presence_penalty", 0)
            }
            
            response = requests.post(
                f"{self.api_base}/v1/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["text"].strip()
            
        except Exception as e:
            print(f"Error in LLM generation: {str(e)}")
            return ""

    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
