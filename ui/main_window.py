"""
Main Application Window
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStackedWidget, QPushButton, QLabel, QFrame,
                             QMessageBox, QMenuBar, QMenu, QToolBar, QStatusBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QFont


class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_module = None
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
        self.content_stack.setStyleSheet("background-color: white;")
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
        # Import modules here to avoid circular imports
        # For now, create placeholder widgets
        
        # Dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout()
        dashboard_label = QLabel("Dashboard Module")
        dashboard_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dashboard_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        dashboard_layout.addWidget(dashboard_label)
        dashboard_widget.setLayout(dashboard_layout)
        self.content_stack.addWidget(dashboard_widget)
        
        # Products
        products_widget = QWidget()
        products_layout = QVBoxLayout()
        products_label = QLabel("Products Module")
        products_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        products_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        products_layout.addWidget(products_label)
        products_widget.setLayout(products_layout)
        self.content_stack.addWidget(products_widget)
        
        # Billing
        billing_widget = QWidget()
        billing_layout = QVBoxLayout()
        billing_label = QLabel("Billing Module")
        billing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        billing_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        billing_layout.addWidget(billing_label)
        billing_widget.setLayout(billing_layout)
        self.content_stack.addWidget(billing_widget)
        
        # Customers
        customers_widget = QWidget()
        customers_layout = QVBoxLayout()
        customers_label = QLabel("Customers Module")
        customers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        customers_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        customers_layout.addWidget(customers_label)
        customers_widget.setLayout(customers_layout)
        self.content_stack.addWidget(customers_widget)
        
        # Reports
        reports_widget = QWidget()
        reports_layout = QVBoxLayout()
        reports_label = QLabel("Reports Module")
        reports_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reports_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        reports_layout.addWidget(reports_label)
        reports_widget.setLayout(reports_layout)
        self.content_stack.addWidget(reports_widget)
        
        # Settings
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_label = QLabel("Settings Module")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_label.setStyleSheet("font-size: 24px; color: #2c3e50;")
        settings_layout.addWidget(settings_label)
        settings_widget.setLayout(settings_layout)
        self.content_stack.addWidget(settings_widget)
    
    def set_active_nav_button(self, name):
        """Set active navigation button"""
        for btn_name, btn in self.nav_buttons.items():
            btn.setChecked(btn_name == name)
    
    def show_dashboard(self):
        """Show dashboard module"""
        self.content_stack.setCurrentIndex(0)
        self.set_active_nav_button("Dashboard")
        self.statusBar().showMessage("Dashboard")
    
    def show_products(self):
        """Show products module"""
        self.content_stack.setCurrentIndex(1)
        self.set_active_nav_button("Products")
        self.statusBar().showMessage("Products Management")
    
    def show_billing(self):
        """Show billing module"""
        self.content_stack.setCurrentIndex(2)
        self.set_active_nav_button("Billing")
        self.statusBar().showMessage("Billing & Invoicing")
    
    def show_customers(self):
        """Show customers module"""
        self.content_stack.setCurrentIndex(3)
        self.set_active_nav_button("Customers")
        self.statusBar().showMessage("Customer Management")
    
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
    
    def refresh_current_module(self):
        """Refresh current module"""
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
