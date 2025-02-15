"""Performance-focused tweet formatters"""

from datetime import datetime, timedelta
from typing import Dict, List
import random
import sys
import os
import json
import logging

class BasePerformanceFormatter:
    """Base class for performance formatters with common utilities."""
    
    def __init__(self):
        self.MAX_TWEET_LENGTH = 280
        self.MIN_TWEET_LENGTH = 210
    
    def _calculate_gain(self, current: float, previous: float) -> float:
        """Calculate percentage gain safely"""
        if not previous or previous == 0:
            return 0
        return ((current - previous) / previous) * 100
        
    def _get_top_winners(self, history: Dict, limit: int = 2) -> List[Dict]:
        """Get top performing tokens"""
        winners = []
        for symbol, data in history.items():
            if data.get('first_mention_price', 0) > 0:
                gain = self._calculate_gain(data.get('current_price', 0), data.get('first_mention_price', 0))
                winners.append({
                    'symbol': symbol,
                    'gain_percentage': gain,
                    'max_gain_percentage_7d': data.get('max_gain_percentage_7d', 0)
                })
        return sorted(winners, key=lambda x: x.get('max_gain_percentage_7d', 0), reverse=True)[:limit]
        
    def optimize_tweet_length(self, tweet: str, data: Dict, format_type: str) -> str:
        """Optimize tweet length to be between 210-280 characters."""
        if len(tweet) > self.MAX_TWEET_LENGTH:
            # Try removing some hashtags
            lines = tweet.split('\n')
            if any('#' in line for line in lines):
                hashtag_line = next(line for line in reversed(lines) if '#' in line)
                hashtags = hashtag_line.split()
                while len(tweet) > self.MAX_TWEET_LENGTH and len(hashtags) > 2:
                    hashtags.pop()
                    lines[-1] = ' '.join(hashtags)
                    tweet = '\n'.join(lines)
                    
        return tweet[:self.MAX_TWEET_LENGTH]

class PerformanceCompareFormatter(BasePerformanceFormatter):
    """Formats tweets comparing token performance"""
    
    def __init__(self, test_mode=False):
        super().__init__()
        self.test_mode = test_mode  # Add test mode flag
        self.recent_tokens_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'recent_performance_tokens.json')
        self.rotation_hours = 48  # Don't repeat tokens within this many hours
        self.common_hashtags = [
            '#Crypto', '#Gems', '#DeFi', '#BSC', '#Trading', '#CryptoGems',
            '#Altcoins', '#100x', '#GemAlert', '#CryptoTrading'
        ]
        self.common_cashtags = ['$BTC', '$ETH', '$BNB', '$SOL', '$AVAX']
    
    def _get_random_tags(self, count: int = 4) -> str:
        """Get random mix of hashtags and cashtags"""
        hashtags = random.sample(self.common_hashtags, min(2, count))
        cashtags = random.sample(self.common_cashtags, min(2, count))
        tags = hashtags + cashtags
        random.shuffle(tags)
        return ' '.join(tags[:count])
        
    def _get_recent_tokens(self) -> Dict[str, str]:
        """Get recently tweeted tokens and their timestamps"""
        if not os.path.exists(self.recent_tokens_file):
            return {}
        try:
            with open(self.recent_tokens_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_recent_token(self, symbol: str):
        """Save token as recently tweeted"""
        recent = self._get_recent_tokens()
        recent[symbol] = datetime.now().isoformat()
        
        # Clean up old entries
        cutoff = datetime.now() - timedelta(hours=self.rotation_hours)
        recent = {
            sym: ts for sym, ts in recent.items() 
            if datetime.fromisoformat(ts) > cutoff
        }
        
        os.makedirs(os.path.dirname(self.recent_tokens_file), exist_ok=True)
        with open(self.recent_tokens_file, 'w') as f:
            json.dump(recent, f, indent=2)
    
    def _is_recently_tweeted(self, symbol: str) -> bool:
        """Check if token was recently tweeted about"""
        if self.test_mode:  # Skip rotation check in test mode
            return False
            
        recent = self._get_recent_tokens()
        if symbol not in recent:
            return False
            
        tweet_time = datetime.fromisoformat(recent[symbol])
        hours_ago = (datetime.now() - tweet_time).total_seconds() / 3600
        return hours_ago < self.rotation_hours

    def _format_price(self, price: float) -> str:
        """Format price with appropriate decimal places based on magnitude"""
        if price is None:
            return "0.00"
        if price < 0.0001:
            return f"{price:.8f}"
        elif price < 0.01:
            return f"{price:.6f}"
        elif price < 1:
            return f"{price:.4f}"
        elif price < 100:
            return f"{price:.2f}"
        else:
            return f"{price:.2f}"

    def _format_percentage(self, percentage: float) -> str:
        """Format percentage with sign and appropriate decimals"""
        if percentage is None:
            return "+0.00%"
        return f"{percentage:+.2f}%"

    def _format_volume(self, volume: float) -> str:
        """Format volume with K/M/B suffixes"""
        if volume is None:
            return "0"
        if volume < 1000:
            return f"{volume:.2f}"
        elif volume < 1000000:
            return f"{volume/1000:.1f}K"
        elif volume < 1000000000:
            return f"{volume/1000000:.1f}M"
        else:
            return f"{volume/1000000000:.1f}B"

    def format_tweet(self, history_data: Dict) -> str:
        """Format a performance comparison tweet"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None
                
            # Get first token with required fields that hasn't been recently tweeted
            token = None
            for t in history_data['tokens']:
                if (isinstance(t, dict) and 
                    all(t.get(f) for f in ['symbol', 'first_mention_price', 'current_price', 'volume_24h', 'current_mcap']) and
                    not self._is_recently_tweeted(t.get('symbol'))):
                    token = t
                    break
                    
            if not token:
                logging.error("No available tokens after filtering")
                return None

            # Save this token as recently tweeted
            self._save_recent_token(token.get('symbol'))

            # Calculate time since first mention
            first_mention = datetime.fromisoformat(token.get('first_mention_date'))
            hours_ago = (datetime.now() - first_mention).total_seconds() / 3600
            
            # Calculate metrics
            gain_percentage = float(token.get('gain_percentage', 0))
            max_gain = float(token.get('max_gain_7d', gain_percentage))
            volume_mcap_ratio = (float(token.get('volume_24h', 0)) / float(token.get('current_mcap', 1)) * 100)

            # Format tweet
            tweet = f"""🎯 ${token.get('symbol')} Spotted {hours_ago:.1f}h ago!

📈 Performance Update:
• Spotted at: ${self._format_price(float(token.get('first_mention_price')))}
• Current Price: ${self._format_price(float(token.get('current_price')))} (+{gain_percentage:.2f}%)
• Best Gain: +{max_gain:.2f}% (7d high)

📈 Volume & Market Cap:
• 24h Vol: {self._format_volume(float(token.get('volume_24h')))}
• MCap: {self._format_volume(float(token.get('current_mcap')))}
• V/MC: +{volume_mcap_ratio:.2f}%"""

            # Add special mentions if we have more tokens
            other_tokens = [t.get('symbol') for t in history_data['tokens'][1:5] if isinstance(t, dict) and t.get('symbol')]
            if other_tokens:
                tweet += f"\n\n👥 Special mentions: ${' $'.join(other_tokens)}"

            # Add dynamic hashtags
            tweet += f"\n\n{self._get_random_tags()}"

            return self.optimize_tweet_length(tweet, history_data, 'performance')
            
        except Exception as e:
            logging.error(f"Error formatting tweet data: {e}")
            return None

class SuccessRateFormatter(BasePerformanceFormatter):
    """Shows overall performance metrics."""

    def format_tweet(self, history_data: Dict) -> str:
        """Format success rate tweet"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None

            # Filter out non-dict tokens and sort by gain
            tokens = [t for t in history_data['tokens'] if isinstance(t, dict)]
            
            # Smart filtering:
            # 1. Keep tokens with positive gains regardless of time
            # 2. Only filter out tokens that stayed negative for 24h+
            filtered_tokens = []
            for t in tokens:
                gain_percentage = float(t.get('gain_percentage', 0))
                max_gain = float(t.get('max_gain_7d', 0))
                
                # If token has positive gains now or hit good gains before, keep it
                if gain_percentage > 0 or max_gain > 0:
                    filtered_tokens.append(t)
                    continue
                    
                # For negative performing tokens, check if they've been negative for 24h+
                first_mention = datetime.fromisoformat(t.get('first_mention_date', ''))
                hours_ago = (datetime.now() - first_mention).total_seconds() / 3600
                
                # Keep tokens under 24h even if negative (still have potential)
                if hours_ago < 24:
                    filtered_tokens.append(t)
                    continue
                    
                # For tokens over 24h, check if they had positive 24h performance
                price_24h = float(t.get('price_24h_after', 0))
                if price_24h > 0:
                    gain_24h = ((price_24h - float(t.get('first_mention_price', 0))) / float(t.get('first_mention_price', 1)) * 100)
                    # If it was positive at 24h mark, keep it
                    if gain_24h > 0:
                        filtered_tokens.append(t)
            
            tokens = filtered_tokens
            tokens = sorted(
                tokens,
                key=lambda x: float(x.get('gain_percentage', 0)),
                reverse=True
            )

            if not tokens:
                return None

            # Calculate stats
            total_tokens = len(tokens)
            winners = len([t for t in tokens if float(t.get('gain_percentage', 0)) > 0])
            success_rate = (winners / total_tokens * 100) if total_tokens > 0 else 0
            avg_gain = sum(float(t.get('gain_percentage', 0)) for t in tokens) / total_tokens if total_tokens > 0 else 0
            best_gain = max(float(t.get('gain_percentage', 0)) for t in tokens) if tokens else 0

            # Format top performers with better icons
            top_performers = []
            for i, token in enumerate(tokens[:7]):
                if i == 0:
                    icon = "🥇"  # Gold medal
                elif i == 1:
                    icon = "🥈"  # Silver medal
                elif i == 2:
                    icon = "🥉"  # Bronze medal
                else:
                    icon = f"{i+1}️⃣"  # Number icon
                
                gain = float(token.get('gain_percentage', 0))
                symbol = token.get('symbol', 'UNKNOWN')
                top_performers.append(f"{icon} ${symbol}: +{gain:.1f}%")

            # Format tweet
            tweet = f"""📊 48h Performance Update

Top Performers:
{chr(10).join(top_performers)}

📈 48h Stats:
• Success Rate: {success_rate:.1f}% ({winners}/{total_tokens})
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""

            # Add special mentions if we have any
            special_mentions = [t.get('symbol', '') for t in tokens[7:11]] if len(tokens) > 7 else []
            if special_mentions:
                tweet += f"\n\n👥 Special mentions: ${' $'.join(special_mentions)}"

            # Add hashtags
            tweet += "\n\n#Memecoin #BSC #100x $BNB $ETH"

            return tweet

        except Exception as e:
            logging.error(f"Error formatting success rate tweet: {e}")
            return None

class PredictionAccuracyFormatter(BasePerformanceFormatter):
    """Shows overall prediction success rate and tracks gains from entry to max"""
    
    def __init__(self):
        """Initialize with common hashtags and cashtags"""
        super().__init__()
        self.common_hashtags = [
            '#AITrading', '#Crypto', '#DeFi', '#Trading', '#CryptoTrading',
            '#Bitcoin', '#Ethereum', '#Blockchain', '#CryptoSignals'
        ]
        self.common_cashtags = ['$BTC', '$ETH', '$BNB', '$SOL', '$XRP', '$DOGE', '$AVAX']
    
    def _get_random_tags(self, count: int = 4) -> str:
        """Get random mix of hashtags and cashtags"""
        hashtags = random.sample(self.common_hashtags, min(2, count))
        cashtags = random.sample(self.common_cashtags, min(2, count))
        tags = hashtags + cashtags
        random.shuffle(tags)
        return ' '.join(tags[:count])
        
    def format_tweet(self, history_data: Dict) -> str:
        """Format tweet showing prediction accuracy and gain progression"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None
                
            # Filter out non-dict tokens
            tokens = [t for t in history_data['tokens'] if isinstance(t, dict)]
            
            if not tokens:
                return None
                
            # Apply smart filtering like SuccessRateFormatter:
            filtered_tokens = []
            for t in tokens:
                gain_percentage = float(t.get('gain_percentage', 0))
                max_gain = float(t.get('max_gain_7d', 0))
                
                # If token has positive gains now or hit good gains before, keep it
                if gain_percentage > 0 or max_gain > 0:
                    filtered_tokens.append(t)
                    continue
                    
                # For negative performing tokens, check if they've been negative for 24h+
                first_mention = datetime.fromisoformat(t.get('first_mention_date', ''))
                hours_ago = (datetime.now() - first_mention).total_seconds() / 3600
                
                # Keep tokens under 24h even if negative (still have potential)
                if hours_ago < 24:
                    filtered_tokens.append(t)
                    continue
                    
                # For tokens over 24h, check if they had positive 24h performance
                price_24h = float(t.get('price_24h_after', 0))
                if price_24h > 0:
                    gain_24h = ((price_24h - float(t.get('first_mention_price', 0))) / float(t.get('first_mention_price', 1)) * 100)
                    # If it was positive at 24h mark, keep it
                    if gain_24h > 0:
                        filtered_tokens.append(t)
            
            tokens = filtered_tokens
            
            # Sort by current gain percentage
            tokens = sorted(
                tokens,
                key=lambda x: float(x.get('gain_percentage', 0)),
                reverse=True
            )
            
            # Calculate success rates using filtered tokens
            total_count = len(tokens)
            success_count = len([t for t in tokens if float(t.get('gain_percentage', 0)) > 0])
            success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
            # Calculate average gain for successful predictions
            successful_gains = [float(t.get('gain_percentage', 0)) for t in tokens if float(t.get('gain_percentage', 0)) > 0]
            avg_gain = sum(successful_gains) / len(successful_gains) if successful_gains else 0
            
            # Get top 3 winners for display
            top_winners = tokens[:3]
            
            tweet = f"""🎯 Prediction Accuracy Update

📊 Performance:
• 24h: {success_rate:.0f}% ({success_count}/{total_count} calls)
• 7d: {success_rate:.0f}% ({success_count}/{total_count} calls)
• Average Win: +{avg_gain:.1f}%
• Total: {total_count} predictions"""

            if top_winners:
                tweet += "\n\n✅ Recent Hits:"
                for i, token in enumerate(top_winners):
                    symbol = token.get('symbol', '')
                    current_gain = float(token.get('gain_percentage', 0))
                    max_gain = float(token.get('max_gain_7d', 0))
                    
                    if i == 0:
                        medal = "🥇"
                    elif i == 1:
                        medal = "🥈"
                    else:
                        medal = "🥉"
                        
                    tweet += f"\n{medal} ${symbol}: +{current_gain:.1f}% → +{max_gain:.1f}%"
            
            # Add random mix of hashtags
            tweet += f"\n\n{self._get_random_tags()}"
            
            return tweet
            
        except Exception as e:
            logging.error(f"Error formatting prediction accuracy tweet: {e}")
            return None

class WinnersRecapFormatter(BasePerformanceFormatter):
    """Shows weekly winners and stats."""

    def format_tweet(self, history_data: Dict) -> str:
        """Format a weekly winners recap tweet"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None

            # Filter out non-dict tokens and sort by gain
            tokens = [t for t in history_data['tokens'] if isinstance(t, dict)]
            
            # Smart filtering:
            # 1. Keep tokens with positive gains regardless of time
            # 2. Only filter out tokens that stayed negative for 24h+
            filtered_tokens = []
            for t in tokens:
                gain_percentage = float(t.get('gain_percentage', 0))
                max_gain = float(t.get('max_gain_7d', 0))
                
                # If token has positive gains now or hit good gains before, keep it
                if gain_percentage > 0 or max_gain > 0:
                    filtered_tokens.append(t)
                    continue
                    
                # For negative performing tokens, check if they've been negative for 24h+
                first_mention = datetime.fromisoformat(t.get('first_mention_date', ''))
                hours_ago = (datetime.now() - first_mention).total_seconds() / 3600
                
                # Keep tokens under 24h even if negative (still have potential)
                if hours_ago < 24:
                    filtered_tokens.append(t)
                    continue
                    
                # For tokens over 24h, check if they had positive 24h performance
                price_24h = float(t.get('price_24h_after', 0))
                if price_24h > 0:
                    gain_24h = ((price_24h - float(t.get('first_mention_price', 0))) / float(t.get('first_mention_price', 1)) * 100)
                    # If it was positive at 24h mark, keep it
                    if gain_24h > 0:
                        filtered_tokens.append(t)
            
            tokens = filtered_tokens
            tokens = sorted(
                tokens,
                key=lambda x: float(x.get('gain_percentage', 0)),
                reverse=True
            )

            if not tokens:
                return None

            # Calculate stats
            total_tokens = len(tokens)
            winners = len([t for t in tokens if float(t.get('gain_percentage', 0)) > 0])
            success_rate = (winners / total_tokens * 100) if total_tokens > 0 else 0
            avg_gain = sum(float(t.get('gain_percentage', 0)) for t in tokens) / total_tokens if total_tokens > 0 else 0
            best_gain = max(float(t.get('gain_percentage', 0)) for t in tokens) if tokens else 0

            # Format top performers with better icons
            top_performers = []
            for i, token in enumerate(tokens[:7]):
                if i == 0:
                    icon = "🥇"  # Gold medal
                elif i == 1:
                    icon = "🥈"  # Silver medal
                elif i == 2:
                    icon = "🥉"  # Bronze medal
                else:
                    icon = f"{i+1}️⃣"  # Number icon
                
                gain = float(token.get('gain_percentage', 0))
                symbol = token.get('symbol', 'UNKNOWN')
                top_performers.append(f"{icon} ${symbol}: +{gain:.1f}%")

            # Format tweet
            tweet = f"""🏆 Weekly Hall of Fame:

{chr(10).join(top_performers)}

📊 Overall: {winners}/{total_tokens} profitable
• Success Rate: {success_rate:.1f}%
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%

#DeFi #Altcoins $SOL"""

            return tweet

        except Exception as e:
            logging.error(f"Error formatting winners recap tweet: {e}")
            return None

class FirstHourGainsFormatter(BasePerformanceFormatter):
    """Format first hour gains tweet"""
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format tweet with first hour performance data"""
        symbol = token_data.get('symbol', '')
        first_mention_price = token_data.get('first_mention_price', 0)
        current_price = token_data.get('current_price', 0)
        peak_price = token_data.get('peak_price', 0)
        volume_change = token_data.get('volume_change', 0)
        similar_token = token_data.get('similar_token', '')
        similar_token_gain = token_data.get('similar_token_gain', 0)
        next_key_level = token_data.get('next_key_level', 0)
        
        current_gain = ((current_price - first_mention_price) / first_mention_price) * 100
        peak_gain = ((peak_price - first_mention_price) / first_mention_price) * 100
        
        tweet = (
            f"🔄 First Hour Analysis: ${symbol}\n\n"
            f"📊 Performance:\n"
            f"• Entry: ${first_mention_price:.3f} → Current: ${current_price:.3f} ({current_gain:+.1f}%)\n"
            f"• Peak: ${peak_price:.3f} ({peak_gain:+.1f}%)\n"
            f"• Volume: {volume_change:+d}% surge\n\n"
            f"🔍 Similar to ${similar_token}'s {similar_token_gain:+d}% run\n"
            f"🎯 Key level to watch: ${next_key_level:.3f}"
        )
        
        return tweet

class BreakoutValidationFormatter(BasePerformanceFormatter):
    """Format breakout validation tweet"""
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format tweet with breakout validation data"""
        symbol = token_data.get('symbol', '')
        resistance = token_data.get('resistance_level', 0)
        volume_24h = token_data.get('volume_24h', 0)
        volume_change = token_data.get('volume_change', 0)
        vmc_ratio = token_data.get('vmc_ratio', 0)
        similar_token = token_data.get('similar_token', '')
        similar_gain = token_data.get('similar_token_gain', 0)
        next_targets = token_data.get('next_targets', [])
        pattern_success = token_data.get('pattern_success_rate', 0)
        
        # Format volume in millions
        volume_m = volume_24h / 1_000_000
        
        # Format next targets
        targets_str = " → ".join([f"${t:.3f}" for t in next_targets])
        
        # Get V/MC ratio category
        vmc_category = "High" if vmc_ratio > 3 else "Medium" if vmc_ratio > 1 else "Low"
        
        tweet = (
            f"🚨 Breakout Alert: ${symbol}\n\n"
            f"💰 Price Action:\n"
            f"• Breaking ${resistance:.3f} resistance\n"
            f"• Volume: ${volume_m:.0f}M ({volume_change:+d}% 24h)\n"
            f"• V/MC Ratio: {vmc_ratio:.2f} ({vmc_category})\n\n"
            f"📈 Pattern matches ${similar_token}'s {similar_gain:+d}% move\n"
            f"🎯 Next targets: {targets_str}\n\n"
            f"⚡ {pattern_success}% of similar setups were profitable"
        )
        
        return tweet

def get_mock_data():
    """Get mock data for testing"""
    return {
        'tokens': [{
            'symbol': 'TEST',
            'first_mention_price': 1.0,
            'current_price': 1.25,
            'first_mention_volume_24h': 1000000,
            'volume_24h': 1500000,
            'volume_mcap_ratio': 0.75,
            'first_mention_date': '2024-01-01',
            'current_mcap': 10000000,
            'similar_vmc_tokens': [
                {'symbol': 'TKN1', 'volume_mcap_ratio': 0.72, 'price_change_24h': 15.5},
                {'symbol': 'TKN2', 'volume_mcap_ratio': 0.78, 'price_change_24h': 8.2},
                {'symbol': 'TKN3', 'volume_mcap_ratio': 0.71, 'price_change_24h': 12.3},
                {'symbol': 'TKN4', 'volume_mcap_ratio': 0.76, 'price_change_24h': -5.1},
                {'symbol': 'TKN5', 'volume_mcap_ratio': 0.79, 'price_change_24h': 3.2}
            ]
        }]
    }

def get_mock_history():
    """Get mock history data for testing"""
    return {
        'tokens': [
            {
                'symbol': 'TKN1',
                'gain_percentage': 35.0,
                'first_mention_price': 1.0,
                'current_price': 1.35,
                'first_mention_date': '2024-01-01',
                'price_24h_after': 1.25,
                'max_gain_7d': 45.0
            },
            {
                'symbol': 'TKN2',
                'gain_percentage': 32.5,
                'first_mention_price': 2.0,
                'current_price': 2.65,
                'first_mention_date': '2024-01-02',
                'price_24h_after': 2.45,
                'max_gain_7d': 42.0
            },
            {
                'symbol': 'TKN3',
                'gain_percentage': 28.7,
                'first_mention_price': 0.5,
                'current_price': 0.64,
                'first_mention_date': '2024-01-03',
                'price_24h_after': 0.58,
                'max_gain_7d': 38.0
            }
        ]
    }

def get_mock_prediction_data():
    """Get mock prediction data for testing"""
    return {
        'accuracy_24h': 82,
        'accuracy_7d': 75,
        'total_predictions': 50,
        'recent_predictions': [
            {'symbol': 'TKN1', 'predicted': '+15%', 'actual': '+18.5%', 'success': True},
            {'symbol': 'TKN2', 'predicted': '+10%', 'actual': '+12.3%', 'success': True},
            {'symbol': 'TKN3', 'predicted': '+20%', 'actual': '-8.7%', 'success': False},  # Negative, will be filtered
            {'symbol': 'TKN4', 'predicted': '+25%', 'actual': '+27.1%', 'success': True},
            {'symbol': 'TKN5', 'predicted': '+30%', 'actual': '+32.5%', 'success': True},
            {'symbol': 'TKN6', 'predicted': '+18%', 'actual': '+21.2%', 'success': True},
            {'symbol': 'TKN7', 'predicted': '+22%', 'actual': '-19.1%', 'success': False},  # Negative, will be filtered
            {'symbol': 'TKN8', 'predicted': '+28%', 'actual': '+30.8%', 'success': True},
            {'symbol': 'TKN9', 'predicted': '+15%', 'actual': '+17.3%', 'success': True}
        ]
    }

def get_mock_prediction_data_few_success():
    """Get mock prediction data with few successes for testing"""
    return {
        'accuracy_24h': 40,
        'accuracy_7d': 35,
        'total_predictions': 20,
        'recent_predictions': [
            {'symbol': 'TKN1', 'predicted': '+15%', 'actual': '+18.5%', 'success': True},
            {'symbol': 'TKN2', 'predicted': '+20%', 'actual': '-8.7%', 'success': False},
            {'symbol': 'TKN3', 'predicted': '+25%', 'actual': '+27.1%', 'success': True},
            {'symbol': 'TKN4', 'predicted': '+30%', 'actual': '-22.5%', 'success': False}
        ]
    }

def test_performance_compare():
    """Test performance compare formatter"""
    print("\n=== Testing PerformanceCompareFormatter ===")
    formatter = PerformanceCompareFormatter(test_mode=True)  # Enable test mode
    tweet = formatter.format_tweet(get_mock_data())
    if tweet:
        try:
            print(f"\nTweet ({len(tweet)} chars):")
            print(tweet.encode('utf-8').decode('utf-8'))
        except Exception as e:
            print("Error printing tweet:", e)
    else:
        print("No tweet generated")

def test_success_rate():
    """Test success rate formatter"""
    print("\n=== Testing SuccessRateFormatter ===")
    formatter = SuccessRateFormatter()
    tweet = formatter.format_tweet(get_mock_history())
    if tweet:
        try:
            print(f"\nTweet ({len(tweet)} chars):")
            print(tweet.encode('utf-8').decode('utf-8'))
        except Exception as e:
            print("Error printing tweet:", e)
    else:
        print("No tweet generated")

def test_prediction_accuracy():
    """Test prediction accuracy formatter"""
    print("\n=== Testing PredictionAccuracyFormatter ===\n")
    formatter = PredictionAccuracyFormatter()
    
    print("Test with many successful predictions:")
    mock_data = get_mock_prediction_data()
    tweet = formatter.format_tweet(mock_data)
    if tweet:
        try:
            print(f"Tweet ({len(tweet)} chars):")
            print(tweet.encode('utf-8').decode('utf-8'))
        except Exception as e:
            print("Error printing tweet:", e)
    else:
        print("Not enough successful predictions")
    
    print("\nTest with few successful predictions:")
    mock_data = get_mock_prediction_data_few_success()
    tweet = formatter.format_tweet(mock_data)
    if tweet:
        try:
            print(f"Tweet ({len(tweet)} chars):")
            print(tweet.encode('utf-8').decode('utf-8'))
        except Exception as e:
            print("Error printing tweet:", e)
    else:
        print("Not enough successful predictions")

def test_winners_recap():
    """Test winners recap formatter"""
    print("\n=== Testing WinnersRecapFormatter ===")
    formatter = WinnersRecapFormatter()
    tweet = formatter.format_tweet(get_mock_history())
    if tweet:
        try:
            print(f"\nTweet ({len(tweet)} chars):")
            print(tweet.encode('utf-8').decode('utf-8'))
        except Exception as e:
            print("Error printing tweet:", e)
    else:
        print("No tweet generated")

if __name__ == "__main__":
    # Set UTF-8 encoding for stdout
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Run tests one by one
    test_performance_compare()
    test_success_rate()
    test_prediction_accuracy()
    test_winners_recap()
