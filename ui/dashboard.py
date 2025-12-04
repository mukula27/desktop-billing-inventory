"""
Dashboard Module - Main overview with statistics and quick actions
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QFrame, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QScrollArea)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta


class StatCard(QFrame):
    """Statistics card widget"""
    def __init__(self, title, value, icon, color, parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                padding: 20px;
            }}
            QFrame#statCard:hover {{
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Icon and title row
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        header_layout.addWidget(icon_label)
        
        header_layout.addStretch()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold;")
        
        layout.addLayout(header_layout)
        layout.addWidget(title_label)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold;")
        layout.addWidget(value_label)
        
        self.setLayout(layout)


class DashboardModule(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_data()
        
        # Auto-refresh every 30 seconds
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_data)
        self.refresh_timer.start(30000)
    
    def init_ui(self):
        """Initialize dashboard UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Current date/time
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        self.update_datetime()
        header_layout.addWidget(self.datetime_label)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        main_layout.addLayout(header_layout)
        
        # Statistics Cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.today_sales_card = StatCard("Today's Sales", "₹0", "💰", "#27ae60")
        self.total_due_card = StatCard("Total Due", "₹0", "💳", "#e74c3c")
        self.low_stock_card = StatCard("Low Stock Items", "0", "📦", "#f39c12")
        self.unpaid_invoices_card = StatCard("Unpaid Invoices", "0", "📄", "#9b59b6")
        
        stats_layout.addWidget(self.today_sales_card, 0, 0)
        stats_layout.addWidget(self.total_due_card, 0, 1)
        stats_layout.addWidget(self.low_stock_card, 0, 2)
        stats_layout.addWidget(self.unpaid_invoices_card, 0, 3)
        
        main_layout.addLayout(stats_layout)
        
        # Content area with two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Left column - Recent Invoices
        left_panel = self.create_recent_invoices_panel()
        content_layout.addWidget(left_panel, 2)
        
        # Right column - Quick Actions & Alerts
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 1)
        
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)
        
        # Update datetime every second
        datetime_timer = QTimer()
        datetime_timer.timeout.connect(self.update_datetime)
        datetime_timer.start(1000)
    
    def update_datetime(self):
        """Update current date/time display"""
        now = datetime.now()
        self.datetime_label.setText(now.strftime("%A, %B %d, %Y • %I:%M:%S %p"))
    
    def create_recent_invoices_panel(self):
        """Create recent invoices panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📋 Recent Invoices")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Table
        self.invoices_table = QTableWidget()
        self.invoices_table.setColumnCount(5)
        self.invoices_table.setHorizontalHeaderLabels(["Invoice #", "Customer", "Date", "Amount", "Status"])
        self.invoices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.invoices_table.setAlternatingRowColors(True)
        self.invoices_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #ecf0f1;
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
        self.invoices_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoices_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.invoices_table)
        
        # View all button
        view_all_btn = QPushButton("View All Invoices →")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                padding: 8px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #2980b9;
                text-decoration: underline;
            }
        """)
        layout.addWidget(view_all_btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Create right panel with quick actions and alerts"""
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Quick Actions
        quick_actions = self.create_quick_actions()
        layout.addWidget(quick_actions)
        
        # Low Stock Alerts
        low_stock_alerts = self.create_low_stock_alerts()
        layout.addWidget(low_stock_alerts)
        
        # Overdue Payments
        overdue_payments = self.create_overdue_payments()
        layout.addWidget(overdue_payments)
        
        layout.addStretch()
        
        panel.setLayout(layout)
        return panel
    
    def create_quick_actions(self):
        """Create quick actions panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        header = QLabel("⚡ Quick Actions")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Action buttons
        actions = [
            ("➕ New Invoice", "#3498db", self.new_invoice),
            ("📦 Add Product", "#27ae60", self.add_product),
            ("👤 Add Customer", "#9b59b6", self.add_customer),
            ("📊 View Reports", "#e67e22", self.view_reports),
        ]
        
        for text, color, callback in actions:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 12px;
                    border-radius: 5px;
                    text-align: left;
                    font-weight: bold;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    opacity: 0.9;
                }}
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_low_stock_alerts(self):
        """Create low stock alerts panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border-radius: 10px;
                padding: 15px;
                border-left: 4px solid #f39c12;
            }
        """)
        
        layout = QVBoxLayout()
        
        header = QLabel("⚠️ Low Stock Alerts")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #856404; margin-bottom: 5px;")
        layout.addWidget(header)
        
        self.low_stock_list = QLabel("Loading...")
        self.low_stock_list.setStyleSheet("color: #856404; font-size: 12px;")
        self.low_stock_list.setWordWrap(True)
        layout.addWidget(self.low_stock_list)
        
        panel.setLayout(layout)
        return panel
    
    def create_overdue_payments(self):
        """Create overdue payments panel"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8d7da;
                border-radius: 10px;
                padding: 15px;
                border-left: 4px solid #e74c3c;
            }
        """)
        
        layout = QVBoxLayout()
        
        header = QLabel("🔴 Overdue Payments")
        header.setStyleSheet("font-size: 14px; font-weight: bold; color: #721c24; margin-bottom: 5px;")
        layout.addWidget(header)
        
        self.overdue_list = QLabel("Loading...")
        self.overdue_list.setStyleSheet("color: #721c24; font-size: 12px;")
        self.overdue_list.setWordWrap(True)
        layout.addWidget(self.overdue_list)
        
        panel.setLayout(layout)
        return panel
    
    def load_data(self):
        """Load dashboard data"""
        # Get statistics
        stats = self.db_manager.get_dashboard_stats()
        
        # Update stat cards
        self.update_stat_card(self.today_sales_card, f"₹{stats['today_sales']:,.2f}")
        self.update_stat_card(self.total_due_card, f"₹{stats['total_due']:,.2f}")
        self.update_stat_card(self.low_stock_card, str(stats['low_stock_count']))
        self.update_stat_card(self.unpaid_invoices_card, str(stats['unpaid_invoices']))
        
        # Load recent invoices
        self.load_recent_invoices()
        
        # Load low stock items
        self.load_low_stock_items()
        
        # Load overdue payments
        self.load_overdue_payments()
    
    def update_stat_card(self, card, value):
        """Update stat card value"""
        # Find the value label (3rd child)
        value_label = card.layout().itemAt(2).widget()
        value_label.setText(str(value))
    
    def load_recent_invoices(self):
        """Load recent invoices into table"""
        invoices = self.db_manager.get_all_invoices(limit=10)
        
        self.invoices_table.setRowCount(len(invoices))
        
        for row, invoice in enumerate(invoices):
            # Invoice number
            self.invoices_table.setItem(row, 0, QTableWidgetItem(invoice['invoice_number']))
            
            # Customer
            self.invoices_table.setItem(row, 1, QTableWidgetItem(invoice['customer_name']))
            
            # Date
            self.invoices_table.setItem(row, 2, QTableWidgetItem(invoice['invoice_date']))
            
            # Amount
            amount_item = QTableWidgetItem(f"₹{invoice['grand_total']:,.2f}")
            amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.invoices_table.setItem(row, 3, amount_item)
            
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
            self.invoices_table.setItem(row, 4, status_item)
    
    def load_low_stock_items(self):
        """Load low stock items"""
        low_stock = self.db_manager.get_low_stock_products()
        
        if not low_stock:
            self.low_stock_list.setText("✅ All products are well stocked!")
        else:
            items = []
            for product in low_stock[:5]:  # Show top 5
                items.append(f"• {product['product_name']}: {product['current_stock']:.0f} {product['unit']}")
            
            text = "\n".join(items)
            if len(low_stock) > 5:
                text += f"\n\n... and {len(low_stock) - 5} more items"
            
            self.low_stock_list.setText(text)
    
    def load_overdue_payments(self):
        """Load overdue payments"""
        # Get unpaid invoices older than 7 days
        seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        overdue = self.db_manager.search_invoices(
            end_date=seven_days_ago,
            payment_status='unpaid'
        )
        
        if not overdue:
            self.overdue_list.setText("✅ No overdue payments!")
        else:
            total_overdue = sum(inv['balance_amount'] for inv in overdue)
            text = f"{len(overdue)} invoice(s) overdue\n"
            text += f"Total: ₹{total_overdue:,.2f}\n\n"
            
            for inv in overdue[:3]:  # Show top 3
                text += f"• {inv['customer_name']}: ₹{inv['balance_amount']:,.2f}\n"
            
            if len(overdue) > 3:
                text += f"\n... and {len(overdue) - 3} more"
            
            self.overdue_list.setText(text)
    
    # Quick action callbacks
    def new_invoice(self):
        """Navigate to new invoice"""
        # This will be connected to main window navigation
        print("Navigate to new invoice")
    
    def add_product(self):
        """Navigate to add product"""
        print("Navigate to add product")
    
    def add_customer(self):
        """Navigate to add customer"""
        print("Navigate to add customer")
    
    def view_reports(self):
        """Navigate to reports"""
        print("Navigate to reports")
