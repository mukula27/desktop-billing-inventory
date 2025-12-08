"""
Login Window
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFrame,
                             QCheckBox, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QColor
import os


class LoginWindow(QWidget):
    login_successful = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Login - Billing & Inventory System")
        # Larger, modern window
        self.setMinimumSize(640, 420)
        self.resize(640, 420)
        
        # Main layout
        main_layout = QVBoxLayout()
        self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #f7fbff, stop:1 #f0f4f8);
                    font-family: 'Segoe UI', 'Helvetica Neue', Arial;
                }
                QFrame#loginFrame {
                    background-color: white;
                    border-radius: 12px;
                    border: 1px solid rgba(0,0,0,0.06);
                }
                QLabel#titleLabel {
                    color: #2c3e50;
                    font-size: 28px;
                    font-weight: 700;
                }
                QLabel#subtitleLabel {
                    color: #7f8c8d;
                    font-size: 13px;
                }
                QLineEdit {
                    padding: 10px;
                    border: 1px solid #e1e8ef;
                    border-radius: 8px;
                    font-size: 14px;
                    background-color: #fbfdff;
                }
                QLineEdit:focus {
                    border: 2px solid #5dade2;
                }
                QPushButton#loginButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4aa3e0, stop:1 #2b88c6);
                    color: white;
                    padding: 12px 18px;
                    border: none;
                    border-radius: 8px;
                    font-size: 15px;
                    font-weight: 600;
                }
                QPushButton#loginButton:disabled {
                    background: #cfeaf8;
                    color: #9fbfd6;
                }
                QPushButton#loginButton:hover:!disabled {
                    filter: brightness(0.95);
                }
                QPushButton {
                    padding: 6px;
                    border-radius: 6px;
                }
            """)
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
        self.username_input.textChanged.connect(self.update_login_button_state)
        frame_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        frame_layout.addWidget(password_label)

        pw_row = QHBoxLayout()
        pw_row.setSpacing(6)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setText("admin123")  # Default for testing
        self.password_input.returnPressed.connect(self.handle_login)
        self.password_input.textChanged.connect(self.update_login_button_state)
        pw_row.addWidget(self.password_input)

        # Show / hide password toggle
        self.show_pw_btn = QPushButton("Show")
        self.show_pw_btn.setCheckable(True)
        self.show_pw_btn.setMaximumWidth(70)
        self.show_pw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.show_pw_btn.clicked.connect(self.toggle_password_visibility)
        pw_row.addWidget(self.show_pw_btn)

        frame_layout.addLayout(pw_row)

        frame_layout.addSpacing(10)

        # Remember me + Login button row
        action_row = QHBoxLayout()

        self.remember_chk = QCheckBox("Remember me")
        self.remember_chk.setStyleSheet("color: #2c3e50;")
        action_row.addWidget(self.remember_chk)

        action_row.addStretch()

        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setObjectName("loginButton")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        self.login_btn.setEnabled(False)
        action_row.addWidget(self.login_btn)

        frame_layout.addLayout(action_row)

        # Info label
        self.info_label = QLabel("Default: admin / admin123")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("color: #95a5a6; font-size: 10px; margin-top: 10px;")
        frame_layout.addWidget(self.info_label)

        # Inline error label
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setStyleSheet("color: #e74c3c; font-size: 11px; margin-top: 6px;")
        frame_layout.addWidget(self.error_label)
        
        login_frame.setLayout(frame_layout)

        # Add subtle drop shadow effect to the login card
        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(28)
            shadow.setOffset(0, 6)
            shadow.setColor(QColor(0, 0, 0, 50))
            login_frame.setGraphicsEffect(shadow)
        except Exception:
            # If GraphicsEffect not available, ignore silently
            pass

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

    def toggle_password_visibility(self, checked: bool):
        """Toggle password show/hide"""
        if self.show_pw_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_pw_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_pw_btn.setText("Show")

    def update_login_button_state(self):
        """Enable login button only when both fields have text"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        self.login_btn.setEnabled(bool(username and password))
    
    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        # Clear previous inline error
        self.error_label.setText("")

        if not username or not password:
            self.error_label.setText("Please enter username and password")
            return
        
        # Verify credentials
        user = self.db_manager.verify_user(username, password)
        
        if user:
            # Optionally remember user (not persisted yet)
            if self.remember_chk.isChecked():
                # placeholder for remembering logic
                pass

            self.login_successful.emit(user)
        else:
            self.error_label.setText("Invalid username or password")
            self.password_input.clear()
            self.password_input.setFocus()
