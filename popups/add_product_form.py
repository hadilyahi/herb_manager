from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QDateEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate
from database.db_functions import fetch_categories


class AddProductForm(QDialog):
    def __init__(self, on_save):
        super().__init__()
        self.on_save = on_save
        self.setWindowTitle("إضافة منتج جديد")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(480)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #E8F5E9;
            }
            QLabel {
                font-size: 14px;
                font-weight: 500;
                color: black;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        # --- اسم المنتج ---
        lbl_name = QLabel("اسم المنتج:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم المنتج...")
        self.name_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border-radius: 10px;
                border: 1px solid #A5D6A7;
                background-color: white;
                min-width: 350px;
                color: black;
            }
        """)

        # --- الفئة ---
        lbl_category = QLabel("الفئة:")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.lineEdit().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.category_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border-radius: 10px;
                border: 1px solid #A5D6A7;
                background-color: white;
                min-width: 350px;
                color: black;
            }
        """)

        # --- تاريخ الانتهاء (اختياري) ---
        lbl_expiry = QLabel("تاريخ الانتهاء (اختياري):")
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setSpecialValueText("")  # لإظهار الحقل فارغًا
        self.expiry_date.setDate(QDate(2000, 1, 1))  # قيمة افتراضية غير صالحة للتاريخ
        self.expiry_date.setMinimumDate(QDate(2000, 1, 1))
        self.expiry_date.setStyleSheet("""
            QDateEdit {
                padding: 8px;
                font-size: 14px;
                border-radius: 10px;
                border: 1px solid #A5D6A7;
                background-color: white;
                min-width: 350px;
                color: black;
            }
        """)

        # --- الوصف (اختياري) ---
        lbl_description = QLabel("الوصف (اختياري):")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("أدخل وصفًا للمنتج إن وُجد...")
        self.description_input.setStyleSheet("""
            QTextEdit {
                padding: 8px;
                font-size: 14px;
                border-radius: 10px;
                border: 1px solid #A5D6A7;
                background-color: white;
                min-width: 350px;
                min-height: 90px;
                color: black;
            }
        """)

        # --- الأزرار ---
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.setSpacing(25)

        btn_cancel = QPushButton("إلغاء")
        btn_save = QPushButton("تأكيد")
        for btn, color in [(btn_cancel, "#FFCDD2"), (btn_save, "#C8E6C9")]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 12px;
                    font-size: 14px;
                    padding: 6px 35px;
                    border: 1px solid #9E9E9E;
                    color: black;
                }}
                QPushButton:hover {{
                    background-color: #A5D6A7;
                }}
            """)

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_product)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        
        layout.addWidget(lbl_name)
        layout.addWidget(self.name_input)
        layout.addWidget(lbl_category)
        layout.addWidget(self.category_combo)
        layout.addWidget(lbl_expiry)
        layout.addWidget(self.expiry_date)
        layout.addWidget(lbl_description)
        layout.addWidget(self.description_input)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    # ✅ تحميل بيانات الفئات
    def load_data(self):
        self.category_combo.clear()
        self.category_combo.addItem("اختر الفئة", None)
        categories = fetch_categories()
        for cat in categories:
            self.category_combo.addItem(cat[1], cat[0])

    # ------------------- دالة حفظ المنتج -------------------
    def save_product(self):
        name = self.name_input.text().strip()
        category_id = self.category_combo.currentData()

        # ✅ جعل التاريخ اختياري وفارغ بشكل افتراضي
        if self.expiry_date.date() == QDate(2000, 1, 1):  # لم يختار المستخدم تاريخًا
            expiry_date = None
        else:
            expiry_date = self.expiry_date.date().toString("yyyy-MM-dd")

        description = self.description_input.toPlainText().strip() or None

        if not name:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المنتج.")
            return

        self.on_save(name, category_id, None, expiry_date, description)
        self.accept()
