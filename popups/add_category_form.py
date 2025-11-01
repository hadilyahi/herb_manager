from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QComboBox, QWidget
)
from PyQt6.QtCore import Qt
from database.db_functions import fetch_categories  # افترض أنك جلبت الدالة من قاعدة البيانات


class AddCategoryForm(QDialog):
    def __init__(self, on_save_callback):
        super().__init__()
        self.on_save_callback = on_save_callback
        self.setWindowTitle("إضافة فئة جديدة")
        self.setFixedSize(500, 380)
        self.setStyleSheet("background-color: #90A796; border-radius: 15px;")
        self.setup_ui()
        self.populate_categories()

    # ------------------- واجهة المستخدم -------------------
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(18)
        self.setLayout(layout)

        # عنوان النافذة
        title = QLabel("إضافة فئة جديدة")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: black;")
        layout.addWidget(title)

        # ---------------- الفئة الجديدة ----------------
        lbl_new = QLabel("فئة جديدة")
        lbl_new.setStyleSheet("font-size: 14px; color: black;")
        layout.addWidget(lbl_new)

        self.input_new_category = QLineEdit()
        self.input_new_category.setPlaceholderText("اضافة فئة جديدة ...")
        self.input_new_category.setFixedHeight(40)
        self.input_new_category.setStyleSheet("""
            background-color: #B0C4AA;
            border: 1px solid #8DAA8C;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
        """)
        layout.addWidget(self.input_new_category)

        # ---------------- الفئة الفرعية ----------------
        lbl_sub = QLabel("فئة فرعية")
        lbl_sub.setStyleSheet("font-size: 14px; color: black;")
        layout.addWidget(lbl_sub)

        self.input_sub_category = QLineEdit()
        self.input_sub_category.setPlaceholderText("اضافة فئة فرعية ...")
        self.input_sub_category.setFixedHeight(40)
        self.input_sub_category.setStyleSheet("""
            background-color: #B0C4AA;
            border: 1px solid #8DAA8C;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 14px;
        """)
        layout.addWidget(self.input_sub_category)

        # ---------------- الفئة الأصلية ----------------
        lbl_parent = QLabel("اختر فئة")
        lbl_parent.setStyleSheet("font-size: 14px; color: black;")
        layout.addWidget(lbl_parent)

        self.combo_parent = QComboBox()
        self.combo_parent.setFixedHeight(40)
        self.combo_parent.setStyleSheet("""
            QComboBox {
                background-color: #B0C4AA;
                border: 1px solid #8DAA8C;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 14px;
                color: black;
            }
            QComboBox QAbstractItemView {
                background-color: #B0C4AA;
                color: black;
                selection-background-color: #8DAA8C;
            }
        """)
        layout.addWidget(self.combo_parent)

        # ---------------- الأزرار ----------------
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_cancel = QPushButton("إلغاء")
        btn_cancel.setFixedSize(130, 45)
        btn_cancel.setStyleSheet("""
            background-color: #D9534F;
            color: white;
            font-weight: bold;
            font-size: 15px;
            border-radius: 12px;
        """)
        btn_cancel.clicked.connect(self.close)

        btn_ok = QPushButton("تأكيد")
        btn_ok.setFixedSize(130, 45)
        btn_ok.setStyleSheet("""
            background-color: #2F62D3;
            color: white;
            font-weight: bold;
            font-size: 15px;
            border-radius: 12px;
        """)
        btn_ok.clicked.connect(self.save_category)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

    # ------------------- ملء قائمة الفئات -------------------
    def populate_categories(self):
        self.categories_list = fetch_categories()  # [(id, name, parent_id), ...]
        tree = self.build_tree(self.categories_list)

        self.combo_parent.clear()
        self.combo_parent.addItem("اختر الفئة", None)

        def add_to_combobox(combo, node, prefix=""):
            combo.addItem(f"{prefix}{node['name']}", node['id'])
            for child in node['children']:
                add_to_combobox(combo, child, prefix + "— ")

        for node in tree.values():
            add_to_combobox(self.combo_parent, node)

    # ------------------- بناء شجرة الفئات -------------------
    @staticmethod
    def build_tree(categories):
        tree = {}
        lookup = {}

        for c in categories:
            cat_id, name, parent_id = c
            lookup[cat_id] = {"id": cat_id, "name": name, "parent": parent_id, "children": []}

        for cat in lookup.values():
            if cat["parent"]:
                parent = lookup.get(cat["parent"])
                if parent:
                    parent["children"].append(cat)
            else:
                tree[cat["id"]] = cat

        return tree

    # ------------------- دالة الحفظ -------------------
    def save_category(self):
        new_cat = self.input_new_category.text().strip()
        sub_cat = self.input_sub_category.text().strip()
        parent_id = self.combo_parent.currentData()

        if new_cat and sub_cat:
            QMessageBox.warning(self, "خطأ", "لا يمكن ملء الفئة الأصلية والفئة الفرعية معًا")
            return

        if new_cat:
            self.on_save_callback(new_cat, None)
        elif sub_cat:
            if not parent_id:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار الفئة الأصلية للفئة الفرعية")
                return
            self.on_save_callback(sub_cat, parent_id)
        else:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال فئة أصلية أو فرعية")
            return

        QMessageBox.information(self, "تم", "تمت إضافة الفئة بنجاح ✅")
        self.close()
