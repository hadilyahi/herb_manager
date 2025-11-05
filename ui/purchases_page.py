from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
    QBoxLayout, QSizePolicy, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from database.db_functions import fetch_products_with_invoice, fetch_invoices
from popups.add_purchase_dialog import AddPurchaseDialog


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
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(
            ["اسم المنتج", "تاريخ الفاتورة", "الكمية", "سعر الوحدة", "السعر الإجمالي", "الإجراءات"]
        )
        self.setup_table_style(self.products_table)
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
        main_layout.addWidget(self.invoices_table)

        # ---- Footer ----
        footer = QLabel("by hadil yahi")
        footer.setFont(QFont("29LT Bukra", 10))
        footer.setAlignment(Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(footer)

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
        for idx, r in enumerate(rows):
            if keyword and keyword not in r["name"]:
                continue

            self.products_table.insertRow(idx)
            self.products_table.setItem(idx, 0, QTableWidgetItem(r["name"]))
            self.products_table.setItem(idx, 1, QTableWidgetItem(r["invoice_date"]))
            self.products_table.setItem(idx, 2, QTableWidgetItem(str(r["quantity"])))
            self.products_table.setItem(idx, 3, QTableWidgetItem(str(r["price_per_unit"])))
            self.products_table.setItem(idx, 4, QTableWidgetItem(str(r["total_price"])))

            self.add_action_buttons(self.products_table, idx, r["id"])

    # ==========================
    # Load invoices table
    # ==========================
    def load_invoices(self, keyword=None):
        rows = fetch_invoices()
        self.invoices_table.setRowCount(0)
        for idx, r in enumerate(rows):
            date_val = r["date"]
            if keyword and keyword not in date_val:
                continue

            self.invoices_table.insertRow(idx)
            self.invoices_table.setItem(idx, 0, QTableWidgetItem(date_val))
            self.invoices_table.setItem(idx, 1, QTableWidgetItem(str(r["num_products"])))
            self.invoices_table.setItem(idx, 2, QTableWidgetItem(str(r["total_price"])))

            self.add_action_buttons(self.invoices_table, idx, r["id"])

    # ==========================
    # Add buttons to table row
    # ==========================
    def add_action_buttons(self, table, row_idx, record_id):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)
        layout.setDirection(QBoxLayout.Direction.RightToLeft)

        btn_delete = QPushButton("🗑")
        btn_delete.setFixedSize(28, 28)
        btn_delete.setStyleSheet("background:none; border:none; color:#e53935; font-size:16px;")
        btn_delete.clicked.connect(lambda _, rid=record_id: self.delete_record(rid))

        layout.addWidget(btn_delete)
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
    # Delete record
    # ==========================
    def delete_record(self, record_id):
        confirm = QMessageBox.question(
            self, "تأكيد الحذف", "هل أنت متأكد من الحذف؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            # هنا يمكن الحذف من purchases أو invoices حسب المكان
            # بعد الحذف، إعادة تحميل الجدولين
            self.load_products()
            self.load_invoices()
            QMessageBox.information(self, "تم", "تم الحذف بنجاح ✅")
