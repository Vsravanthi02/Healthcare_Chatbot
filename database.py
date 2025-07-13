import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='data/chat_history.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables"""
        dir_name = os.path.dirname(self.db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create chat_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                bot_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_message(self, session_id, user_message, bot_response):
        """Save a chat message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_history (session_id, user_message, bot_response)
            VALUES (?, ?, ?)
        ''', (session_id, user_message, bot_response))
        
        # Update session activity
        cursor.execute('''
            INSERT OR REPLACE INTO sessions (session_id, last_activity)
            VALUES (?, ?)
        ''', (session_id, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id, limit=50):
        """Retrieve chat history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, timestamp
            FROM chat_history
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, limit))
        
        history = cursor.fetchall()
        conn.close()
        
        return [{'user': msg[0], 'bot': msg[1], 'timestamp': msg[2]} for msg in reversed(history)]
    
    def clear_history(self, session_id):
        """Clear chat history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM chat_history WHERE session_id = ?', (session_id,))
        conn.commit()
        conn.close()

if __name__ == '__main__':
    # Initialize database when run directly
    db = DatabaseManager()
    print("Database initialized successfully!")