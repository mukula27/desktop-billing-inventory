"""
Main Application Window
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStackedWidget, QPushButton, QLabel, QFrame,
                             QMessageBox, QMenuBar, QMenu, QToolBar, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QFont
from ui.dashboard import DashboardModule
from ui.products_module import ProductsModule
from ui.billing_module import BillingModule
from ui.customers_module import CustomersModule
from ui.reports_module import ReportsModule
from ui.settings_module import SettingsModule


class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_module = None
        self.modules = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize main window UI"""
        self.setWindowTitle("Billing & Inventory Management System")
        self.setGeometry(100, 100, 1400, 800)
        
        # Set stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QFrame#sidebar {
                background-color: #2c3e50;
                border-right: 2px solid #34495e;
            }
            QPushButton#navButton {
                background-color: transparent;
                color: white;
                text-align: left;
                padding: 15px 20px;
                border: none;
                font-size: 14px;
            }
            QPushButton#navButton:hover {
                background-color: #34495e;
            }
            QPushButton#navButton:checked {
                background-color: #3498db;
                border-left: 4px solid #2980b9;
            }
            QLabel#headerLabel {
                color: white;
                font-size: 20px;
                font-weight: bold;
                padding: 20px;
            }
            QLabel#userLabel {
                color: #ecf0f1;
                font-size: 12px;
                padding: 10px 20px;
            }
        """)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet("background-color: #f5f5f5;")
        main_layout.addWidget(self.content_stack)
        
        central_widget.setLayout(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
        # Load modules
        self.load_modules()
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_invoice_action = QAction("&New Invoice", self)
        new_invoice_action.setShortcut("Ctrl+N")
        new_invoice_action.triggered.connect(self.show_billing)
        file_menu.addAction(new_invoice_action)
        
        file_menu.addSeparator()
        
        backup_action = QAction("&Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        restore_action = QAction("&Restore Database", self)
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        dashboard_action = QAction("&Dashboard", self)
        dashboard_action.triggered.connect(self.show_dashboard)
        view_menu.addAction(dashboard_action)
        
        products_action = QAction("&Products", self)
        products_action.triggered.connect(self.show_products)
        view_menu.addAction(products_action)
        
        billing_action = QAction("&Billing", self)
        billing_action.triggered.connect(self.show_billing)
        view_menu.addAction(billing_action)
        
        customers_action = QAction("&Customers", self)
        customers_action.triggered.connect(self.show_customers)
        view_menu.addAction(customers_action)
        
        reports_action = QAction("&Reports", self)
        reports_action.triggered.connect(self.show_reports)
        view_menu.addAction(reports_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add actions
        new_invoice_btn = QAction("New Invoice", self)
        new_invoice_btn.triggered.connect(self.show_billing)
        toolbar.addAction(new_invoice_btn)
        
        toolbar.addSeparator()
        
        refresh_btn = QAction("Refresh", self)
        refresh_btn.setShortcut("F5")
        refresh_btn.triggered.connect(self.refresh_current_module)
        toolbar.addAction(refresh_btn)
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Billing System")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # User info
        user_label = QLabel(f"👤 {self.user_data.get('full_name', 'User')}")
        user_label.setObjectName("userLabel")
        layout.addWidget(user_label)
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Products", "📦", self.show_products),
            ("Billing", "💰", self.show_billing),
            ("Customers", "👥", self.show_customers),
            ("Reports", "📈", self.show_reports),
            ("Settings", "⚙️", self.show_settings),
        ]
        
        for name, icon, callback in nav_items:
            btn = QPushButton(f"{icon}  {name}")
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        layout.addStretch()
        
        # Logout button
        logout_btn = QPushButton("🚪  Logout")
        logout_btn.setObjectName("navButton")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        sidebar.setLayout(layout)
        return sidebar
    
    def create_status_bar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")
    
    def load_modules(self):
        """Load all modules"""
        # Dashboard
        dashboard = DashboardModule(self.db_manager)
        self.modules['dashboard'] = dashboard
        self.content_stack.addWidget(dashboard)
        
        # Products
        products = ProductsModule(self.db_manager)
        self.modules['products'] = products
        self.content_stack.addWidget(products)
        
        # Billing
        billing = BillingModule(self.db_manager)
        self.modules['billing'] = billing
        self.content_stack.addWidget(billing)
        
        # Customers
        customers = CustomersModule(self.db_manager)
        self.modules['customers'] = customers
        self.content_stack.addWidget(customers)
        
        # Reports
        reports = ReportsModule(self.db_manager)
        self.modules['reports'] = reports
        self.content_stack.addWidget(reports)
        
        # Settings
        settings = SettingsModule(self.db_manager)
        self.modules['settings'] = settings
        self.content_stack.addWidget(settings)
    
    def set_active_nav_button(self, name):
        """Set active navigation button"""
        for btn_name, btn in self.nav_buttons.items():
            btn.setChecked(btn_name == name)
    
    def show_dashboard(self):
        """Show dashboard module"""
        self.content_stack.setCurrentIndex(0)
        self.set_active_nav_button("Dashboard")
        self.statusBar().showMessage("Dashboard")
        if 'dashboard' in self.modules:
            self.modules['dashboard'].load_data()
    
    def show_products(self):
        """Show products module"""
        self.content_stack.setCurrentIndex(1)
        self.set_active_nav_button("Products")
        self.statusBar().showMessage("Products Management")
        if 'products' in self.modules:
            self.modules['products'].load_products()
    
    def show_billing(self):
        """Show billing module"""
        self.content_stack.setCurrentIndex(2)
        self.set_active_nav_button("Billing")
        self.statusBar().showMessage("Billing & Invoicing")
        if 'billing' in self.modules:
            self.modules['billing'].load_invoices()
    
    def show_customers(self):
        """Show customers module"""
        self.content_stack.setCurrentIndex(3)
        self.set_active_nav_button("Customers")
        self.statusBar().showMessage("Customer Management")
        if 'customers' in self.modules:
            self.modules['customers'].load_customers()
    
    def show_reports(self):
        """Show reports module"""
        self.content_stack.setCurrentIndex(4)
        self.set_active_nav_button("Reports")
        self.statusBar().showMessage("Reports & Analytics")
    
    def show_settings(self):
        """Show settings module"""
        self.content_stack.setCurrentIndex(5)
        self.set_active_nav_button("Settings")
        self.statusBar().showMessage("Settings")
        if 'settings' in self.modules:
            self.modules['settings'].load_settings()
    
    def refresh_current_module(self):
        """Refresh current module"""
        current_index = self.content_stack.currentIndex()
        
        if current_index == 0 and 'dashboard' in self.modules:
            self.modules['dashboard'].load_data()
        elif current_index == 1 and 'products' in self.modules:
            self.modules['products'].load_products()
        elif current_index == 2 and 'billing' in self.modules:
            self.modules['billing'].load_invoices()
        elif current_index == 3 and 'customers' in self.modules:
            self.modules['customers'].load_customers()
        elif current_index == 5 and 'settings' in self.modules:
            self.modules['settings'].load_settings()
        
        self.statusBar().showMessage("Refreshed", 2000)
    
    def backup_database(self):
        """Backup database"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime
        
        default_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", default_name, "Database Files (*.db)"
        )
        
        if file_path:
            if self.db_manager.backup_database(file_path):
                QMessageBox.information(self, "Success", "Database backed up successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to backup database")
    
    def restore_database(self):
        """Restore database"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Database", "", "Database Files (*.db)"
        )
        
        if file_path:
            reply = QMessageBox.question(
                self, "Confirm Restore",
                "This will replace the current database. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.db_manager.restore_database(file_path):
                    QMessageBox.information(self, "Success", 
                                          "Database restored successfully!\nPlease restart the application.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About",
                         "Billing & Inventory Management System\n\n"
                         "Version 1.0.0\n\n"
                         "A comprehensive desktop application for managing\n"
                         "billing, inventory, and customer relationships.\n\n"
                         "© 2024 MyBusiness")
    
    def logout(self):
        """Logout user"""
        reply = QMessageBox.question(
            self, "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            # Show login window again
            from ui.login_window import LoginWindow
            self.login_window = LoginWindow(self.db_manager)
            self.login_window.show()
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, "Exit",
            "Are you sure you want to exit?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.db_manager.close()
            event.accept()
        else:
            event.ignore()
