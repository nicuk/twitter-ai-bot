"""
Data storage module for ELAI
"""

import os
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import json
from pathlib import Path
from typing import Optional, Dict, List

class DataStorage:
    def __init__(self):
        """Initialize the data storage system"""
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Initialize database
        self.initialize_database()
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def initialize_database(self):
        """Initialize PostgreSQL database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_calls (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            price_usd FLOAT NOT NULL,
            market_cap FLOAT,
            volume_24h FLOAT,
            reason TEXT,
            category TEXT,
            sentiment TEXT,
            tweet_id TEXT
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            price_usd FLOAT NOT NULL,
            volume_24h FLOAT,
            market_cap FLOAT,
            UNIQUE(symbol, timestamp)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS narratives (
            id SERIAL PRIMARY KEY,
            category TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            coins TEXT NOT NULL,
            reason TEXT,
            avg_change_24h FLOAT,
            total_volume_24h FLOAT
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_data (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            data JSONB NOT NULL
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_data (
            id SERIAL PRIMARY KEY,
            project_id TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            data JSONB NOT NULL,
            UNIQUE(project_id, timestamp)
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tweet_history (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            tweet_type TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio_history (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            action TEXT NOT NULL,
            symbol TEXT NOT NULL,
            amount FLOAT NOT NULL,
            price FLOAT NOT NULL,
            metadata JSONB
        )''')

        # Personality tracking tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS personality_journey (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            category TEXT NOT NULL,  -- learnings, achievements, challenges, interactions, insights
            content TEXT NOT NULL,
            impact_score FLOAT,
            metadata JSONB
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS growth_metrics (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            metric_type TEXT NOT NULL,  -- accuracy, engagement, trust, innovation, impact
            value FLOAT NOT NULL,
            context JSONB
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_interactions (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            user_id TEXT NOT NULL,
            interaction_type TEXT NOT NULL,
            sentiment FLOAT,
            content TEXT,
            impact_score FLOAT,
            metadata JSONB
        )''')

        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_journey_timestamp ON personality_journey(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_type_time ON growth_metrics(metric_type, timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_user ON community_interactions(user_id, timestamp)')

        conn.commit()
        conn.close()
    
    def store_coin_call(self, coin_data, tweet_id=None):
        """Store a new coin call/mention"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO coin_calls (
                symbol, name, timestamp, price_usd, market_cap, 
                volume_24h, reason, category, sentiment, tweet_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            coin_data['symbol'],
            coin_data['name'],
            datetime.utcnow(),
            coin_data['price'],
            coin_data.get('market_cap'),
            coin_data.get('volume_24h'),
            coin_data.get('reason'),
            coin_data.get('category'),
            coin_data.get('sentiment', 'neutral'),
            tweet_id
        ))
        conn.commit()
        conn.close()
    
    def update_price_history(self, symbol, price_data):
        """Update price history for a coin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO price_history (
                symbol, timestamp, price_usd, volume_24h, market_cap
            ) VALUES (%s, %s, %s, %s, %s)
        ''', (
            symbol,
            datetime.utcnow(),
            price_data['price'],
            price_data.get('volume_24h'),
            price_data.get('market_cap')
        ))
        conn.commit()
        conn.close()
    
    def store_narrative(self, narrative_data):
        """Store a narrative/sector analysis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO narratives (
                category, timestamp, coins, reason, 
                avg_change_24h, total_volume_24h
            ) VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            narrative_data['category'],
            datetime.utcnow(),
            json.dumps(narrative_data['coins']),
            narrative_data.get('reason'),
            narrative_data.get('avg_change'),
            narrative_data.get('total_volume')
        ))
        conn.commit()
        conn.close()
    
    def store_market_data(self, data):
        """Store market data snapshot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO market_data (timestamp, data) VALUES (%s, %s)
        ''', (
            datetime.utcnow(),
            Json(data)
        ))
        conn.commit()
        conn.close()

    def get_latest_market_data(self):
        """Get latest market data snapshot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT data FROM market_data ORDER BY timestamp DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def store_project_data(self, project_id, data):
        """Store project data snapshot"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO project_data (project_id, timestamp, data) VALUES (%s, %s, %s)
        ''', (
            project_id,
            datetime.utcnow(),
            Json(data)
        ))
        conn.commit()
        conn.close()

    def get_project_data(self, project_id):
        """Get latest project data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT data FROM project_data WHERE project_id = %s ORDER BY timestamp DESC LIMIT 1
        ''', (project_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def store_tweet(self, tweet_type, content, metadata=None):
        """Store tweet in history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tweet_history (timestamp, tweet_type, content, metadata) VALUES (%s, %s, %s, %s)
        ''', (
            datetime.utcnow(),
            tweet_type,
            content,
            Json(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()

    def get_tweet_history(self, limit=100):
        """Get recent tweet history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, tweet_type, content, metadata FROM tweet_history ORDER BY timestamp DESC LIMIT %s
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                'timestamp': row[0],
                'type': row[1],
                'content': row[2],
                'metadata': row[3]
            }
            for row in results
        ]

    def store_portfolio_action(self, action, symbol, amount, price, metadata=None):
        """Store portfolio action in history"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO portfolio_history (timestamp, action, symbol, amount, price, metadata) VALUES (%s, %s, %s, %s, %s, %s)
        ''', (
            datetime.utcnow(),
            action,
            symbol,
            amount,
            price,
            Json(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()

    def get_portfolio_history(self, limit=100):
        """Get recent portfolio actions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, action, symbol, amount, price, metadata FROM portfolio_history ORDER BY timestamp DESC LIMIT %s
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return [
            {
                'timestamp': row[0],
                'action': row[1],
                'symbol': row[2],
                'amount': row[3],
                'price': row[4],
                'metadata': row[5]
            }
            for row in results
        ]
    
    def get_coin_performance(self, symbol, days_back=None):
        """Get performance metrics for a called coin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get initial call data
        cursor.execute('''
            SELECT price_usd, timestamp 
            FROM coin_calls 
            WHERE symbol = %s 
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
            WHERE symbol = %s 
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
        
        conn = self.get_connection()
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT category, COUNT(*) as mentions,
                   AVG(avg_change_24h) as avg_performance
            FROM narratives
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            GROUP BY category
            ORDER BY mentions DESC
        ''', (days_back,))
        
        return cursor.fetchall()

    def cleanup_tracked_coins(self, max_loss_percent=50, min_gain_percent=50, days_inactive=7):
        """Remove coins that have performed poorly or been inactive"""
        try:
            conn = self.get_connection()
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
                WHERE roi <= -%s OR 
                      (EXTRACT(EPOCH FROM (NOW() - last_update)) / 3600) > %s OR
                      volume_24h = 0
            ''', (max_loss_percent, days_inactive))
            
            coins_to_remove = [row[0] for row in cursor.fetchall()]
            
            # Remove these coins from tracking
            if coins_to_remove:
                placeholders = ','.join('%s' * len(coins_to_remove))
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
                WHERE roi >= %s
                ORDER BY roi DESC
            ''', (min_gain_percent,))
            
            high_performers = [{
                'symbol': row[0],
                'roi': row[1],
                'volume_24h': row[2],
                'initial_price': row[3],
                'current_price': row[4]
            } for row in cursor.fetchall()]
            
            conn.commit()
            conn.close()
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
            conn = self.get_connection()
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
                    ) VALUES (%s, %s, %s, %s, %s)
                ''', updates)
                
            # Cleanup old price history (keep last 30 days)
            cursor.execute('''
                DELETE FROM price_history 
                WHERE timestamp < NOW() - INTERVAL '30 days'
            ''')
            
            conn.commit()
            conn.close()
            return len(updates)
                
        except Exception as e:
            print(f"Error updating tracked coins: {e}")
            return None

    def store_journey_event(self, category: str, content: str, impact_score: float = 0.0, metadata: Dict[str, str] = None):
        """Store a personality journey event"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO personality_journey (timestamp, category, content, impact_score, metadata)
        VALUES (%s, %s, %s, %s, %s)
        ''', (
            datetime.utcnow(),
            category,
            content,
            impact_score,
            Json(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()

    def update_growth_metric(self, metric_type: str, value: float, context: Dict[str, str] = None):
        """Update a growth metric"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO growth_metrics (timestamp, metric_type, value, context)
        VALUES (%s, %s, %s, %s)
        ''', (
            datetime.utcnow(),
            metric_type,
            value,
            Json(context) if context else None
        ))
        conn.commit()
        conn.close()

    def store_community_interaction(self, user_id: str, interaction_type: str, content: str,
                                 sentiment: float = 0.0, impact_score: float = 0.0,
                                 metadata: Dict[str, str] = None):
        """Store a community interaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO community_interactions 
        (timestamp, user_id, interaction_type, sentiment, content, impact_score, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            datetime.utcnow(),
            user_id,
            interaction_type,
            sentiment,
            content,
            impact_score,
            Json(metadata) if metadata else None
        ))
        conn.commit()
        conn.close()

    def get_recent_journey_events(self, category: str = None, limit: int = 10) -> List:
        """Get recent journey events, optionally filtered by category"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if category:
            cursor.execute('''
            SELECT * FROM personality_journey 
            WHERE category = %s 
            ORDER BY timestamp DESC LIMIT %s
            ''', (category, limit))
        else:
            cursor.execute('''
            SELECT * FROM personality_journey 
            ORDER BY timestamp DESC LIMIT %s
            ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_growth_metrics_history(self, metric_type: str, days: int = 30) -> List:
        """Get historical data for a growth metric"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT timestamp, value, context 
        FROM growth_metrics 
        WHERE metric_type = %s
        AND timestamp >= NOW() - INTERVAL '%s days'
        ORDER BY timestamp DESC
        ''', (metric_type, days))
        results = cursor.fetchall()
        conn.close()
        return results

    def get_user_interactions(self, user_id: str, limit: int = 10) -> List:
        """Get interaction history with a specific user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT * FROM community_interactions 
        WHERE user_id = %s
        ORDER BY timestamp DESC LIMIT %s
        ''', (user_id, limit))
        results = cursor.fetchall()
        conn.close()
        return results
