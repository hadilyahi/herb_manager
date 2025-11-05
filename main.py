import sys
import os
import json
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont

from ui.login_window import LoginWindow


SESSION_FILE = "session.json"

if __name__ == "__main__":
    app = QApplication(sys.argv)

  
    font_path = "assets/font/29ltbukrabolditalic.ttf"
    font_id = QFontDatabase.addApplicationFont(font_path)
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))  
    else:
        print(f"⚠️ لم يتم العثور على الخط في المسار المحدد: {font_path}")


    DEV_MODE = True

    if DEV_MODE:
      
        from ui.main_window import MainWindow
        window = MainWindow()
    else:
      
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE, "r", encoding="utf-8") as f:
                    session = json.load(f)
                if session.get("logged_in"):
                    from ui.main_window import MainWindow
                    window = MainWindow()
                else:
                    window = LoginWindow()
            except Exception:
                window = LoginWindow()
        else:
            window = LoginWindow()

   
    window.show()
    sys.exit(app.exec())
