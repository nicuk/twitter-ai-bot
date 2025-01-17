"""
Market analysis and data processing for Elion AI
"""

import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from .data_storage import DataStorage

class MarketAnalysis:
    def __init__(self):
        self.rss_feeds = [
            'https://cointelegraph.com/rss',
            'https://cryptonews.com/news/feed/',
            'https://decrypt.co/feed',
        ]
        
        # Add gem tracking
        self.storage = DataStorage()  # Use existing storage
        
        self.key_accounts = [
            '@VitalikButerin',
            '@cz_binance',
            '@SBF_FTX',
            '@elonmusk'
        ]
        
        # Technical analysis settings
        self.indicators = {
            'rsi': {
                'oversold': 30,
                'overbought': 70,
                'timeframes': ['1h', '4h', '1d']
            },
            'ma_crossovers': {
                'fast': 20,
                'slow': 50,
                'timeframes': ['4h', '1d']
            },
            'volume_analysis': {
                'significant_change': 2.0,  # 2x normal volume
                'timeframes': ['1h', '4h', '1d']
            }
        }
        
        # Whale tracking settings
        self.whale_settings = {
            'min_eth_balance': 1000,
            'min_btc_balance': 100,
            'significant_transfer': 1000000,  # $1M USD
            'tracking_period': 24 * 60 * 60  # 24 hours
        }
        
        # Smart contract monitoring
        self.contract_monitors = {
            'dex': {
                'uniswap_v3': '0x...',
                'sushiswap': '0x...',
                'pancakeswap': '0x...'
            },
            'lending': {
                'aave': '0x...',
                'compound': '0x...'
            },
            'gaming': {
                'axie': '0x...',
                'sandbox': '0x...',
                'illuvium': '0x...'
            }
        }
        
        # Market sentiment indicators
        self.sentiment_sources = {
            'fear_greed_index': 'https://api.alternative.me/fng/',
            'social_sentiment': {
                'twitter': self.key_accounts,
                'reddit': ['r/CryptoCurrency', 'r/Bitcoin', 'r/ethereum']
            },
            'trend_indicators': {
                'google_trends': ['bitcoin', 'ethereum', 'crypto', 'web3'],
                'twitter_trends': ['#Bitcoin', '#Ethereum', '#Crypto']
            }
        }
    
    def analyze_market_conditions(self):
        """Analyze overall market conditions"""
        try:
            conditions = {
                'technical': self._analyze_technical_indicators(),
                'onchain': self._analyze_onchain_metrics(),
                'sentiment': self._analyze_market_sentiment(),
                'whale_activity': self._track_whale_movements(),
                'smart_contracts': self._monitor_smart_contracts()
            }
            
            # Determine overall market state
            bullish_signals = 0
            bearish_signals = 0
            
            for category, signals in conditions.items():
                if signals['bias'] == 'bullish':
                    bullish_signals += 1
                elif signals['bias'] == 'bearish':
                    bearish_signals += 1
            
            # Calculate overall bias
            if bullish_signals > bearish_signals:
                market_bias = 'bullish'
            elif bearish_signals > bullish_signals:
                market_bias = 'bearish'
            else:
                market_bias = 'neutral'
            
            return {
                'bias': market_bias,
                'conditions': conditions,
                'timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error analyzing market conditions: {e}")
            return None
    
    def _analyze_technical_indicators(self):
        """Analyze technical indicators across timeframes"""
        try:
            analysis = {
                'rsi': self._check_rsi_conditions(),
                'ma_crossovers': self._check_ma_crossovers(),
                'volume': self._analyze_volume_patterns()
            }
            
            # Determine technical bias
            bullish_signals = sum(1 for k, v in analysis.items() if v['bias'] == 'bullish')
            bearish_signals = sum(1 for k, v in analysis.items() if v['bias'] == 'bearish')
            
            if bullish_signals > bearish_signals:
                bias = 'bullish'
            elif bearish_signals > bullish_signals:
                bias = 'bearish'
            else:
                bias = 'neutral'
            
            return {
                'bias': bias,
                'signals': analysis
            }
            
        except Exception as e:
            print(f"Error in technical analysis: {e}")
            return None
    
    def _analyze_onchain_metrics(self):
        """Analyze on-chain metrics"""
        try:
            metrics = {
                'network_activity': self._analyze_network_activity(),
                'wallet_distribution': self._analyze_wallet_distribution(),
                'defi_metrics': self._analyze_defi_activity()
            }
            
            # Calculate on-chain bias
            active_wallets_trend = metrics['network_activity']['active_wallets_trend']
            whale_accumulation = metrics['wallet_distribution']['whale_accumulation']
            defi_tvl_trend = metrics['defi_metrics']['tvl_trend']
            
            if all(x == 'up' for x in [active_wallets_trend, whale_accumulation, defi_tvl_trend]):
                bias = 'bullish'
            elif all(x == 'down' for x in [active_wallets_trend, whale_accumulation, defi_tvl_trend]):
                bias = 'bearish'
            else:
                bias = 'neutral'
            
            return {
                'bias': bias,
                'metrics': metrics
            }
            
        except Exception as e:
            print(f"Error analyzing on-chain metrics: {e}")
            return None
    
    def _analyze_market_sentiment(self):
        """Analyze market sentiment from various sources"""
        try:
            sentiment = {
                'fear_greed': self._get_fear_greed_index(),
                'social': self._analyze_social_sentiment(),
                'trends': self._analyze_trend_indicators()
            }
            
            # Calculate overall sentiment
            if sentiment['fear_greed'] > 60 and sentiment['social']['bias'] == 'positive':
                bias = 'bullish'
            elif sentiment['fear_greed'] < 40 and sentiment['social']['bias'] == 'negative':
                bias = 'bearish'
            else:
                bias = 'neutral'
            
            return {
                'bias': bias,
                'sentiment': sentiment
            }
            
        except Exception as e:
            print(f"Error analyzing market sentiment: {e}")
            return None
    
    def _track_whale_movements(self):
        """Track and analyze whale wallet movements"""
        try:
            movements = {
                'eth_whales': self._track_eth_whales(),
                'btc_whales': self._track_btc_whales(),
                'token_whales': self._track_token_whales()
            }
            
            # Analyze whale behavior
            accumulation_count = 0
            distribution_count = 0
            
            for whale_type, data in movements.items():
                if data['behavior'] == 'accumulating':
                    accumulation_count += 1
                elif data['behavior'] == 'distributing':
                    distribution_count += 1
            
            if accumulation_count > distribution_count:
                bias = 'bullish'
            elif distribution_count > accumulation_count:
                bias = 'bearish'
            else:
                bias = 'neutral'
            
            return {
                'bias': bias,
                'movements': movements
            }
            
        except Exception as e:
            print(f"Error tracking whale movements: {e}")
            return None
    
    def _monitor_smart_contracts(self):
        """Monitor smart contract activity"""
        try:
            activity = {
                'dex': self._monitor_dex_activity(),
                'lending': self._monitor_lending_activity(),
                'gaming': self._monitor_gaming_activity()
            }
            
            # Analyze contract activity
            bullish_sectors = 0
            bearish_sectors = 0
            
            for sector, data in activity.items():
                if data['trend'] == 'increasing':
                    bullish_sectors += 1
                elif data['trend'] == 'decreasing':
                    bearish_sectors += 1
            
            if bullish_sectors > bearish_sectors:
                bias = 'bullish'
            elif bearish_sectors > bullish_sectors:
                bias = 'bearish'
            else:
                bias = 'neutral'
            
            return {
                'bias': bias,
                'activity': activity
            }
            
        except Exception as e:
            print(f"Error monitoring smart contracts: {e}")
            return None
    
    def _check_rsi_conditions(self):
        """Check RSI conditions across timeframes"""
        # Implementation will pull data from API
        pass
    
    def _check_ma_crossovers(self):
        """Check moving average crossovers"""
        # Implementation will pull data from API
        pass
    
    def _analyze_volume_patterns(self):
        """Analyze volume patterns"""
        # Implementation will pull data from API
        pass
    
    def _analyze_network_activity(self):
        """Analyze blockchain network activity"""
        # Implementation will pull data from API
        pass
    
    def _analyze_wallet_distribution(self):
        """Analyze wallet balance distribution"""
        # Implementation will pull data from API
        pass
    
    def _analyze_defi_activity(self):
        """Analyze DeFi protocol activity"""
        # Implementation will pull data from API
        pass
    
    def _get_fear_greed_index(self):
        """Get current fear and greed index"""
        try:
            response = requests.get(self.sentiment_sources['fear_greed_index'])
            data = response.json()
            return int(data['data'][0]['value'])
        except Exception as e:
            print(f"Error fetching fear/greed index: {e}")
            return 50  # Neutral default
    
    def _analyze_social_sentiment(self):
        """Analyze sentiment from social media"""
        # Implementation will pull data from API
        pass
    
    def _analyze_trend_indicators(self):
        """Analyze various trend indicators"""
        # Implementation will pull data from API
        pass
    
    def _track_eth_whales(self):
        """Track Ethereum whale wallets"""
        # Implementation will pull data from API
        pass
    
    def _track_btc_whales(self):
        """Track Bitcoin whale wallets"""
        # Implementation will pull data from API
        pass
    
    def _track_token_whales(self):
        """Track major token whale wallets"""
        # Implementation will pull data from API
        pass
    
    def _monitor_dex_activity(self):
        """Monitor DEX contract activity"""
        # Implementation will pull data from API
        pass
    
    def _monitor_lending_activity(self):
        """Monitor lending protocol activity"""
        # Implementation will pull data from API
        pass
    
    def _monitor_gaming_activity(self):
        """Monitor gaming protocol activity"""
        # Implementation will pull data from API
        pass

    def track_gem_performance(self, symbol, current_data):
        """Track performance of a called gem"""
        if symbol not in self.storage.gem_history['calls']:
            self.storage.gem_history['calls'][symbol] = {
                'timestamp': datetime.now(),
                'initial_price': current_data['price'],
                'initial_mcap': current_data['market_cap'],
                'initial_volume': current_data['volume_24h'],
                'reason': current_data.get('reason', ''),
                'category': current_data.get('category', '')
            }
        
        # Update current performance
        self.storage.gem_history['performance'][symbol] = {
            'current_price': current_data['price'],
            'current_mcap': current_data['market_cap'],
            'current_volume': current_data['volume_24h'],
            'roi': ((current_data['price'] - self.storage.gem_history['calls'][symbol]['initial_price']) 
                   / self.storage.gem_history['calls'][symbol]['initial_price']) * 100
        }
        
        return self.storage.gem_history['performance'][symbol]

    def get_best_performers(self, limit=3):
        """Get the best performing gems we've called"""
        performers = []
        for symbol, perf in self.storage.gem_history['performance'].items():
            if perf['roi'] > 0:  # Only include positive ROI
                performers.append({
                    'symbol': symbol,
                    'roi': perf['roi'],
                    'initial_price': self.storage.gem_history['calls'][symbol]['initial_price'],
                    'current_price': perf['current_price']
                })
        
        return sorted(performers, key=lambda x: x['roi'], reverse=True)[:limit]
