from .db_connection import get_connection


# ---------------------------------------
# دوال المنتجات والفئات

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


# ---------------------------------------
# دوال المشتريات

def fetch_purchases():
    """جلب جميع عمليات الشراء مع أسماء المنتجات"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT p.id, pr.name, p.quantity, p.price_per_unit, p.total_price, p.date
        FROM purchases p
        JOIN products pr ON p.product_id = pr.id
        ORDER BY p.date DESC
    ''')
    data = c.fetchall()
    conn.close()
    return data


def insert_purchase(product_id, quantity, price_per_unit, date):
    """إضافة عملية شراء جديدة"""
    total_price = quantity * price_per_unit
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO purchases (product_id, quantity, price_per_unit, total_price, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (product_id, quantity, price_per_unit, total_price, date))
    conn.commit()
    conn.close()
    
def fetch_products_with_invoice():
    """جلب كل المنتجات مع بيانات الفاتورة التي تخصها"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT p.id, pr.name, p.quantity, p.price_per_unit, p.total_price, i.date AS invoice_date
        FROM purchases p
        JOIN products pr ON p.product_id = pr.id
        JOIN invoices i ON p.invoice_id = i.id
        ORDER BY i.date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_invoices():
    """جلب جميع الفواتير مع عدد المنتجات وإجمالي السعر"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT i.id, i.date, COUNT(p.id) AS num_products, SUM(p.total_price) AS total_price
        FROM invoices i
        LEFT JOIN purchases p ON p.invoice_id = i.id
        GROUP BY i.id
        ORDER BY i.date DESC
    """)
    rows = c.fetchall()
    conn.close()
    return rows

