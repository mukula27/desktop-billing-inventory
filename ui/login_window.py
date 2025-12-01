"""
Login Window
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Login - Billing & Inventory System")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
            QFrame#loginFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
            }
            QLabel#titleLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton#loginButton {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#loginButton:hover {
                background-color: #2980b9;
            }
            QPushButton#loginButton:pressed {
                background-color: #21618c;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Login frame
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Billing System")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_layout.addWidget(title)
        
        subtitle = QLabel("Please login to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        frame_layout.addWidget(subtitle)
        
        frame_layout.addSpacing(20)
        
        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        frame_layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setText("admin")  # Default for testing
        frame_layout.addWidget(self.username_input)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        frame_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("admin123")  # Default for testing
        self.password_input.returnPressed.connect(self.handle_login)
        frame_layout.addWidget(self.password_input)
        
        frame_layout.addSpacing(10)
        
        # Login button
        login_btn = QPushButton("Login")
        login_btn.setObjectName("loginButton")
        login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        login_btn.clicked.connect(self.handle_login)
        frame_layout.addWidget(login_btn)
        
        # Info label
        info_label = QLabel("Default: admin / admin123")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #95a5a6; font-size: 10px; margin-top: 10px;")
        frame_layout.addWidget(info_label)
        
        login_frame.setLayout(frame_layout)
        main_layout.addWidget(login_frame)
        
        self.setLayout(main_layout)
        
        # Center window
        self.center_window()
    
    def center_window(self):
        """Center window on screen"""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
        
        # Verify credentials
        user = self.db_manager.verify_user(username, password)
        
        if user:
            self.login_successful.emit(user)
        else:
            QMessageBox.critical(self, "Login Failed", 
                               "Invalid username or password.\n\nDefault credentials:\nUsername: admin\nPassword: admin123")
            self.password_input.clear()
            self.password_input.setFocus()
