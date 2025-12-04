"""
Products Module - Product and inventory management
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QComboBox, 
                             QDoubleSpinBox, QMessageBox, QFileDialog, QFrame,
                             QTabWidget, QTextEdit, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
from utils.pdf_price_extractor import PDFPriceExtractor


class PDFImportThread(QThread):
    """Thread for PDF import processing"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, pdf_path, existing_products):
        super().__init__()
        self.pdf_path = pdf_path
        self.existing_products = existing_products
    
    def run(self):
        try:
            self.progress.emit(10, "Reading PDF file...")
            extractor = PDFPriceExtractor()
            
            self.progress.emit(30, "Extracting product data...")
            extracted_items = extractor.extract_from_pdf(self.pdf_path)
            
            self.progress.emit(60, "Matching with existing products...")
            matched_items = extractor.match_with_existing_products(
                extracted_items, self.existing_products
            )
            
            self.progress.emit(100, "Complete!")
            self.finished.emit(matched_items)
            
        except Exception as e:
            self.error.emit(str(e))


class ProductDialog(QDialog):
    """Dialog for adding/editing products"""
    def __init__(self, db_manager, product=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product = product
        self.is_edit = product is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_product_data()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Edit Product" if self.is_edit else "Add New Product")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Form
        form_layout = QFormLayout()
        
        # Product Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g., PROD001")
        form_layout.addRow("Product Code *:", self.code_input)
        
        # Product Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Dell Laptop")
        form_layout.addRow("Product Name *:", self.name_input)
        
        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Category:", self.category_combo)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["PCS", "KG", "LITER", "METER", "BOX", "DOZEN"])
        self.unit_combo.setEditable(True)
        form_layout.addRow("Unit:", self.unit_combo)
        
        # Purchase Price
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setMaximum(999999.99)
        self.purchase_price_input.setPrefix("₹ ")
        form_layout.addRow("Purchase Price:", self.purchase_price_input)
        
        # Selling Price
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setMaximum(999999.99)
        self.selling_price_input.setPrefix("₹ ")
        form_layout.addRow("Selling Price *:", self.selling_price_input)
        
        # GST Rate
        self.gst_input = QDoubleSpinBox()
        self.gst_input.setMaximum(100)
        self.gst_input.setSuffix(" %")
        self.gst_input.setValue(18)
        form_layout.addRow("GST Rate:", self.gst_input)
        
        # Opening Stock (only for new products)
        if not self.is_edit:
            self.opening_stock_input = QDoubleSpinBox()
            self.opening_stock_input.setMaximum(999999)
            form_layout.addRow("Opening Stock:", self.opening_stock_input)
        
        # Min Stock Level
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setMaximum(999999)
        self.min_stock_input.setValue(10)
        form_layout.addRow("Min Stock Level:", self.min_stock_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Product")
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
        save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_categories(self):
        """Load categories into combo box"""
        categories = self.db_manager.get_all_categories()
        self.category_combo.addItem("-- Select Category --", None)
        for cat in categories:
            self.category_combo.addItem(cat['name'], cat['id'])
    
    def load_product_data(self):
        """Load product data for editing"""
        self.code_input.setText(self.product['product_code'])
        self.code_input.setEnabled(False)  # Can't change code
        self.name_input.setText(self.product['product_name'])
        
        # Set category
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == self.product.get('category_id'):
                self.category_combo.setCurrentIndex(i)
                break
        
        self.unit_combo.setCurrentText(self.product['unit'])
        self.purchase_price_input.setValue(self.product['purchase_price'])
        self.selling_price_input.setValue(self.product['selling_price'])
        self.gst_input.setValue(self.product['gst_rate'])
        self.min_stock_input.setValue(self.product['min_stock_level'])
    
    def save_product(self):
        """Save product"""
        # Validate
        if not self.code_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product code is required")
            return
        
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Product name is required")
            return
        
        if self.selling_price_input.value() <= 0:
            QMessageBox.warning(self, "Validation Error", "Selling price must be greater than 0")
            return
        
        # Prepare data
        product_data = {
            'product_code': self.code_input.text().strip(),
            'product_name': self.name_input.text().strip(),
            'category_id': self.category_combo.currentData(),
            'unit': self.unit_combo.currentText(),
            'purchase_price': self.purchase_price_input.value(),
            'selling_price': self.selling_price_input.value(),
            'gst_rate': self.gst_input.value(),
            'min_stock_level': self.min_stock_input.value()
        }
        
        if not self.is_edit:
            product_data['opening_stock'] = self.opening_stock_input.value()
        
        # Save
        try:
            if self.is_edit:
                success = self.db_manager.update_product(self.product['id'], product_data)
                message = "Product updated successfully!"
            else:
                product_id = self.db_manager.add_product(product_data)
                success = product_id > 0
                message = "Product added successfully!"
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to save product")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving product: {str(e)}")


class PDFImportDialog(QDialog):
    """Dialog for importing prices from PDF"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.matched_items = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Import Prices from PDF")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "📄 Upload a supplier price list PDF to automatically extract and update product prices.\n"
            "The system will match products by code or name and show you a preview before updating."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("📁 Browse PDF")
        browse_btn.clicked.connect(self.browse_pdf)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Match", "Extracted Code", "Extracted Name", "Extracted Price",
            "Current Price", "Confidence"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setVisible(False)
        layout.addWidget(self.results_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        self.apply_btn = QPushButton("Apply Updates")
        self.apply_btn.setStyleSheet("""
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
        self.apply_btn.setVisible(False)
        self.apply_btn.clicked.connect(self.apply_updates)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_pdf(self):
        """Browse for PDF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF Price List", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.file_label.setText(file_path)
            self.process_pdf(file_path)
    
    def process_pdf(self, pdf_path):
        """Process PDF file"""
        self.progress_bar.setVisible(True)
        self.progress_label.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Get existing products
        existing_products = self.db_manager.get_all_products()
        
        # Start import thread
        self.import_thread = PDFImportThread(pdf_path, existing_products)
        self.import_thread.progress.connect(self.update_progress)
        self.import_thread.finished.connect(self.show_results)
        self.import_thread.error.connect(self.show_error)
        self.import_thread.start()
    
    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def show_results(self, matched_items):
        """Show extraction results"""
        self.matched_items = matched_items
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        self.results_table.setVisible(True)
        self.apply_btn.setVisible(True)
        
        # Populate table
        self.results_table.setRowCount(len(matched_items))
        
        for row, item in enumerate(matched_items):
            # Match status
            match_item = QTableWidgetItem("✅ Matched" if item['matched'] else "❌ No Match")
            match_item.setForeground(QColor("#27ae60") if item['matched'] else QColor("#e74c3c"))
            self.results_table.setItem(row, 0, match_item)
            
            # Extracted code
            self.results_table.setItem(row, 1, QTableWidgetItem(item['extracted_code']))
            
            # Extracted name
            self.results_table.setItem(row, 2, QTableWidgetItem(item['extracted_name']))
            
            # Extracted price
            price_item = QTableWidgetItem(f"₹{item['extracted_price']:.2f}")
            self.results_table.setItem(row, 3, price_item)
            
            # Current price
            if item['matched']:
                current_price = QTableWidgetItem(f"₹{item['current_price']:.2f}")
            else:
                current_price = QTableWidgetItem("-")
            self.results_table.setItem(row, 4, current_price)
            
            # Confidence
            confidence_item = QTableWidgetItem(f"{item['confidence']}%")
            if item['confidence'] >= 90:
                confidence_item.setForeground(QColor("#27ae60"))
            elif item['confidence'] >= 70:
                confidence_item.setForeground(QColor("#f39c12"))
            else:
                confidence_item.setForeground(QColor("#e74c3c"))
            self.results_table.setItem(row, 5, confidence_item)
    
    def show_error(self, error_message):
        """Show error message"""
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        QMessageBox.critical(self, "Error", f"Failed to process PDF:\n{error_message}")
    
    def apply_updates(self):
        """Apply price updates"""
        matched_count = sum(1 for item in self.matched_items if item['matched'])
        
        reply = QMessageBox.question(
            self, "Confirm Update",
            f"Update prices for {matched_count} matched products?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            updated = 0
            for item in self.matched_items:
                if item['matched'] and item['matched_product_id']:
                    product_data = {
                        'product_name': item['matched_product_name'],
                        'selling_price': item['extracted_price'],
                        'purchase_price': item['extracted_price'] * 0.8,  # Assume 20% margin
                        'gst_rate': 18,  # Default
                        'min_stock_level': 10  # Default
                    }
                    
                    if self.db_manager.update_product(item['matched_product_id'], product_data):
                        updated += 1
            
            QMessageBox.information(self, "Success", f"Updated {updated} products successfully!")
            self.accept()


class ProductsModule(QWidget):
    """Products management module"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("📦 Products & Inventory")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search products...")
        self.search_input.setMinimumWidth(300)
        self.search_input.textChanged.connect(self.search_products)
        header_layout.addWidget(self.search_input)
        
        # Add Product button
        add_btn = QPushButton("➕ Add Product")
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
        add_btn.clicked.connect(self.add_product)
        header_layout.addWidget(add_btn)
        
        # Import from PDF button
        import_btn = QPushButton("📄 Import from PDF")
        import_btn.setStyleSheet("""
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
        import_btn.clicked.connect(self.import_from_pdf)
        header_layout.addWidget(import_btn)
        
        layout.addLayout(header_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(9)
        self.products_table.setHorizontalHeaderLabels([
            "Code", "Name", "Category", "Unit", "Purchase Price",
            "Selling Price", "GST%", "Stock", "Actions"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
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
        
        layout.addWidget(self.products_table)
        
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
            
            # Category
            category = product.get('category_name', '-')
            self.products_table.setItem(row, 2, QTableWidgetItem(category))
            
            # Unit
            self.products_table.setItem(row, 3, QTableWidgetItem(product['unit']))
            
            # Purchase Price
            purchase_item = QTableWidgetItem(f"₹{product['purchase_price']:.2f}")
            purchase_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 4, purchase_item)
            
            # Selling Price
            selling_item = QTableWidgetItem(f"₹{product['selling_price']:.2f}")
            selling_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 5, selling_item)
            
            # GST
            gst_item = QTableWidgetItem(f"{product['gst_rate']:.1f}%")
            gst_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 6, gst_item)
            
            # Stock
            stock_item = QTableWidgetItem(f"{product['current_stock']:.0f}")
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Color code stock
            if product['current_stock'] <= product['min_stock_level']:
                stock_item.setForeground(QColor("#e74c3c"))
            elif product['current_stock'] <= product['min_stock_level'] * 2:
                stock_item.setForeground(QColor("#f39c12"))
            else:
                stock_item.setForeground(QColor("#27ae60"))
            
            self.products_table.setItem(row, 7, stock_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("✏️ Edit")
            edit_btn.setStyleSheet("padding: 4px 8px;")
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            actions_layout.addWidget(edit_btn)
            
            actions_widget.setLayout(actions_layout)
            self.products_table.setCellWidget(row, 8, actions_widget)
    
    def add_product(self):
        """Add new product"""
        dialog = ProductDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def edit_product(self, product):
        """Edit product"""
        dialog = ProductDialog(self.db_manager, product, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def import_from_pdf(self):
        """Import prices from PDF"""
        dialog = PDFImportDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
