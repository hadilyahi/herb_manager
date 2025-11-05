from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtCore import Qt

class ProductDetailsDialog(QDialog):
    def __init__(self, product_data):
        super().__init__()
        self.product_data = product_data
        self.setWindowTitle("تفاصيل المنتج")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(400)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #E8F5E9; }
            QLabel { font-size: 14px; color: black; }
            QTextEdit { 
                background-color: white; 
                color: black; 
                border: 1px solid #A5D6A7; 
                border-radius: 8px; 
                font-size: 14px; 
                padding: 6px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        product_id, name, category, expiry_date, description = self.product_data

        lbl_name = QLabel(f"<b>اسم المنتج:</b> {name}")
        lbl_category = QLabel(f"<b>الفئة:</b> {category or 'غير مصنف'}")
        lbl_expiry = QLabel(f"<b>تاريخ الانتهاء:</b> {expiry_date or 'غير محدد'}")
        lbl_desc = QLabel("<b>الوصف:</b>")
        txt_desc = QTextEdit()
        txt_desc.setReadOnly(True)
        txt_desc.setPlainText(description or "")
        txt_desc.setFixedHeight(80)

        for w in [lbl_name, lbl_category, lbl_expiry, lbl_desc, txt_desc]:
            layout.addWidget(w)

        self.setLayout(layout)
