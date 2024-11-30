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