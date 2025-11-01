from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

from ui.products_page import ProductsPage
from ui.purchases_page import PurchasesPage
from ui.stats_page import StatsPage



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🪴 herb manager")
        self.setGeometry(300, 100, 1000, 650)

        # ⚙️ إعداد الخلفية العامة (بيضاء فقط)
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(p)

        # 🧭 شريط علوي
        navbar = self.create_navbar()

        # 🪴 محتوى الصفحات
        self.stack = QStackedWidget()
        self.products_page = ProductsPage()
        self.purchases_page = PurchasesPage()
        self.stats_page = StatsPage()
        self.stack.addWidget(self.products_page)
        self.stack.addWidget(self.purchases_page)
        self.stack.addWidget(self.stats_page)

        # ⚙️ تخطيط عام
        main_layout = QVBoxLayout()
        main_layout.addWidget(navbar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

    def create_navbar(self):
        """إنشاء الشريط العلوي"""
        bar = QWidget()
        bar.setStyleSheet("""
            background-color: #81C784;
            border-bottom: 2px solid #66BB6A;
        """)

        # أزرار التنقل
        btn_home = QPushButton("الرئيسية")
        btn_products = QPushButton("إدارة المنتجات")
        btn_purchases = QPushButton("إدارة المشتريات")
        btn_stats = QPushButton("الإحصائيات")

        for btn in [btn_home, btn_products, btn_purchases, btn_stats]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: black;
                    font-weight: bold;
                    font-size: 15px;
                    padding: 10px 18px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #A5D6A7;
                    border-radius: 6px;
                }
            """)

        # ربط الأزرار بالصفحات
        btn_products.clicked.connect(lambda: self.stack.setCurrentWidget(self.products_page))
        btn_purchases.clicked.connect(lambda: self.stack.setCurrentWidget(self.purchases_page))
        btn_stats.clicked.connect(lambda: self.stack.setCurrentWidget(self.stats_page))
        btn_home.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        # التخطيط الأفقي للشريط
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(btn_stats)
        layout.addWidget(btn_purchases)
        layout.addWidget(btn_products)
        layout.addWidget(btn_home)
        layout.addStretch()

        bar.setLayout(layout)
        return bar
