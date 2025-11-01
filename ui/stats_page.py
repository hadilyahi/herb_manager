from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📊 صفحة الإحصائيات"))
        self.setLayout(layout)
