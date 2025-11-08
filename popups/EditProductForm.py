from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from database.db_functions import fetch_categories

class EditProductForm(QDialog):
    def __init__(self, product_data, on_save):
        super().__init__()
        self.on_save = on_save
        self.product_data = product_data  # tuple: (id, name, category, description)
        self.setWindowTitle("تعديل المنتج")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(480)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #E8F5E9; }
            QLabel { font-size: 14px; font-weight: 500; color: black; }
            QLineEdit, QTextEdit, QComboBox { 
                font-size: 14px; color: black; background-color: white; border: 1px solid #A5D6A7; border-radius: 8px; padding: 6px;
            }
            QPushButton { 
                color: black; border-radius: 12px; padding: 6px 30px; font-size: 14px; border: 1px solid #9E9E9E; 
            }
            QPushButton:hover { background-color: #A5D6A7; }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        # الاسم
        lbl_name = QLabel("اسم المنتج:")
        self.name_input = QLineEdit()
        layout.addWidget(lbl_name)
        layout.addWidget(self.name_input)

        # الفئة
        lbl_category = QLabel("الفئة:")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.lineEdit().setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_category)
        layout.addWidget(self.category_combo)

        # الوصف
        lbl_desc = QLabel("الوصف (اختياري):")
        self.description_input = QTextEdit()
        layout.addWidget(lbl_desc)
        layout.addWidget(self.description_input)

        # الأزرار
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("حفظ")
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_product)
        btn_layout.addWidget(btn_save)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_data(self):
        prod_id, name, category, description = self.product_data
        self.name_input.setText(name)

        categories = fetch_categories()
        self.category_combo.addItem("اختر الفئة", None)
        for cat in categories:
            self.category_combo.addItem(cat[1], cat[0])
        if category:
            index = self.category_combo.findText(category)
            if index != -1:
                self.category_combo.setCurrentIndex(index)

        self.description_input.setText(description or "")

    def save_product(self):
        name = self.name_input.text().strip()
        category_id = self.category_combo.currentData()
        description = self.description_input.toPlainText().strip() or None

        if not name:
            return

        self.on_save(name, category_id, None, description)  # لم يعد هناك expiry_date
        self.accept()
