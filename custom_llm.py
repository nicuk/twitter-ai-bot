"""
Custom LLM implementation for Google's Gemini API
"""
from typing import Any, Dict, List, Optional
import json
import requests
import os
import re
import logging

logger = logging.getLogger(__name__)

class GeminiComponent:
    """Custom LLM component for Gemini"""
    
    def __init__(self, api_key: str = None, api_base: str = None):
        """Initialize Gemini component"""
        # Use provided values or fall back to env vars
        self.api_key = api_key or os.getenv('AI_ACCESS_TOKEN')
        self.api_base = api_base or os.getenv('AI_API_URL', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent')
        self.model = 'gemini-1.5-flash'
        
        # Initialize session with longer timeouts
        self.session = requests.Session()
        self.session.headers.update({
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
        
        self.display_name = "Gemini"

    def generate(self, prompt: str, max_tokens: int = 300, system_message: str = None) -> str:
        """Generate text from prompt"""
        try:
            # Format request body for Gemini API
            data = {
                "contents": [{
                    "parts": [{
                        "text": f"{system_message}\n\n{prompt}" if system_message else prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            # Add API key to URL
            url = f"{self.api_base}?key={self.api_key}"
            logger.info(f"Making API request to Gemini")
            
            # Make API request with longer timeout
            response = self.session.post(
                url,
                json=data,
                timeout=(10, 60)  # (connect timeout, read timeout)
            )
            
            # Check for HTTP errors
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                return None
            
            # Parse response
            try:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        parts = candidate['content']['parts']
                        if parts and 'text' in parts[0]:
                            return parts[0]['text'].strip()
                            
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
            
    def generate_post(self, prompt: str) -> str:
        """Generate a tweet-length post from prompt"""
        # Add tweet length constraint to system message
        system_message = """
        You are ELAI, an AI crypto trading bot. Keep your responses focused on market analysis.
        IMPORTANT: Your response must be under 280 characters and suitable for Twitter.
        Use emojis appropriately but don't overdo it.
        """
        
        # Generate with smaller max tokens since we need tweet-length
        response = self.generate(prompt, max_tokens=100, system_message=system_message)
        
        if response:
            # Ensure response is tweet-length
            if len(response) > 280:
                response = response[:277] + "..."
            return response
        
        return "🤖 *Processing market data... neural nets recalibrating* Meanwhile, stay sharp and watch those charts! 👀"
            
    def __call__(self, prompt: str, **kwargs) -> str:
        """Make the class callable"""
        return self.generate(prompt, **kwargs)
# Added a comment to force file save
