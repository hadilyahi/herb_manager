import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
    QBoxLayout, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
from database.db_functions import (
    fetch_products_with_invoice, 
    fetch_invoices, 
    delete_product_from_invoice,
    delete_invoice
)

from popups.add_purchase_dialog import AddPurchaseDialog
from functools import partial
from popups.edit_purchase_dialog import EditPurchaseDialog
from popups.details_dialog import DetailsDialog
from popups.edit_invoice_dialog import EditInvoiceDialog
from popups.details_invoice_dialog import DetailsInvoiceDialog
import os

class PurchasesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_products()
        self.load_invoices()

    def setup_ui(self):
        self.setStyleSheet("background-color: white; color: black;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(18)

        # ---- Title ----
        title = QLabel("إدارة المشتريات")
        title.setFont(QFont("29LT Bukra", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # ---- Products Section ----
        products_label = QLabel("المنتجات التي تم شراؤها:")
        products_label.setFont(QFont("29LT Bukra", 14, QFont.Weight.Bold))
        main_layout.addWidget(products_label)

        products_toolbar = QHBoxLayout()
        products_toolbar.setDirection(QBoxLayout.Direction.RightToLeft)
        products_toolbar.setSpacing(10)

        add_product_btn = QPushButton("➕ إضافة فاتورة")
        add_product_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_product_btn.setFixedHeight(36)
        add_product_btn.setStyleSheet("""
            QPushButton { background-color:#A3CBAB; border:none; border-radius:10px; font-weight:bold; }
            QPushButton:hover { background-color:#8FBF97; }
        """)
        add_product_btn.clicked.connect(self.open_add_dialog)

        self.search_products = QLineEdit()
        self.search_products.setPlaceholderText("🔍 البحث باسم المنتج")
        self.search_products.setFixedHeight(36)
        self.search_products.textChanged.connect(self.search_products_table)

        products_toolbar.addWidget(add_product_btn)
        products_toolbar.addWidget(self.search_products)
        main_layout.addLayout(products_toolbar)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels(
            ["اسم المنتج", "تاريخ الفاتورة", "تاريخ الانتهاء", "سعر الوحدة", "الكمية", "السعر الإجمالي", "الإجراءات"]
        )

        self.setup_table_style(self.products_table)
        self.products_table.setMaximumHeight(10 * 40 + 40)
        self.products_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.products_table.verticalHeader().setDefaultSectionSize(40)
        main_layout.addWidget(self.products_table)

        # ---- Invoices Section ----
        invoices_label = QLabel("الفواتير:")
        invoices_label.setFont(QFont("29LT Bukra", 14, QFont.Weight.Bold))
        main_layout.addWidget(invoices_label)

        invoices_toolbar = QHBoxLayout()
        invoices_toolbar.setDirection(QBoxLayout.Direction.RightToLeft)
        invoices_toolbar.setSpacing(10)

        self.search_invoices = QLineEdit()
        self.search_invoices.setPlaceholderText("🔍 البحث بتاريخ الفاتورة")
        self.search_invoices.setFixedHeight(36)
        self.search_invoices.textChanged.connect(self.search_invoices_table)
        invoices_toolbar.addWidget(self.search_invoices)
        main_layout.addLayout(invoices_toolbar)

        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(4)
        self.invoices_table.setHorizontalHeaderLabels(
            ["تاريخ الفاتورة", "عدد المنتجات", "إجمالي السعر", "الإجراءات"]
        )
        self.setup_table_style(self.invoices_table)
        self.invoices_table.setMaximumHeight(10 * 40 + 40)
        self.invoices_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.invoices_table.verticalHeader().setDefaultSectionSize(35)
        main_layout.addWidget(self.invoices_table)

        self.setLayout(main_layout)

    def setup_table_style(self, table):
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        table.setStyleSheet("""
            QHeaderView::section {
                background-color: #A3CBAB;
                color: black;
                font-weight: bold;
                font-size: 13px;
                height: 36px;
            }
            QTableWidget {
                background-color: #DFF0D8;
                gridline-color: rgba(0,0,0,0.08);
                font-size: 13px;
                selection-background-color: #9CCC65;
            }
            QTableWidget::item { padding: 6px; }
        """)

    # ==========================
    # Open Add Purchase Dialog
    # ==========================
    def open_add_dialog(self):
        dlg = AddPurchaseDialog()
        if dlg.exec():
            self.load_products()
            self.load_invoices()

    # ==========================
    # Load products table
    # ==========================
    def load_products(self, keyword=None):
        rows = fetch_products_with_invoice()
        self.products_table.setRowCount(0)

        # ترتيب من الأحدث للأقدم
        rows_sorted = sorted(rows, key=lambda x: (x["invoice_date"], x["purchase_id"]), reverse=True)

        # تحديد آخر عملية شراء لكل منتج
        last_purchase_index = {}
        for idx, r in enumerate(rows_sorted):
            name = r["product_name"]
            if name not in last_purchase_index:
                last_purchase_index[name] = idx

        keyword_lower = keyword.lower().strip() if keyword else None
        row_idx = 0

        # تحميل البيانات في الجدول
        for idx, r in enumerate(rows_sorted):
            name = r["product_name"]
            date = r["invoice_date"]
            expiry_date = r["expiry_date"] if r["expiry_date"] else "-"
            price_per_unit = float(r["price_per_unit"])
            quantity = float(r["quantity"])
            total = float(r["total_price"])

            # فلترة حسب الاسم
            if keyword_lower and keyword_lower not in name.lower():
                continue

            self.products_table.insertRow(row_idx)

            # الأعمدة الأساسية
            self.products_table.setItem(row_idx, 0, QTableWidgetItem(name))          # اسم المنتج
            self.products_table.setItem(row_idx, 1, QTableWidgetItem(date))          # تاريخ الفاتورة
            self.products_table.setItem(row_idx, 2, QTableWidgetItem(expiry_date))   # تاريخ الانتهاء

            # أيقونات الأسهم وسعر الوحدة
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
            up_icon = os.path.join(icon_dir, "arrow_up.svg")
            down_icon = os.path.join(icon_dir, "arrow_down.svg")
            equal_icon = os.path.join(icon_dir, "equal.svg")

            if idx == last_purchase_index[name]:
                next_price = None
                for next_r in rows_sorted[idx+1:]:
                    if next_r["product_name"] == name:
                        next_price = float(next_r["price_per_unit"])
                        break
                if next_price is not None:
                    if price_per_unit > next_price:
                        icon_label.setPixmap(QIcon(up_icon).pixmap(QSize(16, 16)))
                    elif price_per_unit < next_price:
                        icon_label.setPixmap(QIcon(down_icon).pixmap(QSize(16, 16)))
                    else:
                        icon_label.setPixmap(QIcon(equal_icon).pixmap(QSize(16, 16)))
                else:
                    icon_label.setPixmap(QIcon(equal_icon).pixmap(QSize(16, 16)))
            else:
                icon_label.clear()

            price_widget = QWidget()
            layout = QHBoxLayout(price_widget)
            layout.setContentsMargins(4, 0, 4, 0)
            layout.setSpacing(6)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)
            layout.addWidget(QLabel(f"{price_per_unit:.2f}"))
            self.products_table.setCellWidget(row_idx, 3, price_widget)             # سعر الوحدة مع الأيقونات

            # بقية الأعمدة
            self.products_table.setItem(row_idx, 4, QTableWidgetItem(str(quantity)))   # الكمية
            self.products_table.setItem(row_idx, 5, QTableWidgetItem(f"{total:.2f}")) # السعر الإجمالي

            # أزرار الإجراءات
            self.add_action_buttons(self.products_table, row_idx, r["purchase_id"], record_type="product")
            row_idx += 1

    # ==========================
    # Load invoices table
    # ==========================
    def load_invoices(self, keyword=None):
        rows = fetch_invoices()
        self.invoices_table.setRowCount(0)
        rows_sorted = sorted(rows, key=lambda x: x["date"], reverse=True)
        keyword_lower = keyword.lower().strip() if keyword else None
        row_idx = 0
        for r in rows_sorted:
            date_val = r["date"]
            if keyword_lower and keyword_lower not in date_val.lower():
                continue
            self.invoices_table.insertRow(row_idx)
            self.invoices_table.setItem(row_idx, 0, QTableWidgetItem(date_val))
            self.invoices_table.setItem(row_idx, 1, QTableWidgetItem(str(r["num_products"])))
            self.invoices_table.setItem(row_idx, 2, QTableWidgetItem(str(r["total_price"])))
            self.add_action_buttons(self.invoices_table, row_idx, r["id"], record_type="invoice")
            row_idx += 1

    # ==========================
    # Add buttons to table row
    # ==========================
    
    def add_action_buttons(self, table, row_idx, record_id, record_type="product"):
        icon_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        icons = {
            "delete": os.path.join(icon_dir, "delete.svg"),
            "edit": os.path.join(icon_dir, "edit.svg"),
            "details": os.path.join(icon_dir, "more.svg"),
            "print": os.path.join(icon_dir, "printe.svg"),
        }

        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        layout.setDirection(QBoxLayout.Direction.RightToLeft)

        btn_size = QSize(28, 28)
        icon_size = QSize(18, 18)

        def make_icon_button(icon_path, tooltip, callback):
            btn = QPushButton()
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedSize(btn_size)
            btn.setToolTip(tooltip)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(icon_size)
            else:
                btn.setText(tooltip[0:2])
            btn.setStyleSheet("background:none; border:none;")
            btn.clicked.connect(callback)
            return btn

        btn_delete = make_icon_button(icons["delete"], "حذف", partial(self.delete_record, record_id, record_type))
        layout.addWidget(btn_delete)

        btn_edit = make_icon_button(icons["edit"], "تعديل", partial(self.edit_record, record_id, record_type))
        layout.addWidget(btn_edit)

        btn_details = make_icon_button(icons["details"], "تفاصيل", partial(self.view_details, record_id, record_type))
        layout.addWidget(btn_details)

        if record_type == "invoice":
            btn_print = make_icon_button(icons["print"], "طباعة", partial(self.print_invoice, record_id))
            layout.addWidget(btn_print)

        table.setCellWidget(row_idx, table.columnCount() - 1, widget)

    # ==========================
    # Search handlers
    # ==========================
    def search_products_table(self):
        keyword = self.search_products.text().strip()
        self.load_products(keyword if keyword else None)

    def search_invoices_table(self):
        keyword = self.search_invoices.text().strip()
        self.load_invoices(keyword if keyword else None)

    # ==========================
    # Action handlers
    # ==========================
    def delete_record(self, record_id, record_type="product"):
        confirm = QMessageBox.question(
            self, "تأكيد الحذف", "هل أنت متأكد من الحذف؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if record_type == "product":
                delete_product_from_invoice(record_id)
                QMessageBox.information(self, "تم", "تم حذف المنتج من الفاتورة ✅")
            elif record_type == "invoice":
                if delete_invoice(record_id):
                    QMessageBox.information(self, "تم", "تم حذف الفاتورة وكل المنتجات المرتبطة بها ✅")
            # إعادة تحميل الجداول مباشرة بعد الحذف
            self.load_products()
            self.load_invoices()

    def edit_record(self, record_id, record_type="product"):
        if record_type == "product":
            dlg = EditPurchaseDialog(record_id, record_type)
        else:
            dlg = EditInvoiceDialog(record_id)
        if dlg.exec():
            self.load_products()
            self.load_invoices()

    def view_details(self, record_id, record_type="product"):
        if record_type == "product":
            dlg = DetailsDialog(record_id, record_type)
        else:
            dlg = DetailsInvoiceDialog(record_id)
        dlg.exec()

    def print_invoice(self, invoice_id):
        QMessageBox.information(self, "طباعة", f"طباعة الفاتورة (id={invoice_id})")
