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

            # Get token with highest gain
            token = max(history_data['tokens'], key=lambda x: float(x.get('gain_percentage', 0)))
            
            # Format numbers
            volume_24h = float(token.get('volume_24h', 0))
            mcap = float(token.get('current_mcap', 0))
            volume_mcap_ratio = (volume_24h / mcap * 100) if mcap > 0 else 0
            gain_percentage = float(token.get('gain_percentage', 0))
            max_gain_7d = float(token.get('max_gain_percentage_7d', 0))
            first_mention_date = datetime.fromisoformat(token.get('first_mention_date'))
            hours_since_mention = (datetime.now() - first_mention_date).total_seconds() / 3600

            # Get similar tokens for special mentions
            similar_tokens = [t for t in history_data['tokens'] if t['symbol'] != token['symbol']]
            similar_tokens = sorted(similar_tokens, key=lambda x: float(x.get('gain_percentage', 0)), reverse=True)[:4]
            special_mentions = [t['symbol'] for t in similar_tokens]

            # Format tweet with more context and clearer language
            tweet = f"""🎯 ${token['symbol']} Spotted {hours_since_mention:.1f}h ago!

📈 Performance Update:
• Spotted at: ${self._format_price(token['first_mention_price'])}
• Current Price: ${self._format_price(token['current_price'])} ({self._format_percentage(gain_percentage)})
• Best Gain: {self._format_percentage(max_gain_7d)} (7d high)

📈 Volume & Market Cap:
• 24h Vol: {self._format_volume(volume_24h)}
• MCap: {self._format_volume(mcap)}
• V/MC: {self._format_percentage(volume_mcap_ratio)}

👥 Special mentions: ${' $'.join(special_mentions)}

#Crypto #Gems #AltSeason"""

            return self.optimize_tweet_length(tweet, history_data, 'performance')
            
        except Exception as e:
            logging.error(f"Error formatting performance tweet: {e}")
            return None

class SuccessRateFormatter(BasePerformanceFormatter):
    """Shows overall performance metrics."""

    def format_tweet(self, history_data: Dict) -> str:
        """Format success rate tweet"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None

            # Sort tokens by gain
            tokens = sorted(
                history_data['tokens'],
                key=lambda x: float(x.get('gain_percentage', 0)),
                reverse=True
            )

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
                top_performers.append(f"{icon} ${token['symbol']} (+{gain:.1f}%)")

            # Get next 4 tokens for special mentions
            special_mentions = [t['symbol'] for t in tokens[7:11]] if len(tokens) > 7 else []

            # Format tweet
            tweet = f"""📊 48h Performance Update

Top Performers:
{chr(10).join(top_performers)}

📈 48h Stats:
• Success Rate: {success_rate:.1f}% ({winners}/{total_tokens})
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""

            # Add special mentions if we have any
            if special_mentions:
                tweet += f"\n\n👥 Special mentions: ${' $'.join(special_mentions)}"

            # Add hashtags
            tweet += "\n\n#Memecoin #BSC #100x $BNB $ETH"

            return tweet

        except Exception as e:
            logging.error(f"Error formatting success rate tweet: {e}")
            return None

class PredictionAccuracyFormatter(BasePerformanceFormatter):
    """Shows overall prediction success rate"""
    
    def __init__(self):
        """Initialize with common hashtags and cashtags"""
        super().__init__()
        self.common_hashtags = [
            '#AITrading', '#Crypto', '#DeFi', '#Trading', '#CryptoTrading',
            '#Bitcoin', '#Ethereum', '#Blockchain', '#CryptoSignals'
        ]
        self.common_cashtags = ['$BTC', '$ETH', '$BNB', '$SOL', '$XRP', '$DOGE', '$AVAX']
    
    def _get_random_tags(self, count: int = 3) -> str:
        """Get random mix of hashtags and cashtags"""
        hashtags = random.sample(self.common_hashtags, min(2, count))
        cashtags = random.sample(self.common_cashtags, min(2, count))
        tags = hashtags + cashtags
        random.shuffle(tags)
        return ' '.join(tags[:count])
        
    def format_tweet(self, history_data: Dict) -> str:
        """Format tweet showing prediction accuracy"""
        try:
            if not history_data:
                return None
                
            # Calculate real success rates from history
            now = datetime.now()
            
            # Handle both list and dict formats
            if isinstance(history_data, dict) and 'tokens' not in history_data:
                # Convert dict format to list format
                tokens = [
                    {
                        'symbol': data['symbol'],
                        'gain_percentage': self._calculate_gain(
                            float(data.get('current_price', 0)),
                            float(data.get('first_mention_price', 0))
                        ),
                        'first_mention_date': data.get('first_mention_date'),
                        'predicted_gain': data.get('predicted_gain', None)  # Get predicted gain if available
                    }
                    for symbol, data in history_data.items()
                ]
            else:
                tokens = history_data['tokens']
            
            # Get 24h and 7d tokens that have predictions
            tokens_24h = [
                token for token in tokens
                if (datetime.fromisoformat(token['first_mention_date']) > 
                    now - timedelta(days=1)) and
                token.get('predicted_gain') is not None
            ]
            
            tokens_7d = [
                token for token in tokens
                if (datetime.fromisoformat(token['first_mention_date']) > 
                    now - timedelta(days=7)) and
                token.get('predicted_gain') is not None
            ]
            
            # Count successes (where actual gain >= predicted gain)
            success_24h = sum(1 for token in tokens_24h 
                            if float(token['gain_percentage']) >= float(token['predicted_gain']))
            success_7d = sum(1 for token in tokens_7d 
                            if float(token['gain_percentage']) >= float(token['predicted_gain']))
            
            # Calculate success rates
            rate_24h = (success_24h/len(tokens_24h)*100) if tokens_24h else 0
            rate_7d = (success_7d/len(tokens_7d)*100) if tokens_7d else 0
            
            # Calculate average gain for successful predictions
            successful_gains = [
                float(token['gain_percentage']) 
                for token in tokens_24h + tokens_7d 
                if float(token['gain_percentage']) >= float(token['predicted_gain'])
            ]
            avg_gain = sum(successful_gains) / len(successful_gains) if successful_gains else 0
            
            # Start building tweet
            tweet = """🎯 Prediction Accuracy Update

📊 Performance:
• 24h: {:.0f}% ({}/{} calls)
• 7d: {:.0f}% ({}/{} calls)
• Average Win: +{:.1f}%
• Total: {} predictions

✅ Recent Hits:""".format(
                rate_24h, success_24h, len(tokens_24h),
                rate_7d, success_7d, len(tokens_7d),
                avg_gain,
                len(tokens_24h) + len(tokens_7d)
            )
            
            # Sort by predicted gain and show predicted vs actual for top 4
            recent_hits = sorted(
                [t for t in tokens_24h if float(t['gain_percentage']) >= float(t['predicted_gain'])],
                key=lambda x: float(x['predicted_gain']),
                reverse=True
            )[:4]
            
            # If no hits, show message
            if not recent_hits:
                tweet += "\nNo successful predictions in last 24h"
            else:
                for token in recent_hits:
                    predicted = float(token['predicted_gain'])
                    actual = float(token['gain_percentage'])
                    tweet += f"\n• ${token['symbol']}: +{predicted:.1f}% → +{actual:.1f}%"
                
            # Get random tags
            tags = self._get_random_tags(3)
            tweet += f"\n\n{tags}"
            
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

            # Sort tokens by gain
            tokens = sorted(
                history_data['tokens'],
                key=lambda x: float(x.get('gain_percentage', 0)),
                reverse=True
            )

            # Calculate stats
            total_tokens = len(tokens)
            winners = len([t for t in tokens if float(t.get('gain_percentage', 0)) > 0])
            success_rate = (winners / total_tokens * 100) if total_tokens > 0 else 0
            avg_gain = sum(float(t.get('gain_percentage', 0)) for t in tokens) / total_tokens if total_tokens > 0 else 0
            best_gain = max(float(t.get('gain_percentage', 0)) for t in tokens) if tokens else 0

            # Debug stats
            print("\nDebug - Winners:")
            for token in tokens[:7]:
                print(f"{token['symbol']}: {token['gain_percentage']}%")

            print("\nDebug - Stats:")
            print(f"Total tokens: {total_tokens}")
            print(f"Winners: {winners}")
            print(f"Success rate: {success_rate:.1f}%")
            print(f"Avg gain: {avg_gain:.1f}%")
            print(f"Best gain: {best_gain:.1f}%")

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
                top_performers.append(f"{icon} ${token['symbol']} (+{gain:.1f}%)")

            # Format tweet
            tweet = f"""🏆 Weekly Hall of Fame

{chr(10).join(top_performers)}

📈 Weekly Stats:
• Success Rate: {success_rate:.1f}% ({winners}/{total_tokens})
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
        'symbol': 'TEST',
        'first_mention_price': 1.0,
        'current_price': 1.25,
        'first_mention_volume_24h': 1000000,
        'volume_24h': 1500000,
        'volume_mcap_ratio': 0.75,
        'first_mention_date': '2024-01-01',
        'similar_vmc_tokens': [
            {'symbol': 'TKN1', 'volume_mcap_ratio': 0.72, 'price_change_24h': 15.5},
            {'symbol': 'TKN2', 'volume_mcap_ratio': 0.78, 'price_change_24h': 8.2},
            {'symbol': 'TKN3', 'volume_mcap_ratio': 0.71, 'price_change_24h': 12.3},
            {'symbol': 'TKN4', 'volume_mcap_ratio': 0.76, 'price_change_24h': -5.1},
            {'symbol': 'TKN5', 'volume_mcap_ratio': 0.79, 'price_change_24h': 3.2}
        ]
    }

def get_mock_history():
    """Get mock history data for testing"""
    return {
        'success_rate': 78,
        'avg_gain': 35,
        'best_gain': 45,
        'top_performers': [
            {'symbol': 'TKN1', 'gain': 35.0},
            {'symbol': 'TKN2', 'gain': 32.5},
            {'symbol': 'TKN3', 'gain': 28.7},
            {'symbol': 'TKN4', 'gain': 25.3},
            {'symbol': 'TKN5', 'gain': 22.1},
            {'symbol': 'TKN6', 'gain': 18.9},
            {'symbol': 'TKN7', 'gain': 15.4}
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
    formatter = PerformanceCompareFormatter()
    tweet = formatter.format_tweet(get_mock_data())
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}")

def test_success_rate():
    """Test success rate formatter"""
    print("\n=== Testing SuccessRateFormatter ===")
    formatter = SuccessRateFormatter()
    tweet = formatter.format_tweet(get_mock_history())
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}")

def test_prediction_accuracy():
    """Test prediction accuracy formatter"""
    print("\n=== Testing PredictionAccuracyFormatter ===\n")
    formatter = PredictionAccuracyFormatter()
    
    print("Test with many successful predictions:")
    mock_data = get_mock_prediction_data()
    tweet = formatter.format_tweet(mock_data)
    if tweet:
        print(f"Tweet ({len(tweet)} chars):")
        print(tweet)
    else:
        print("Not enough successful predictions")
    
    print("\nTest with few successful predictions:")
    mock_data = get_mock_prediction_data_few_success()
    tweet = formatter.format_tweet(mock_data)
    if tweet:
        print(f"Tweet ({len(tweet)} chars):")
        print(tweet)
    else:
        print("Not enough successful predictions")

def test_winners_recap():
    """Test winners recap formatter"""
    print("\n=== Testing WinnersRecapFormatter ===")
    formatter = WinnersRecapFormatter()
    tweet = formatter.format_tweet(get_mock_history())
    print(f"\nTweet ({len(tweet)} chars):\n{tweet}")

if __name__ == "__main__":
    # Run tests one by one
    test_performance_compare()
    test_success_rate()
    test_prediction_accuracy()
    test_winners_recap()
