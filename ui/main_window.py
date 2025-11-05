from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QKeySequence, QShortcut
import json
import os

from ui.products_page import ProductsPage
from ui.purchases_page import PurchasesPage
from ui.stats_page import StatsPage


# ----------------------------------------
# الصفحة الرئيسية
# ----------------------------------------
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("مرحباً بك في تطبيق 🌿 Herb Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: black;")

        desc = QLabel("اختر من القائمة أعلاه لإدارة المنتجات، المشتريات أو الإحصائيات.")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 16px; color: black; margin-top: 10px;")

        layout.addWidget(title)
        layout.addWidget(desc)
        self.setLayout(layout)


# ----------------------------------------
# النافذة الرئيسية
# ----------------------------------------
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🪴 Herb Manager")
        self.setGeometry(300, 100, 1000, 650)

        # خلفية بيضاء
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        self.setPalette(p)

        # الصفحات
        self.stack = QStackedWidget()
        self.home_page = HomePage()
        self.products_page = ProductsPage()
        self.purchases_page = PurchasesPage()
        self.stats_page = StatsPage()

        self.stack.addWidget(self.home_page)       # فهرس 0
        self.stack.addWidget(self.products_page)   # فهرس 1
        self.stack.addWidget(self.purchases_page)  # فهرس 2
        self.stack.addWidget(self.stats_page)      # فهرس 3

        # شريط التنقل
        navbar = self.create_navbar()

        # التخطيط العام
        main_layout = QVBoxLayout()
        main_layout.addWidget(navbar)
        main_layout.addWidget(self.stack)
        self.setLayout(main_layout)

        # تفعيل الاختصارات
        self.setup_shortcuts()

    # ----------------------------------------
    # إنشاء شريط التنقل
    # ----------------------------------------
    def create_navbar(self):
        bar = QWidget()
        bar.setStyleSheet("""
            background-color: #ffffff;
            border: none;
            padding: 10px;
        """)

        # الأزرار
        buttons_info = [
            ("تسجيل الخروج\nF9", None, "F9"),
            ("الإحصائيات\nF7", self.stats_page, "F7"),
            ("إدارة المشتريات\nF5", self.purchases_page, "F5"),
            ("إدارة المنتجات\nF3", self.products_page, "F3"),
            ("الرئيسية\nF1", self.home_page, "F1"),
        ]

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        self.nav_buttons = []
        for text, page, key in buttons_info:
            btn = QPushButton(text)
            btn.setFixedSize(130, 70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #d3d3d3;
                    color: black;
                    font-weight: bold;
                    font-size: 13px;
                    border-radius: 12px;
                    border: 1px solid #bdbdbd;
                }
                QPushButton:hover {
                    background-color: #c0c0c0;
                }
            """)

            if page is not None:
                btn.clicked.connect(lambda _, p=page: self.stack.setCurrentWidget(p))
            else:
                btn.clicked.connect(self.logout)  # 🔹 هنا نربط زر الخروج بدالة logout()

            layout.addWidget(btn)
            self.nav_buttons.append((btn, key, page))

        bar.setLayout(layout)
        return bar

    # ----------------------------------------
    # إعداد الاختصارات (F1 - F9)
    # ----------------------------------------
    def setup_shortcuts(self):
        shortcuts = {
            "F1": self.home_page,
            "F3": self.products_page,
            "F5": self.purchases_page,
            "F7": self.stats_page,
            "F9": None,  # خروج
        }

        for key, page in shortcuts.items():
            sc = QShortcut(QKeySequence(key), self)
            if page is not None:
                sc.activated.connect(lambda p=page: self.stack.setCurrentWidget(p))
            else:
                sc.activated.connect(self.logout)  # 🔹 زر F9 أيضًا للخروج

    # ----------------------------------------
    # دالة تسجيل الخروج
    # ----------------------------------------
    def logout(self):
        """تسجيل الخروج وإعادة المستخدم إلى صفحة تسجيل الدخول"""
        try:
            # تحديث حالة الجلسة
            with open("session.json", "w", encoding="utf-8") as f:
                json.dump({"logged_in": False}, f)
        except Exception as e:
            print(f"❌ خطأ أثناء تحديث ملف الجلسة: {e}")

        # استيراد نافذة تسجيل الدخول
        from ui.login_window import LoginWindow

        # إغلاق النافذة الحالية وفتح نافذة تسجيل الدخول
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


# ----------------------------------------
# تشغيل التطبيق بشكل مستقل للاختبار
# ----------------------------------------
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
