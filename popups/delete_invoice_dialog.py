import sqlite3
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from database.db_connection import get_connection


class DeleteInvoiceDialog(QDialog):
    def __init__(self, invoice_id):
        super().__init__()
        self.invoice_id = invoice_id
        self.setWindowTitle("حذف الفاتورة")
        self.setMinimumWidth(300)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        msg = QLabel("هل أنت متأكد من حذف هذه الفاتورة وجميع مشترياتها؟")
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(msg)

        confirm_btn = QPushButton("🗑️ نعم، احذف")
        cancel_btn = QPushButton("إلغاء")

        confirm_btn.clicked.connect(self.delete_invoice)
        cancel_btn.clicked.connect(self.close)

        layout.addWidget(confirm_btn)
        layout.addWidget(cancel_btn)

    def delete_invoice(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM purchases WHERE invoice_id = ?", (self.invoice_id,))
        cur.execute("DELETE FROM invoices WHERE id = ?", (self.invoice_id,))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "تم", "تم حذف الفاتورة بنجاح ✅")
        self.accept()
