from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class ProductDetailsDialog(QDialog):
    def __init__(self, product_data):
        super().__init__()
        self.product_data = product_data  # tuple: (id, name, category, description)
        self.setWindowTitle("تفاصيل المنتج")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        prod_id, name, category, description = self.product_data  # الآن 4 عناصر فقط

        lbl_name = QLabel(f"<b>اسم المنتج:</b> {name}")
        lbl_name.setWordWrap(True)
        layout.addWidget(lbl_name)

        lbl_category = QLabel(f"<b>الفئة:</b> {category if category else 'غير مصنف'}")
        lbl_category.setWordWrap(True)
        layout.addWidget(lbl_category)

        lbl_description = QLabel(f"<b>الوصف:</b> {description if description else 'لا يوجد وصف'}")
        lbl_description.setWordWrap(True)
        layout.addWidget(lbl_description)

        # زر إغلاق
        btn_close = QPushButton("إغلاق")
        btn_close.clicked.connect(self.accept)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
