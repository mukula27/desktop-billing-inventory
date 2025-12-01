"""
Database Manager - Handles all database operations
"""
import sqlite3
import os
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class DatabaseManager:
    def __init__(self, db_path: str = "billing_inventory.db"):
        """Initialize database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def initialize_database(self):
        """Create database and tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            
            # Read and execute schema
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            if os.path.exists(schema_path):
                with open(schema_path, 'r') as f:
                    schema = f.read()
                    self.cursor.executescript(schema)
                    self.conn.commit()
            
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SELECT query and return results"""
        try:
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error executing update: {e}")
            self.conn.rollback()
            return -1
    
    # ==================== USER OPERATIONS ====================
    
    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = "SELECT * FROM users WHERE username = ? AND password_hash = ? AND is_active = 1"
        results = self.execute_query(query, (username, password_hash))
        return results[0] if results else None
    
    def create_user(self, username: str, password: str, full_name: str, role: str = 'admin') -> int:
        """Create new user"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        query = """INSERT INTO users (username, password_hash, full_name, role) 
                   VALUES (?, ?, ?, ?)"""
        return self.execute_update(query, (username, password_hash, full_name, role))
    
    # ==================== CATEGORY OPERATIONS ====================
    
    def get_all_categories(self) -> List[Dict]:
        """Get all categories"""
        return self.execute_query("SELECT * FROM categories ORDER BY name")
    
    def add_category(self, name: str, description: str = "") -> int:
        """Add new category"""
        query = "INSERT INTO categories (name, description) VALUES (?, ?)"
        return self.execute_update(query, (name, description))
    
    # ==================== PRODUCT OPERATIONS ====================
    
    def get_all_products(self, active_only: bool = True) -> List[Dict]:
        """Get all products"""
        query = """SELECT p.*, c.name as category_name 
                   FROM products p 
                   LEFT JOIN categories c ON p.category_id = c.id"""
        if active_only:
            query += " WHERE p.is_active = 1"
        query += " ORDER BY p.product_name"
        return self.execute_query(query)
    
    def search_products(self, search_term: str) -> List[Dict]:
        """Search products by name or code"""
        query = """SELECT p.*, c.name as category_name 
                   FROM products p 
                   LEFT JOIN categories c ON p.category_id = c.id
                   WHERE (p.product_name LIKE ? OR p.product_code LIKE ?) 
                   AND p.is_active = 1
                   ORDER BY p.product_name"""
        search = f"%{search_term}%"
        return self.execute_query(query, (search, search))
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """Get product by ID"""
        query = "SELECT * FROM products WHERE id = ?"
        results = self.execute_query(query, (product_id,))
        return results[0] if results else None
    
    def get_product_by_code(self, product_code: str) -> Optional[Dict]:
        """Get product by code"""
        query = "SELECT * FROM products WHERE product_code = ?"
        results = self.execute_query(query, (product_code,))
        return results[0] if results else None
    
    def add_product(self, product_data: Dict) -> int:
        """Add new product"""
        query = """INSERT INTO products 
                   (product_code, product_name, category_id, unit, purchase_price, 
                    selling_price, gst_rate, opening_stock, current_stock, min_stock_level)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        opening_stock = product_data.get('opening_stock', 0)
        params = (
            product_data['product_code'],
            product_data['product_name'],
            product_data.get('category_id'),
            product_data.get('unit', 'PCS'),
            product_data.get('purchase_price', 0),
            product_data['selling_price'],
            product_data.get('gst_rate', 0),
            opening_stock,
            opening_stock,  # current_stock = opening_stock initially
            product_data.get('min_stock_level', 0)
        )
        return self.execute_update(query, params)
    
    def update_product(self, product_id: int, product_data: Dict) -> bool:
        """Update existing product"""
        query = """UPDATE products SET 
                   product_name = ?, category_id = ?, unit = ?, 
                   purchase_price = ?, selling_price = ?, gst_rate = ?, 
                   min_stock_level = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?"""
        params = (
            product_data['product_name'],
            product_data.get('category_id'),
            product_data.get('unit', 'PCS'),
            product_data.get('purchase_price', 0),
            product_data['selling_price'],
            product_data.get('gst_rate', 0),
            product_data.get('min_stock_level', 0),
            product_id
        )
        return self.execute_update(query, params) != -1
    
    def update_product_stock(self, product_id: int, quantity: float, transaction_type: str, 
                            reference_type: str = None, reference_id: int = None, notes: str = "") -> bool:
        """Update product stock and record transaction"""
        try:
            # Get current stock
            product = self.get_product_by_id(product_id)
            if not product:
                return False
            
            # Calculate new stock
            if transaction_type in ['sale', 'damage', 'return_to_supplier']:
                new_stock = product['current_stock'] - quantity
            else:  # purchase, return_from_customer, adjustment
                new_stock = product['current_stock'] + quantity
            
            # Update product stock
            query = "UPDATE products SET current_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            self.execute_update(query, (new_stock, product_id))
            
            # Record transaction
            query = """INSERT INTO stock_transactions 
                       (product_id, transaction_type, quantity, reference_type, reference_id, notes, transaction_date)
                       VALUES (?, ?, ?, ?, ?, ?, DATE('now'))"""
            self.execute_update(query, (product_id, transaction_type, quantity, reference_type, reference_id, notes))
            
            return True
        except Exception as e:
            print(f"Error updating stock: {e}")
            return False
    
    def get_low_stock_products(self) -> List[Dict]:
        """Get products with stock below minimum level"""
        query = """SELECT p.*, c.name as category_name 
                   FROM products p 
                   LEFT JOIN categories c ON p.category_id = c.id
                   WHERE p.current_stock <= p.min_stock_level AND p.is_active = 1
                   ORDER BY p.current_stock"""
        return self.execute_query(query)
    
    # ==================== CUSTOMER OPERATIONS ====================
    
    def get_all_customers(self) -> List[Dict]:
        """Get all customers"""
        return self.execute_query("SELECT * FROM customers ORDER BY customer_name")
    
    def search_customers(self, search_term: str) -> List[Dict]:
        """Search customers by name or phone"""
        query = """SELECT * FROM customers 
                   WHERE customer_name LIKE ? OR phone LIKE ?
                   ORDER BY customer_name"""
        search = f"%{search_term}%"
        return self.execute_query(query, (search, search))
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        query = "SELECT * FROM customers WHERE id = ?"
        results = self.execute_query(query, (customer_id,))
        return results[0] if results else None
    
    def add_customer(self, customer_data: Dict) -> int:
        """Add new customer"""
        query = """INSERT INTO customers 
                   (customer_name, phone, email, address, gstin, opening_balance)
                   VALUES (?, ?, ?, ?, ?, ?)"""
        params = (
            customer_data['customer_name'],
            customer_data.get('phone', ''),
            customer_data.get('email', ''),
            customer_data.get('address', ''),
            customer_data.get('gstin', ''),
            customer_data.get('opening_balance', 0)
        )
        return self.execute_update(query, params)
    
    def update_customer(self, customer_id: int, customer_data: Dict) -> bool:
        """Update existing customer"""
        query = """UPDATE customers SET 
                   customer_name = ?, phone = ?, email = ?, address = ?, gstin = ?,
                   updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?"""
        params = (
            customer_data['customer_name'],
            customer_data.get('phone', ''),
            customer_data.get('email', ''),
            customer_data.get('address', ''),
            customer_data.get('gstin', ''),
            customer_id
        )
        return self.execute_update(query, params) != -1
    
    # ==================== INVOICE OPERATIONS ====================
    
    def generate_invoice_number(self) -> str:
        """Generate next invoice number"""
        settings = self.get_company_settings()
        prefix = settings.get('invoice_prefix', 'INV')
        counter = settings.get('invoice_counter', 1000)
        
        # Update counter
        query = "UPDATE company_settings SET invoice_counter = invoice_counter + 1"
        self.execute_update(query)
        
        return f"{prefix}{counter + 1}"
    
    def create_invoice(self, invoice_data: Dict, items: List[Dict]) -> Tuple[int, str]:
        """Create new invoice with items"""
        try:
            # Generate invoice number
            invoice_number = self.generate_invoice_number()
            
            # Insert invoice
            query = """INSERT INTO invoices 
                       (invoice_number, customer_id, customer_name, customer_phone, customer_address,
                        invoice_date, invoice_time, subtotal, discount_amount, discount_percent,
                        tax_amount, grand_total, rounded_total, payment_status, amount_paid, balance_amount, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            
            params = (
                invoice_number,
                invoice_data.get('customer_id'),
                invoice_data['customer_name'],
                invoice_data.get('customer_phone', ''),
                invoice_data.get('customer_address', ''),
                invoice_data.get('invoice_date', datetime.now().strftime('%Y-%m-%d')),
                invoice_data.get('invoice_time', datetime.now().strftime('%H:%M:%S')),
                invoice_data['subtotal'],
                invoice_data.get('discount_amount', 0),
                invoice_data.get('discount_percent', 0),
                invoice_data['tax_amount'],
                invoice_data['grand_total'],
                invoice_data['rounded_total'],
                invoice_data.get('payment_status', 'unpaid'),
                invoice_data.get('amount_paid', 0),
                invoice_data.get('balance_amount', invoice_data['rounded_total']),
                invoice_data.get('notes', '')
            )
            
            invoice_id = self.execute_update(query, params)
            
            if invoice_id == -1:
                return -1, ""
            
            # Insert invoice items and update stock
            item_query = """INSERT INTO invoice_items 
                           (invoice_id, product_id, product_code, product_name, quantity, unit,
                            unit_price, discount_percent, discount_amount, taxable_amount,
                            gst_rate, gst_amount, total_amount)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            
            for item in items:
                item_params = (
                    invoice_id,
                    item.get('product_id'),
                    item['product_code'],
                    item['product_name'],
                    item['quantity'],
                    item.get('unit', 'PCS'),
                    item['unit_price'],
                    item.get('discount_percent', 0),
                    item.get('discount_amount', 0),
                    item['taxable_amount'],
                    item.get('gst_rate', 0),
                    item.get('gst_amount', 0),
                    item['total_amount']
                )
                self.execute_update(item_query, item_params)
                
                # Update stock
                if item.get('product_id'):
                    self.update_product_stock(
                        item['product_id'],
                        item['quantity'],
                        'sale',
                        'invoice',
                        invoice_id,
                        f"Sale via invoice {invoice_number}"
                    )
            
            return invoice_id, invoice_number
        except Exception as e:
            print(f"Error creating invoice: {e}")
            self.conn.rollback()
            return -1, ""
    
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Dict]:
        """Get invoice by ID"""
        query = "SELECT * FROM invoices WHERE id = ?"
        results = self.execute_query(query, (invoice_id,))
        return results[0] if results else None
    
    def get_invoice_by_number(self, invoice_number: str) -> Optional[Dict]:
        """Get invoice by number"""
        query = "SELECT * FROM invoices WHERE invoice_number = ?"
        results = self.execute_query(query, (invoice_number,))
        return results[0] if results else None
    
    def get_invoice_items(self, invoice_id: int) -> List[Dict]:
        """Get all items for an invoice"""
        query = "SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id"
        return self.execute_query(query, (invoice_id,))
    
    def get_all_invoices(self, limit: int = 100) -> List[Dict]:
        """Get recent invoices"""
        query = "SELECT * FROM invoices ORDER BY invoice_date DESC, invoice_time DESC LIMIT ?"
        return self.execute_query(query, (limit,))
    
    def search_invoices(self, search_term: str = "", start_date: str = "", end_date: str = "", 
                       payment_status: str = "") -> List[Dict]:
        """Search invoices with filters"""
        query = "SELECT * FROM invoices WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (invoice_number LIKE ? OR customer_name LIKE ?)"
            search = f"%{search_term}%"
            params.extend([search, search])
        
        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)
        
        if payment_status:
            query += " AND payment_status = ?"
            params.append(payment_status)
        
        query += " ORDER BY invoice_date DESC, invoice_time DESC"
        return self.execute_query(query, tuple(params))
    
    # ==================== PAYMENT OPERATIONS ====================
    
    def add_payment(self, payment_data: Dict) -> int:
        """Add payment for an invoice"""
        try:
            # Insert payment
            query = """INSERT INTO payments 
                       (invoice_id, payment_date, payment_time, amount, payment_mode, reference_number, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)"""
            params = (
                payment_data['invoice_id'],
                payment_data.get('payment_date', datetime.now().strftime('%Y-%m-%d')),
                payment_data.get('payment_time', datetime.now().strftime('%H:%M:%S')),
                payment_data['amount'],
                payment_data['payment_mode'],
                payment_data.get('reference_number', ''),
                payment_data.get('notes', '')
            )
            payment_id = self.execute_update(query, params)
            
            # Update invoice payment status
            invoice = self.get_invoice_by_id(payment_data['invoice_id'])
            if invoice:
                new_amount_paid = invoice['amount_paid'] + payment_data['amount']
                new_balance = invoice['grand_total'] - new_amount_paid
                
                if new_balance <= 0:
                    status = 'paid'
                elif new_amount_paid > 0:
                    status = 'partially_paid'
                else:
                    status = 'unpaid'
                
                update_query = """UPDATE invoices SET 
                                 amount_paid = ?, balance_amount = ?, payment_status = ?,
                                 updated_at = CURRENT_TIMESTAMP
                                 WHERE id = ?"""
                self.execute_update(update_query, (new_amount_paid, new_balance, status, payment_data['invoice_id']))
            
            return payment_id
        except Exception as e:
            print(f"Error adding payment: {e}")
            return -1
    
    def get_invoice_payments(self, invoice_id: int) -> List[Dict]:
        """Get all payments for an invoice"""
        query = "SELECT * FROM payments WHERE invoice_id = ? ORDER BY payment_date DESC, payment_time DESC"
        return self.execute_query(query, (invoice_id,))
    
    # ==================== COMPANY SETTINGS ====================
    
    def get_company_settings(self) -> Dict:
        """Get company settings"""
        results = self.execute_query("SELECT * FROM company_settings LIMIT 1")
        return results[0] if results else {}
    
    def update_company_settings(self, settings: Dict) -> bool:
        """Update company settings"""
        query = """UPDATE company_settings SET 
                   company_name = ?, address = ?, phone = ?, email = ?, gstin = ?,
                   logo_path = ?, invoice_prefix = ?, tax_enabled = ?,
                   updated_at = CURRENT_TIMESTAMP
                   WHERE id = 1"""
        params = (
            settings.get('company_name', ''),
            settings.get('address', ''),
            settings.get('phone', ''),
            settings.get('email', ''),
            settings.get('gstin', ''),
            settings.get('logo_path', ''),
            settings.get('invoice_prefix', 'INV'),
            settings.get('tax_enabled', 1)
        )
        return self.execute_update(query, params) != -1
    
    # ==================== REPORTS ====================
    
    def get_dashboard_stats(self) -> Dict:
        """Get dashboard statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Today's sales
        query = "SELECT SUM(grand_total) as total FROM invoices WHERE invoice_date = ?"
        result = self.execute_query(query, (today,))
        today_sales = result[0]['total'] if result and result[0]['total'] else 0
        
        # Total due
        query = "SELECT SUM(balance_amount) as total FROM invoices WHERE payment_status != 'paid'"
        result = self.execute_query(query)
        total_due = result[0]['total'] if result and result[0]['total'] else 0
        
        # Low stock count
        query = "SELECT COUNT(*) as count FROM products WHERE current_stock <= min_stock_level AND is_active = 1"
        result = self.execute_query(query)
        low_stock_count = result[0]['count'] if result else 0
        
        # Unpaid invoices count
        query = "SELECT COUNT(*) as count FROM invoices WHERE payment_status = 'unpaid'"
        result = self.execute_query(query)
        unpaid_count = result[0]['count'] if result else 0
        
        return {
            'today_sales': today_sales,
            'total_due': total_due,
            'low_stock_count': low_stock_count,
            'unpaid_invoices': unpaid_count
        }
    
    def get_sales_report(self, start_date: str, end_date: str) -> List[Dict]:
        """Get sales report for date range"""
        query = """SELECT invoice_date, COUNT(*) as invoice_count, 
                   SUM(grand_total) as total_sales, SUM(amount_paid) as total_paid,
                   SUM(balance_amount) as total_due
                   FROM invoices 
                   WHERE invoice_date BETWEEN ? AND ?
                   GROUP BY invoice_date
                   ORDER BY invoice_date DESC"""
        return self.execute_query(query, (start_date, end_date))
    
    def get_customer_ledger(self, customer_id: int) -> Dict:
        """Get customer ledger with all transactions"""
        invoices = self.execute_query(
            "SELECT * FROM invoices WHERE customer_id = ? ORDER BY invoice_date DESC",
            (customer_id,)
        )
        
        total_purchases = sum(inv['grand_total'] for inv in invoices)
        total_paid = sum(inv['amount_paid'] for inv in invoices)
        total_due = sum(inv['balance_amount'] for inv in invoices)
        
        return {
            'invoices': invoices,
            'total_purchases': total_purchases,
            'total_paid': total_paid,
            'total_due': total_due
        }
    
    # ==================== BACKUP & RESTORE ====================
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            import shutil
            self.close()
            shutil.copy2(backup_path, self.db_path)
            self.initialize_database()
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
