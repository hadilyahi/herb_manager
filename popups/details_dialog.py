from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_connection import DB_PATH
import sqlite3


class DetailsDialog(QDialog):
    def __init__(self, record_id, record_type="product"):
        super().__init__()
        self.record_id = record_id
        self.record_type = record_type
        self.setWindowTitle("تفاصيل السجل")
        self.setStyleSheet("background-color:white; color:black;")
        self.setFixedWidth(400)
        self.setup_ui()
        self.load_details()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("تفاصيل السجل")
        title.setFont(QFont("29LT Bukra", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.details_label = QLabel()
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.details_label.setWordWrap(True)
        self.details_label.setFont(QFont("29LT Bukra", 13))
        layout.addWidget(self.details_label)

        btn_close = QPushButton("إغلاق")
        btn_close.setStyleSheet(
            "background-color:#A3CBAB; border:none; border-radius:10px; padding:8px; font-weight:bold;"
        )
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def load_details(self):
        """تحميل تفاصيل السجل"""
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        text = ""
        row = None

        # ✅ حالة عرض تفاصيل منتج من جدول المشتريات
        if self.record_type == "product":
            cur.execute("""
                SELECT 
                    p.name AS product_name,
                    u.name AS unit_name,
                    pu.quantity,
                    pu.price_per_unit,
                    pu.total_price,
                    pu.date
                FROM purchases pu
                JOIN products p ON pu.product_id = p.id
                JOIN units u ON pu.unit_id = u.id
                WHERE pu.id = ?
            """, (self.record_id,))
            row = cur.fetchone()

            if row:
                text = f"""
                <b>اسم المنتج:</b> {row[0]}<br>
                <b>الوحدة:</b> {row[1]}<br>
                <b>الكمية:</b> {row[2]}<br>
                <b>سعر الوحدة:</b> {row[3]}<br>
                <b>السعر الإجمالي:</b> {row[4]}<br>
                <b>تاريخ الشراء:</b> {row[5]}
                """

        # ✅ حالة عرض تفاصيل فاتورة كاملة
        else:
            cur.execute("""
                SELECT i.date, COUNT(pu.id) AS num_products, SUM(pu.total_price) AS total_price
                FROM invoices i
                LEFT JOIN purchases pu ON i.id = pu.invoice_id
                WHERE i.id = ?
                GROUP BY i.id
            """, (self.record_id,))
            row = cur.fetchone()

            if row:
                text = f"""
                <b>تاريخ الفاتورة:</b> {row[0]}<br>
                <b>عدد المنتجات:</b> {row[1]}<br>
                <b>إجمالي السعر:</b> {row[2]}
                """

        conn.close()
        self.details_label.setText(text if row else "❌ لم يتم العثور على البيانات.")
