"""Performance-focused tweet formatters"""

from datetime import datetime, timedelta, timezone
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
        
    def _get_current_time(self) -> datetime:
        """Get current time as timezone-aware datetime"""
        return datetime.now(timezone.utc)

    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to timezone-aware datetime"""
        try:
            if 'T' in date_str:
                # Full ISO format
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Date only format
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.replace(tzinfo=timezone.utc)
        except Exception as e:
            logging.error(f"Error parsing date {date_str}: {e}")
            return self._get_current_time()
        
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
    """Shows performance comparison between current and entry price"""
    
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
        # Use UTC timezone for consistency
        recent[symbol] = self._get_current_time().isoformat()
        
        # Clean up old entries
        cutoff = self._get_current_time() - timedelta(hours=self.rotation_hours)
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
        hours_ago = (self._get_current_time() - tweet_time).total_seconds() / 3600
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
        """Format tweet showing performance comparison"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None
                
            # Get token details
            token = history_data['tokens'][0] if isinstance(history_data['tokens'], list) else None
            if not token or not isinstance(token, dict):
                return None
                
            symbol = token.get('symbol', '')
            first_mention_price = float(token.get('first_mention_price', 0))
            current_price = float(token.get('current_price', 0))
            max_gain = float(token.get('max_gain_7d', 0))
            volume_24h = float(token.get('volume_24h', 0))
            mcap = float(token.get('current_mcap', 0))
            first_mention_date = self._parse_date(token.get('first_mention_date', ''))
            
            if not all([symbol, first_mention_price, current_price, first_mention_date]):
                return None
                
            # Calculate metrics
            gain_percentage = ((current_price - first_mention_price) / first_mention_price) * 100
            hours_ago = (self._get_current_time() - first_mention_date).total_seconds() / 3600
            volume_mcap_ratio = (volume_24h / mcap * 100) if mcap > 0 else 0
            
            # Format prices nicely
            def format_price(price: float) -> str:
                if price < 0.0001:
                    return f"${price:.10f}"
                elif price < 0.01:
                    return f"${price:.6f}"
                elif price < 1:
                    return f"${price:.4f}"
                else:
                    return f"${price:.2f}"
            
            # Format volume/mcap nicely
            def format_amount(amount: float) -> str:
                if amount >= 1_000_000_000:
                    return f"{amount/1_000_000_000:.1f}B"
                elif amount >= 1_000_000:
                    return f"{amount/1_000_000:.1f}M"
                elif amount >= 1_000:
                    return f"{amount/1_000:.1f}K"
                else:
                    return f"{amount:.1f}"
            
            # Build tweet
            tweet = f"""✨ Special Highlight ✨
🔄 ${symbol} Spotted {hours_ago:.1f}h ago!

📊 Performance Update:
• Spotted at: {format_price(first_mention_price)}
• Current Price: {format_price(current_price)} ({'+' if gain_percentage > 0 else ''}{gain_percentage:.2f}%)
• Best Gain: +{max_gain:.2f}% (7d high)

📊 Volume & Market Cap:
• 24h Vol: {format_amount(volume_24h)}
• MCap: {format_amount(mcap)}
• V/MC: +{volume_mcap_ratio:.2f}%"""
            
            # Get other tokens to mention
            other_tokens = []
            for t in history_data.get('tokens', [])[1:]:  # Skip first token as it's our main one
                if isinstance(t, dict):
                    other_symbol = t.get('symbol', '')
                    if other_symbol and other_symbol != symbol:
                        other_tokens.append(other_symbol)
            
            # Add special mentions if we have other tokens
            if other_tokens:
                mentions = ' '.join(f"${s}" for s in other_tokens[:4])  # Show up to 4 other tokens
                tweet += f"\n\n✨ Special mentions: {mentions}"
            
            # Add random hashtags
            tweet += f"\n\n{self._get_random_tags()}"
            
            return tweet
            
        except Exception as e:
            logging.error(f"Error formatting performance compare tweet: {e}")
            return None

class SuccessRateFormatter(BasePerformanceFormatter):
    """Shows 48h performance metrics."""
    
    def format_stats(self, total_tokens: int, successful_tokens: int, avg_gain: float, best_gain: float) -> str:
        """Format the statistics section of the tweet"""
        return (
            "📈 48h Stats:\n"
            f"• Tracked {total_tokens} Gems\n"
            f"• Avg Gain: +{avg_gain:.1f}%\n"
            f"💎 {successful_tokens}/{total_tokens} Certified Moonshots"
        )

    def format_tweet(self, history_data: Dict) -> str:
        """Format a 48h performance tweet"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None

            # Filter out non-dict tokens and sort by gain
            tokens = [t for t in history_data['tokens'] if isinstance(t, dict)]
            
            # Filter for last 48h and calculate success
            filtered_tokens = []
            success_threshold = 5.0  # Minimum % gain to count as success
            
            current_time = self._get_current_time()
            
            for t in tokens:
                gain_percentage = float(t.get('gain_percentage', 0))
                max_gain = float(t.get('max_gain_7d', 0))
                first_mention = self._parse_date(t.get('first_mention_date', ''))
                hours_ago = (current_time - first_mention).total_seconds() / 3600
                
                # Only look at last 48h
                if hours_ago > 48:  # 48 hours
                    continue
                    
                # Check if token hit success threshold
                t['is_success'] = gain_percentage >= success_threshold
                filtered_tokens.append(t)
            
            tokens = filtered_tokens
            # Sort by current gain percentage
            tokens = sorted(
                tokens,
                key=lambda x: float(x.get('gain_percentage', 0)),
                reverse=True
            )

            if not tokens:
                return None

            # Calculate stats
            total_tokens = len(tokens)
            winners = len([t for t in tokens if t.get('is_success', False)])
            
            # Calculate average gain
            gains = [float(t.get('gain_percentage', 0)) for t in tokens]
            avg_gain = sum(gains) / len(gains) if gains else 0

            # Format top performers
            top_movers = []
            for i, token in enumerate(tokens[:7]):
                gain = float(token.get('gain_percentage', 0))
                symbol = token.get('symbol', 'UNKNOWN')
                
                if i == 0:
                    icon = "🥇"
                    suffix = " 🌙" if gain > 0 else ""
                elif i == 1:
                    icon = "🥈"
                    suffix = " 🚀" if gain > 0 else ""
                elif i == 2:
                    icon = "🥉"
                    suffix = " 🚀" if gain > 0 else ""
                else:
                    icon = f"{i+1}️⃣"
                    suffix = ""
                    
                top_movers.append(f"{icon} ${symbol}: +{gain:.1f}%{suffix}")
            
            # Format stats
            stats = self.format_stats(total_tokens, winners, avg_gain, max(gains) if gains else 0)

            # Format tweet
            tweet = f"""📊 48h Gem Highlights

Top Movers:
{chr(10).join(top_movers)}

{stats}"""

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
            '#Crypto', '#BSC', '#100x', '#GemAlert', '#DeFi',
            '#Altcoins', '#CryptoGems', '#Trading'
        ]
        self.common_cashtags = ['$BTC', '$ETH', '$BNB', '$SOL', '$AVAX']
        
    def _get_random_tags(self, count: int = 3) -> str:
        """Get random mix of hashtags and cashtags"""
        hashtags = random.sample(self.common_hashtags, min(2, count))
        cashtags = random.sample(self.common_cashtags, min(1, count))
        tags = hashtags + cashtags
        random.shuffle(tags)
        return ' '.join(tags[:count])
        
    def _get_gain_emoji(self, gain: float) -> str:
        """Get appropriate emoji for gain percentage"""
        if gain >= 20:
            return "🌙"  # Moon for big gains
        elif gain >= 10:
            return "🚀"  # Rocket for good gains
        elif gain >= 5:
            return "⭐"  # Star for decent gains
        return ""
        
    def format_tweet(self, history_data: Dict) -> str:
        """Format tweet showing prediction accuracy and gain progression"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None
                
            # Filter out non-dict tokens
            tokens = [t for t in history_data['tokens'] if isinstance(t, dict)]
            
            if not tokens:
                return None
                
            current_time = self._get_current_time()
            
            # Get recent winners (any positive gain)
            winners = []
            for t in tokens:
                gain_percentage = float(t.get('gain_percentage', 0))
                max_gain = float(t.get('max_gain_7d', 0))
                first_mention = self._parse_date(t.get('first_mention_date', ''))
                
                if gain_percentage > 0:
                    winners.append({
                        'symbol': t.get('symbol', ''),
                        'gain': gain_percentage,
                        'max_gain': max_gain,
                        'first_mention': first_mention
                    })
            
            # Sort winners by current gain
            winners.sort(key=lambda x: x['gain'], reverse=True)
            
            # Get fresh calls (last 24h, not in winners)
            fresh_calls = []
            for t in tokens:
                symbol = t.get('symbol', '')
                first_mention = self._parse_date(t.get('first_mention_date', ''))
                hours_ago = (current_time - first_mention).total_seconds() / 3600
                
                # Skip if already in winners
                if any(w['symbol'] == symbol for w in winners):
                    continue
                    
                if hours_ago <= 24:
                    fresh_calls.append(symbol)
            
            # Get watchlist (not in winners or fresh calls, good volume)
            watchlist = []
            for t in tokens:
                symbol = t.get('symbol', '')
                volume = float(t.get('volume_24h', 0))
                mcap = float(t.get('current_mcap', 0))
                
                # Skip if already included
                if any(w['symbol'] == symbol for w in winners) or symbol in fresh_calls:
                    continue
                    
                # Add if good volume/mcap ratio
                if mcap > 0 and (volume / mcap) > 0.1:  # 10% volume/mcap ratio
                    watchlist.append(symbol)
            
            # Format tweet
            tweet = "🔄 Prediction Accuracy Update\n\n"
            
            # Recent Winners section
            if winners:
                tweet += "📈 Recent Winners:\n"
                for i, w in enumerate(winners[:3]):  # Top 3 winners
                    if i == 0:
                        medal = "🥇"
                    elif i == 1:
                        medal = "🥈"
                    else:
                        medal = "🥉"
                        
                    gain_emoji = self._get_gain_emoji(w['gain'])
                    tweet += f"{medal} ${w['symbol']}: +{w['gain']:.1f}% → +{w['max_gain']:.1f}% {gain_emoji}\n"
                tweet += "\n"
            
            # Fresh Calls section
            if fresh_calls:
                tweet += "🔥 Fresh Calls (24h):\n"
                symbols = ' '.join(f"${s}" for s in fresh_calls[:4])  # Top 4 fresh calls
                tweet += f"{symbols}\n"
                tweet += "Volume spikes detected! 👀\n\n"
            
            # Watchlist section
            if watchlist:
                tweet += "💎 Watchlist:\n"
                top_picks = ' '.join(f"${s}" for s in watchlist[:4])  # Top 4 watchlist
                tweet += f"Top picks: {top_picks}\n"
            
            # Total monitored
            tweet += f"Monitoring {len(tokens)} potential gems! 🎯\n\n"
            
            # Add random mix of hashtags
            tweet += self._get_random_tags()
            
            return tweet
            
        except Exception as e:
            logging.error(f"Error formatting prediction accuracy tweet: {e}")
            return None

class WinnersRecapFormatter(BasePerformanceFormatter):
    """Shows weekly winners and stats."""

    def format_stats(self, total_tokens: int, successful_tokens: int, avg_gain: float, best_gain: float) -> str:
        """Format the statistics section of the tweet"""
        success_rate = (successful_tokens / total_tokens) * 100 if total_tokens > 0 else 0
        
        if success_rate < 50:
            return (
                "📊 Overall:\n"
                f"• {successful_tokens} Verified Gems from {total_tokens}\n"
                f"• Avg Gain: +{avg_gain:.1f}%\n"
                f"• Best: +{best_gain:.1f}%"
            )
        else:
            return (
                "📊 Overall:\n"
                f"• {successful_tokens}/{total_tokens} Winners\n"
                f"• {success_rate:.0f}% Success Rate\n"
                f"• Best: +{best_gain:.1f}%"
            )

    def format_tweet(self, history_data: Dict) -> str:
        """Format a weekly winners recap tweet"""
        try:
            if not history_data or not history_data.get('tokens'):
                return None

            # Filter out non-dict tokens and sort by gain
            tokens = [t for t in history_data['tokens'] if isinstance(t, dict)]
            
            # Weekly stats:
            # 1. Look at last 7 days of data
            # 2. Use max gain achieved in the period
            filtered_tokens = []
            success_threshold = 10.0  # Minimum % gain to count as success
            
            current_time = self._get_current_time()
            
            for t in tokens:
                gain_percentage = float(t.get('gain_percentage', 0))
                max_gain = float(t.get('max_gain_7d', 0))
                first_mention = self._parse_date(t.get('first_mention_date', ''))
                hours_ago = (current_time - first_mention).total_seconds() / 3600
                
                # Only look at last 7 days
                if hours_ago > 168:  # 7 days * 24 hours
                    continue
                    
                # Count success based on max gain achieved
                t['is_success'] = max_gain >= success_threshold
                t['display_gain'] = max_gain  # Use max gain for display
                filtered_tokens.append(t)
            
            tokens = filtered_tokens
            # Sort by max 7d gain
            tokens = sorted(
                tokens,
                key=lambda x: float(x.get('max_gain_7d', 0)),
                reverse=True
            )

            if not tokens:
                return None

            # Calculate stats
            total_tokens = len(tokens)
            winners = len([t for t in tokens if t.get('is_success', False)])
            
            # Calculate average of max gains
            gains = [float(t.get('max_gain_7d', 0)) for t in tokens]
            avg_gain = sum(gains) / len(gains) if gains else 0
            best_gain = max(gains) if gains else 0

            # Format top performers
            top_movers = []
            for i, token in enumerate(tokens[:7]):
                gain = float(token.get('gain_percentage', 0))
                max_gain = float(token.get('max_gain_7d', 0))
                symbol = token.get('symbol', 'UNKNOWN')
                
                # Show both current and max gain if they're different
                gain_text = f"+{max_gain:.1f}%" if abs(gain - max_gain) < 0.1 else f"+{gain:.1f}% → +{max_gain:.1f}%"
                
                if i == 0:
                    icon = "🥇"
                    suffix = " 🌙" if max_gain >= 20 else " 🚀" if max_gain >= 10 else ""
                elif i == 1:
                    icon = "🥈"
                    suffix = " 🌙" if max_gain >= 20 else " 🚀" if max_gain >= 10 else ""
                elif i == 2:
                    icon = "🥉"
                    suffix = " 🌙" if max_gain >= 20 else " 🚀" if max_gain >= 10 else ""
                else:
                    icon = f"{i+1}️⃣"
                    suffix = " 🌙" if max_gain >= 20 else " 🚀" if max_gain >= 10 else ""
                
                top_movers.append(f"{icon} ${symbol}: {gain_text}{suffix}")

            # Format tweet
            tweet = (
                "🏆 Weekly Winners Recap\n\n"
                "Top Performers:\n"
                f"{chr(10).join(top_movers)}\n\n"
            )
            
            # Add stats section
            tweet += self.format_stats(total_tokens, winners, avg_gain, best_gain)

            # Add special mentions if we have any
            special_mentions = [t.get('symbol', '') for t in tokens[7:11]] if len(tokens) > 7 else []
            if special_mentions:
                tweet += f"\n\n👥 Special mentions: ${' $'.join(special_mentions)}"

            # Add hashtags
            tweet += "\n\n#Crypto #BSC #100x $BNB $ETH"

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
