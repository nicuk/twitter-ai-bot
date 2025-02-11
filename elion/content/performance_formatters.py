"""Performance-focused tweet formatters"""

from datetime import datetime, timedelta
from typing import Dict, List
import random
import sys
import os
import json

# Add parent directory to path so we can import elion modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from elion.content.tweet_formatters import TweetFormatters

class BasePerformanceFormatter(TweetFormatters):
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
        """Optimize tweet length to be between 210-280 characters.
        
        Args:
            tweet: Base tweet to optimize
            data: Data dictionary used to generate the tweet
            format_type: Type of tweet format
            
        Returns:
            Optimized tweet with length between 210-280 characters
        """
        # If tweet is already in range, return as is
        if self.MIN_TWEET_LENGTH <= len(tweet) <= self.MAX_TWEET_LENGTH:
            return tweet
            
        # If tweet is too long, truncate it
        if len(tweet) > self.MAX_TWEET_LENGTH:
            return tweet[:self.MAX_TWEET_LENGTH-3] + "..."
            
        # If tweet is too short, add relevant insight
        insights = {
            'performance_compare': [
                "\n\n💡 Strong momentum with increasing volume",
                "\n\n💡 Pattern suggests potential continuation",
                "\n\n💡 Technical indicators remain bullish",
                "\n\n💡 Similar setups had positive outcomes"
            ],
            'success_rate': [
                "\n\n💡 Consistent performance across cycles",
                "\n\n💡 Strategy shows improving accuracy",
                "\n\n💡 Risk management remains key focus",
                "\n\n💡 Data-driven approach yields results"
            ],
            'prediction_accuracy': [
                "\n\n💡 Pattern recognition improving",
                "\n\n💡 Models show high confidence",
                "\n\n💡 Historical accuracy validates approach",
                "\n\n💡 Continuous model refinement"
            ],
            'winners_recap': [
                "\n\n💡 Winners show strong fundamentals",
                "\n\n💡 Volume profile remains healthy",
                "\n\n💡 Technical setup looks promising",
                "\n\n💡 Market sentiment stays positive"
            ]
        }
        
        if format_type in insights:
            # Get random insight for this type
            available_insights = insights[format_type]
            insight = random.choice(available_insights)
            
            # Add insight if it fits
            if len(tweet) + len(insight) <= self.MAX_TWEET_LENGTH:
                return tweet + insight
                
        return tweet

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

    def format_tweet(self, token_data: Dict) -> str:
        """Format a performance comparison tweet"""
        if not token_data or not token_data.get('tokens'):
            return None
            
        # Get the best performing token
        tokens = sorted(token_data['tokens'], key=lambda x: float(x['gain_percentage']), reverse=True)
        if not tokens:
            return None
            
        token = tokens[0]  # Get the best performer
        
        # Calculate volume change
        volume_24h = float(token.get('volume_24h', 0))
        mcap = float(token.get('current_mcap', 0))
        vmc_ratio = (volume_24h / mcap * 100) if mcap > 0 else 0
        
        # Base tweet with formatted values
        tweet = f"""🤖 Performance: ${token['symbol']}

💰 Price Action:
• Entry: ${self._format_price(float(token['first_mention_price']))}
• Current: ${self._format_price(float(token['current_price']))}
• Change: {self._format_percentage(float(token['gain_percentage']))}

📈 Volume & Market Cap:
• 24h Vol: {self._format_volume(volume_24h)}
• MCap: {self._format_volume(mcap)}
• V/MC: {self._format_percentage(vmc_ratio)}"""

        # Add pattern suggestion based on metrics
        if float(token['gain_percentage']) > 20 and vmc_ratio > 10:
            tweet += "\n\n💡 Strong momentum with high volume"
        elif float(token['gain_percentage']) > 10:
            tweet += "\n\n💡 Showing upward momentum"
        elif vmc_ratio > 20:
            tweet += "\n\n💡 High volume relative to market cap"
            
        return tweet

class SuccessRateFormatter(BasePerformanceFormatter):
    """Shows overall performance metrics."""
    
    def _get_rank_emoji(self, rank: int) -> str:
        """Get emoji for rank"""
        if rank == 1:
            return "1.💎"  # Diamond for 1st
        elif rank == 2:
            return "2.👑"  # Crown for 2nd
        elif rank == 3:
            return "3.⭐"  # Star for 3rd
        elif rank <= 5:
            return f"{rank}.🔥"  # Fire for 4th-5th
        else:
            return f"{rank}.⚡"  # Lightning for others
    
    def format_tweet(self, token_data: Dict) -> str:
        """Format a success rate tweet"""
        if not token_data or not token_data.get('tokens'):
            return None
            
        # Calculate stats
        tokens = token_data['tokens']
        winners = [t for t in tokens if float(t['gain_percentage']) > 0]
        
        success_rate = (len(winners) / len(tokens) * 100) if tokens else 0
        avg_gain = sum(float(t['gain_percentage']) for t in winners) / len(winners) if winners else 0
        best_gain = max((float(t['gain_percentage']) for t in winners), default=0)
        
        tweet = f"""📊 48h Performance Update

🏆 Top Performers:"""
        
        # Add top 5 winners with emojis
        for i, token in enumerate(sorted(winners, key=lambda x: float(x['gain_percentage']), reverse=True)[:5]):
            emoji = ['💎', '👑', '⭐', '🔥', '⚡'][i]
            gain = float(token['gain_percentage'])
            tweet += f"\n{i+1}.{emoji} ${token['symbol']} (+{gain:.1f}%)"
        
        # Add stats
        tweet += f"""

📈 48h Stats:
• Success Rate: {success_rate:.0f}%
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""

        return tweet

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
        if not history_data or not history_data.get('tokens'):
            return None
            
        # Calculate real success rates from history
        now = datetime.now()
        tokens = history_data['tokens']
        
        # Count successes (tokens with positive gain)
        success_24h = sum(1 for token in tokens if float(token['gain_percentage']) > 0)
        total_24h = len(tokens)
        
        # Get 7d data from performance analysis
        perf_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'performance_analysis.json')
        with open(perf_file, 'r') as f:
            performance_data = json.load(f)
        
        success_7d = performance_data['summary']['tokens_with_gains']['7d']
        total_7d = performance_data['summary']['total_tokens_tracked']
        
        # Calculate success rates
        rate_24h = (success_24h/total_24h*100) if total_24h > 0 else 0
        rate_7d = (success_7d/total_7d*100) if total_7d > 0 else 0
        
        # Get top winners (only positive gains)
        winners = sorted(
            [
                (token['symbol'], float(token['gain_percentage']))
                for token in tokens
                if float(token['gain_percentage']) > 0
            ],
            key=lambda x: x[1],
            reverse=True
        )
        
        # Calculate average gain for successful predictions only
        successful_gains = [
            float(token['gain_percentage']) 
            for token in tokens 
            if float(token['gain_percentage']) > 0
        ]
        avg_gain = sum(successful_gains) / len(successful_gains) if successful_gains else 0
        
        tweet = f"""🎯 Prediction Accuracy Update

📊 Success Rates:
• Last 24h: {rate_24h:.0f}% ({success_24h}/{total_24h} calls)
• Last 7d: {rate_7d:.0f}% ({success_7d}/{total_7d} calls)
• Average Win: {avg_gain:+.1f}%

✅ Recent Winners:"""

        # Add up to 5 winners - medals for top 3, stars for 4th and 5th
        medals = ['🥇', '🥈', '🥉', '⭐', '⭐']
        for i, ((symbol, gain), medal) in enumerate(zip(winners[:5], medals)):
            tweet += f"\n{i+1}.{medal} ${symbol} (+{gain:.1f}%)"
            
        # If no winners, show message
        if not winners:
            tweet += "\nNo winning trades in last 24h"
            
        # Get random tags
        tags = self._get_random_tags(3)
        tweet += f"\n\n{tags}"
        
        return tweet

class WinnersRecapFormatter(BasePerformanceFormatter):
    """Shows weekly winners with key stats."""
    
    def __init__(self):
        """Initialize with common hashtags and cashtags"""
        super().__init__()
        self.common_hashtags = [
            '#Trading', '#Crypto', '#Gains', '#DeFi', '#Altcoins',
            '#CryptoTrading', '#Bitcoin', '#Ethereum', '#Blockchain',
            '#CryptoNews', '#Binance', '#Coinbase', '#CryptoSignals'
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
        """Format winners recap tweet"""
        if not history_data:
            return None
            
        # Sort winners by gain
        winners = sorted(
            [
                {
                    'symbol': token['symbol'].lstrip('$'),  # Remove any existing $ to avoid doubles
                    'gain': float(token['gain_percentage']),
                    'peak': float(token.get('max_gain_7d', token['gain_percentage']))
                }
                for token in history_data['tokens']
                if float(token['gain_percentage']) > 0  # Only include winners
            ],
            key=lambda x: x['gain'],
            reverse=True
        )
        
        print("\nDebug - Winners:")
        for w in winners[:5]:
            print(f"{w['symbol']}: {w['gain']}%")
        
        if not winners:
            return None
            
        # Calculate stats
        gains = [w['gain'] for w in winners]
        avg_gain = sum(gains) / len(gains) if gains else 0
        best_gain = max(gains) if gains else 0
        success_count = len(winners)
        total_count = len(history_data['tokens'])
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
            
        print(f"\nDebug - Stats:")
        print(f"Total tokens: {total_count}")
        print(f"Winners: {success_count}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Avg gain: {avg_gain:.1f}%")
        print(f"Best gain: {best_gain:.1f}%")
        
        # Start with base tweet format
        base_tweet = """🏆 Weekly Winners Recap

Top Performers:"""
        
        # Add winners with emojis
        emojis = ['💎', '👑', '⭐', '💫', '✨', '🔥', '🚀', '💰', '🌟', '✅']
        for i, winner in enumerate(winners[:5]):  # Only show top 5 winners
            winner_line = f"\n{i+1}.{emojis[i % len(emojis)]} ${winner['symbol']} (+{winner['gain']:.1f}%)"
            base_tweet += winner_line
            
        # Add stats section
        stats_section = f"""

📈 Weekly Stats:
• Success Rate: {success_rate:.0f}%
• Avg Gain: +{avg_gain:.1f}%
• Best: +{best_gain:.1f}%"""
        
        base_tweet += stats_section
        
        # Get random tags
        tags = self._get_random_tags(3)
        base_tweet += f"\n\n{tags}"
        
        return base_tweet

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
