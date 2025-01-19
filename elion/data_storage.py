"""
Data storage module for Elion
"""

import sqlite3
from datetime import datetime
import json
from pathlib import Path

class DataStorage:
    def __init__(self, db_path="data/elion.db"):
        """Initialize the data storage system"""
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db_path = db_path
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            price_usd REAL NOT NULL,
            market_cap REAL,
            volume_24h REAL,
            reason TEXT,
            category TEXT,
            sentiment TEXT,
            tweet_id TEXT
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            price_usd REAL NOT NULL,
            volume_24h REAL,
            market_cap REAL,
            UNIQUE(symbol, timestamp)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS narratives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            coins TEXT NOT NULL,
            reason TEXT,
            avg_change_24h REAL,
            total_volume_24h REAL
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            data TEXT NOT NULL,
            UNIQUE(project_id, timestamp)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweet_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tweet_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action TEXT NOT NULL,
            symbol TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL,
            metadata TEXT
        )''')

        conn.commit()
        conn.close()

    def store_coin_call(self, coin_data, tweet_id=None):
        """Store a new coin call/mention"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO coin_calls (
                    symbol, name, timestamp, price_usd, market_cap, 
                    volume_24h, reason, category, sentiment, tweet_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                coin_data['symbol'],
                coin_data['name'],
                datetime.utcnow().isoformat(),
                coin_data['price'],
                coin_data.get('market_cap'),
                coin_data.get('volume_24h'),
                coin_data.get('reason'),
                coin_data.get('category'),
                coin_data.get('sentiment', 'neutral'),
                tweet_id
            ))
            conn.commit()
    
    def update_price_history(self, symbol, price_data):
        """Update price history for a coin"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO price_history (
                    symbol, timestamp, price_usd, volume_24h, market_cap
                ) VALUES (?, ?, ?, ?, ?)
            ''', (
                symbol,
                datetime.utcnow().isoformat(),
                price_data['price'],
                price_data.get('volume_24h'),
                price_data.get('market_cap')
            ))
            conn.commit()
    
    def store_narrative(self, narrative_data):
        """Store a narrative/sector analysis"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO narratives (
                    category, timestamp, coins, reason, 
                    avg_change_24h, total_volume_24h
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                narrative_data['category'],
                datetime.utcnow().isoformat(),
                json.dumps(narrative_data['coins']),
                narrative_data.get('reason'),
                narrative_data.get('avg_change'),
                narrative_data.get('total_volume')
            ))
            conn.commit()
    
    def store_market_data(self, data):
        """Store market data snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO market_data (timestamp, data) VALUES (?, ?)',
            (datetime.utcnow().isoformat(), json.dumps(data))
        )
        
        conn.commit()
        conn.close()

    def get_latest_market_data(self):
        """Get latest market data snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT data FROM market_data ORDER BY timestamp DESC LIMIT 1'
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return json.loads(result[0]) if result else None

    def store_project_data(self, project_id, data):
        """Store project data snapshot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT OR REPLACE INTO project_data (project_id, timestamp, data) VALUES (?, ?, ?)',
            (project_id, datetime.utcnow().isoformat(), json.dumps(data))
        )
        
        conn.commit()
        conn.close()

    def get_project_data(self, project_id):
        """Get latest project data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT data FROM project_data WHERE project_id = ? ORDER BY timestamp DESC LIMIT 1',
            (project_id,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        return json.loads(result[0]) if result else None

    def store_tweet(self, tweet_type, content, metadata=None):
        """Store tweet in history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO tweet_history (timestamp, tweet_type, content, metadata) VALUES (?, ?, ?, ?)',
            (datetime.utcnow().isoformat(), tweet_type, content, json.dumps(metadata) if metadata else None)
        )
        
        conn.commit()
        conn.close()

    def get_tweet_history(self, limit=100):
        """Get recent tweet history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT timestamp, tweet_type, content, metadata FROM tweet_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'type': row[1],
                'content': row[2],
                'metadata': json.loads(row[3]) if row[3] else None
            }
            for row in results
        ]

    def store_portfolio_action(self, action, symbol, amount, price, metadata=None):
        """Store portfolio action in history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO portfolio_history (timestamp, action, symbol, amount, price, metadata) VALUES (?, ?, ?, ?, ?, ?)',
            (datetime.utcnow().isoformat(), action, symbol, amount, price, json.dumps(metadata) if metadata else None)
        )
        
        conn.commit()
        conn.close()

    def get_portfolio_history(self, limit=100):
        """Get recent portfolio actions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT timestamp, action, symbol, amount, price, metadata FROM portfolio_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        )
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'timestamp': row[0],
                'action': row[1],
                'symbol': row[2],
                'amount': row[3],
                'price': row[4],
                'metadata': json.loads(row[5]) if row[5] else None
            }
            for row in results
        ]
    
    def get_coin_performance(self, symbol, days_back=None):
        """Get performance metrics for a called coin"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get initial call data
            cursor.execute('''
                SELECT price_usd, timestamp 
                FROM coin_calls 
                WHERE symbol = ? 
                ORDER BY timestamp ASC 
                LIMIT 1
            ''', (symbol,))
            initial_call = cursor.fetchone()
            
            if not initial_call:
                return None
                
            # Get latest price
            cursor.execute('''
                SELECT price_usd, timestamp 
                FROM price_history 
                WHERE symbol = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (symbol,))
            latest_price = cursor.fetchone()
            
            if not latest_price:
                return None
                
            # Calculate performance
            initial_price = initial_call[0]
            current_price = latest_price[0]
            roi = ((current_price - initial_price) / initial_price) * 100
            
            return {
                'symbol': symbol,
                'call_date': initial_call[1],
                'call_price': initial_price,
                'current_price': current_price,
                'roi': roi
            }
    
    def get_best_performers(self, limit=5):
        """Get the best performing coins we've called"""
        performers = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DISTINCT symbol 
                FROM coin_calls
            ''')
            
            for (symbol,) in cursor.fetchall():
                performance = self.get_coin_performance(symbol)
                if performance:
                    performers.append(performance)
        
        # Sort by ROI and return top performers
        return sorted(performers, key=lambda x: x['roi'], reverse=True)[:limit]
    
    def get_recent_narratives(self, days_back=7):
        """Get recent narrative trends"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, COUNT(*) as mentions,
                       AVG(avg_change_24h) as avg_performance
                FROM narratives
                WHERE timestamp >= datetime('now', ?)
                GROUP BY category
                ORDER BY mentions DESC
            ''', (f'-{days_back} days',))
            
            return cursor.fetchall()

    def cleanup_tracked_coins(self, max_loss_percent=50, min_gain_percent=50, days_inactive=7):
        """Remove coins that have performed poorly or been inactive"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get coins to remove (down >50% or inactive)
                cursor.execute('''
                    WITH latest_prices AS (
                        SELECT 
                            symbol,
                            price_usd as current_price,
                            volume_24h,
                            timestamp,
                            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
                        FROM price_history
                    ),
                    performance AS (
                        SELECT 
                            c.symbol,
                            c.price_usd as initial_price,
                            lp.current_price,
                            lp.volume_24h,
                            lp.timestamp as last_update,
                            ((lp.current_price - c.price_usd) / c.price_usd * 100) as roi
                        FROM coin_calls c
                        JOIN latest_prices lp ON c.symbol = lp.symbol AND lp.rn = 1
                    )
                    SELECT symbol
                    FROM performance
                    WHERE roi <= -? OR 
                          (julianday('now') - julianday(last_update)) > ? OR
                          volume_24h = 0
                ''', (max_loss_percent, days_inactive))
                
                coins_to_remove = [row[0] for row in cursor.fetchall()]
                
                # Remove these coins from tracking
                if coins_to_remove:
                    placeholders = ','.join('?' * len(coins_to_remove))
                    cursor.execute(f'''
                        DELETE FROM coin_calls 
                        WHERE symbol IN ({placeholders})
                    ''', coins_to_remove)
                    
                    cursor.execute(f'''
                        DELETE FROM price_history 
                        WHERE symbol IN ({placeholders})
                    ''', coins_to_remove)
                
                # Get high performers (up >50%)
                cursor.execute('''
                    WITH latest_prices AS (
                        SELECT 
                            symbol,
                            price_usd as current_price,
                            volume_24h,
                            ROW_NUMBER() OVER (PARTITION BY symbol ORDER BY timestamp DESC) as rn
                        FROM price_history
                    ),
                    performance AS (
                        SELECT 
                            c.symbol,
                            c.price_usd as initial_price,
                            lp.current_price,
                            lp.volume_24h,
                            ((lp.current_price - c.price_usd) / c.price_usd * 100) as roi
                        FROM coin_calls c
                        JOIN latest_prices lp ON c.symbol = lp.symbol AND lp.rn = 1
                    )
                    SELECT 
                        symbol,
                        roi,
                        volume_24h,
                        initial_price,
                        current_price
                    FROM performance
                    WHERE roi >= ?
                    ORDER BY roi DESC
                ''', (min_gain_percent,))
                
                high_performers = [{
                    'symbol': row[0],
                    'roi': row[1],
                    'volume_24h': row[2],
                    'initial_price': row[3],
                    'current_price': row[4]
                } for row in cursor.fetchall()]
                
                return {
                    'removed_coins': coins_to_remove,
                    'high_performers': high_performers
                }
                
        except Exception as e:
            print(f"Error cleaning up tracked coins: {e}")
            return {'removed_coins': [], 'high_performers': []}

    def update_tracked_coins(self, market_data):
        """Update price history for tracked coins, respecting rate limits"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get list of coins we're tracking
                cursor.execute('SELECT DISTINCT symbol FROM coin_calls')
                tracked_coins = [row[0] for row in cursor.fetchall()]
                
                # Get current hour to determine update schedule
                current_hour = datetime.utcnow().hour
                
                # Only update during market hours (00:00, 08:00, 14:00, 20:00 UTC)
                if current_hour not in [0, 8, 14, 20]:
                    return None
                
                # Update prices for tracked coins
                updates = []
                for symbol in tracked_coins:
                    if symbol in market_data:
                        data = market_data[symbol]
                        updates.append((
                            symbol,
                            datetime.utcnow(),
                            data['price'],
                            data.get('volume_24h', 0),
                            data.get('market_cap', 0)
                        ))
                
                # Batch insert price updates
                if updates:
                    cursor.executemany('''
                        INSERT INTO price_history (
                            symbol, timestamp, price_usd, volume_24h, market_cap
                        ) VALUES (?, ?, ?, ?, ?)
                    ''', updates)
                    
                # Cleanup old price history (keep last 30 days)
                cursor.execute('''
                    DELETE FROM price_history 
                    WHERE julianday('now') - julianday(timestamp) > 30
                ''')
                
                return len(updates)
                
        except Exception as e:
            print(f"Error updating tracked coins: {e}")
            return None
