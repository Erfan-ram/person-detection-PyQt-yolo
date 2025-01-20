import sqlite3


class DBHelper:
    def __init__(self) -> None:
        self.db_name = "person_dt.db"
        self.conn = sqlite3.connect(self.db_name ,check_same_thread=False)
        self.create_table()

    def create_table(self):
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
              admin_name TEXT,
              admin_user_id INTEGER)"""
        )
        
        self.conn.commit()
        
    def get_all_users(self):
        c = self.conn.cursor()
        c.execute("SELECT user_id FROM tgmembers")
        return c.fetchall()
    
    def user_exists(self, user_id):
        c = self.conn.cursor()
        c.execute("SELECT * FROM tgmembers WHERE user_id = ?", (user_id,))
        if c.fetchone():
            return True
        else:
            return False
    
    def add_user(self, name, user_id):
        c = self.conn.cursor()
        c.execute("INSERT INTO tgmembers (name, user_id) VALUES (?, ?)", (name, user_id))
        self.conn.commit()
        
    def get_bot_token(self):
        c = self.conn.cursor()
        token = c.execute("SELECT token FROM bot_tokens").fetchone()
        if token:
            return token[0]
        return None

    def is_sametoken(self, token):
        c = self.conn.cursor()
        lasttoken = c.execute("SELECT token FROM bot_tokens").fetchone()
        
        if lasttoken:
            if token == lasttoken[-1]:
                return True
        return False
    
    def replace_token(self, token):
        c = self.conn.cursor()
        c.execute("DELETE FROM bot_tokens")
        c.execute("INSERT INTO bot_tokens (token) VALUES (?)", (token,))
        self.conn.commit()
        
    def get_admins(self):
        c = self.conn.cursor()
        admins = c.execute("SELECT admin_user_id FROM admins").fetchall()
        if admins != []:
            return admins
        return None