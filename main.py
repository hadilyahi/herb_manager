import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont  # ✅ هذا السطر هو المهم
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # تحميل الخط 29LT Bukra
    font_id = QFontDatabase.addApplicationFont("assets/font/29ltbukrabolditalic.ttf")
    if font_id != -1:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 12))  
       
    

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
