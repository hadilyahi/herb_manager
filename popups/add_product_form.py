from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
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
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        lbl_name = QLabel("اسم المنتج:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("أدخل اسم المنتج...")

        lbl_category = QLabel("الفئة:")
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.lineEdit().setAlignment(Qt.AlignmentFlag.AlignRight)

        lbl_description = QLabel("الوصف (اختياري):")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("أدخل وصفًا للمنتج إن وُجد...")

        # الأزرار
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("إلغاء")
        btn_save = QPushButton("تأكيد")
        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_product)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_save)

        layout.addWidget(lbl_name)
        layout.addWidget(self.name_input)
        layout.addWidget(lbl_category)
        layout.addWidget(self.category_combo)
        layout.addWidget(lbl_description)
        layout.addWidget(self.description_input)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_data(self):
        self.category_combo.clear()
        self.category_combo.addItem("اختر الفئة", None)
        categories = fetch_categories()
        for cat in categories:
            self.category_combo.addItem(cat[1], cat[0])

    def save_product(self):
        name = self.name_input.text().strip()
        category_id = self.category_combo.currentData()
        description = self.description_input.toPlainText().strip() or None

        if not name:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المنتج.")
            return

        self.on_save(name, category_id, None, None, description)
        self.accept()
