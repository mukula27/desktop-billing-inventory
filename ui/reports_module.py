"""
Reports Module - Generate and export various reports
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QFrame, QComboBox,
                             QDateEdit, QGroupBox, QGridLayout, QTextEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from datetime import datetime, timedelta
from utils.pdf_generator import PDFGenerator


class ReportsModule(QWidget):
    """Reports and analytics module"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📈 Reports & Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Report selection
        selection_frame = QFrame()
        selection_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        selection_layout = QVBoxLayout()
        
        # Report type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Report Type:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Sales Report",
            "Stock Report",
            "Low Stock Report",
            "Payment Report",
            "Customer Summary"
        ])
        self.report_type_combo.currentTextChanged.connect(self.on_report_type_changed)
        type_layout.addWidget(self.report_type_combo)
        type_layout.addStretch()
        
        selection_layout.addLayout(type_layout)
        
        # Date range (for applicable reports)
        self.date_range_group = QGroupBox("Date Range")
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        date_layout.addWidget(self.from_date)
        
        date_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.to_date)
        
        date_layout.addStretch()
        
        self.date_range_group.setLayout(date_layout)
        selection_layout.addWidget(self.date_range_group)
        
        # Generate button
        generate_layout = QHBoxLayout()
        generate_layout.addStretch()
        
        self.generate_btn = QPushButton("📊 Generate Report")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        generate_layout.addWidget(self.generate_btn)
        
        self.export_pdf_btn = QPushButton("📄 Export PDF")
        self.export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.export_pdf_btn.clicked.connect(self.export_pdf)
        self.export_pdf_btn.setEnabled(False)
        generate_layout.addWidget(self.export_pdf_btn)
        
        selection_layout.addLayout(generate_layout)
        
        selection_frame.setLayout(selection_layout)
        layout.addWidget(selection_frame)
        
        # Report summary
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        self.summary_layout = QHBoxLayout()
        self.summary_frame.setLayout(self.summary_layout)
        self.summary_frame.setVisible(False)
        layout.addWidget(self.summary_frame)
        
        # Report table
        self.report_table = QTableWidget()
        self.report_table.setAlternatingRowColors(True)
        self.report_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ecf0f1;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.report_table)
        
        self.setLayout(layout)
    
    def on_report_type_changed(self, report_type):
        """Handle report type change"""
        # Show/hide date range based on report type
        if report_type in ["Sales Report", "Payment Report"]:
            self.date_range_group.setVisible(True)
        else:
            self.date_range_group.setVisible(False)
    
    def generate_report(self):
        """Generate selected report"""
        report_type = self.report_type_combo.currentText()
        
        if report_type == "Sales Report":
            self.generate_sales_report()
        elif report_type == "Stock Report":
            self.generate_stock_report()
        elif report_type == "Low Stock Report":
            self.generate_low_stock_report()
        elif report_type == "Payment Report":
            self.generate_payment_report()
        elif report_type == "Customer Summary":
            self.generate_customer_summary()
        
        self.export_pdf_btn.setEnabled(True)
    
    def generate_sales_report(self):
        """Generate sales report"""
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        
        invoices = self.db_manager.search_invoices(start_date=from_date, end_date=to_date)
        
        # Calculate summary
        total_sales = sum(inv['grand_total'] for inv in invoices)
        total_paid = sum(inv['amount_paid'] for inv in invoices)
        total_due = sum(inv['balance_amount'] for inv in invoices)
        
        # Update summary
        self.update_summary([
            ("Total Sales", f"₹{total_sales:,.2f}", "#3498db"),
            ("Total Paid", f"₹{total_paid:,.2f}", "#27ae60"),
            ("Total Due", f"₹{total_due:,.2f}", "#e74c3c"),
            ("Invoices", str(len(invoices)), "#9b59b6")
        ])
        
        # Populate table
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "Date", "Invoice #", "Customer", "Amount", "Paid", "Status"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            self.report_table.setItem(row, 0, QTableWidgetItem(invoice['invoice_date']))
            self.report_table.setItem(row, 1, QTableWidgetItem(invoice['invoice_number']))
            self.report_table.setItem(row, 2, QTableWidgetItem(invoice['customer_name']))
            
            amount_item = QTableWidgetItem(f"₹{invoice['grand_total']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.report_table.setItem(row, 3, amount_item)
            
            paid_item = QTableWidgetItem(f"₹{invoice['amount_paid']:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.report_table.setItem(row, 4, paid_item)
            
            status = invoice['payment_status'].upper()
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if status == 'PAID':
                status_item.setForeground(QColor("#27ae60"))
            elif status == 'UNPAID':
                status_item.setForeground(QColor("#e74c3c"))
            else:
                status_item.setForeground(QColor("#f39c12"))
            
            self.report_table.setItem(row, 5, status_item)
    
    def generate_stock_report(self):
        """Generate stock report"""
        products = self.db_manager.get_all_products()
        
        # Calculate summary
        total_products = len(products)
        total_stock_value = sum(p['current_stock'] * p['purchase_price'] for p in products)
        low_stock_count = len([p for p in products if p['current_stock'] <= p['min_stock_level']])
        
        # Update summary
        self.update_summary([
            ("Total Products", str(total_products), "#3498db"),
            ("Stock Value", f"₹{total_stock_value:,.2f}", "#27ae60"),
            ("Low Stock Items", str(low_stock_count), "#e74c3c")
        ])
        
        # Populate table
        self.report_table.setColumnCount(7)
        self.report_table.setHorizontalHeaderLabels([
            "Code", "Product", "Unit", "Current Stock", "Min Level", "Value", "Status"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.report_table.setItem(row, 0, QTableWidgetItem(product['product_code']))
            self.report_table.setItem(row, 1, QTableWidgetItem(product['product_name']))
            self.report_table.setItem(row, 2, QTableWidgetItem(product['unit']))
            
            stock_item = QTableWidgetItem(f"{product['current_stock']:.0f}")
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if product['current_stock'] <= product['min_stock_level']:
                stock_item.setForeground(QColor("#e74c3c"))
            elif product['current_stock'] <= product['min_stock_level'] * 2:
                stock_item.setForeground(QColor("#f39c12"))
            else:
                stock_item.setForeground(QColor("#27ae60"))
            
            self.report_table.setItem(row, 3, stock_item)
            
            min_item = QTableWidgetItem(f"{product['min_stock_level']:.0f}")
            min_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.report_table.setItem(row, 4, min_item)
            
            value = product['current_stock'] * product['purchase_price']
            value_item = QTableWidgetItem(f"₹{value:,.2f}")
            value_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.report_table.setItem(row, 5, value_item)
            
            if product['current_stock'] <= product['min_stock_level']:
                status = "🔴 Low"
                color = QColor("#e74c3c")
            elif product['current_stock'] <= product['min_stock_level'] * 2:
                status = "🟡 Warning"
                color = QColor("#f39c12")
            else:
                status = "🟢 Good"
                color = QColor("#27ae60")
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(color)
            self.report_table.setItem(row, 6, status_item)
    
    def generate_low_stock_report(self):
        """Generate low stock report"""
        products = self.db_manager.get_low_stock_products()
        
        # Update summary
        self.update_summary([
            ("Low Stock Items", str(len(products)), "#e74c3c"),
            ("Action Required", "Reorder Soon", "#f39c12")
        ])
        
        # Populate table
        self.report_table.setColumnCount(6)
        self.report_table.setHorizontalHeaderLabels([
            "Code", "Product", "Current Stock", "Min Level", "Shortage", "Reorder Qty"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.report_table.setItem(row, 0, QTableWidgetItem(product['product_code']))
            self.report_table.setItem(row, 1, QTableWidgetItem(product['product_name']))
            
            stock_item = QTableWidgetItem(f"{product['current_stock']:.0f} {product['unit']}")
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stock_item.setForeground(QColor("#e74c3c"))
            self.report_table.setItem(row, 2, stock_item)
            
            min_item = QTableWidgetItem(f"{product['min_stock_level']:.0f} {product['unit']}")
            min_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.report_table.setItem(row, 3, min_item)
            
            shortage = product['min_stock_level'] - product['current_stock']
            shortage_item = QTableWidgetItem(f"{shortage:.0f} {product['unit']}")
            shortage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            shortage_item.setForeground(QColor("#e74c3c"))
            self.report_table.setItem(row, 4, shortage_item)
            
            reorder_qty = product['min_stock_level'] * 2  # Suggest 2x minimum
            reorder_item = QTableWidgetItem(f"{reorder_qty:.0f} {product['unit']}")
            reorder_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            reorder_item.setForeground(QColor("#27ae60"))
            self.report_table.setItem(row, 5, reorder_item)
    
    def generate_payment_report(self):
        """Generate payment report"""
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        
        # Get all invoices in date range
        invoices = self.db_manager.search_invoices(start_date=from_date, end_date=to_date)
        
        # Separate by status
        paid_invoices = [inv for inv in invoices if inv['payment_status'] == 'paid']
        unpaid_invoices = [inv for inv in invoices if inv['payment_status'] == 'unpaid']
        partial_invoices = [inv for inv in invoices if inv['payment_status'] == 'partially_paid']
        
        total_paid = sum(inv['amount_paid'] for inv in invoices)
        total_due = sum(inv['balance_amount'] for inv in invoices)
        
        # Update summary
        self.update_summary([
            ("Paid", f"{len(paid_invoices)} (₹{sum(inv['grand_total'] for inv in paid_invoices):,.2f})", "#27ae60"),
            ("Unpaid", f"{len(unpaid_invoices)} (₹{sum(inv['grand_total'] for inv in unpaid_invoices):,.2f})", "#e74c3c"),
            ("Partial", f"{len(partial_invoices)} (₹{sum(inv['balance_amount'] for inv in partial_invoices):,.2f})", "#f39c12")
        ])
        
        # Populate table
        self.report_table.setColumnCount(7)
        self.report_table.setHorizontalHeaderLabels([
            "Invoice #", "Date", "Customer", "Total", "Paid", "Balance", "Status"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            self.report_table.setItem(row, 0, QTableWidgetItem(invoice['invoice_number']))
            self.report_table.setItem(row, 1, QTableWidgetItem(invoice['invoice_date']))
            self.report_table.setItem(row, 2, QTableWidgetItem(invoice['customer_name']))
            
            total_item = QTableWidgetItem(f"₹{invoice['grand_total']:,.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.report_table.setItem(row, 3, total_item)
            
            paid_item = QTableWidgetItem(f"₹{invoice['amount_paid']:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            paid_item.setForeground(QColor("#27ae60"))
            self.report_table.setItem(row, 4, paid_item)
            
            balance_item = QTableWidgetItem(f"₹{invoice['balance_amount']:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            balance_item.setForeground(QColor("#e74c3c") if invoice['balance_amount'] > 0 else QColor("#27ae60"))
            self.report_table.setItem(row, 5, balance_item)
            
            status = invoice['payment_status'].upper()
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if status == 'PAID':
                status_item.setForeground(QColor("#27ae60"))
            elif status == 'UNPAID':
                status_item.setForeground(QColor("#e74c3c"))
            else:
                status_item.setForeground(QColor("#f39c12"))
            
            self.report_table.setItem(row, 6, status_item)
    
    def generate_customer_summary(self):
        """Generate customer summary report"""
        customers = self.db_manager.get_all_customers()
        
        customer_data = []
        total_sales = 0
        total_due = 0
        
        for customer in customers:
            ledger = self.db_manager.get_customer_ledger(customer['id'])
            
            if ledger:
                purchases = sum(t['debit'] for t in ledger)
                paid = sum(t['credit'] for t in ledger)
                balance = purchases - paid
                
                customer_data.append({
                    'name': customer['customer_name'],
                    'phone': customer.get('phone', '-'),
                    'purchases': purchases,
                    'paid': paid,
                    'balance': balance
                })
                
                total_sales += purchases
                total_due += balance
        
        # Update summary
        self.update_summary([
            ("Total Customers", str(len(customers)), "#3498db"),
            ("Total Sales", f"₹{total_sales:,.2f}", "#27ae60"),
            ("Total Outstanding", f"₹{total_due:,.2f}", "#e74c3c")
        ])
        
        # Populate table
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels([
            "Customer", "Phone", "Total Purchases", "Total Paid", "Balance"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.report_table.setRowCount(len(customer_data))
        
        for row, data in enumerate(customer_data):
            self.report_table.setItem(row, 0, QTableWidgetItem(data['name']))
            self.report_table.setItem(row, 1, QTableWidgetItem(data['phone']))
            
            purchases_item = QTableWidgetItem(f"₹{data['purchases']:,.2f}")
            purchases_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.report_table.setItem(row, 2, purchases_item)
            
            paid_item = QTableWidgetItem(f"₹{data['paid']:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            paid_item.setForeground(QColor("#27ae60"))
            self.report_table.setItem(row, 3, paid_item)
            
            balance_item = QTableWidgetItem(f"₹{data['balance']:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            balance_item.setForeground(QColor("#e74c3c") if data['balance'] > 0 else QColor("#27ae60"))
            self.report_table.setItem(row, 4, balance_item)
    
    def update_summary(self, items):
        """Update summary display"""
        # Clear existing
        while self.summary_layout.count():
            child = self.summary_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add new items
        for label, value, color in items:
            item_layout = QVBoxLayout()
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold;")
            item_layout.addWidget(label_widget)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet(f"color: {color}; font-size: 18px; font-weight: bold;")
            item_layout.addWidget(value_widget)
            
            self.summary_layout.addLayout(item_layout)
        
        self.summary_layout.addStretch()
        self.summary_frame.setVisible(True)
    
    def export_pdf(self):
        """Export report to PDF"""
        report_type = self.report_type_combo.currentText()
        
        try:
            pdf_gen = PDFGenerator()
            filename = f"{report_type.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # For now, show success message
            # Actual PDF generation would require implementing report-specific PDF methods
            QMessageBox.information(self, "Export", 
                                  f"Report export functionality will generate:\n{filename}\n\n"
                                  "This feature requires implementing report-specific PDF templates.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting report: {str(e)}")
