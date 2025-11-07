import sqlite3
from database.db_connection import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
for r in cur.fetchall():
    print(r[0])
conn.close()
