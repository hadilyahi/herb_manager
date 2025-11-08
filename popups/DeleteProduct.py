from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class DeleteProductDialog(QDialog):
    def __init__(self, product_name, on_confirm):
        super().__init__()
        self.product_name = product_name
        self.on_confirm = on_confirm
        self.setWindowTitle("تأكيد الحذف")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setFixedWidth(350)
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #E8F5E9; color: black; }
            QLabel { font-size: 14px; color: black; }
            QPushButton { color: black; border-radius: 10px; padding: 6px 25px; font-size: 14px; }
            QPushButton:hover { background-color: #A5D6A7; }
        """)

        layout = QVBoxLayout()
        label = QLabel(f"هل أنت متأكد أنك تريد حذف المنتج: {self.product_name}?")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        btn_confirm = QPushButton("حذف")
        btn_cancel = QPushButton("إلغاء")
        btn_cancel.clicked.connect(self.reject)
        btn_confirm.clicked.connect(self.confirm_delete)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_confirm)

        layout.addWidget(label)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def confirm_delete(self):
        self.on_confirm()
        self.accept()
