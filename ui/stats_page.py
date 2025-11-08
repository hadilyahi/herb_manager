import sys
import sqlite3
import plotly.graph_objects as go
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QComboBox, QFrame, QSizePolicy, QMessageBox, QScrollArea, QWidgetItem, QBoxLayout
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView

from database.db_connection import get_connection

# دالة مساعدة لإنشاء HTML من plotly figure
def plotly_to_html(fig):
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


class StatsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("إدارة الإحصائيات")
        self.resize(1100, 700)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setStyleSheet("background-color: white; color: black;")
        self._setup_fonts()
        self._build_ui()
        self.refresh_products_list()

        # اختيار أول منتج تلقائيًا إذا وجد
        if self.product_combo.count() > 0:
            self.product_combo.setCurrentIndex(0)

    def _setup_fonts(self):
        self.title_font = QFont("29LT Bukra", 22, QFont.Weight.Bold)
        self.section_font = QFont("29LT Bukra", 16, QFont.Weight.Bold)
        self.label_font = QFont("29LT Bukra", 12)
        self.box_font = QFont("29LT Bukra", 14, QFont.Weight.Bold)
        self.pill_font = QFont("29LT Bukra", 11, QFont.Weight.Normal)

    def _build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(22, 16, 22, 16)

        title = QLabel("ادارة الإحصائيات")
        title.setFont(self.title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        switch_layout = QHBoxLayout()
        self.btn_expenses = QPushButton("قسم المصاريف")
        self.btn_products = QPushButton("قسم المنتجات")

        # تقليل حجم الخط للزرين
        smaller_font = QFont("29LT Bukra", 14, QFont.Weight.Bold)

        for b in (self.btn_expenses, self.btn_products):
            b.setFixedHeight(40)
            b.setFont(smaller_font)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet("background-color: #BDE5C8; border-radius: 10px; padding: 2px; min-width: 160px;")

        switch_layout.addStretch()
        switch_layout.addWidget(self.btn_products)
        switch_layout.addSpacing(160)
        switch_layout.addWidget(self.btn_expenses)
        switch_layout.addStretch()
        main_layout.addLayout(switch_layout)

        # الأقسام
        self.expenses_frame = self._create_expenses_frame()
        self.products_frame = self._create_products_frame()

        main_layout.addWidget(self.expenses_frame)
        main_layout.addWidget(self.products_frame)

        self.setLayout(main_layout)

        self.btn_expenses.clicked.connect(self.show_expenses)
        self.btn_products.clicked.connect(self.show_products)
        self.show_expenses()

    # ---------- قسم المصاريف ---------- (تبقى كما كانت)
    def _create_expenses_frame(self):
        frame = QFrame()
        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        outer_layout.setSpacing(20)

        # section title centered
        section_title = QLabel("قسم المصاريف :")
        section_title.setFont(self.section_font)
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        outer_layout.addWidget(section_title)

        # central area: two columns
        central_h = QHBoxLayout()
        central_h.setContentsMargins(40, 10, 40, 10)
        central_h.setSpacing(80)
        central_h.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- RIGHT column: labels + period pickers (stacked vertically, aligned right) ---
        right_col = QVBoxLayout()
        right_col.setSpacing(22)
        right_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        lbl_top_month_title = QLabel("اكثر شهر تم فيها الشراء :")
        lbl_top_month_title.setFont(self.label_font)
        lbl_top_month_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(lbl_top_month_title, alignment=Qt.AlignmentFlag.AlignRight)
        right_col.addSpacing(20)

        lbl_amount_title = QLabel("المبلغ المنفق على المشتريات :")
        lbl_amount_title.setFont(self.label_font)
        lbl_amount_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(lbl_amount_title, alignment=Qt.AlignmentFlag.AlignRight)
        right_col.addSpacing(20)

        lbl_period_title = QLabel("حدد الفترة :")
        lbl_period_title.setFont(self.label_font)
        lbl_period_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_col.addWidget(lbl_period_title, alignment=Qt.AlignmentFlag.AlignRight)

        # period pickers
        def styled_date_edit(initial_date):
            holder = QFrame()
            holder.setStyleSheet("""
                background-color: #E7F9EE;
                border-radius: 10px;
            """)
            holder.setFixedSize(240, 40)
            hold_layout = QHBoxLayout()
            hold_layout.setContentsMargins(8, 4, 8, 4)
            d = QDateEdit()
            d.setCalendarPopup(True)
            d.setDate(initial_date)
            d.setFixedHeight(30)
            d.setFixedWidth(180)
            d.setStyleSheet("""
                QDateEdit { border: none; background: transparent; }
            """)
            hold_layout.addWidget(d, alignment=Qt.AlignmentFlag.AlignRight)
            holder.setLayout(hold_layout)
            return holder, d

        from_holder, self.from_date = styled_date_edit(QDate.currentDate().addMonths(-1))
        from_layout = QHBoxLayout()
        from_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        from_layout.setDirection(QBoxLayout.Direction.RightToLeft)
        lbl_from = QLabel("من :")
        lbl_from.setFont(self.label_font)
        from_layout.addWidget(from_holder)
        from_layout.addSpacing(8)
        from_layout.addWidget(lbl_from, alignment=Qt.AlignmentFlag.AlignRight)
        right_col.addLayout(from_layout)

        to_holder, self.to_date = styled_date_edit(QDate.currentDate())
        to_layout = QHBoxLayout()
        to_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        to_layout.setDirection(QBoxLayout.Direction.RightToLeft)
        lbl_to = QLabel("إلى :")
        lbl_to.setFont(self.label_font)
        to_layout.addWidget(to_holder)
        to_layout.addSpacing(8)
        to_layout.addWidget(lbl_to, alignment=Qt.AlignmentFlag.AlignRight)
        right_col.addLayout(to_layout)

        # --- LEFT column: green boxes (month and amount) ---
        left_col = QVBoxLayout()
        left_col.setSpacing(40)
        left_col.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        month_box = QFrame()
        month_box.setFixedSize(180, 70)
        month_box.setStyleSheet("""
            background-color: #CFF7DD;
            border-radius: 12px;
        """)
        mb_layout = QVBoxLayout()
        mb_layout.setContentsMargins(10, 10, 10, 10)
        self.top_month_label = QLabel("شهر نوفمبر")
        self.top_month_label.setFont(self.box_font)
        self.top_month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mb_layout.addWidget(self.top_month_label, alignment=Qt.AlignmentFlag.AlignCenter)
        month_box.setLayout(mb_layout)

        left_col.addSpacing(10)
        left_col.addWidget(month_box, alignment=Qt.AlignmentFlag.AlignLeft)

        amount_box = QFrame()
        amount_box.setFixedSize(220, 110)
        amount_box.setStyleSheet("""
            background-color: #CFF7DD;
            border-radius: 12px;
        """)
        ab_layout = QHBoxLayout()
        ab_layout.setContentsMargins(16, 12, 16, 12)
        self.total_label = QLabel("30000.00 دج")
        self.total_label.setFont(self.box_font)
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ab_layout.addWidget(self.total_label, alignment=Qt.AlignmentFlag.AlignCenter)
        amount_box.setLayout(ab_layout)

        left_col.addWidget(amount_box, alignment=Qt.AlignmentFlag.AlignLeft)

        central_h.addLayout(right_col)
        central_h.addLayout(left_col)

        outer_layout.addLayout(central_h)

        # --- centered button ---
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_show_expenses = QPushButton("عرض النتائج")
        self.btn_show_expenses.setFont(self.label_font)
        self.btn_show_expenses.setFixedWidth(160)
        self.btn_show_expenses.setFixedHeight(40)
        self.btn_show_expenses.setStyleSheet("""
            background-color: #CFF0D7;
            border-radius: 10px;
        """)
        self.btn_show_expenses.clicked.connect(self.on_show_expenses)
        btn_layout.addWidget(self.btn_show_expenses)
        outer_layout.addLayout(btn_layout)

        frame.setLayout(outer_layout)
        return frame

    def on_show_expenses(self):
        start = self.from_date.date().toString("yyyy-MM-dd")
        end = self.to_date.date().toString("yyyy-MM-dd")
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("""
                SELECT IFNULL(SUM(total_price),0) AS total
                FROM invoices
                WHERE date(date) BETWEEN ? AND ?
            """, (start, end))
            row_total = c.fetchone()
            if isinstance(row_total, dict) or (hasattr(row_total, 'keys') and 'total' in row_total):
                total = row_total["total"]
            else:
                total = row_total[0] if row_total is not None else 0

            c.execute("""
                SELECT strftime('%m', date) AS month, SUM(total_price) AS total
                FROM invoices
                GROUP BY month ORDER BY total DESC LIMIT 1
            """)
            r = c.fetchone()
            months = ["يناير","فبراير","مارس","أبريل","ماي","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
            if r:
                month_value = None
                if isinstance(r, dict) or (hasattr(r, 'keys') and 'month' in r):
                    month_value = r["month"]
                else:
                    month_value = r[0]

                if month_value is not None and month_value.isdigit():
                    month_index = int(month_value)
                    top_month = months[month_index - 1]
                else:
                    top_month = "-"
            else:
                top_month = "-"

            c.execute("""
                SELECT strftime('%Y-%m-%d', date(date)) as day, IFNULL(SUM(total_price),0) as total
                FROM invoices
                WHERE date BETWEEN ? AND ?
                GROUP BY day
                ORDER BY day
            """, (start, end))
            rows = c.fetchall()
            conn.close()

            self.total_label.setText(f"{total:.2f} دج")
            self.top_month_label.setText(top_month)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", str(e))

    # ---------- قسم المنتجات (التصميم الجديد) ----------
    def _create_products_frame(self):
        # سنستخدم ScrollArea لحال كان المحتوى طويلًا
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        frame = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 8, 20, 20)
        layout.setSpacing(18)

        # عنوان القسم كبير ومركزي
        header = QLabel("قسم المنتجات :")
        header.setFont(self.section_font)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # أعلى السطر: صناديق خضراء (يمين ويسار) ومساحة مركزية
        top_row = QHBoxLayout()
        top_row.setSpacing(40)
        top_row.setContentsMargins(30, 8, 30, 8)

        # صندوق أيمن: الأكثر شراء حسب الكمية (مربّع ملوّن)
        right_box = QFrame()
        right_box.setFixedSize(220, 160)
        right_box.setStyleSheet("""
            background-color: #CFF7DD;
            border-radius: 12px;
        """)
        rb_layout = QVBoxLayout()
        rb_layout.setContentsMargins(12, 12, 12, 12)
        rb_layout.setSpacing(8)
        lbl_title_qty = QLabel(" الأكثر شراء حسب الكمية")
        lbl_title_qty.setFont(self.label_font)
        lbl_title_qty.setAlignment(Qt.AlignmentFlag.AlignRight)
        rb_layout.addWidget(lbl_title_qty, alignment=Qt.AlignmentFlag.AlignRight)

        self.most_qty_box = QFrame()
        self.most_qty_box.setStyleSheet("""
            background-color: #E6FFEF;
            border-radius: 10px;
            border: 2px solid transparent;
            font-size: 14px;
            
        """)
        self.most_qty_box.setFixedSize(160, 60)
        mq_layout = QVBoxLayout()
        mq_layout.setContentsMargins(8, 4, 8, 4)
        self.most_qty_label = QLabel("-")
        self.most_qty_label.setFont(self.box_font)
        self.most_qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mq_layout.addWidget(self.most_qty_label)
        self.most_qty_box.setLayout(mq_layout)
        rb_layout.addWidget(self.most_qty_box, alignment=Qt.AlignmentFlag.AlignCenter)

        right_box.setLayout(rb_layout)

        # صندوق أيسر: الأكثر شراء حسب السعر
        left_box = QFrame()
        left_box.setFixedSize(220, 160)
        left_box.setStyleSheet("""
            background-color: #CFF7DD;
            border-radius: 12px;
            font-size: 14px;
        """)
        lb_layout = QVBoxLayout()
        lb_layout.setContentsMargins(12, 12, 12, 12)
        lb_layout.setSpacing(8)
        lbl_title_price = QLabel(" الأكثر شراء حسب السعر")
        lbl_title_price.setFont(self.label_font)
        lbl_title_price.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lb_layout.addWidget(lbl_title_price, alignment=Qt.AlignmentFlag.AlignLeft)

        self.most_price_box = QFrame()
        self.most_price_box.setStyleSheet("""
            background-color: #E6FFEF;
            border-radius: 10px;
            font-size: 14px;
             /* لإظهار المحدد كما في الصورة */
        """)
        self.most_price_box.setFixedSize(160, 60)
        mp_layout = QVBoxLayout()
        mp_layout.setContentsMargins(8, 4, 8, 4)
        self.most_price_label = QLabel("-")
        self.most_price_label.setFont(self.box_font)
        self.most_price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mp_layout.addWidget(self.most_price_label)
        self.most_price_box.setLayout(mp_layout)
        lb_layout.addWidget(self.most_price_box, alignment=Qt.AlignmentFlag.AlignCenter)

        left_box.setLayout(lb_layout)

        # في الوسط: نترك مساحة لعرض المنتج المحدد كبوكس كبير
       
        sp_layout = QVBoxLayout()
        sp_layout.setContentsMargins(12, 12, 12, 12)
        self.selected_product_label = QLabel("-")
        self.selected_product_label.setFont(QFont("29LT Bukra", 18, QFont.Weight.Bold))
        self.selected_product_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sp_layout.addWidget(self.selected_product_label, alignment=Qt.AlignmentFlag.AlignCenter)
        

        center_col = QVBoxLayout()
        center_col.setSpacing(20)

        
        # ضف العناصر إلى الصف العلوي (الترتيب: يمين - مركز - يسار مع محاذاة واضحة)
        top_row.addWidget(right_box, alignment=Qt.AlignmentFlag.AlignRight)
        top_row.addLayout(center_col)
        top_row.addWidget(left_box, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addLayout(top_row)

        # منطقة اختيار المنتج والازرار الصغيرة تحتها
        select_row = QHBoxLayout()
        select_row.setContentsMargins(50, 4, 50, 4)
        select_row.setSpacing(14)
        label_choose = QLabel("اختر منتج لمتابعة تغيّره :")
        label_choose.setFont(self.label_font)
        select_row.addWidget(label_choose, alignment=Qt.AlignmentFlag.AlignRight)

        self.product_combo = QComboBox()
        self.product_combo.setMinimumWidth(300)
        self.product_combo.setFont(self.label_font)
        self.product_combo.setStyleSheet("QComboBox { padding: 6px; border-radius: 8px; background: #CFF0D7; }")
        select_row.addWidget(self.product_combo, alignment=Qt.AlignmentFlag.AlignRight)

        # أزرار جانبية صغيرة (تطوّر السعر/الكمية الخ)
        small_btns = QHBoxLayout()
        small_btns.setSpacing(8)
        self.btn_price_trend = QPushButton("تطور السعر")
        self.btn_qty_trend = QPushButton("تطور الكمية")
        for b in (self.btn_price_trend, self.btn_qty_trend):
            b.setFixedHeight(36)
            b.setStyleSheet("background-color: #CFF0D7; border-radius: 8px;")
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            small_btns.addWidget(b)
        select_row.addLayout(small_btns)

        layout.addLayout(select_row)

        # مساحة الرسم البياني
        self.product_plot = QWebEngineView()
        self.product_plot.setMinimumHeight(370)
        self.product_plot.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.product_plot)

        frame.setLayout(layout)
        scroll_area.setWidget(frame)

        # ربط الأزرار والإشارات
        self.btn_price_trend.clicked.connect(self.on_price_trend)
        self.btn_qty_trend.clicked.connect(self.on_qty_trend)
       
        self.product_combo.currentIndexChanged.connect(self._on_product_selected)

        return scroll_area

    def _on_pill_clicked(self, which):
        # سلوك افتراضي للأزرار الصغيرة — يمكن تعديل حسب رغبتك
        if which == "qty":
            QMessageBox.information(self, "فلتر", "تم اختيار فِلْتر: حسب الكمية")
        elif which == "price":
            QMessageBox.information(self, "فلتر", "تم اختيار فِلْتر: حسب السعر")
        else:
            QMessageBox.information(self, "فلتر", "خيارات إضافية...")

    def _on_product_selected(self, idx):
        # عند اختيار منتج من الـ ComboBox نحدّث مربع المنتج المُحدَّد
        prod_id = self.product_combo.currentData()
        if prod_id and hasattr(self, "product_map"):
            name = self.product_map.get(prod_id, "-")
            self.selected_product_label.setText(name)
        else:
            self.selected_product_label.setText("-")

    def refresh_products_list(self):
        try:
            conn = get_connection()
            c = conn.cursor()
            # أعلى حسب الكمية
            c.execute("""
                SELECT p.name, SUM(pr.quantity) as total_qty
                FROM purchases pr
                JOIN products p ON p.id = pr.product_id
                GROUP BY pr.product_id
                ORDER BY total_qty DESC LIMIT 1
            """)
            top_qty = c.fetchone()
            top_qty_name = top_qty["name"] if top_qty else "-"

            # أعلى حسب السعر
            c.execute("""
                SELECT p.name, SUM(pr.total_price) as total_price
                FROM purchases pr
                JOIN products p ON p.id = pr.product_id
                GROUP BY pr.product_id
                ORDER BY total_price DESC LIMIT 1
            """)
            top_price = c.fetchone()
            top_price_name = top_price["name"] if top_price else "-"

            c.execute("SELECT id, name FROM products ORDER BY name")
            rows = c.fetchall()
            conn.close()

            self.most_qty_label.setText(top_qty_name)
            self.most_price_label.setText(top_price_name)
            self.selected_product_label.setText(rows[0]["name"] if rows else "-")

            self.product_combo.clear()
            self.product_map = {}
            for r in rows:
                self.product_combo.addItem(r["name"], r["id"])
                self.product_map[r["id"]] = r["name"]

            if self.product_combo.count() > 0:
                self.product_combo.setCurrentIndex(0)

        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", str(e))

    def on_price_trend(self):
        self._show_product_trend("price_per_unit", "متوسط السعر", "السعر لكل وحدة (دج)")

    def on_qty_trend(self):
        self._show_product_trend("quantity", "الكمية المشتراة", "الكمية")

    def _show_product_trend(self, field, title, y_label):
        prod_id = self.product_combo.currentData()
        if not prod_id:
            QMessageBox.warning(self, "اختيار المنتج", "يرجى اختيار منتج أولاً.")
            return

        try:
            conn = get_connection()
            c = conn.cursor()
            if field == "price_per_unit":
                c.execute("""
                    SELECT strftime('%Y-%m-%d', date) as day, AVG(price_per_unit) as avg_val
                    FROM purchases WHERE product_id = ? AND date IS NOT NULL
                    GROUP BY day ORDER BY day
                """, (prod_id,))
            else:
                c.execute("""
                    SELECT strftime('%Y-%m-%d', date) as day, SUM(quantity) as avg_val
                    FROM purchases WHERE product_id = ? AND date IS NOT NULL
                    GROUP BY day ORDER BY day
                """, (prod_id,))
            rows = c.fetchall()
            conn.close()

            days = [r["day"] for r in rows]
            values = [r["avg_val"] for r in rows]

            if days:
                fig = go.Figure(go.Bar(
                    x=days,
                    y=values,
                    marker_color="#379237"
                ))

                fig.update_layout(
                    height=500,
                    title=f"{title} — {self.product_map.get(prod_id,'')}",
                    xaxis_title="التاريخ",
                    yaxis_title=y_label,
                    font=dict(family="29LT Bukra", size=16),
                    template="plotly_white",
                )
            else:
                fig = go.Figure()
                fig.add_annotation(
                    text="لا توجد بيانات كافية لعرض المخطط",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, family="29LT Bukra")
                )
                fig.update_layout(template="plotly_white")

            self.product_plot.setHtml(plotly_to_html(fig))

        except sqlite3.Error as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", str(e))

    # ---------- التحكم بالعرض ----------
    def show_expenses(self):
        self.expenses_frame.show()
        self.products_frame.hide()
        self.btn_expenses.setStyleSheet("background-color: #9BD5A8; border-radius: 10px;")
        self.btn_products.setStyleSheet("background-color: #BDE5C8; border-radius: 10px;")
        # 🔹 لا نعرض النتائج مباشرة
        self.top_month_label.setText("-")
        self.total_label.setText("0.00 دج")

    def show_products(self):
        self.expenses_frame.hide()
        self.products_frame.show()
        self.btn_products.setStyleSheet("background-color: #9BD5A8; border-radius: 10px;")
        self.btn_expenses.setStyleSheet("background-color: #BDE5C8; border-radius: 10px;")
        # تحديث أعلى المنتجات فور عرض القسم
        self.refresh_products_list()


# ------------------ تشغيل التطبيق ------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = StatsWindow()
    w.show()
    sys.exit(app.exec())
