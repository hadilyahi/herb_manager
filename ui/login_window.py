import sys, json, os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette
from auth_utils import verify_password  

SESSION_FILE = "session.json"
ADMIN_DB = "database/admin.json"


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🪴 تسجيل الدخول - Herb Manager")
        self.setFixedSize(450, 400)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setup_ui()

    def setup_ui(self):
        # خلفية الصفحة
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.ColorRole.Window, QColor("white"))
        self.setPalette(p)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        # العنوان الرئيسي
        title = QLabel("عشاب السلطان")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #1B5E20;")

        subtitle = QLabel("عند لمجد العشاب")
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: black;")

        # صندوق تسجيل الدخول
        login_box = QWidget()
        login_box.setStyleSheet("""
            background-color: #E6F4EA;
            border-radius: 15px;
        """)
        login_layout = QVBoxLayout()
        login_layout.setContentsMargins(40, 40, 40, 40)
        login_layout.setSpacing(24)

        # الاسم
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("الاسم:")
        self.username_input.setStyleSheet("""
            background-color: #A3CBAB;
            padding: 8px;
            border-radius: 8px;
            border: none;
            color: black;
            height: 25px;
            font-size: 13px;
        """)

        # كلمة المرور
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور:")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            background-color: #A3CBAB;
            padding: 8px;
            border-radius: 8px;
            border: none;
            color: black;
            height: 25px;
            font-size: 13px;
        """)

        # زر الدخول
        login_button = QPushButton("الدخول")
        login_button.clicked.connect(self.handle_login)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #1565c0;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
                font-size: 13px;
                height: 20px;
            }
            QPushButton:hover {
                background-color: #0d47a1;
            }
        """)

        login_layout.addWidget(self.username_input)
        login_layout.addWidget(self.password_input)
        login_layout.addWidget(login_button)
        login_box.setLayout(login_layout)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addWidget(login_box)
        self.setLayout(main_layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        # التحقق من وجود ملف قاعدة البيانات
        if not os.path.exists(ADMIN_DB):
            QMessageBox.critical(self, "خطأ", "ملف المستخدمين غير موجود!")
            return

        with open(ADMIN_DB, "r", encoding="utf-8") as f:
            users = json.load(f)

        user = next((u for u in users if u["username"] == username), None)

        if user and verify_password(user["password"], password):
            self.save_session(username)
            QMessageBox.information(self, "تم الدخول", "تم تسجيل الدخول بنجاح ✅")
            self.open_main_window()
            self.close()
        else:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة ❌")

    def save_session(self, username):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"logged_in": True, "username": username}, f)

    def open_main_window(self):
        from ui.main_window import MainWindow
        self.main = MainWindow()
        self.main.show()


# النافذة الرئيسية
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("الصفحة الرئيسية 🌿")
        self.setFixedSize(500, 400)
        layout = QVBoxLayout()
        label = QLabel("مرحبًا بك في نظام عشاب السلطان!", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)


# تشغيل التطبيق
if __name__ == "__main__":
    app = QApplication(sys.argv)

    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            session = json.load(f)
            if session.get("logged_in"):
                window = MainWindow()
            else:
                window = LoginWindow()
    else:
        window = LoginWindow()

    window.show()
    sys.exit(app.exec())
