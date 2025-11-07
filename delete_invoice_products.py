import sqlite3
from database.db_connection import DB_PATH

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("DROP TABLE IF EXISTS invoice_products")
    conn.commit()
    print("✅ تم حذف جدول invoice_products بنجاح.")
except Exception as e:
    print("❌ حدث خطأ:", e)
finally:
    conn.close()

