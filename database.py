import sqlite3
import os

def get_db_connection():
    """Create a database connection"""
    conn = sqlite3.connect('spotify_ai.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        spotify_client_id TEXT,
        spotify_client_secret TEXT,
        spotify_access_token TEXT,
        spotify_refresh_token TEXT,
        gemini_api_key TEXT,
        encryption_key TEXT
    )
    ''')
    conn.commit()
    conn.close()




