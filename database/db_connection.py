import sqlite3
import os

DB_PATH = "database/herb_store.db"

def get_connection():
    """إرجاع اتصال بقاعدة البيانات"""
    return sqlite3.connect(DB_PATH)

def create_db():
    """إنشاء قاعدة البيانات والجداول من البداية (مع الحفاظ على البيانات إن وجدت)"""
   
    if not os.path.exists("database"):
        os.makedirs("database")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # إنشاء الجداول فقط إن لم تكن موجودة
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
            expiry_date TEXT,       -- تاريخ الانتهاء اختياري
            description TEXT,       -- الوصف اختياري
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (unit_id) REFERENCES units(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            price_per_unit REAL NOT NULL,
            total_price REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')

    # تعبئة جدول الوحدات الافتراضي إن كان فارغًا
    c.execute("SELECT COUNT(*) FROM units")
    if c.fetchone()[0] == 0:
        c.executemany('INSERT INTO units (name, type) VALUES (?, ?)', [
            ('غرام', 'weight'),
            ('كغ', 'weight'),
            ('مليلتر', 'liquid'),
            ('لتر', 'liquid'),
            ('دج', 'money'),
            ('طرد', 'money')
        ])

    conn.commit()
    conn.close()
    print("✅ قاعدة البيانات جاهزة ومحدثة بنجاح")

if __name__ == "__main__":
    create_db()
