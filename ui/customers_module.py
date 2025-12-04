"""
Customers Module - Customer management and ledger
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QTextEdit,
                             QMessageBox, QFrame, QTabWidget, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from utils.pdf_generator import PDFGenerator


class CustomerDialog(QDialog):
    """Dialog for adding/editing customers"""
    def __init__(self, db_manager, customer=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer = customer
        self.is_edit = customer is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_customer_data()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Customer" if self.is_edit else "Add New Customer")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QFormLayout()
        
        # Customer Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., John Doe")
        form_layout.addRow("Customer Name *:", self.name_input)
        
        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g., 9876543210")
        form_layout.addRow("Phone:", self.phone_input)
        
        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g., john@example.com")
        form_layout.addRow("Email:", self.email_input)
        
        # Address
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("Enter full address...")
        self.address_input.setMaximumHeight(80)
        form_layout.addRow("Address:", self.address_input)
        
        # GSTIN
        self.gstin_input = QLineEdit()
        self.gstin_input.setPlaceholderText("e.g., 22AAAAA0000A1Z5")
        form_layout.addRow("GSTIN:", self.gstin_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Customer")
        save_btn.setStyleSheet("""
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
        save_btn.clicked.connect(self.save_customer)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_customer_data(self):
        """Load customer data for editing"""
        self.name_input.setText(self.customer['customer_name'])
        self.phone_input.setText(self.customer.get('phone', ''))
        self.email_input.setText(self.customer.get('email', ''))
        self.address_input.setPlainText(self.customer.get('address', ''))
        self.gstin_input.setText(self.customer.get('gstin', ''))
    
    def save_customer(self):
        """Save customer"""
        # Validate
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Customer name is required")
            return
        
        # Prepare data
        customer_data = {
            'customer_name': self.name_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'address': self.address_input.toPlainText().strip(),
            'gstin': self.gstin_input.text().strip()
        }
        
        # Save
        try:
            if self.is_edit:
                success = self.db_manager.update_customer(self.customer['id'], customer_data)
                message = "Customer updated successfully!"
            else:
                customer_id = self.db_manager.add_customer(customer_data)
                success = customer_id > 0
                message = "Customer added successfully!"
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save customer")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving customer: {str(e)}")


class CustomerLedgerDialog(QDialog):
    """Dialog for viewing customer ledger"""
    def __init__(self, db_manager, customer, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.customer = customer
        self.init_ui()
        self.load_ledger()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle(f"Customer Ledger - {self.customer['customer_name']}")
        self.setModal(True)
        self.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        
        # Customer info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        info_layout = QGridLayout()
        
        info_layout.addWidget(QLabel("Customer:"), 0, 0)
        info_layout.addWidget(QLabel(self.customer['customer_name']), 0, 1)
        
        info_layout.addWidget(QLabel("Phone:"), 0, 2)
        info_layout.addWidget(QLabel(self.customer.get('phone', '-')), 0, 3)
        
        info_layout.addWidget(QLabel("Email:"), 1, 0)
        info_layout.addWidget(QLabel(self.customer.get('email', '-')), 1, 1)
        
        info_layout.addWidget(QLabel("GSTIN:"), 1, 2)
        info_layout.addWidget(QLabel(self.customer.get('gstin', '-')), 1, 3)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Summary
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        summary_layout = QHBoxLayout()
        
        self.total_purchases_label = QLabel("Total Purchases: ₹0.00")
        self.total_purchases_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3498db;")
        summary_layout.addWidget(self.total_purchases_label)
        
        self.total_paid_label = QLabel("Total Paid: ₹0.00")
        self.total_paid_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #27ae60;")
        summary_layout.addWidget(self.total_paid_label)
        
        self.total_due_label = QLabel("Total Due: ₹0.00")
        self.total_due_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e74c3c;")
        summary_layout.addWidget(self.total_due_label)
        
        summary_frame.setLayout(summary_layout)
        layout.addWidget(summary_frame)
        
        # Transactions table
        self.ledger_table = QTableWidget()
        self.ledger_table.setColumnCount(6)
        self.ledger_table.setHorizontalHeaderLabels([
            "Date", "Invoice #", "Description", "Debit", "Credit", "Balance"
        ])
        self.ledger_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ledger_table.setAlternatingRowColors(True)
        self.ledger_table.setStyleSheet("""
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
        
        layout.addWidget(self.ledger_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        export_btn = QPushButton("📄 Export PDF")
        export_btn.setStyleSheet("""
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
        export_btn.clicked.connect(self.export_ledger)
        button_layout.addWidget(export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_ledger(self):
        """Load customer ledger"""
        ledger = self.db_manager.get_customer_ledger(self.customer['id'])
        
        if not ledger:
            return
        
        # Calculate totals
        total_purchases = sum(t['debit'] for t in ledger)
        total_paid = sum(t['credit'] for t in ledger)
        total_due = total_purchases - total_paid
        
        self.total_purchases_label.setText(f"Total Purchases: ₹{total_purchases:,.2f}")
        self.total_paid_label.setText(f"Total Paid: ₹{total_paid:,.2f}")
        self.total_due_label.setText(f"Total Due: ₹{total_due:,.2f}")
        
        # Populate table
        self.ledger_table.setRowCount(len(ledger))
        
        running_balance = 0
        for row, transaction in enumerate(ledger):
            # Date
            self.ledger_table.setItem(row, 0, QTableWidgetItem(transaction['date']))
            
            # Invoice #
            self.ledger_table.setItem(row, 1, QTableWidgetItem(transaction.get('invoice_number', '-')))
            
            # Description
            self.ledger_table.setItem(row, 2, QTableWidgetItem(transaction['description']))
            
            # Debit
            debit_item = QTableWidgetItem(f"₹{transaction['debit']:,.2f}" if transaction['debit'] > 0 else "-")
            debit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if transaction['debit'] > 0:
                debit_item.setForeground(QColor("#e74c3c"))
            self.ledger_table.setItem(row, 3, debit_item)
            
            # Credit
            credit_item = QTableWidgetItem(f"₹{transaction['credit']:,.2f}" if transaction['credit'] > 0 else "-")
            credit_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if transaction['credit'] > 0:
                credit_item.setForeground(QColor("#27ae60"))
            self.ledger_table.setItem(row, 4, credit_item)
            
            # Balance
            running_balance += transaction['debit'] - transaction['credit']
            balance_item = QTableWidgetItem(f"₹{running_balance:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            balance_item.setForeground(QColor("#e74c3c") if running_balance > 0 else QColor("#27ae60"))
            self.ledger_table.setItem(row, 5, balance_item)
    
    def export_ledger(self):
        """Export ledger to PDF"""
        try:
            ledger = self.db_manager.get_customer_ledger(self.customer['id'])
            company = self.db_manager.get_company_settings()
            
            pdf_gen = PDFGenerator()
            filename = f"ledger_{self.customer['customer_name'].replace(' ', '_')}.pdf"
            
            if pdf_gen.generate_customer_ledger(self.customer, ledger, company, filename):
                QMessageBox.information(self, "Success", f"Ledger exported as {filename}")
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting ledger: {str(e)}")


class CustomersModule(QWidget):
    """Customers management module"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_customers()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("👥 Customer Management")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search customers...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.search_customers)
        header_layout.addWidget(self.search_input)
        
        # Add Customer button
        add_btn = QPushButton("➕ Add Customer")
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
        add_btn.clicked.connect(self.add_customer)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        
        self.total_customers_card = self.create_stat_card("Total Customers", "0", "#3498db")
        stats_layout.addWidget(self.total_customers_card)
        
        self.total_due_card = self.create_stat_card("Total Outstanding", "₹0.00", "#e74c3c")
        stats_layout.addWidget(self.total_due_card)
        
        self.active_customers_card = self.create_stat_card("Active This Month", "0", "#27ae60")
        stats_layout.addWidget(self.active_customers_card)
        
        layout.addLayout(stats_layout)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(7)
        self.customers_table.setHorizontalHeaderLabels([
            "Name", "Phone", "Email", "Total Purchases", "Total Paid", "Balance", "Actions"
        ])
        self.customers_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.customers_table.setAlternatingRowColors(True)
        self.customers_table.setStyleSheet("""
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
        
        layout.addWidget(self.customers_table)
        
        self.setLayout(layout)
    
    def create_stat_card(self, title, value, color):
        """Create statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        value_label.setObjectName("value_label")
        layout.addWidget(value_label)
        
        card.setLayout(layout)
        return card
    
    def update_stat_card(self, card, value):
        """Update stat card value"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(str(value))
    
    def load_customers(self):
        """Load customers into table"""
        customers = self.db_manager.get_all_customers()
        self.populate_table(customers)
        
        # Update statistics
        self.update_stat_card(self.total_customers_card, str(len(customers)))
        
        # Calculate total due
        total_due = 0
        for customer in customers:
            ledger = self.db_manager.get_customer_ledger(customer['id'])
            if ledger:
                purchases = sum(t['debit'] for t in ledger)
                paid = sum(t['credit'] for t in ledger)
                total_due += (purchases - paid)
        
        self.update_stat_card(self.total_due_card, f"₹{total_due:,.2f}")
    
    def search_customers(self):
        """Search customers"""
        search_term = self.search_input.text().strip()
        
        if search_term:
            customers = self.db_manager.search_customers(search_term)
        else:
            customers = self.db_manager.get_all_customers()
        
        self.populate_table(customers)
    
    def populate_table(self, customers):
        """Populate customers table"""
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            # Name
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer['customer_name']))
            
            # Phone
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer.get('phone', '-')))
            
            # Email
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer.get('email', '-')))
            
            # Get ledger data
            ledger = self.db_manager.get_customer_ledger(customer['id'])
            
            if ledger:
                total_purchases = sum(t['debit'] for t in ledger)
                total_paid = sum(t['credit'] for t in ledger)
                balance = total_purchases - total_paid
            else:
                total_purchases = 0
                total_paid = 0
                balance = 0
            
            # Total Purchases
            purchases_item = QTableWidgetItem(f"₹{total_purchases:,.2f}")
            purchases_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.customers_table.setItem(row, 3, purchases_item)
            
            # Total Paid
            paid_item = QTableWidgetItem(f"₹{total_paid:,.2f}")
            paid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            paid_item.setForeground(QColor("#27ae60"))
            self.customers_table.setItem(row, 4, paid_item)
            
            # Balance
            balance_item = QTableWidgetItem(f"₹{balance:,.2f}")
            balance_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            
            if balance > 0:
                balance_item.setForeground(QColor("#e74c3c"))
            elif balance < 0:
                balance_item.setForeground(QColor("#27ae60"))
            
            self.customers_table.setItem(row, 5, balance_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setStyleSheet("padding: 4px 8px;")
            edit_btn.clicked.connect(lambda checked, c=customer: self.edit_customer(c))
            actions_layout.addWidget(edit_btn)
            
            ledger_btn = QPushButton("📊 Ledger")
            ledger_btn.setStyleSheet("padding: 4px 8px; background-color: #3498db; color: white;")
            ledger_btn.clicked.connect(lambda checked, c=customer: self.view_ledger(c))
            actions_layout.addWidget(ledger_btn)
            
            actions_widget.setLayout(actions_layout)
            self.customers_table.setCellWidget(row, 6, actions_widget)
    
    def add_customer(self):
        """Add new customer"""
        dialog = CustomerDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def edit_customer(self, customer):
        """Edit customer"""
        dialog = CustomerDialog(self.db_manager, customer, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
    
    def view_ledger(self, customer):
        """View customer ledger"""
        dialog = CustomerLedgerDialog(self.db_manager, customer, parent=self)
        dialog.exec()
