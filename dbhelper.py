# A.Piskun
# 05/11/2018
#
#
import sqlite3
from datetime import datetime


class DBHelper(object):
    def __init__(self, path2db):
        self.path2db = path2db
        self.conn = sqlite3.connect(self.path2db, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        sql = '''
        CREATE TABLE IF NOT EXISTS user_log(
        date DATE, 
        name TEXT, 
        action TEXT)'''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    def select_sights_between(self, lat_1, lat_2, lon_1, lon_2):
        sql = '''
        SELECT sight_id, lat, lon, address, description, quest, answer 
        FROM sights 
        WHERE (lat between (?) and (?)) and (lon between (?) and (?))'''
        args = (lat_1, lat_2, lon_1, lon_2)
        cur = self.conn.cursor()
        cur.execute(sql, args)
        return cur.fetchall()

    def select_history(self, sight_id):
        sql = '''
        SELECT sight_id, history 
        FROM history 
        WHERE sight_id = (?)'''
        cur = self.conn.cursor()
        cur.execute(sql, (sight_id,))
        return cur.fetchall()

    def add_user_log(self, name, action):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = 'INSERT INTO user_log VALUES (?, ?, ?)'
        cur = self.conn.cursor()
        cur.execute(sql, (date, name, action))
        self.conn.commit()

