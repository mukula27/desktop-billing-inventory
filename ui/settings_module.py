"""
Settings Module - Application settings and configuration
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QMessageBox, QFrame,
                             QTabWidget, QFormLayout, QTextEdit, QFileDialog,
                             QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime
import hashlib


class UserDialog(QDialog):
    """Dialog for adding/editing users"""
    def __init__(self, db_manager, user=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user = user
        self.is_edit = user is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_user_data()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit User" if self.is_edit else "Add New User")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QFormLayout()
        
        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., john_doe")
        if self.is_edit:
            self.username_input.setEnabled(False)
        form_layout.addRow("Username *:", self.username_input)
        
        # Full Name
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("e.g., John Doe")
        form_layout.addRow("Full Name *:", self.fullname_input)
        
        # Password (only for new users or if changing)
        if not self.is_edit:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setPlaceholderText("Enter password")
            form_layout.addRow("Password *:", self.password_input)
            
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setPlaceholderText("Confirm password")
            form_layout.addRow("Confirm Password *:", self.confirm_password_input)
        else:
            self.change_password_check = QCheckBox("Change Password")
            self.change_password_check.stateChanged.connect(self.toggle_password_fields)
            form_layout.addRow("", self.change_password_check)
            
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setPlaceholderText("Enter new password")
            self.password_input.setEnabled(False)
            form_layout.addRow("New Password:", self.password_input)
            
            self.confirm_password_input = QLineEdit()
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_input.setPlaceholderText("Confirm new password")
            self.confirm_password_input.setEnabled(False)
            form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        # Role
        self.role_input = QLineEdit()
        self.role_input.setText("user")
        self.role_input.setPlaceholderText("e.g., admin, user, manager")
        form_layout.addRow("Role:", self.role_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save User")
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
        save_btn.clicked.connect(self.save_user)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def toggle_password_fields(self, state):
        """Toggle password fields"""
        enabled = state == Qt.CheckState.Checked.value
        self.password_input.setEnabled(enabled)
        self.confirm_password_input.setEnabled(enabled)
    
    def load_user_data(self):
        """Load user data for editing"""
        self.username_input.setText(self.user['username'])
        self.fullname_input.setText(self.user['full_name'])
        self.role_input.setText(self.user['role'])
    
    def save_user(self):
        """Save user"""
        # Validate
        if not self.username_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Username is required")
            return
        
        if not self.fullname_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Full name is required")
            return
        
        # Check password for new users or if changing
        if not self.is_edit or (self.is_edit and self.change_password_check.isChecked()):
            if not self.password_input.text():
                QMessageBox.warning(self, "Validation Error", "Password is required")
                return
            
            if self.password_input.text() != self.confirm_password_input.text():
                QMessageBox.warning(self, "Validation Error", "Passwords do not match")
                return
        
        # Prepare data
        user_data = {
            'username': self.username_input.text().strip(),
            'full_name': self.fullname_input.text().strip(),
            'role': self.role_input.text().strip() or 'user'
        }
        
        # Add password if needed
        if not self.is_edit or (self.is_edit and self.change_password_check.isChecked()):
            password = self.password_input.text()
            user_data['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
        
        # Save
        try:
            if self.is_edit:
                success = self.db_manager.update_user(self.user['id'], user_data)
                message = "User updated successfully!"
            else:
                user_id = self.db_manager.create_user(
                    user_data['username'],
                    user_data['password_hash'],
                    user_data['full_name'],
                    user_data['role']
                )
                success = user_id > 0
                message = "User added successfully!"
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save user")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving user: {str(e)}")


class SettingsModule(QWidget):
    """Settings and configuration module"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("⚙️ Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        # Company Settings Tab
        company_tab = self.create_company_tab()
        tabs.addTab(company_tab, "🏢 Company")
        
        # User Management Tab
        users_tab = self.create_users_tab()
        tabs.addTab(users_tab, "👥 Users")
        
        # Backup & Restore Tab
        backup_tab = self.create_backup_tab()
        tabs.addTab(backup_tab, "💾 Backup")
        
        # About Tab
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "ℹ️ About")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def create_company_tab(self):
        """Create company settings tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Form
        form_group = QGroupBox("Company Information")
        form_layout = QFormLayout()
        
        # Company Name
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("Enter company name")
        form_layout.addRow("Company Name:", self.company_name_input)
        
        # Address
        self.company_address_input = QTextEdit()
        self.company_address_input.setMaximumHeight(80)
        self.company_address_input.setPlaceholderText("Enter company address")
        form_layout.addRow("Address:", self.company_address_input)
        
        # Phone
        self.company_phone_input = QLineEdit()
        self.company_phone_input.setPlaceholderText("Enter phone number")
        form_layout.addRow("Phone:", self.company_phone_input)
        
        # Email
        self.company_email_input = QLineEdit()
        self.company_email_input.setPlaceholderText("Enter email address")
        form_layout.addRow("Email:", self.company_email_input)
        
        # GSTIN
        self.company_gstin_input = QLineEdit()
        self.company_gstin_input.setPlaceholderText("Enter GSTIN")
        form_layout.addRow("GSTIN:", self.company_gstin_input)
        
        # Invoice Prefix
        self.invoice_prefix_input = QLineEdit()
        self.invoice_prefix_input.setPlaceholderText("e.g., INV")
        form_layout.addRow("Invoice Prefix:", self.invoice_prefix_input)
        
        # Tax Enabled
        self.tax_enabled_check = QCheckBox("Enable GST/Tax Calculations")
        self.tax_enabled_check.setChecked(True)
        form_layout.addRow("", self.tax_enabled_check)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Save button
        save_layout = QHBoxLayout()
        save_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_company_settings)
        save_layout.addWidget(save_btn)
        
        layout.addLayout(save_layout)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_users_tab(self):
        """Create users management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        header_label = QLabel("User Accounts")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        header_layout.addStretch()
        
        add_user_btn = QPushButton("➕ Add User")
        add_user_btn.setStyleSheet("""
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
        add_user_btn.clicked.connect(self.add_user)
        header_layout.addWidget(add_user_btn)
        
        layout.addLayout(header_layout)
        
        # Users table
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Role", "Status", "Actions"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setStyleSheet("""
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
        
        layout.addWidget(self.users_table)
        
        tab.setLayout(layout)
        return tab
    
    def create_backup_tab(self):
        """Create backup & restore tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Backup section
        backup_group = QGroupBox("💾 Backup Database")
        backup_layout = QVBoxLayout()
        
        backup_info = QLabel(
            "Create a backup of your database to protect your data.\n"
            "Backups include all invoices, products, customers, and settings."
        )
        backup_info.setWordWrap(True)
        backup_info.setStyleSheet("color: #7f8c8d; padding: 10px;")
        backup_layout.addWidget(backup_info)
        
        backup_btn_layout = QHBoxLayout()
        backup_btn_layout.addStretch()
        
        backup_btn = QPushButton("📥 Create Backup")
        backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        backup_btn.clicked.connect(self.backup_database)
        backup_btn_layout.addWidget(backup_btn)
        
        backup_layout.addLayout(backup_btn_layout)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Restore section
        restore_group = QGroupBox("📤 Restore Database")
        restore_layout = QVBoxLayout()
        
        restore_info = QLabel(
            "⚠️ WARNING: Restoring will replace all current data!\n"
            "Make sure you have a recent backup before restoring.\n"
            "This action cannot be undone."
        )
        restore_info.setWordWrap(True)
        restore_info.setStyleSheet("color: #e74c3c; padding: 10px; font-weight: bold;")
        restore_layout.addWidget(restore_info)
        
        restore_btn_layout = QHBoxLayout()
        restore_btn_layout.addStretch()
        
        restore_btn = QPushButton("📤 Restore from Backup")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        restore_btn.clicked.connect(self.restore_database)
        restore_btn_layout.addWidget(restore_btn)
        
        restore_layout.addLayout(restore_btn_layout)
        
        restore_group.setLayout(restore_layout)
        layout.addWidget(restore_group)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_about_tab(self):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # App info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        info_layout = QVBoxLayout()
        
        app_name = QLabel("Billing & Inventory Management System")
        app_name.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(app_name)
        
        version = QLabel("Version 1.0.0")
        version.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(version)
        
        description = QLabel(
            "\nA comprehensive desktop application for managing\n"
            "billing, inventory, and customer relationships.\n\n"
            "Features:\n"
            "• Invoice generation and management\n"
            "• Product and stock tracking\n"
            "• Customer ledger and payments\n"
            "• PDF reports and exports\n"
            "• Backup and restore\n"
        )
        description.setStyleSheet("color: #34495e; padding: 20px;")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(description)
        
        copyright_label = QLabel("© 2024 MyBusiness. All rights reserved.")
        copyright_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(copyright_label)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def load_settings(self):
        """Load settings"""
        # Load company settings
        company = self.db_manager.get_company_settings()
        
        if company:
            self.company_name_input.setText(company.get('company_name', ''))
            self.company_address_input.setPlainText(company.get('address', ''))
            self.company_phone_input.setText(company.get('phone', ''))
            self.company_email_input.setText(company.get('email', ''))
            self.company_gstin_input.setText(company.get('gstin', ''))
            self.invoice_prefix_input.setText(company.get('invoice_prefix', 'INV'))
            self.tax_enabled_check.setChecked(company.get('tax_enabled', 1) == 1)
        
        # Load users
        self.load_users()
    
    def load_users(self):
        """Load users into table"""
        users = self.db_manager.get_all_users()
        
        self.users_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            # Username
            self.users_table.setItem(row, 0, QTableWidgetItem(user['username']))
            
            # Full Name
            self.users_table.setItem(row, 1, QTableWidgetItem(user['full_name']))
            
            # Role
            role_item = QTableWidgetItem(user['role'].upper())
            role_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if user['role'] == 'admin':
                role_item.setForeground(QColor("#e74c3c"))
            self.users_table.setItem(row, 2, role_item)
            
            # Status
            status = "Active" if user['is_active'] else "Inactive"
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QColor("#27ae60") if user['is_active'] else QColor("#7f8c8d"))
            self.users_table.setItem(row, 3, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setStyleSheet("padding: 4px 8px;")
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))
            actions_layout.addWidget(edit_btn)
            
            actions_widget.setLayout(actions_layout)
            self.users_table.setCellWidget(row, 4, actions_widget)
    
    def save_company_settings(self):
        """Save company settings"""
        settings = {
            'company_name': self.company_name_input.text().strip(),
            'address': self.company_address_input.toPlainText().strip(),
            'phone': self.company_phone_input.text().strip(),
            'email': self.company_email_input.text().strip(),
            'gstin': self.company_gstin_input.text().strip(),
            'invoice_prefix': self.invoice_prefix_input.text().strip() or 'INV',
            'tax_enabled': 1 if self.tax_enabled_check.isChecked() else 0
        }
        
        try:
            if self.db_manager.update_company_settings(settings):
                QMessageBox.information(self, "Success", "Settings saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save settings")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving settings: {str(e)}")
    
    def add_user(self):
        """Add new user"""
        dialog = UserDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
    
    def edit_user(self, user):
        """Edit user"""
        dialog = UserDialog(self.db_manager, user, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
    
    def backup_database(self):
        """Backup database"""
        default_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Backup Database", default_name, "Database Files (*.db)"
        )
        
        if file_path:
            if self.db_manager.backup_database(file_path):
                QMessageBox.information(self, "Success", 
                                      f"Database backed up successfully!\n\nSaved to:\n{file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to backup database")
    
    def restore_database(self):
        """Restore database"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Restore Database", "", "Database Files (*.db)"
        )
        
        if file_path:
            reply = QMessageBox.warning(
                self, "⚠️ Confirm Restore",
                "This will replace ALL current data with the backup!\n\n"
                "Are you absolutely sure you want to continue?\n\n"
                "This action CANNOT be undone!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.db_manager.restore_database(file_path):
                    QMessageBox.information(self, "Success", 
                                          "Database restored successfully!\n\n"
                                          "Please restart the application for changes to take effect.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database")
