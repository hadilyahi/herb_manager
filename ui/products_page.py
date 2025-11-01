from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from database.db_functions import fetch_products, fetch_categories, add_category_to_db, get_connection
from popups.add_category_form import AddCategoryForm
from popups.add_product_form import AddProductForm   # 🔹 استيراد بوباب إضافة المنتج الجديد


class ProductsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        title = QLabel("إدارة المنتجات")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: black; margin-top: 10px; margin-bottom: 20px;")

        # الأزرار
        btn_add_category = QPushButton("➕ إضافة فئة جديدة")
        btn_add_product = QPushButton("➕ إضافة منتج جديد")
        for btn in [btn_add_category, btn_add_product]:
            btn.setStyleSheet("""
                background-color: #C8E6C9;
                border: 1px solid #388E3C;
                color: black;
                border-radius: 15px;
                padding: 6px 18px;
                font-size: 13px;
                font-weight: 500;
            """)

        btn_add_category.clicked.connect(self.open_add_category_popup)
        btn_add_product.clicked.connect(self.open_add_product_popup)

        button_layout = QHBoxLayout()
        button_layout.addWidget(btn_add_product)
        button_layout.addWidget(btn_add_category)
        button_layout.addStretch()

        # جدول المنتجات الآن 5 أعمدة
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["المنتج", "الفئة", "تاريخ الانتهاء", "الوصف", "التفاصيل"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #E8F5E9;
                alternate-background-color: #F1F8E9;
                gridline-color: #A5D6A7;
                font-size: 15px;
                color: black;
                selection-background-color: #A5D6A7;
            }
            QHeaderView::section {
                background-color: #A5D6A7;
                font-weight: bold;
                font-size: 16px;
                color: black;
                border: none;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def load_data(self):
        products = fetch_products()
        self.table.setRowCount(len(products))

        for row, (prod_id, name, category, expiry_date, description) in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(category if category else "غير مصنف"))
            self.table.setItem(row, 2, QTableWidgetItem(expiry_date if expiry_date else "—"))
            self.table.setItem(row, 3, QTableWidgetItem(description if description else "—"))
            self.table.setCellWidget(row, 4, self.create_action_buttons())

    def create_action_buttons(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)

        btn_delete = QPushButton()
        btn_delete.setIcon(QIcon("assets/icons/delete.svg"))
        btn_delete.setToolTip("حذف")
        btn_delete.setStyleSheet("background: none; border: none;")

        btn_edit = QPushButton()
        btn_edit.setIcon(QIcon("assets/icons/edit.svg"))
        btn_edit.setToolTip("تعديل")
        btn_edit.setStyleSheet("background: none; border: none;")

        btn_info = QPushButton()
        btn_info.setIcon(QIcon("assets/icons/more.svg"))
        btn_info.setToolTip("تفاصيل")
        btn_info.setStyleSheet("background: none; border: none;")

        for btn in [btn_delete, btn_edit, btn_info]:
            layout.addWidget(btn)

        container = QWidget()
        container.setLayout(layout)
        return container

    def open_add_category_popup(self):
        categories_list = fetch_categories()

        def on_save(name, parent_id):
            add_category_to_db(name, parent_id)
            self.load_data()

        popup = AddCategoryForm(on_save)
        popup.exec()

    def open_add_product_popup(self):
        def on_save(name, category_id, unit_id, expiry_date, description):
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO products (name, category_id, unit_id, expiry_date, description)
                VALUES (?, ?, ?, ?, ?)
            """, (name, category_id, unit_id, expiry_date, description))
            conn.commit()
            conn.close()
            self.load_data()

        popup = AddProductForm(on_save)
        popup.exec()
