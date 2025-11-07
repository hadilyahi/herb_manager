import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QHBoxLayout, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_connection import get_connection


class DetailsInvoiceDialog(QDialog):
    def __init__(self, invoice_id):
        super().__init__()
        self.invoice_id = invoice_id
        self.setWindowTitle("تفاصيل الفاتورة")
        self.setMinimumWidth(800)
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 10px;
            }
            QLabel {
                font-family: '29LT Bukra';
                color: #333333;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QTableWidget {
                background-color: #A3CBAB;
                alternate-background-color: #f0f0f0;
                border: 1px solid #ccc;
                font-size: 13px;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #A3CBAB;
                padding: 5px;
                font-weight: bold;
                border: 1px solid #d0d0d0;
            }
        """)
        self.setup_ui()
        self.load_invoice_details()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # العنوان
        self.title_label = QLabel("تفاصيل الفاتورة", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("29LT Bukra", 18, QFont.Weight.Bold))

        # معلومات الفاتورة
        self.info_label = QLabel("", self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14px; margin-bottom: 8px; color: #555;")

        # جدول التفاصيل
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المنتج", "الوحدة", "الكمية", "السعر الفردي", "السعر الإجمالي"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # زر الإغلاق
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)

        layout.addWidget(self.title_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)

    def load_invoice_details(self):
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # جلب بيانات الفاتورة
        cur.execute("SELECT id, total_price, date FROM invoices WHERE id = ?", (self.invoice_id,))
        invoice = cur.fetchone()

        # جلب المنتجات المرتبطة بالفاتورة
        cur.execute("""
            SELECT p.name AS product_name, u.name AS unit_name, pu.quantity, pu.price_per_unit, pu.total_price
            FROM purchases pu
            JOIN products p ON pu.product_id = p.id
            JOIN units u ON pu.unit_id = u.id
            WHERE pu.invoice_id = ?
        """, (self.invoice_id,))
        rows = cur.fetchall()
        conn.close()

        if not invoice:
            self.info_label.setText("❌ لم يتم العثور على الفاتورة.")
            return

        self.info_label.setText(
            f"🧾 رقم الفاتورة: {invoice['id']}  |  💰 الإجمالي: {invoice['total_price']} دج  |  📅 التاريخ: {invoice['date']}"
        )

        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(r["product_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["unit_name"]))
            self.table.setItem(i, 2, QTableWidgetItem(str(r["quantity"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(r["price_per_unit"])))
            self.table.setItem(i, 4, QTableWidgetItem(str(r["total_price"])))
