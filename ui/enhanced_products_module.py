"""
Enhanced Products Module - Improved UI/UX with better spacing and features
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QDialog, QFormLayout, QComboBox, 
                             QDoubleSpinBox, QMessageBox, QFrame, QSpinBox,
                             QProgressBar, QTextEdit, QGroupBox, QGridLayout,
                             QFileDialog, QCheckBox, QTabWidget, QScrollArea,
                             QSplitter, QToolButton, QMenu)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QColor, QFont, QIcon
from utils.pdf_price_extractor import EnhancedPDFPriceExtractor
from datetime import datetime


class PDFImportThread(QThread):
    """Background thread for PDF import"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, pdf_path, existing_products):
        super().__init__()
        self.pdf_path = pdf_path
        self.existing_products = existing_products
    
    def run(self):
        """Run PDF import in background"""
        try:
            self.progress.emit(10, "Opening PDF file...")
            
            extractor = EnhancedPDFPriceExtractor()
            
            self.progress.emit(30, "Extracting products from PDF...")
            extracted = extractor.extract_from_pdf(self.pdf_path)
            
            if not extracted:
                self.error.emit("No products found in PDF")
                return
            
            self.progress.emit(60, f"Found {len(extracted)} products. Matching...")
            
            matched = extractor.match_with_existing_products(self.existing_products)
            
            self.progress.emit(90, "Finalizing results...")
            
            self.finished.emit(matched)
            
        except Exception as e:
            self.error.emit(f"Error: {str(e)}")


class EnhancedProductDialog(QDialog):
    """Enhanced product add/edit dialog with better layout"""
    def __init__(self, db_manager, product=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product = product
        self.is_edit = product is not None
        self.init_ui()
        
        if self.is_edit:
            self.load_product_data()
    
    def init_ui(self):
        """Initialize enhanced UI"""
        self.setWindowTitle("Edit Product" if self.is_edit else "Add New Product")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header
        header = QLabel("✏️ Edit Product" if self.is_edit else "➕ Add New Product")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        layout.addWidget(header)
        
        # Tabs for organized input
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 5px;
                background: white;
                padding: 15px;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 2px solid #3498db;
            }
        """)
        
        # Basic Info Tab
        basic_tab = self.create_basic_info_tab()
        tabs.addTab(basic_tab, "📋 Basic Info")
        
        # Pricing Tab
        pricing_tab = self.create_pricing_tab()
        tabs.addTab(pricing_tab, "💰 Pricing")
        
        # Stock Tab
        stock_tab = self.create_stock_tab()
        tabs.addTab(stock_tab, "📦 Stock")
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Save Product")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_product)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_basic_info_tab(self):
        """Create basic information tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Product Code
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("e.g., SOLAR-550W")
        self.code_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Product Code *:", self.code_input)
        
        # Product Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., 550W Mono PERC Solar Panel")
        self.name_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Product Name *:", self.name_input)
        
        # Category
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.setStyleSheet("padding: 8px; font-size: 13px;")
        self.load_categories()
        category_layout.addWidget(self.category_combo)
        
        add_category_btn = QToolButton()
        add_category_btn.setText("➕")
        add_category_btn.setToolTip("Add new category")
        add_category_btn.clicked.connect(self.add_category)
        category_layout.addWidget(add_category_btn)
        
        form.addRow("Category:", category_layout)
        
        # Unit
        unit_layout = QHBoxLayout()
        self.unit_combo = QComboBox()
        self.unit_combo.setEditable(True)
        self.unit_combo.addItems(["PCS", "KG", "LITER", "METER", "BOX", "SET", "PAIR"])
        self.unit_combo.setStyleSheet("padding: 8px; font-size: 13px;")
        unit_layout.addWidget(self.unit_combo)
        
        form.addRow("Unit:", unit_layout)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter product description, specifications, etc.")
        self.description_input.setMaximumHeight(100)
        self.description_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_pricing_tab(self):
        """Create pricing tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Purchase Price
        self.purchase_price_input = QDoubleSpinBox()
        self.purchase_price_input.setRange(0, 9999999)
        self.purchase_price_input.setDecimals(2)
        self.purchase_price_input.setPrefix("₹ ")
        self.purchase_price_input.setStyleSheet("padding: 8px; font-size: 13px;")
        self.purchase_price_input.valueChanged.connect(self.calculate_margin)
        form.addRow("Purchase Price:", self.purchase_price_input)
        
        # Selling Price
        self.selling_price_input = QDoubleSpinBox()
        self.selling_price_input.setRange(0, 9999999)
        self.selling_price_input.setDecimals(2)
        self.selling_price_input.setPrefix("₹ ")
        self.selling_price_input.setStyleSheet("padding: 8px; font-size: 13px;")
        self.selling_price_input.valueChanged.connect(self.calculate_margin)
        form.addRow("Selling Price *:", self.selling_price_input)
        
        # Margin Display
        self.margin_label = QLabel("Margin: ₹0.00 (0%)")
        self.margin_label.setStyleSheet("""
            padding: 8px;
            background-color: #ecf0f1;
            border-radius: 4px;
            font-weight: bold;
            color: #27ae60;
        """)
        form.addRow("Profit Margin:", self.margin_label)
        
        # GST Rate
        self.gst_input = QDoubleSpinBox()
        self.gst_input.setRange(0, 100)
        self.gst_input.setDecimals(1)
        self.gst_input.setSuffix(" %")
        self.gst_input.setValue(18.0)
        self.gst_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("GST Rate:", self.gst_input)
        
        # MRP (Optional)
        self.mrp_input = QDoubleSpinBox()
        self.mrp_input.setRange(0, 9999999)
        self.mrp_input.setDecimals(2)
        self.mrp_input.setPrefix("₹ ")
        self.mrp_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("MRP (Optional):", self.mrp_input)
        
        # Discount
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setDecimals(2)
        self.discount_input.setSuffix(" %")
        self.discount_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Discount %:", self.discount_input)
        
        layout.addLayout(form)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def create_stock_tab(self):
        """Create stock management tab"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Opening Stock
        self.opening_stock_input = QDoubleSpinBox()
        self.opening_stock_input.setRange(0, 999999)
        self.opening_stock_input.setDecimals(2)
        self.opening_stock_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Opening Stock:", self.opening_stock_input)
        
        # Minimum Stock Level
        self.min_stock_input = QDoubleSpinBox()
        self.min_stock_input.setRange(0, 999999)
        self.min_stock_input.setDecimals(2)
        self.min_stock_input.setValue(5)
        self.min_stock_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Min Stock Level:", self.min_stock_input)
        
        # Reorder Level
        self.reorder_level_input = QDoubleSpinBox()
        self.reorder_level_input.setRange(0, 999999)
        self.reorder_level_input.setDecimals(2)
        self.reorder_level_input.setValue(10)
        self.reorder_level_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Reorder Level:", self.reorder_level_input)
        
        # Maximum Stock Level
        self.max_stock_input = QDoubleSpinBox()
        self.max_stock_input.setRange(0, 999999)
        self.max_stock_input.setDecimals(2)
        self.max_stock_input.setValue(100)
        self.max_stock_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Max Stock Level:", self.max_stock_input)
        
        # Location/Warehouse
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g., Warehouse A, Shelf 5")
        self.location_input.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("Storage Location:", self.location_input)
        
        # Track Stock
        self.track_stock_check = QCheckBox("Enable stock tracking for this product")
        self.track_stock_check.setChecked(True)
        self.track_stock_check.setStyleSheet("padding: 8px; font-size: 13px;")
        form.addRow("", self.track_stock_check)
        
        layout.addLayout(form)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab
    
    def load_categories(self):
        """Load categories"""
        categories = self.db_manager.get_all_categories()
        self.category_combo.clear()
        self.category_combo.addItem("-- Select Category --")
        for cat in categories:
            self.category_combo.addItem(cat['category_name'])
    
    def add_category(self):
        """Add new category"""
        from PyQt6.QtWidgets import QInputDialog
        
        category, ok = QInputDialog.getText(self, "Add Category", "Category Name:")
        if ok and category.strip():
            if self.db_manager.add_category(category.strip()):
                self.load_categories()
                self.category_combo.setCurrentText(category.strip())
                QMessageBox.information(self, "Success", "Category added successfully!")
    
    def calculate_margin(self):
        """Calculate and display profit margin"""
        purchase = self.purchase_price_input.value()
        selling = self.selling_price_input.value()
        
        if purchase > 0:
            margin_amount = selling - purchase
            margin_percent = (margin_amount / purchase) * 100
            
            color = "#27ae60" if margin_amount >= 0 else "#e74c3c"
            self.margin_label.setText(f"Margin: ₹{margin_amount:,.2f} ({margin_percent:.1f}%)")
            self.margin_label.setStyleSheet(f"""
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
                font-weight: bold;
                color: {color};
            """)
    
    def load_product_data(self):
        """Load product data for editing"""
        self.code_input.setText(self.product['product_code'])
        self.name_input.setText(self.product['product_name'])
        self.category_combo.setCurrentText(self.product.get('category', ''))
        self.unit_combo.setCurrentText(self.product['unit'])
        self.purchase_price_input.setValue(self.product['purchase_price'])
        self.selling_price_input.setValue(self.product['selling_price'])
        self.gst_input.setValue(self.product['gst_rate'])
        self.opening_stock_input.setValue(self.product['current_stock'])
        self.min_stock_input.setValue(self.product['min_stock_level'])
    
    def save_product(self):
        """Save product with validation"""
        # Validate required fields
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
            'category': self.category_combo.currentText(),
            'unit': self.unit_combo.currentText(),
            'purchase_price': self.purchase_price_input.value(),
            'selling_price': self.selling_price_input.value(),
            'gst_rate': self.gst_input.value(),
            'opening_stock': self.opening_stock_input.value(),
            'current_stock': self.opening_stock_input.value() if not self.is_edit else self.product['current_stock'],
            'min_stock_level': self.min_stock_input.value()
        }
        
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


class EnhancedProductsModule(QWidget):
    """Enhanced products module with improved UI/UX"""
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.pdf_import_thread = None
        self.init_ui()
        self.load_products()
    
    def init_ui(self):
        """Initialize enhanced UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Header with actions
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        title = QLabel("📦 Products & Inventory")
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #2c3e50;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search with icon
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 5, 10, 5)
        search_layout.setSpacing(8)
        
        search_icon = QLabel("🔍")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products by code, name, or category...")
        self.search_input.setMinimumWidth(350)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)
        
        search_frame.setLayout(search_layout)
        header_layout.addWidget(search_frame)
        
        # Action buttons
        add_btn = QPushButton("➕ Add Product")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_btn.clicked.connect(self.add_product)
        header_layout.addWidget(add_btn)
        
        import_btn = QPushButton("📄 Import PDF")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        import_btn.clicked.connect(self.import_from_pdf)
        header_layout.addWidget(import_btn)
        
        # More actions menu
        more_btn = QToolButton()
        more_btn.setText("⋮")
        more_btn.setStyleSheet("""
            QToolButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 18px;
            }
            QToolButton:hover {
                background-color: #7f8c8d;
            }
        """)
        more_menu = QMenu()
        more_menu.addAction("📊 Export to Excel", self.export_to_excel)
        more_menu.addAction("📄 Export to PDF", self.export_to_pdf)
        more_menu.addSeparator()
        more_menu.addAction("🔄 Refresh", self.load_products)
        more_btn.setMenu(more_menu)
        more_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        header_layout.addWidget(more_btn)
        
        layout.addLayout(header_layout)
        
        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.total_products_card = self.create_stat_card("Total Products", "0", "#3498db", "📦")
        stats_layout.addWidget(self.total_products_card)
        
        self.total_value_card = self.create_stat_card("Total Stock Value", "₹0", "#27ae60", "💰")
        stats_layout.addWidget(self.total_value_card)
        
        self.low_stock_card = self.create_stat_card("Low Stock Items", "0", "#e74c3c", "⚠️")
        stats_layout.addWidget(self.low_stock_card)
        
        self.categories_card = self.create_stat_card("Categories", "0", "#9b59b6", "📂")
        stats_layout.addWidget(self.categories_card)
        
        layout.addLayout(stats_layout)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.category_filter.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.category_filter)
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItems(["All Stock", "In Stock", "Low Stock", "Out of Stock"])
        self.stock_filter.currentTextChanged.connect(self.filter_products)
        filter_layout.addWidget(self.stock_filter)
        
        filter_layout.addStretch()
        
        self.view_mode_btn = QPushButton("📋 Table View")
        self.view_mode_btn.setCheckable(True)
        self.view_mode_btn.setChecked(True)
        filter_layout.addWidget(self.view_mode_btn)
        
        layout.addLayout(filter_layout)
        
        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(10)
        self.products_table.setHorizontalHeaderLabels([
            "Code", "Name", "Category", "Unit", "Purchase", "Selling", "GST%", "Stock", "Status", "Actions"
        ])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                gridline-color: #ecf0f1;
                background-color: white;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px 8px;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 12px 8px;
                border: none;
                font-weight: bold;
                font-size: 13px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.products_table)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.count_label = QLabel("Showing 0 products")
        self.count_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        status_layout.addWidget(self.count_label)
        
        layout.addLayout(status_layout)
        
        self.setLayout(layout)
    
    def create_stat_card(self, title, value, color, icon):
        """Create enhanced statistics card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                padding: 20px;
            }}
            QFrame:hover {{
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"""
            font-size: 36px;
            color: {color};
        """)
        layout.addWidget(icon_label)
        
        # Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: bold;")
        text_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 24px; font-weight: bold;")
        value_label.setObjectName("value_label")
        text_layout.addWidget(value_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        card.setLayout(layout)
        return card
    
    def update_stat_card(self, card, value):
        """Update stat card value"""
        value_label = card.findChild(QLabel, "value_label")
        if value_label:
            value_label.setText(str(value))
    
    def load_products(self):
        """Load products with enhanced display"""
        products = self.db_manager.get_all_products()
        self.populate_table(products)
        
        # Update statistics
        self.update_stat_card(self.total_products_card, str(len(products)))
        
        total_value = sum(p['current_stock'] * p['purchase_price'] for p in products)
        self.update_stat_card(self.total_value_card, f"₹{total_value:,.0f}")
        
        low_stock = len([p for p in products if p['current_stock'] <= p['min_stock_level']])
        self.update_stat_card(self.low_stock_card, str(low_stock))
        
        categories = self.db_manager.get_all_categories()
        self.update_stat_card(self.categories_card, str(len(categories)))
        
        # Update category filter
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        for cat in categories:
            self.category_filter.addItem(cat['category_name'])
        
        self.status_label.setText("Products loaded successfully")
        self.count_label.setText(f"Showing {len(products)} products")
    
    def populate_table(self, products):
        """Populate products table with enhanced styling"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Set row height
            self.products_table.setRowHeight(row, 50)
            
            # Code
            code_item = QTableWidgetItem(product['product_code'])
            code_item.setFont(QFont("Courier", 11, QFont.Weight.Bold))
            self.products_table.setItem(row, 0, code_item)
            
            # Name
            name_item = QTableWidgetItem(product['product_name'])
            name_item.setFont(QFont("Arial", 11))
            self.products_table.setItem(row, 1, name_item)
            
            # Category
            self.products_table.setItem(row, 2, QTableWidgetItem(product.get('category', '-')))
            
            # Unit
            unit_item = QTableWidgetItem(product['unit'])
            unit_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 3, unit_item)
            
            # Purchase Price
            purchase_item = QTableWidgetItem(f"₹{product['purchase_price']:,.2f}")
            purchase_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 4, purchase_item)
            
            # Selling Price
            selling_item = QTableWidgetItem(f"₹{product['selling_price']:,.2f}")
            selling_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            selling_item.setForeground(QColor("#27ae60"))
            selling_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            self.products_table.setItem(row, 5, selling_item)
            
            # GST
            gst_item = QTableWidgetItem(f"{product['gst_rate']:.1f}%")
            gst_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.products_table.setItem(row, 6, gst_item)
            
            # Stock
            stock_item = QTableWidgetItem(f"{product['current_stock']:.0f}")
            stock_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stock_item.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            
            if product['current_stock'] <= 0:
                stock_item.setForeground(QColor("#e74c3c"))
                stock_item.setText(f"{product['current_stock']:.0f} ⚠️")
            elif product['current_stock'] <= product['min_stock_level']:
                stock_item.setForeground(QColor("#f39c12"))
                stock_item.setText(f"{product['current_stock']:.0f} ⚠️")
            else:
                stock_item.setForeground(QColor("#27ae60"))
                stock_item.setText(f"{product['current_stock']:.0f} ✓")
            
            self.products_table.setItem(row, 7, stock_item)
            
            # Status badge
            if product['current_stock'] <= 0:
                status = "🔴 Out"
                color = "#e74c3c"
            elif product['current_stock'] <= product['min_stock_level']:
                status = "🟡 Low"
                color = "#f39c12"
            else:
                status = "🟢 Good"
                color = "#27ae60"
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item.setForeground(QColor(color))
            status_item.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.products_table.setItem(row, 8, status_item)
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setToolTip("Edit product")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setToolTip("Delete product")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    padding: 6px 10px;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.products_table.setCellWidget(row, 9, actions_widget)
    
    def search_products(self):
        """Search products with enhanced filtering"""
        search_term = self.search_input.text().strip()
        
        if search_term:
            products = self.db_manager.search_products(search_term)
            self.status_label.setText(f"Search results for '{search_term}'")
        else:
            products = self.db_manager.get_all_products()
            self.status_label.setText("Showing all products")
        
        self.populate_table(products)
        self.count_label.setText(f"Showing {len(products)} products")
    
    def filter_products(self):
        """Filter products by category and stock status"""
        category = self.category_filter.currentText()
        stock_status = self.stock_filter.currentText()
        
        products = self.db_manager.get_all_products()
        
        # Filter by category
        if category != "All Categories":
            products = [p for p in products if p.get('category') == category]
        
        # Filter by stock status
        if stock_status == "In Stock":
            products = [p for p in products if p['current_stock'] > p['min_stock_level']]
        elif stock_status == "Low Stock":
            products = [p for p in products if 0 < p['current_stock'] <= p['min_stock_level']]
        elif stock_status == "Out of Stock":
            products = [p for p in products if p['current_stock'] <= 0]
        
        self.populate_table(products)
        self.count_label.setText(f"Showing {len(products)} products")
        self.status_label.setText(f"Filtered by {category} - {stock_status}")
    
    def add_product(self):
        """Add new product"""
        dialog = EnhancedProductDialog(self.db_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def edit_product(self, product):
        """Edit product"""
        dialog = EnhancedProductDialog(self.db_manager, product, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()
    
    def delete_product(self, product):
        """Delete product with confirmation"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete:\n\n{product['product_name']}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_product(product['id']):
                QMessageBox.information(self, "Success", "Product deleted successfully!")
                self.load_products()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete product")
    
    def import_from_pdf(self):
        """Import products from PDF with enhanced UI"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select PDF File", "", "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        # Show progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle("Importing from PDF")
        progress_dialog.setModal(True)
        progress_dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        status_label = QLabel("Starting import...")
        layout.addWidget(status_label)
        
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        layout.addWidget(progress_bar)
        
        progress_dialog.setLayout(layout)
        progress_dialog.show()
        
        # Start import thread
        existing_products = self.db_manager.get_all_products()
        self.pdf_import_thread = PDFImportThread(file_path, existing_products)
        
        self.pdf_import_thread.progress.connect(
            lambda value, msg: (progress_bar.setValue(value), status_label.setText(msg))
        )
        
        self.pdf_import_thread.finished.connect(
            lambda results: self.show_import_results(results, progress_dialog)
        )
        
        self.pdf_import_thread.error.connect(
            lambda error: (QMessageBox.critical(self, "Error", error), progress_dialog.close())
        )
        
        self.pdf_import_thread.start()
    
    def show_import_results(self, matched_products, progress_dialog):
        """Show import results with enhanced UI"""
        progress_dialog.close()
        
        if not matched_products:
            QMessageBox.information(self, "No Results", "No products found in PDF")
            return
        
        # Create results dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("PDF Import Results")
        dialog.setModal(True)
        dialog.setMinimumSize(900, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Summary
        matched_count = sum(1 for m in matched_products if m['status'] == 'matched')
        no_match_count = len(matched_products) - matched_count
        
        summary = QLabel(
            f"📊 Found {len(matched_products)} products | "
            f"✅ {matched_count} matched | "
            f"❌ {no_match_count} new"
        )
        summary.setStyleSheet("""
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(summary)
        
        # Results table
        results_table = QTableWidget()
        results_table.setColumnCount(6)
        results_table.setHorizontalHeaderLabels([
            "Status", "Code", "Name", "New Price", "Current Price", "Confidence"
        ])
        results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        results_table.setAlternatingRowColors(True)
        results_table.setRowCount(len(matched_products))
        
        for row, match in enumerate(matched_products):
            extracted = match['extracted']
            matched_prod = match['matched']
            confidence = match['confidence']
            
            # Status
            if match['status'] == 'matched':
                status_item = QTableWidgetItem("✅ Matched")
                status_item.setForeground(QColor("#27ae60"))
            else:
                status_item.setForeground(QColor("#e74c3c"))
                status_item = QTableWidgetItem("❌ New")
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            results_table.setItem(row, 0, status_item)
            
            # Code
            results_table.setItem(row, 1, QTableWidgetItem(extracted['product_code']))
            
            # Name
            results_table.setItem(row, 2, QTableWidgetItem(extracted['product_name']))
            
            # New Price
            new_price_item = QTableWidgetItem(f"₹{extracted['price']:,.2f}")
            new_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            new_price_item.setForeground(QColor("#3498db"))
            results_table.setItem(row, 3, new_price_item)
            
            # Current Price
            if matched_prod:
                current_price = f"₹{matched_prod['selling_price']:,.2f}"
            else:
                current_price = "-"
            current_price_item = QTableWidgetItem(current_price)
            current_price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            results_table.setItem(row, 4, current_price_item)
            
            # Confidence
            conf_item = QTableWidgetItem(f"{confidence:.0f}%")
            conf_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if confidence >= 90:
                conf_item.setForeground(QColor("#27ae60"))
            elif confidence >= 70:
                conf_item.setForeground(QColor("#f39c12"))
            else:
                conf_item.setForeground(QColor("#e74c3c"))
            
            results_table.setItem(row, 5, conf_item)
        
        layout.addWidget(results_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply Updates")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        apply_btn.clicked.connect(lambda: self.apply_price_updates(matched_products, dialog))
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def apply_price_updates(self, matched_products, dialog):
        """Apply price updates from PDF import"""
        updated_count = 0
        
        for match in matched_products:
            if match['status'] == 'matched' and match['matched']:
                product_id = match['matched']['id']
                new_price = match['extracted']['price']
                
                if self.db_manager.update_product(product_id, {'selling_price': new_price}):
                    updated_count += 1
        
        dialog.accept()
        QMessageBox.information(self, "Success", 
                              f"Updated prices for {updated_count} products!")
        self.load_products()
    
    def export_to_excel(self):
        """Export products to Excel"""
        QMessageBox.information(self, "Coming Soon", "Excel export feature coming soon!")
    
    def export_to_pdf(self):
        """Export products to PDF"""
        QMessageBox.information(self, "Coming Soon", "PDF export feature coming soon!")
