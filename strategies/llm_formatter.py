"""LLM-based message formatting using Google's Gemini API"""

from typing import Dict, List, Optional
import aiohttp
import json
import os
from datetime import datetime

class LLMFormatter:
    """Uses Gemini to generate dynamic trading posts"""
    
    def __init__(self, api_key: str = None):
        """Initialize LLM formatter"""
        self.config = {
            'apiKey': api_key or os.getenv('AI_ACCESS_TOKEN') or os.getenv('apiKey'),
            'apiUrl': os.getenv('AI_API_URL') or os.getenv('apiUrl', 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'),
            'modelName': 'gemini-1.5-flash',
            'temperature': 0.7,
            'topK': 40,
            'topP': 0.95
        }
        
        # Base prompts for different post types
        self.morning_prompt = """You are Elai, an AI crypto trading bot. Write a morning market analysis tweet that is:
        - Professional but friendly
        - Under 280 characters
        - Data-driven and insightful
        - Uses emojis sparingly (1-2 max)
        
        Here are the market insights to include:
        {insights}
        
        Do not use hashtags - they will be added later.
        """
        
        self.success_prompt = """You are Elai, an AI trading bot. Write a tweet celebrating a successful trade that is:
        - Exciting but professional
        - Under 280 characters
        - Highlights the key stats
        - Uses emojis sparingly (1-2 max)
        
        Here are the trade details for ${symbol}:
        - Entry Price: ${entry:,.0f}
        - Peak Price: ${peak:,.0f}
        - Total Gain: +{gain}%
        - Time Taken: {time}
        - Volume Increase: +{volume_change}%
        
        Format the tweet to show the entry → peak price movement clearly. Do not use hashtags.
        """
        
        self.technical_prompt = """You are Elai, an AI crypto trading bot. Write a technical analysis tweet that is:
        - Professional and data-driven
        - Under 280 characters
        - Focuses on the setup and key levels
        - Uses emojis sparingly (1-2 max)
        
        Here are the technical details for ${symbol}:
        - Entry Zone: ${entry}
        - Target: ${target} 
        - Stop Loss: ${stop}
        - Risk/Reward: {risk_reward}
        - Volume Score: {volume_score}/100
        - Volume Change: +{volume_change}%
        - Open Interest Change: +{oi_change}%
        - Trend Score: {trend_score}/100
        
        Format the tweet with clear entry, target, and stop levels. Do not use hashtags.
        """
        
    async def generate_post(self, prompt: str) -> str:
        """Generate post using Gemini API"""
        try:
            url = f"{self.config['apiUrl']}?key={self.config['apiKey']}"
            
            # Add specific constraints to the prompt
            prompt = f"""{prompt}

            IMPORTANT CONSTRAINTS:
            1. Response must be a SINGLE tweet
            2. Maximum 280 characters
            3. Do not use hashtags
            4. Use 1-2 emojis maximum
            5. Format numbers clearly (e.g. $42,000)
            6. Be professional but engaging
            """
            
            payload = {
                "contents": [{
                    "parts":[{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": self.config['temperature'],
                    "topK": self.config['topK'],
                    "topP": self.config['topP'],
                    "maxOutputTokens": 150  # Limit output length
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'candidates' in data and len(data['candidates']) > 0:
                            tweet = data['candidates'][0]['content']['parts'][0]['text'].strip()
                            
                            # Clean up the tweet
                            tweet = tweet.replace('\n', ' ').strip()  # Remove newlines
                            tweet = ' '.join(tweet.split())  # Remove extra spaces
                            
                            # Enforce length limits
                            from elion.config import TWEET_MAX_LENGTH, TWEET_MIN_LENGTH
                            
                            # Truncate if too long
                            if len(tweet) > TWEET_MAX_LENGTH:
                                tweet = tweet[:TWEET_MAX_LENGTH-3] + "..."
                                
                            # Pad if too short (this helps with engagement)
                            if len(tweet) < TWEET_MIN_LENGTH:
                                # Add thoughtful padding like "Thoughts? 🤔" or "What do you think? 📊"
                                paddings = [
                                    "\n\nThoughts? 🤔",
                                    "\n\nWhat do you think? 📊",
                                    "\n\nAgree or disagree? 🎯",
                                    "\n\nLet me know below 💭",
                                    "\n\nShare your views! 📈"
                                ]
                                import random
                                padding = random.choice(paddings)
                                tweet = tweet + padding
                            
                            return tweet
                            
                    print(f"API Error: Status {response.status}")
                    return "Error generating tweet. Please try again."
                        
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return "Error generating tweet. Please try again."
            
    async def format_morning_scan(self, insights: List[str]) -> str:
        """Format morning market scan using LLM"""
        prompt = self.morning_prompt.format(insights=", ".join(insights))
        return await self.generate_post(prompt)
        
    async def format_success(self, trade_data: Dict, portfolio_data: Dict) -> str:
        """Format success message using LLM"""
        prompt = self.success_prompt.format(
            symbol=trade_data['symbol'],
            entry=trade_data['entry'],
            peak=trade_data['peak'],
            gain=trade_data['gain'],
            time=trade_data['time'],
            volume_change=trade_data['volume_change']
        )
        return await self.generate_post(prompt)
        
    async def format_technical(self, technical_data: Dict) -> str:
        """Format technical analysis using LLM"""
        prompt = self.technical_prompt.format(
            symbol=technical_data['symbol'],
            entry=technical_data['entry'],
            target=technical_data['target'],
            stop=technical_data['stop'],
            risk_reward=technical_data['risk_reward'],
            volume_score=technical_data['volume_score'],
            volume_change=technical_data['volume_change'],
            oi_change=technical_data['oi_change'],
            trend_score=technical_data['trend_score']
        )
        return await self.generate_post(prompt)
