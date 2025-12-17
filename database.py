"""
Database module for storing user settings.
"""

import sqlite3
from typing import Optional


class Database:
    def __init__(self, db_path: str = "bot_data.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database and create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    default_group TEXT,
                    notifications_enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def set_default_group(self, user_id: int, group: str):
        """Set default group for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, default_group)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET default_group = ?
            """, (user_id, group, group))
            conn.commit()
    
    def get_default_group(self, user_id: int) -> Optional[str]:
        """Get user's default group."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT default_group FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def set_notifications(self, user_id: int, enabled: bool):
        """Enable or disable notifications for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, notifications_enabled)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET notifications_enabled = ?
            """, (user_id, int(enabled), int(enabled)))
            conn.commit()
    
    def get_notifications_enabled(self, user_id: int) -> bool:
        """Check if notifications are enabled for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT notifications_enabled FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else True  # Default: enabled
    
    def get_all_users_with_notifications(self) -> list:
        """Get all users who have notifications enabled and a default group set."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, default_group 
                FROM users 
                WHERE notifications_enabled = 1 AND default_group IS NOT NULL
            """)
            return cursor.fetchall()
