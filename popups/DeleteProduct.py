from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class DeleteProductDialog(QDialog):
    def __init__(self, product_name, on_confirm):
        super().__init__()
        self.on_confirm = on_confirm
        self.setWindowTitle("تأكيد الحذف")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(350)
        self.setup_ui(product_name)

    def setup_ui(self, product_name):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl = QLabel(f"هل أنت متأكد من حذف المنتج:\n\"{product_name}\"؟")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("font-size: 14px; font-weight: 500; color: black;")
        layout.addWidget(lbl)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_cancel = QPushButton("إلغاء")
        btn_confirm = QPushButton("حذف")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm.clicked.connect(self.confirm_delete)

        for btn, color in [(btn_cancel, "#FFCDD2"), (btn_confirm, "#C8E6C9")]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 12px;
                    padding: 6px 25px;
                    font-size: 14px;
                    color: black;
                }}
                QPushButton:hover {{
                    background-color: #A5D6A7;
                }}
            """)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def confirm_delete(self):
        self.on_confirm()
        self.accept()
