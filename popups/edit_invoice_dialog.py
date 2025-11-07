import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_connection import get_connection


class EditInvoiceDialog(QDialog):
    def __init__(self, invoice_id):
        super().__init__()
        self.invoice_id = invoice_id
        self.setWindowTitle("🧾 تعديل الفاتورة")
        self.setMinimumWidth(750)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: black;
                border-radius: 12px;
            }
            QLabel {
                font-size: 15px;
                color: black;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #2ecc71;
                border-radius: 6px;
                background-color: #A3CBAB;
                color: black;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QTableWidget {
                background-color: #A3CBAB;
                border: 1px solid #ddd;
                border-radius: 6px;
                gridline-color: #ccc;
                color: black;
            }
        """)

        self.setup_ui()
        self.load_invoice_data()
        self.load_products_in_invoice()
        self.load_all_products()
        self.load_all_units()  # ⬅️ تحميل الوحدات من قاعدة البيانات

    # ===== واجهة المستخدم =====
    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("✏️ تعديل الفاتورة")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("29LT Bukra", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # معلومات عامة
        self.total_input = QLineEdit()
        self.date_input = QLineEdit()

        layout.addWidget(QLabel("إجمالي الفاتورة (دج):"))
        layout.addWidget(self.total_input)
        layout.addWidget(QLabel("تاريخ الفاتورة:"))
        layout.addWidget(self.date_input)

        # جدول المنتجات في الفاتورة
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["المنتج", "الوحدة", "الكمية", "السعر الفردي", "السعر الإجمالي", "🗑 حذف"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("🧺 المنتجات في هذه الفاتورة:"))
        layout.addWidget(self.table)

        # إضافة منتج جديد
        form_row = QHBoxLayout()
        self.product_combo = QComboBox()
        self.unit_combo = QComboBox()  # ⬅️ قائمة الوحدات بدل QLineEdit
        self.qty_input = QLineEdit()
        self.price_input = QLineEdit()
        add_btn = QPushButton("➕ إضافة المنتج")
        add_btn.clicked.connect(self.add_product_to_invoice)

        form_row.addWidget(QLabel("المنتج:"))
        form_row.addWidget(self.product_combo)
        form_row.addWidget(QLabel("الوحدة:"))
        form_row.addWidget(self.unit_combo)
        form_row.addWidget(QLabel("الكمية:"))
        form_row.addWidget(self.qty_input)
        form_row.addWidget(QLabel("السعر الفردي:"))
        form_row.addWidget(self.price_input)
        form_row.addWidget(add_btn)
        layout.addLayout(form_row)

        # زر الحفظ
        save_btn = QPushButton("💾 حفظ التعديلات")
        save_btn.clicked.connect(self.save_changes)
        layout.addWidget(save_btn)

    # ===== تحميل بيانات الفاتورة =====
    def load_invoice_data(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT total_price, date FROM invoices WHERE id = ?", (self.invoice_id,))
        invoice = cur.fetchone()
        conn.close()

        if invoice:
            self.total_input.setText(str(invoice["total_price"]))
            self.date_input.setText(invoice["date"])
        else:
            QMessageBox.warning(self, "خطأ", "❌ لم يتم العثور على الفاتورة.")

    # ===== تحميل المنتجات الحالية في الفاتورة =====
    def load_products_in_invoice(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT pu.id, p.name, u.name, pu.quantity, pu.price_per_unit, pu.total_price
            FROM purchases pu
            JOIN products p ON pu.product_id = p.id
            JOIN units u ON pu.unit_id = u.id
            WHERE pu.invoice_id = ?
        """, (self.invoice_id,))
        rows = cur.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(row[1]))
            self.table.setItem(i, 1, QTableWidgetItem(row[2]))
            self.table.setItem(i, 2, QTableWidgetItem(str(row[3])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row[4])))
            self.table.setItem(i, 4, QTableWidgetItem(str(row[5])))

            # زر حذف
            delete_btn = QPushButton("🗑")
            delete_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 6px;")
            delete_btn.clicked.connect(lambda _, pid=row[0]: self.delete_product_from_invoice(pid))
            self.table.setCellWidget(i, 5, delete_btn)

    # ===== تحميل قائمة المنتجات =====
    def load_all_products(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM products")
        self.products = cur.fetchall()
        conn.close()
        self.product_combo.clear()
        for p in self.products:
            self.product_combo.addItem(p["name"], p["id"])

    # ===== تحميل قائمة الوحدات =====
    def load_all_units(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM units")
        self.units = cur.fetchall()
        conn.close()
        self.unit_combo.clear()
        for u in self.units:
            self.unit_combo.addItem(u["name"], u["id"])

    # ===== إضافة منتج إلى الفاتورة =====
    def add_product_to_invoice(self):
        try:
            product_id = self.product_combo.currentData()
            unit_id = self.unit_combo.currentData()
            quantity = float(self.qty_input.text())
            price = float(self.price_input.text())
            total = quantity * price

            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO purchases (invoice_id, product_id, unit_id, quantity, price_per_unit, total_price, date)
                VALUES (?, ?, ?, ?, ?, ?, date('now'))
            """, (self.invoice_id, product_id, unit_id, quantity, price, total))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "✅", "تمت إضافة المنتج بنجاح.")
            self.load_products_in_invoice()
            self.update_invoice_total()
        except ValueError:
            QMessageBox.warning(self, "⚠️", "يرجى إدخال أرقام صحيحة للكمية والسعر.")

    # ===== حذف منتج من الفاتورة =====
    def delete_product_from_invoice(self, purchase_id):
        confirm = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا المنتج؟", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
            conn.commit()
            conn.close()
            self.load_products_in_invoice()
            self.update_invoice_total()

    # ===== تحديث إجمالي الفاتورة =====
    def update_invoice_total(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT SUM(total_price) FROM purchases WHERE invoice_id = ?", (self.invoice_id,))
        total = cur.fetchone()[0] or 0
        cur.execute("UPDATE invoices SET total_price = ? WHERE id = ?", (total, self.invoice_id))
        conn.commit()
        conn.close()
        self.total_input.setText(str(total))

    # ===== حفظ التعديلات العامة =====
    def save_changes(self):
        date = self.date_input.text().strip()
        total = float(self.total_input.text() or 0)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE invoices SET total_price = ?, date = ? WHERE id = ?", (total, date, self.invoice_id))
        conn.commit()
        conn.close()
        QMessageBox.information(self, "تم", "تم حفظ التعديلات بنجاح ✅")
        self.accept()
