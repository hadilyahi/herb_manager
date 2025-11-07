import sqlite3
from .db_connection import get_connection, DB_PATH

# ---------------------------------------
# دوال المنتجات والفئات
# ---------------------------------------
def fetch_products():
    """جلب جميع المنتجات مع اسم الفئة"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
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
    conn.row_factory = sqlite3.Row
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
# دوال المشتريات والفواتير
# ---------------------------------------
def fetch_purchases():
    """جلب جميع عمليات الشراء مع أسماء المنتجات"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT p.id, pr.name AS product_name, p.quantity, p.price_per_unit, p.total_price, p.date, p.invoice_id
        FROM purchases p
        JOIN products pr ON p.product_id = pr.id
        ORDER BY p.date DESC
    ''')
    data = c.fetchall()
    conn.close()
    return data


def insert_purchase(product_id, quantity, price_per_unit, date, invoice_id=None, unit_id=None):
    """إضافة عملية شراء جديدة"""
    total_price = quantity * price_per_unit
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO purchases (product_id, unit_id, quantity, price_per_unit, total_price, date, invoice_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (product_id, unit_id, quantity, price_per_unit, total_price, date, invoice_id))
    conn.commit()
    conn.close()


def fetch_products_with_invoice():
    import sqlite3
    from database.db_connection import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            p.id AS purchase_id,
            pr.id AS product_id,
            pr.name AS product_name,
            i.date AS invoice_date,
            p.quantity AS quantity,
            p.price_per_unit AS price_per_unit,
            p.total_price AS total_price
        FROM purchases p
        JOIN products pr ON p.product_id = pr.id
        JOIN invoices i ON p.invoice_id = i.id
        ORDER BY pr.name ASC, i.date DESC
    """)
    
    rows = cur.fetchall()
    conn.close()
    return rows


def fetch_invoices():
    """جلب جميع الفواتير مع عدد المنتجات وإجمالي السعر"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
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


def update_invoice_product(purchase_id, quantity, price):
    """تحديث منتج ضمن فاتورة"""
    total = quantity * price
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE purchases
        SET quantity = ?, price_per_unit = ?, total_price = ?
        WHERE id = ?
    """, (quantity, price, total, purchase_id))
    conn.commit()
    conn.close()


def delete_product_from_invoice(purchase_id):
    """حذف منتج من فاتورة"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM purchases WHERE id=?", (purchase_id,))
    conn.commit()
    conn.close()
