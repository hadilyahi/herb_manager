import sqlite3
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QWidget, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont
from database.db_connection import DB_PATH
from database.db_functions import fetch_products, insert_purchase


class AddPurchaseDialog(QDialog):
    def __init__(self, db_path=DB_PATH):
        super().__init__()
        self.db_path = db_path
        self.setWindowTitle("إضافة فاتورة جديدة")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # الحجم المبدئي والإعدادات
        self.min_height = 360
        self.max_height = 650
        self.current_height = self.min_height
        self.setFixedWidth(700)
        self.setFixedHeight(self.current_height)

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLabel {
                color: #000000;
                font-size: 14px;
                font-weight: 600;
            }
            QLineEdit, QComboBox {
                background-color: #DFF0D8;
                border: none;
                border-radius: 6px;
                padding: 4px 6px;
                color: #666666;
                font-size: 12px;
            }
            QPushButton {
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(10)

        # ---------------- Header ----------------
        header = QWidget()
        header.setStyleSheet("background-color: #ffffff; border-radius: 10px;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(6)

        title = QLabel("إضافة فاتورة جديدة")
        title.setFont(QFont("29LT Bukra", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        date_time_layout = QHBoxLayout()
        date_time_layout.setSpacing(10)
        date_time_layout.setDirection(QHBoxLayout.Direction.RightToLeft)

        lbl_date = QLabel("تاريخ الفاتورة :")
        self.date_edit = QLineEdit()
        self.date_edit.setReadOnly(True)
        self.date_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_time = QLabel("توقيت الفاتورة :")
        self.time_edit = QLineEdit()
        self.time_edit.setReadOnly(True)
        self.time_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)

        date_time_layout.addWidget(lbl_time)
        date_time_layout.addWidget(self.time_edit)
        date_time_layout.addWidget(lbl_date)
        date_time_layout.addWidget(self.date_edit)
        header_layout.addLayout(date_time_layout)
        main.addWidget(header)

        # تحديث التاريخ والوقت
        def update_dt():
            now = QDateTime.currentDateTime()
            self.date_edit.setText(now.toString("dd/MM/yyyy"))
            self.time_edit.setText(now.toString("HH:mm:ss"))
        timer = QTimer(self)
        timer.timeout.connect(update_dt)
        timer.start(1000)
        update_dt()

        # ---------------- Products Section ----------------
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        main.addWidget(self.scroll_area)

        # أول صف
        self.add_product_row()

        # زر إضافة منتج
        add_btn = QPushButton("⊕ إضافة منتج آخر")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet("background: transparent; color: #666; font-weight: 600;")
        add_btn.clicked.connect(self.handle_add_more)
        main.addWidget(add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # ---------------- Total ----------------
        total_layout = QHBoxLayout()
        total_layout.setDirection(QHBoxLayout.Direction.RightToLeft)
        lbl = QLabel("السعر الإجمالي للفاتورة كاملة:")
        lbl.setFont(QFont("29LT Bukra", 12, QFont.Weight.Bold))
        self.total_display = QLineEdit("0.00 دج")
        self.total_display.setReadOnly(True)
        self.total_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_display.setStyleSheet("""
            background-color: #DFF0D8;
            font-weight: bold;
            font-size: 14px;
            color: #333;
            border-radius: 8px;
        """)
        total_layout.addWidget(lbl)
        total_layout.addWidget(self.total_display)
        main.addLayout(total_layout)

        # ---------------- Buttons ----------------
        btns = QHBoxLayout()
        btns.setDirection(QHBoxLayout.Direction.RightToLeft)
        confirm = QPushButton("تأكيد")
        confirm.setStyleSheet("background-color: #1E5AF6; color: white;")
        confirm.setFixedHeight(44)
        confirm.clicked.connect(self.on_confirm)

        cancel = QPushButton("إلغاء")
        cancel.setStyleSheet("background-color: #D93025; color: white;")
        cancel.setFixedHeight(44)
        cancel.clicked.connect(self.reject)

        btns.addWidget(cancel)
        btns.addWidget(confirm)
        main.addLayout(btns)

    # ---------------- Helpers ----------------
    def add_product_row(self):
        row = QWidget()
        row.setStyleSheet("background-color: #FFFFFF; border-radius: 10px;")
        layout = QHBoxLayout(row)
        layout.setSpacing(10)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setDirection(QHBoxLayout.Direction.RightToLeft)  # ترتيب الأعمدة من اليمين لليسار

        # --- الحقول ---
        combo = QComboBox()
        combo.addItem("اختر المنتج ....", None)
        products = fetch_products()
        for p in products:
            combo.addItem(p[1], p[0])
        combo.setFixedWidth(160)
        combo.setStyleSheet("background-color: #E8F5E9; border-radius: 6px; color: #000;")
        combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        price = QLineEdit("0.00")
        price.setFixedWidth(70)
        price.setAlignment(Qt.AlignmentFlag.AlignRight)
        price.setStyleSheet("background-color: #E8F5E9; border-radius: 6px;")

        qty = QLineEdit("0")
        qty.setFixedWidth(50)
        qty.setAlignment(Qt.AlignmentFlag.AlignRight)
        qty.setStyleSheet("background-color: #E8F5E9; border-radius: 6px;")

        unit_combo = QComboBox()
        unit_combo.setFixedWidth(70)
        unit_combo.setStyleSheet("background-color: #E8F5E9; border-radius: 6px; color: #000;")
        unit_combo.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        subtotal = QLabel("0.00 دج")
        subtotal.setFixedWidth(80)
        subtotal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtotal.setStyleSheet("font-weight: bold; color: #000;")

        # ---------------- دوال مساعدة ----------------
        def update_units(idx):
            unit_combo.clear()
            product_id = combo.itemData(idx)

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # جلب جميع الوحدات
            cur.execute("SELECT id, name FROM units")
            all_units = cur.fetchall()

            # جلب وحدة المنتج إن وجدت
            selected_unit_id = None
            if product_id:
                cur.execute("SELECT unit_id FROM products WHERE id=?", (product_id,))
                result = cur.fetchone()
                if result:
                    selected_unit_id = result[0]

            conn.close()

            # إضافة الوحدات لكل القائمة
            for unit in all_units:
                unit_combo.addItem(unit[1], unit[0])

            # تحديد الوحدة الخاصة بالمنتج إذا وُجدت
            if selected_unit_id:
                index_to_select = unit_combo.findData(selected_unit_id)
                if index_to_select != -1:
                    unit_combo.setCurrentIndex(index_to_select)

            unit_combo.clear()
            product_id = combo.itemData(idx)
            if product_id:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                # جلب الوحدة الخاصة بالمنتج من جدول products مع جدول units
                cur.execute("""
                    SELECT units.id, units.name 
                    FROM products 
                    JOIN units ON products.unit_id = units.id 
                    WHERE products.id=?
                """, (product_id,))
                u = cur.fetchone()
                # إضافة كل الوحدات الممكنة من جدول units
                cur.execute("SELECT id, name FROM units")
                all_units = cur.fetchall()
                conn.close()
                if u:
                    # أضف الوحدة الخاصة أولاً
                    unit_combo.addItem(u[1], u[0])
                # أضف باقي الوحدات (تجنب تكرار الوحدة نفسها)
                for unit in all_units:
                    if u and unit[0] == u[0]:
                        continue
                    unit_combo.addItem(unit[1], unit[0])

        combo.currentIndexChanged.connect(update_units)
        combo.setCurrentIndex(0)
        update_units(0)

        def recalc():
            try:
                total = float(qty.text()) * float(price.text())
                subtotal.setText(f"{total:.2f} دج")
            except:
                subtotal.setText("0.00 دج")
            self.update_total_display()

        qty.textChanged.connect(recalc)
        price.textChanged.connect(recalc)

        # ---------------- Layouts ----------------
        def make_field_layout(label_text, widget):
            layout = QVBoxLayout()
            layout.setSpacing(2)
            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(lbl)
            layout.addWidget(widget)
            return layout

        layout.addLayout(make_field_layout("المجموع:", subtotal))
        layout.addLayout(make_field_layout("الوحدة:", unit_combo))
        layout.addLayout(make_field_layout("الكمية:", qty))
        layout.addLayout(make_field_layout("سعر الوحدة:", price))
        layout.addLayout(make_field_layout("المنتج:", combo))

        self.scroll_layout.addWidget(row)

    def handle_add_more(self):
        self.add_product_row()
        self.animate_growth()

    def animate_growth(self):
        if self.current_height < self.max_height:
            new_height = min(self.current_height + 60, self.max_height)
            anim = QPropertyAnimation(self, b"size")
            anim.setDuration(300)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.setStartValue(self.size())
            anim.setEndValue(QSize(self.width(), new_height))
            anim.finished.connect(lambda: self.setFixedHeight(new_height))
            anim.start()
            self.animation = anim
            self.current_height = new_height

    def update_total_display(self):
        total = 0
        for i in range(self.scroll_layout.count()):
            row = self.scroll_layout.itemAt(i).widget()
            for lbl in row.findChildren(QLabel):
                if lbl.text().endswith("دج"):
                    total += float(lbl.text().replace("دج", "").strip())
        self.total_display.setText(f"{total:.2f} دج")

    def on_confirm(self):
        total_value = float(self.total_display.text().replace("دج", "").strip())
        if total_value <= 0:
            QMessageBox.warning(self, "تنبيه", "يجب إضافة منتج واحد على الأقل.")
            return

        date_str = f"{self.date_edit.text()} {self.time_edit.text()}"

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("INSERT INTO invoices (date, total_price) VALUES (?, ?)", (date_str, total_value))
        invoice_id = cur.lastrowid

        for i in range(self.scroll_layout.count()):
            row = self.scroll_layout.itemAt(i).widget()
            combo = row.findChildren(QComboBox)[0]
            unit_combo = row.findChildren(QComboBox)[1]
            qty = row.findChildren(QLineEdit)[0]
            price = row.findChildren(QLineEdit)[1]

            product_id = combo.currentData()
            unit_id = unit_combo.currentData()
            quantity = float(qty.text())
            price_per_unit = float(price.text())
            total_price = quantity * price_per_unit

            if product_id and unit_id:
                cur.execute("""
                    INSERT INTO purchases (invoice_id, product_id, unit_id, quantity, price_per_unit, total_price, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (invoice_id, product_id, unit_id, quantity, price_per_unit, total_price, date_str))

        conn.commit()
        conn.close()
        QMessageBox.information(self, "تم", "تم حفظ الفاتورة بنجاح ✅")
        self.accept()
