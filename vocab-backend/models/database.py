import sqlite3
import json
from typing import List, Dict, Any, Tuple, Optional

from config import DATABASE_PATH

class Database:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        
    def get_connection(self) -> sqlite3.Connection:
        """Create and return a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    
    def initialize_db(self) -> None:
        """Create the database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create groups table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Create words table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            english TEXT NOT NULL,
            marathi TEXT NOT NULL,
            FOREIGN KEY (group_id) REFERENCES groups (id),
            UNIQUE (group_id, english)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_group(self, name: str) -> int:
        """Add a new group and return its ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO groups (name) VALUES (?)', (name,))
            group_id = cursor.lastrowid
            conn.commit()
            return group_id
        except sqlite3.IntegrityError:
            # Group already exists, get its ID
            cursor.execute('SELECT id FROM groups WHERE name = ?', (name,))
            group_id = cursor.fetchone()['id']
            return group_id
        finally:
            conn.close()
    
    def get_group_by_id(self, group_id: int) -> Optional[Dict[str, Any]]:
        """Get a group by its ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM groups WHERE id = ?', (group_id,))
        group = cursor.fetchone()
        conn.close()
        
        if group:
            return dict(group)
        return None
    
    def get_group_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a group by its name."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name FROM groups WHERE name = ?', (name,))
        group = cursor.fetchone()
        conn.close()
        
        if group:
            return dict(group)
        return None
    
    def add_words(self, group_id: int, words: List[Dict[str, str]]) -> None:
        """Add multiple words to a group."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for word in words:
            try:
                cursor.execute(
                    'INSERT INTO words (group_id, english, marathi) VALUES (?, ?, ?)',
                    (group_id, word['english'], word['marathi'])
                )
            except sqlite3.IntegrityError:
                # Word already exists for this group, update it
                cursor.execute(
                    'UPDATE words SET marathi = ? WHERE group_id = ? AND english = ?',
                    (word['marathi'], group_id, word['english'])
                )
        
        conn.commit()
        conn.close()
    
    def get_words_by_group_id(self, group_id: int) -> List[Dict[str, str]]:
        """Get all words for a specific group ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT english, marathi FROM words WHERE group_id = ?',
            (group_id,)
        )
        words = [dict(word) for word in cursor.fetchall()]
        conn.close()
        
        return words