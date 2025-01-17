"""
Custom LLM implementation for Meta Llama model
"""
from typing import Any, Dict, List, Optional
import json
import requests

class MetaLlamaComponent:
    """Custom LLM component for Meta Llama model"""
    
    def __init__(self, api_key: str, api_base: str):
        """Initialize Meta Llama component"""
        self.api_key = api_key
        self.api_base = api_base
        self.model_name = "Meta-Llama-3.3-70B-Instruct"
        self.display_name = "Meta-Llama"

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": prompt}
                ],
                "model": self.model_name,
                "stop": ["<|eot_id|>"],
                "stream": True,
                "stream_options": {"include_usage": True}
            }
            
            print(f"\nMaking LLM request to: {self.api_base}")
            print(f"Headers: {headers}")
            print(f"Data: {data}\n")
            
            response = requests.post(
                self.api_base,
                headers=headers,
                json=data,
                stream=True
            )
            
            if response.status_code not in [200, 201]:
                print(f"API Error: {response.status_code} - {response.text}")
                return ""
                
            # Handle streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        try:
                            json_str = line[6:]  # Remove "data: " prefix
                            if json_str == "[DONE]":
                                continue
                            
                            chunk = json.loads(json_str)
                            if "choices" in chunk and chunk["choices"]:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    content = delta["content"]
                                    print(content, end="", flush=True)
                                    full_response += content
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e}")
                            continue
            
            print("\n")  # Add newline after streaming
            return full_response.strip()
            
        except Exception as e:
            print(f"Error in LLM generation: {str(e)}")
            return ""

    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
