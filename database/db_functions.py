from .db_connection import get_connection


# ---------------------------------------
# دوال مساعدة

def fetch_products():
    """جلب جميع المنتجات مع اسم الفئة"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.id, p.name, c.name AS category, p.expiry_date, p.description
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
    ''')
    data = c.fetchall()
    conn.close()
    return data

def fetch_categories():
    """جلب جميع الفئات (الأصلية والفرعية)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, parent_id FROM categories ORDER BY name")
    categories = c.fetchall()
    conn.close()
    return categories

def add_category_to_db(name, parent_id=None, sub_name=None):
    """إضافة فئة جديدة مع إمكانية إضافة فئة فرعية"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (name, parent_id) VALUES (?, ?)", (name, parent_id))
    if sub_name:
        parent_for_sub = cur.lastrowid
        cur.execute("INSERT INTO categories (name, parent_id) VALUES (?, ?)", (sub_name, parent_for_sub))
    conn.commit()
    conn.close()

def insert_category(name):
    """إضافة فئة بدون فرعية"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
