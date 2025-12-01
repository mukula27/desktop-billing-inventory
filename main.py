"""
Main Application Entry Point
Desktop Billing & Inventory Management System
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt, QTimer
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager


class BillingApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Billing & Inventory Manager")
        self.app.setOrganizationName("MyBusiness")
        
        # Set application style
        self.app.setStyle('Fusion')
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        # Show splash screen
        self.show_splash()
        
        # Show login window
        self.login_window = LoginWindow(self.db_manager)
        self.login_window.login_successful.connect(self.on_login_success)
        
    def show_splash(self):
        """Show splash screen"""
        splash_pix = QPixmap(400, 300)
        splash_pix.fill(Qt.GlobalColor.white)
        
        splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
        splash.showMessage("Loading Billing & Inventory System...", 
                          Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                          Qt.GlobalColor.black)
        splash.show()
        
        # Close splash after 2 seconds
        QTimer.singleShot(2000, splash.close)
        self.app.processEvents()
    
    def on_login_success(self, user_data):
        """Handle successful login"""
        self.login_window.close()
        self.main_window = MainWindow(self.db_manager, user_data)
        self.main_window.show()
    
    def run(self):
        """Run the application"""
        self.login_window.show()
        return self.app.exec()


if __name__ == "__main__":
    app = BillingApp()
    sys.exit(app.run())
