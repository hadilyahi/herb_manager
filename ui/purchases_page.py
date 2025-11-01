from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("💰 صفحة إدارة  المشتريات"))
        self.setLayout(layout)
