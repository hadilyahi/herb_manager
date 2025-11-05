import sqlite3
import os

DB_PATH = "database/herb_store.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # ← يجعل كل صف dict-like
    return conn

def create_db():
    """إنشاء قاعدة البيانات والجداول من البداية (مع الحفاظ على البيانات إن وجدت)"""

    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # إنشاء الجداول الأساسية
    c.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            parent_id INTEGER DEFAULT NULL,
            UNIQUE(name, parent_id),
            FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS units (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('weight', 'liquid', 'money'))
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            unit_id INTEGER,
            expiry_date TEXT,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (unit_id) REFERENCES units(id)
        )
    ''')

    # ✅ جدول الفواتير الرئيسي
    c.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_price REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    # ✅ جدول المشتريات المرتبطة بكل فاتورة
    c.execute('''
       CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    unit_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    price_per_unit REAL NOT NULL,
    total_price REAL NOT NULL,
    date TEXT NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (unit_id) REFERENCES units(id)
)

    ''')

    # تعبئة جدول الوحدات إن كان فارغًا
    c.execute("SELECT COUNT(*) FROM units")
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO units (name, type) VALUES (?, ?)', [
            ('غرام', 'weight'),
            ('كغ', 'weight'),
            ('مليلتر', 'liquid'),
            ('لتر', 'liquid'),
            ('دج', 'money'),
            
        ])

    conn.commit()
    conn.close()
    print("✅ The database is ready and successfully updated (with invoicing support)")

if __name__ == "__main__":
    create_db()
