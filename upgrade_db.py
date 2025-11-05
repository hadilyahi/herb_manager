import sqlite3
from database.db_connection import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# إضافة العمود unit_id إذا لم يكن موجودًا
try:
    cur.execute("ALTER TABLE purchases ADD COLUMN unit_id INTEGER")
    print("✅ تم إضافة العمود unit_id بنجاح")
except sqlite3.OperationalError:
    print("⚠️ العمود unit_id موجود بالفعل")

conn.commit()
conn.close()
