"""Database management for trade tracking"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os
import json

class TradeDatabase:
    """Manages trade and portfolio data"""
    
    def __init__(self, db_path: str = 'trades.db'):
        """Initialize database"""
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create portfolio table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    balance REAL NOT NULL,
                    total_trades INTEGER DEFAULT 0,
                    winning_trades INTEGER DEFAULT 0,
                    best_trade_symbol TEXT,
                    best_trade_gain REAL,
                    daily_pnl REAL DEFAULT 0.0
                )
            ''')
            
            # Create trades table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY,
                    date TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    pnl REAL NOT NULL,
                    pnl_percentage REAL NOT NULL,
                    trade_type TEXT NOT NULL,
                    duration TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            ''')
            
            # Insert initial portfolio if not exists
            cursor.execute('SELECT COUNT(*) FROM portfolio')
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                    INSERT INTO portfolio (date, balance, total_trades)
                    VALUES (?, ?, ?)
                ''', (datetime.now().strftime('%Y-%m-%d'), 100.0, 0))
            
            conn.commit()
    
    def add_trade(self, trade_data: Dict) -> bool:
        """Add a new trade to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert trade
                cursor.execute('''
                    INSERT INTO trades (
                        date, symbol, entry_price, exit_price, 
                        quantity, pnl, pnl_percentage, trade_type,
                        duration, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data['date'],
                    trade_data['symbol'],
                    trade_data['entry_price'],
                    trade_data['exit_price'],
                    trade_data['quantity'],
                    trade_data['pnl'],
                    trade_data['pnl_percentage'],
                    trade_data['trade_type'],
                    trade_data['duration'],
                    trade_data['status']
                ))
                
                # Update portfolio
                self.update_portfolio(trade_data['pnl'])
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error adding trade: {e}")
            return False
    
    def update_portfolio(self, pnl: float) -> bool:
        """Update portfolio with trade PNL"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current portfolio
                cursor.execute('SELECT balance, daily_pnl FROM portfolio ORDER BY id DESC LIMIT 1')
                current = cursor.fetchone()
                
                if current:
                    new_balance = current[0] + pnl
                    new_daily_pnl = current[1] + pnl
                    
                    # Update portfolio
                    cursor.execute('''
                        UPDATE portfolio 
                        SET balance = ?, daily_pnl = ?
                        WHERE id = (SELECT MAX(id) FROM portfolio)
                    ''', (new_balance, new_daily_pnl))
                    
                    conn.commit()
                    return True
                    
                return False
                
        except Exception as e:
            print(f"Error updating portfolio: {e}")
            return False
    
    def get_portfolio_stats(self) -> Dict:
        """Get current portfolio statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT 
                        balance, 
                        total_trades,
                        winning_trades,
                        best_trade_symbol,
                        best_trade_gain,
                        daily_pnl,
                        date
                    FROM portfolio 
                    ORDER BY id DESC 
                    LIMIT 1
                ''')
                
                row = cursor.fetchone()
                if row:
                    return {
                        'current_balance': row[0],
                        'total_trades': row[1],
                        'winning_trades': row[2],
                        'best_trade': {
                            'symbol': row[3],
                            'gain': row[4]
                        },
                        'daily_pnl': row[5],
                        'date': row[6]
                    }
                    
                return None
                
        except Exception as e:
            print(f"Error getting portfolio stats: {e}")
            return None
    
    def reset_daily_stats(self):
        """Reset daily statistics (called at market open)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert new day's record
                cursor.execute('''
                    INSERT INTO portfolio (
                        date, balance, total_trades, winning_trades,
                        best_trade_symbol, best_trade_gain, daily_pnl
                    )
                    SELECT 
                        ?, balance, 0, 0,
                        NULL, NULL, 0.0
                    FROM portfolio 
                    ORDER BY id DESC 
                    LIMIT 1
                ''', (datetime.now().strftime('%Y-%m-%d'),))
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error resetting daily stats: {e}")
            return False
