import sqlite3
import json
import time
from config import CACHE_DIR

CACHE_DIR.mkdir(exist_ok=True)

DB_PATH = CACHE_DIR / "cache.db"


class Cache:

    def __init__(self):

        self.conn = sqlite3.connect(DB_PATH)

        self.create_table()

    def create_table(self):

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                url TEXT PRIMARY KEY,
                html TEXT,
                timestamp INTEGER
            )
        """)

        self.conn.commit()

    def get(self, url):

        cur = self.conn.cursor()

        cur.execute("SELECT html FROM pages WHERE url=?", (url,))

        row = cur.fetchone()

        if row:

            return row[0]

        return None

    def set(self, url, html):

        self.conn.execute(
            "INSERT OR REPLACE INTO pages VALUES (?, ?, ?)",
            (url, html, int(time.time()))
        )

        self.conn.commit()