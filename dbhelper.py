# A.Piskun
# 05/11/2018
#
# db wrapper
#
import sqlite3
from datetime import datetime


class DBHelper(object):
    def __init__(self, path2db):
        self.path2db = path2db
        self.conn = sqlite3.connect(self.path2db, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()

        cur.execute('''
        CREATE TABLE IF NOT EXISTS user_log(
        date DATE, 
        name TEXT, 
        action TEXT);''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS sights(
        sight_id integer PRIMARY KEY,
        lat real NOT NULL,
        lon real NOT NULL,
        event TEXT,
        cp_id TEXT NOT NULL,
        address TEXT NOT NULL,
        description TEXT,
        quest TEXT,
        answer TEXT,
        year integer);''')

        cur.execute('''
        CREATE TABLE IF NOT EXISTS history(
        sight_id INTEGER PRIMARY KEY,
        event TEXT,
        cp_id TEXT NOT NULL,
        history TEXT);''')

        self.conn.commit()

    def clear_tables(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM sights')
        cur.execute('DELETE FROM history')
        self.conn.commit()

    def add_sights(self, parsed):
        sql = 'INSERT INTO sights VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        cur = self.conn.cursor()
        cur.executemany(sql, parsed)
        self.conn.commit()

    def add_histories(self, parsed):
        sql = 'INSERT INTO history VALUES(?, ?, ?, ?)'
        cur = self.conn.cursor()
        cur.executemany(sql, parsed)
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

    def select_sights_by_event(self, event):
        sql = '''
        SELECT sight_id, lat, lon, address, description, quest, answer 
        FROM sights 
        WHERE event = (?)'''
        cur = self.conn.cursor()
        cur.execute(sql, (event,))
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

    def get_max_sight_id(self):
        cur = self.conn.cursor()
        cur.execute('SELECT max(sight_id) FROM sights')
        try:
            sight_id = cur.fetchall()[0][0]
            if sight_id is None:
                return 0
        except IndexError:
            return 0
        return sight_id



