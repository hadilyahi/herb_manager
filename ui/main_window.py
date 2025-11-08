from PyQt6.QtCore import Qt, QCoreApplication
QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QHBoxLayout,
    QLabel, QStackedWidget, QApplication
)

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor, QKeySequence, QShortcut
import json
import os
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap


from ui.products_page import ProductsPage
from ui.purchases_page import PurchasesPage
from ui.stats_page import  StatsWindow

QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

from PyQt6.QtWebEngineWidgets import QWebEngineView

# ----------------------------------------
# الصفحة الرئيسية
# ----------------------------------------


class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.current_image_index = 0
        self.images = [
            "assets/page_one/photo1.png",
            "assets/page_one/photo2.png",
            "assets/page_one/photo3.png"
        ]
        self.setup_ui()
        self.start_image_rotation()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setSpacing(50)

        # --------------------
        # الصورة على اليسار
        # --------------------
        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label)

        # --------------------
        # النصوص على اليمين
        # --------------------
        text_layout = QVBoxLayout()
        text_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        

        self.title = QLabel("مرحباً بك في\nبرنامج إدارة")
        self.title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.title.setStyleSheet("font-size: 55px; font-weight: bold; color: black;")
        text_layout.addWidget(self.title)

        self.subtitle = QLabel(" عشاب السلطان")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.subtitle.setStyleSheet("font-size: 55px; font-weight: bold; color: green; margin-top: 8px;")
        text_layout.addWidget(self.subtitle)

        main_layout.addLayout(text_layout)

        self.setLayout(main_layout)

    def start_image_rotation(self):
        self.update_image()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(3000)

    def update_image(self):
        pixmap = QPixmap(self.images[self.current_image_index])
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        self.current_image_index = (self.current_image_index + 1) % len(self.images)


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
        self.stats_page =  StatsWindow()

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

            buttons_info = [
                ("تسجيل الخروج", None, "F9"),
                ("الإحصائيات", self.stats_page, "F7"),
                ("إدارة المشتريات", self.purchases_page, "F5"),
                ("إدارة المنتجات", self.products_page, "F3"),
                ("الرئيسية", self.home_page, "F1"),
            ]

            layout = QHBoxLayout()
            layout.setContentsMargins(20, 0, 20, 0)
            layout.setSpacing(0)

            self.nav_buttons = []

            for i, (main_text, page, shortcut) in enumerate(buttons_info):
                # إنشاء زر كـ QWidget
                btn_widget = QWidget()
                btn_widget.setFixedSize(130, 70)
                btn_layout = QVBoxLayout()
                btn_layout.setContentsMargins(0, 0, 0, 0)
                btn_layout.setSpacing(0)
                btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # النص الرئيسي
                label_main = QLabel(main_text)
                label_main.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_main.setStyleSheet("color: black; font-weight: bold; font-size: 13px;")
                btn_layout.addWidget(label_main)

                # الاختصار باللون الأزرق
                label_shortcut = QLabel(shortcut)
                label_shortcut.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_shortcut.setStyleSheet("color: blue; font-size: 11px;")
                btn_layout.addWidget(label_shortcut)

                btn_widget.setLayout(btn_layout)
                btn_widget.setStyleSheet("""
                    QWidget {
                        background-color: #d3d3d3;
                        border-radius: 12px;
                        
                    }
                   
                """)
                btn_widget.setCursor(Qt.CursorShape.PointingHandCursor)

                # ربط الضغط بالوظيفة المناسبة
                def make_callback(p=page):
                    if p is not None:
                        return lambda _: self.stack.setCurrentWidget(p)
                    else:
                        return lambda _: self.logout()

                btn_widget.mousePressEvent = make_callback(page)

                layout.addWidget(btn_widget)
                self.nav_buttons.append((btn_widget, shortcut, page))

                # إضافة مساحة مرنة بين الأزرار إلا بعد الأخير
                if i != len(buttons_info) - 1:
                    layout.addStretch(1)

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
