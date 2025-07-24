"""Database handler for the person detection system."""

import sqlite3
from ..core.config import Config


class DBHelper:
    """Database helper class for managing user data and bot settings."""
    
    def __init__(self):
        self.db_name = Config.DATABASE_NAME
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.create_table()

    def create_table(self):
        """Create necessary database tables."""
        c = self.conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS tgmembers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     name TEXT,
                      user_id INTEGER)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS bot_tokens
             (token TEXT PRIMARY KEY)"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS admins
             (admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
              admin_user_id INTEGER)"""
        )
        
        self.conn.commit()
        
    def get_all_users(self):
        """Get all registered users."""
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM tgmembers")
        return c.fetchall()
    
    def user_exists(self, user_id):
        """Check if a user exists in the database."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM tgmembers WHERE user_id = ?", (user_id,))
        return c.fetchone() is not None
    
    def add_user(self, name, user_id):
        """Add a new user to the database."""
        c = self.conn.cursor()
        c.execute("INSERT INTO tgmembers (name, user_id) VALUES (?, ?)", (name, user_id))
        self.conn.commit()
        
    def get_bot_token(self):
        """Get the bot token from the database."""
        c = self.conn.cursor()
        token = c.execute("SELECT token FROM bot_tokens").fetchone()
        return token[0] if token else None

    def is_sametoken(self, token):
        """Check if the provided token is the same as the stored one."""
        c = self.conn.cursor()
        lasttoken = c.execute("SELECT token FROM bot_tokens").fetchone()
        
        if lasttoken:
            return token == lasttoken[-1]
        return False
    
    def replace_token(self, token):
        """Replace the bot token in the database."""
        c = self.conn.cursor()
        c.execute("DELETE FROM bot_tokens")
        c.execute("INSERT INTO bot_tokens (token) VALUES (?)", (token,))
        self.conn.commit()
        
    def get_admins(self):
        """Get all admin user IDs."""
        c = self.conn.cursor()
        admins = c.execute("SELECT admin_user_id FROM admins").fetchall()
        return [admin[0] for admin in admins] if admins else None
    
    def add_new_admins(self, admin_user_ids: list):
        """Add new admin user IDs, replacing existing ones."""
        c = self.conn.cursor()
        c.execute("DELETE FROM admins")
        for admin_user_id in admin_user_ids:
            c.execute("INSERT INTO admins (admin_user_id) VALUES (?)", (admin_user_id,))
        self.conn.commit()