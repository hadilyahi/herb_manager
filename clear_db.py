import sqlite3
from database.db_connection import get_connection

def clear_database():
    """حذف جميع الفئات والمنتجات والفواتير والمشتريات مؤقتًا"""
    conn = get_connection()
    c = conn.cursor()

    # حذف كل المنتجات أولًا
    c.execute("DELETE FROM products")

    # حذف كل الفئات
    c.execute("DELETE FROM categories")

    # حذف الفواتير والمشتريات
    c.execute("DELETE FROM purchases")
    c.execute("DELETE FROM invoices")

    conn.commit()
    conn.close()
    print("✅ تم تفريغ قاعدة البيانات مؤقتًا")

if __name__ == "__main__":
    clear_database()
