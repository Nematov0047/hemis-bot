import sqlite3
import time
import json

class DB():
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
    
    def initialize(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS users_cookies (login TEXT, cookies TEXT, time INTEGER)")
        self.conn.commit()

    def get_cookies(self, login):
        result = self.c.execute("SELECT * FROM users_cookies WHERE login='"+login+"'").fetchone()
        self.conn.commit()
        if result != None:
            if int(int(result[2]) > int(time.time())):
                return json.loads(result[1])
            else:
                return 'expired'
        else:
            return False
    
    def insert_cookies(self, login, cookies):
        r = self.c.execute("SELECT * FROM users_cookies WHERE login='"+login+"'").fetchall()
        self.conn.commit()
        if len(r) > 0:
            self.c.execute("DELETE FROM users_cookies WHERE login='"+login+"'")
            self.conn.commit()
        self.c.execute("INSERT INTO users_cookies VALUES (?,?,?)",(login, cookies,int(time.time()+3540)))
        self.conn.commit()

    def update_cookies(self, login, cookies):
        self.c.execute("UPDATE users_cookies SET cookies='"+cookies+"' WHERE login='"+login+"'")
        self.conn.commit()
                        
db = DB()