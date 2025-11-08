import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QMessageBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from database.db_connection import DB_PATH


class EditPurchaseDialog(QDialog):
    def __init__(self, record_id, record_type="product"):
        super().__init__()
        self.record_id = record_id
        self.record_type = record_type
        self.setWindowTitle("تعديل السجل")
        self.setStyleSheet("background-color:white; color:black;")
        self.setFixedWidth(420)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("تعديل بيانات المشتريات")
        title.setFont(QFont("29LT Bukra", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # اسم المنتج
        self.name_label = QLabel("اسم المنتج:")
        self.name_label.setFont(QFont("29LT Bukra", 12))
        self.name_input = QLineEdit()
        self.name_input.setReadOnly(True)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # الكمية
        self.quantity_label = QLabel("الكمية:")
        self.quantity_label.setFont(QFont("29LT Bukra", 12))
        self.quantity_input = QLineEdit()
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)

        # السعر للوحدة
        self.price_label = QLabel("سعر الوحدة:")
        self.price_label.setFont(QFont("29LT Bukra", 12))
        self.price_input = QLineEdit()
        layout.addWidget(self.price_label)
        layout.addWidget(self.price_input)

        # الوحدة
        self.unit_label = QLabel("الوحدة:")
        self.unit_label.setFont(QFont("29LT Bukra", 12))
        self.unit_combo = QComboBox()
        layout.addWidget(self.unit_label)
        layout.addWidget(self.unit_combo)

        # تاريخ الانتهاء
        self.expiry_label = QLabel("تاريخ الانتهاء (اختياري):")
        self.expiry_label.setFont(QFont("29LT Bukra", 12))
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDisplayFormat("dd/MM/yyyy")
        self.expiry_date.setFixedWidth(120)
        self.expiry_date.setDate(QDate.currentDate())
        layout.addWidget(self.expiry_label)
        layout.addWidget(self.expiry_date)

        # الأزرار
        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.setDirection(QHBoxLayout.Direction.RightToLeft)

        btn_save = QPushButton("💾 حفظ")
        btn_save.setStyleSheet("background-color:#A3CBAB; border:none; border-radius:8px; padding:8px; font-weight:bold;")
        btn_save.clicked.connect(self.save_changes)

        btn_cancel = QPushButton("إلغاء")
        btn_cancel.setStyleSheet("background-color:#ccc; border:none; border-radius:8px; padding:8px; font-weight:bold;")
        btn_cancel.clicked.connect(self.reject)

        btns.addWidget(btn_save)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

        self.setLayout(layout)

    def load_data(self):
        """تحميل بيانات المشتريات"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # تحميل بيانات الشراء حسب record_id
        cur.execute("""
            SELECT 
                pr.id AS purchase_id,
                prod.name AS product_name,
                pr.quantity,
                pr.price_per_unit,
                pr.unit_id,
                pr.total_price,
                pr.date,
                pr.expiry_date
            FROM purchases pr
            JOIN products prod ON prod.id = pr.product_id
            WHERE pr.id=?
        """, (self.record_id,))
        row = cur.fetchone()

        # تحميل جميع الوحدات
        cur.execute("SELECT id, name FROM units")
        units = cur.fetchall()
        self.unit_combo.clear()
        for u in units:
            self.unit_combo.addItem(u["name"], u["id"])

        if row:
            self.name_input.setText(row["product_name"])
            self.quantity_input.setText(str(row["quantity"]))
            self.price_input.setText(str(row["price_per_unit"]))

            # تحديد الوحدة الحالية
            idx = self.unit_combo.findData(row["unit_id"])
            if idx >= 0:
                self.unit_combo.setCurrentIndex(idx)

            # تعيين تاريخ الانتهاء إذا موجود
            if row["expiry_date"]:
                dt = QDate.fromString(row["expiry_date"], "yyyy-MM-dd")
                if dt.isValid():
                    self.expiry_date.setDate(dt)

        conn.close()

    def save_changes(self):
        """حفظ التعديلات"""
        qty = self.quantity_input.text().strip()
        price = self.price_input.text().strip()

        if not qty or not price:
            QMessageBox.warning(self, "تنبيه", "الرجاء إدخال الكمية والسعر.")
            return

        try:
            qty = float(qty)
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "خطأ", "القيم المدخلة غير صحيحة.")
            return

        unit_id = self.unit_combo.currentData()
        total = qty * price

        expiry_qdate = self.expiry_date.date()
        expiry_str = expiry_qdate.toString("yyyy-MM-dd") if expiry_qdate else None

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            UPDATE purchases
            SET quantity=?, price_per_unit=?, total_price=?, unit_id=?, expiry_date=?
            WHERE id=?
        """, (qty, price, total, unit_id, expiry_str, self.record_id))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "تم", "تم حفظ التعديلات بنجاح ✅")
        self.accept()
