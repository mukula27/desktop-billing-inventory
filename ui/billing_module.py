"""
Billing Module - Invoice creation and management
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QComboBox, 
                             QDoubleSpinBox, QMessageBox, QTextEdit, QFrame,
                             QSpinBox, QDateEdit, QGroupBox, QGridLayout, QScrollArea)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from datetime import datetime
from utils.pdf_generator import PDFGenerator


class ProductSelectionDialog(QDialog):
    """Dialog for selecting products to add to invoice"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_products = []
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Select Products")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Search
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Search:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by code or name...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels([
            "Code", "Name", "Unit", "Price", "Stock", "Select"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.products_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Add Selected")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_btn.clicked.connect(self.add_selected)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_products(self):
        """Load products into table"""
        products = self.db_manager.get_all_products()
        self.populate_table(products)
    
    def search_products(self):
        """Search products"""
        search_term = self.search_input.text().strip()
        
        if search_term:
            products = self.db_manager.search_products(search_term)
        else:
            products = self.db_manager.get_all_products()
        
        self.populate_table(products)
    
    def populate_table(self, products):
        """Populate products table"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Code
            self.products_table.setItem(row, 0, QTableWidgetItem(product['product_code']))
            
            # Name
            self.products_table.setItem(row, 1, QTableWidgetItem(product['product_name']))
            
            # Unit
            self.products_table.setItem(row, 2, QTableWidgetItem(product['unit']))
            
            # Price
            price_item = QTableWidgetItem(f"₹{product['selling_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 3, price_item)
            
            # Stock
            stock_item = QTableWidgetItem(f"{product['current_stock']:.0f}")
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if product['current_stock'] <= 0:
                stock_item.setForeground(QColor("#e74c3c"))
            elif product['current_stock'] <= product['min_stock_level']:
                stock_item.setForeground(QColor("#f39c12"))
            else:
                stock_item.setForeground(QColor("#27ae60"))
            
            self.products_table.setItem(row, 4, stock_item)
            
            # Select button
            select_btn = QPushButton("➕ Add")
            select_btn.setStyleSheet("padding: 4px 8px;")
            select_btn.clicked.connect(lambda checked, p=product: self.select_product(p))
            self.products_table.setCellWidget(row, 5, select_btn)
    
    def select_product(self, product):
        """Select a product"""
        # Open quantity dialog
        quantity, ok = self.get_quantity_dialog(product)
        
        if ok and quantity > 0:
            if quantity > product['current_stock']:
                reply = QMessageBox.question(
                    self, "Low Stock",
                    f"Only {product['current_stock']:.0f} {product['unit']} available.\nContinue anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
            
            self.selected_products.append({
                'product_id': product['id'],
                'product_code': product['product_code'],
                'product_name': product['product_name'],
                'unit': product['unit'],
                'unit_price': product['selling_price'],
                'gst_rate': product['gst_rate'],
                'quantity': quantity,
                'discount': 0
            })
            
            QMessageBox.information(self, "Added", f"Added {product['product_name']} to invoice")
    
    def get_quantity_dialog(self, product):
        """Show quantity input dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Quantity")
        dialog.setModal(True)
        
        layout = QVBoxLayout()
        
        info = QLabel(f"Product: {product['product_name']}\nAvailable: {product['current_stock']:.0f} {product['unit']}")
        layout.addWidget(info)
        
        form = QFormLayout()
        
        quantity_input = QDoubleSpinBox()
        quantity_input.setMinimum(0.01)
        quantity_input.setMaximum(999999)
        quantity_input.setValue(1)
        form.addRow("Quantity:", quantity_input)
        
        layout.addLayout(form)
        
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        buttons.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
            }
        """)
        ok_btn.clicked.connect(dialog.accept)
        buttons.addWidget(ok_btn)
        
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        
        result = dialog.exec()
        return quantity_input.value(), result == QDialog.DialogCode.Accepted
    
    def add_selected(self):
        """Add selected products and close"""
        if not self.selected_products:
            QMessageBox.warning(self, "No Selection", "Please select at least one product")
            return
        
        self.accept()


class BillingModule(QWidget):
    """Billing and invoicing module"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.invoice_items = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("💰 Billing & Invoicing")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # New Invoice button
        new_invoice_btn = QPushButton("➕ New Invoice")
        new_invoice_btn.setStyleSheet("""
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
        new_invoice_btn.clicked.connect(self.new_invoice)
        header_layout.addWidget(new_invoice_btn)
        
        layout.addLayout(header_layout)
        
        # Main content area
        self.content_stack = QWidget()
        content_layout = QVBoxLayout()
        
        # Invoice form (initially hidden)
        self.invoice_form = self.create_invoice_form()
        self.invoice_form.setVisible(False)
        content_layout.addWidget(self.invoice_form)
        
        # Invoice list
        self.invoice_list = self.create_invoice_list()
        content_layout.addWidget(self.invoice_list)
        
        self.content_stack.setLayout(content_layout)
        layout.addWidget(self.content_stack)
        
        self.setLayout(layout)
        
        # Load invoices
        self.load_invoices()
    
    def create_invoice_form(self):
        """Create invoice creation form"""
        form_widget = QFrame()
        form_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Form header
        form_header = QHBoxLayout()
        
        form_title = QLabel("📝 Create New Invoice")
        form_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        form_header.addWidget(form_title)
        
        form_header.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.cancel_invoice)
        form_header.addWidget(cancel_btn)
        
        layout.addLayout(form_header)
        
        # Customer section
        customer_group = QGroupBox("Customer Details")
        customer_layout = QGridLayout()
        
        # Customer selection
        customer_layout.addWidget(QLabel("Customer:"), 0, 0)
        self.customer_combo = QComboBox()
        self.customer_combo.setEditable(True)
        self.load_customers()
        customer_layout.addWidget(self.customer_combo, 0, 1)
        
        add_customer_btn = QPushButton("➕ New")
        add_customer_btn.clicked.connect(self.add_new_customer)
        customer_layout.addWidget(add_customer_btn, 0, 2)
        
        # Customer details
        customer_layout.addWidget(QLabel("Phone:"), 1, 0)
        self.customer_phone = QLineEdit()
        customer_layout.addWidget(self.customer_phone, 1, 1, 1, 2)
        
        customer_layout.addWidget(QLabel("Address:"), 2, 0)
        self.customer_address = QTextEdit()
        self.customer_address.setMaximumHeight(60)
        customer_layout.addWidget(self.customer_address, 2, 1, 1, 2)
        
        customer_group.setLayout(customer_layout)
        layout.addWidget(customer_group)
        
        # Invoice items section
        items_group = QGroupBox("Invoice Items")
        items_layout = QVBoxLayout()
        
        # Add product button
        add_product_btn = QPushButton("➕ Add Products")
        add_product_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_product_btn.clicked.connect(self.add_products)
        items_layout.addWidget(add_product_btn)
        
        # Items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(8)
        self.items_table.setHorizontalHeaderLabels([
            "Product", "Unit", "Quantity", "Price", "Discount", "Taxable", "GST", "Total"
        ])
        self.items_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.items_table.setAlternatingRowColors(True)
        items_layout.addWidget(self.items_table)
        
        items_group.setLayout(items_layout)
        layout.addWidget(items_group)
        
        # Totals section
        totals_layout = QHBoxLayout()
        totals_layout.addStretch()
        
        totals_frame = QFrame()
        totals_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        totals_grid = QGridLayout()
        
        totals_grid.addWidget(QLabel("Subtotal:"), 0, 0)
        self.subtotal_label = QLabel("₹0.00")
        self.subtotal_label.setStyleSheet("font-weight: bold;")
        totals_grid.addWidget(self.subtotal_label, 0, 1)
        
        totals_grid.addWidget(QLabel("GST:"), 1, 0)
        self.gst_label = QLabel("₹0.00")
        self.gst_label.setStyleSheet("font-weight: bold;")
        totals_grid.addWidget(self.gst_label, 1, 1)
        
        totals_grid.addWidget(QLabel("Grand Total:"), 2, 0)
        self.total_label = QLabel("₹0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60;")
        totals_grid.addWidget(self.total_label, 2, 1)
        
        totals_frame.setLayout(totals_grid)
        totals_layout.addWidget(totals_frame)
        
        layout.addLayout(totals_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Invoice")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_invoice)
        action_layout.addWidget(save_btn)
        
        layout.addLayout(action_layout)
        
        form_widget.setLayout(layout)
        return form_widget
    
    def create_invoice_list(self):
        """Create invoice list view"""
        list_widget = QFrame()
        list_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Search and filters
        filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search invoices...")
        self.search_input.textChanged.connect(self.search_invoices)
        filter_layout.addWidget(self.search_input)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["All Status", "Paid", "Unpaid", "Partially Paid"])
        self.status_filter.currentTextChanged.connect(self.filter_invoices)
        filter_layout.addWidget(self.status_filter)
        
        layout.addLayout(filter_layout)
        
        # Invoices table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(7)
        self.invoices_table.setHorizontalHeaderLabels([
            "Invoice #", "Date", "Customer", "Amount", "Paid", "Balance", "Status"
        ])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
            }
        """)
        self.invoices_table.doubleClicked.connect(self.view_invoice)
        
        layout.addWidget(self.invoices_table)
        
        list_widget.setLayout(layout)
        return list_widget
    
    def load_customers(self):
        """Load customers into combo box"""
        customers = self.db_manager.get_all_customers()
        self.customer_combo.clear()
        self.customer_combo.addItem("-- Select or Enter Customer --", None)
        
        for customer in customers:
            self.customer_combo.addItem(customer['customer_name'], customer)
    
    def new_invoice(self):
        """Start new invoice"""
        self.invoice_form.setVisible(True)
        self.invoice_list.setVisible(False)
        self.invoice_items = []
        self.items_table.setRowCount(0)
        self.calculate_totals()
    
    def cancel_invoice(self):
        """Cancel invoice creation"""
        self.invoice_form.setVisible(False)
        self.invoice_list.setVisible(True)
        self.invoice_items = []
    
    def add_new_customer(self):
        """Add new customer inline"""
        # Simple inline customer addition
        name = self.customer_combo.currentText().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Please enter customer name")
            return
        
        customer_data = {
            'customer_name': name,
            'phone': self.customer_phone.text().strip(),
            'address': self.customer_address.toPlainText().strip()
        }
        
        customer_id = self.db_manager.add_customer(customer_data)
        if customer_id:
            QMessageBox.information(self, "Success", "Customer added successfully!")
            self.load_customers()
    
    def add_products(self):
        """Add products to invoice"""
        dialog = ProductSelectionDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            for product in dialog.selected_products:
                self.invoice_items.append(product)
            
            self.update_items_table()
            self.calculate_totals()
    
    def update_items_table(self):
        """Update items table"""
        self.items_table.setRowCount(len(self.invoice_items))
        
        for row, item in enumerate(self.invoice_items):
            # Product name
            self.items_table.setItem(row, 0, QTableWidgetItem(item['product_name']))
            
            # Unit
            self.items_table.setItem(row, 1, QTableWidgetItem(item['unit']))
            
            # Quantity
            qty_item = QTableWidgetItem(f"{item['quantity']:.2f}")
            qty_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.items_table.setItem(row, 2, qty_item)
            
            # Price
            price_item = QTableWidgetItem(f"₹{item['unit_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items_table.setItem(row, 3, price_item)
            
            # Discount
            discount_item = QTableWidgetItem(f"₹{item['discount']:.2f}")
            discount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items_table.setItem(row, 4, discount_item)
            
            # Calculate amounts
            taxable = (item['quantity'] * item['unit_price']) - item['discount']
            gst_amount = taxable * (item['gst_rate'] / 100)
            total = taxable + gst_amount
            
            # Taxable
            taxable_item = QTableWidgetItem(f"₹{taxable:.2f}")
            taxable_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items_table.setItem(row, 5, taxable_item)
            
            # GST
            gst_item = QTableWidgetItem(f"₹{gst_amount:.2f}")
            gst_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items_table.setItem(row, 6, gst_item)
            
            # Total
            total_item = QTableWidgetItem(f"₹{total:.2f}")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            total_item.setForeground(QColor("#27ae60"))
            self.items_table.setItem(row, 7, total_item)
    
    def calculate_totals(self):
        """Calculate invoice totals"""
        subtotal = 0
        gst_total = 0
        
        for item in self.invoice_items:
            taxable = (item['quantity'] * item['unit_price']) - item['discount']
            gst_amount = taxable * (item['gst_rate'] / 100)
            
            subtotal += taxable
            gst_total += gst_amount
        
        grand_total = subtotal + gst_total
        
        self.subtotal_label.setText(f"₹{subtotal:,.2f}")
        self.gst_label.setText(f"₹{gst_total:,.2f}")
        self.total_label.setText(f"₹{grand_total:,.2f}")
    
    def save_invoice(self):
        """Save invoice"""
        # Validate
        if not self.invoice_items:
            QMessageBox.warning(self, "Error", "Please add at least one product")
            return
        
        customer_name = self.customer_combo.currentText().strip()
        if not customer_name or customer_name == "-- Select or Enter Customer --":
            QMessageBox.warning(self, "Error", "Please select or enter customer name")
            return
        
        # Calculate totals
        subtotal = 0
        tax_amount = 0
        
        for item in self.invoice_items:
            taxable = (item['quantity'] * item['unit_price']) - item['discount']
            gst = taxable * (item['gst_rate'] / 100)
            subtotal += taxable
            tax_amount += gst
        
        grand_total = subtotal + tax_amount
        
        # Prepare invoice data
        invoice_data = {
            'customer_name': customer_name,
            'customer_phone': self.customer_phone.text().strip(),
            'customer_address': self.customer_address.toPlainText().strip(),
            'subtotal': subtotal,
            'tax_amount': tax_amount,
            'grand_total': grand_total,
            'rounded_total': round(grand_total),
            'payment_status': 'unpaid',
            'amount_paid': 0,
            'balance_amount': round(grand_total)
        }
        
        # Prepare items
        items = []
        for item in self.invoice_items:
            taxable = (item['quantity'] * item['unit_price']) - item['discount']
            gst_amount = taxable * (item['gst_rate'] / 100)
            total = taxable + gst_amount
            
            items.append({
                'product_id': item['product_id'],
                'product_code': item['product_code'],
                'product_name': item['product_name'],
                'unit': item['unit'],
                'quantity': item['quantity'],
                'unit_price': item['unit_price'],
                'discount': item['discount'],
                'taxable_amount': taxable,
                'gst_rate': item['gst_rate'],
                'gst_amount': gst_amount,
                'total_amount': total
            })
        
        # Save to database
        try:
            invoice_id, invoice_number = self.db_manager.create_invoice(invoice_data, items)
            
            if invoice_id:
                QMessageBox.information(self, "Success", 
                                      f"Invoice {invoice_number} created successfully!")
                
                # Ask to print
                reply = QMessageBox.question(
                    self, "Print Invoice",
                    "Do you want to print the invoice?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.print_invoice(invoice_id)
                
                # Reset form
                self.cancel_invoice()
                self.load_invoices()
            else:
                QMessageBox.critical(self, "Error", "Failed to create invoice")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating invoice: {str(e)}")
    
    def print_invoice(self, invoice_id):
        """Print invoice"""
        try:
            invoice = self.db_manager.get_invoice_by_id(invoice_id)
            items = self.db_manager.get_invoice_items(invoice_id)
            company = self.db_manager.get_company_settings()
            
            pdf_gen = PDFGenerator()
            filename = f"invoice_{invoice['invoice_number']}.pdf"
            
            if pdf_gen.generate_invoice(invoice, items, company, filename):
                QMessageBox.information(self, "Success", f"Invoice saved as {filename}")
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating PDF: {str(e)}")
    
    def load_invoices(self):
        """Load invoices into table"""
        invoices = self.db_manager.get_all_invoices()
        self.populate_invoices_table(invoices)
    
    def search_invoices(self):
        """Search invoices"""
        search_term = self.search_input.text().strip()
        
        if search_term:
            invoices = self.db_manager.search_invoices(search_term=search_term)
        else:
            invoices = self.db_manager.get_all_invoices()
        
        self.populate_invoices_table(invoices)
    
    def filter_invoices(self):
        """Filter invoices by status"""
        status = self.status_filter.currentText()
        
        if status == "All Status":
            invoices = self.db_manager.get_all_invoices()
        else:
            status_map = {
                "Paid": "paid",
                "Unpaid": "unpaid",
                "Partially Paid": "partially_paid"
            }
            invoices = self.db_manager.search_invoices(payment_status=status_map[status])
        
        self.populate_invoices_table(invoices)
    
    def populate_invoices_table(self, invoices):
        """Populate invoices table"""
        self.invoices_table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            # Invoice number
            self.invoices_table.setItem(row, 0, QTableWidgetItem(invoice['invoice_number']))
            
            # Date
            self.invoices_table.setItem(row, 1, QTableWidgetItem(invoice['invoice_date']))
            
            # Customer
            self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice['customer_name']))
            
            # Amount
            amount_item = QTableWidgetItem(f"₹{invoice['grand_total']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.invoices_table.setItem(row, 3, amount_item)
            
            # Paid
            paid_item = QTableWidgetItem(f"₹{invoice['amount_paid']:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.invoices_table.setItem(row, 4, paid_item)
            
            # Balance
            balance_item = QTableWidgetItem(f"₹{invoice['balance_amount']:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.invoices_table.setItem(row, 5, balance_item)
            
            # Status
            status = invoice['payment_status'].upper()
            status_item = QTableWidgetItem(status)
            
            if status == 'PAID':
                status_item.setForeground(QColor("#27ae60"))
            elif status == 'UNPAID':
                status_item.setForeground(QColor("#e74c3c"))
            else:
                status_item.setForeground(QColor("#f39c12"))
            
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.invoices_table.setItem(row, 6, status_item)
    
    def view_invoice(self, index):
        """View invoice details"""
        row = index.row()
        invoice_number = self.invoices_table.item(row, 0).text()
        
        # Find invoice
        invoices = self.db_manager.search_invoices(search_term=invoice_number)
        if invoices:
            invoice = invoices[0]
            QMessageBox.information(self, "Invoice Details", 
                                  f"Invoice: {invoice['invoice_number']}\n"
                                  f"Customer: {invoice['customer_name']}\n"
                                  f"Date: {invoice['invoice_date']}\n"
                                  f"Amount: ₹{invoice['grand_total']:,.2f}\n"
                                  f"Status: {invoice['payment_status'].upper()}")
