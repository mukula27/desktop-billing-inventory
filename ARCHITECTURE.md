# Architecture Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Dashboard │  │ Products │  │ Billing  │  │ Reports  │   │
│  │  Module  │  │  Module  │  │  Module  │  │  Module  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│         PyQt6 Widgets & Custom Components                    │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Invoice    │  │    Stock     │  │   Payment    │     │
│  │  Calculator  │  │   Manager    │  │   Processor  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Data Access Layer                         │
│                   ┌──────────────────┐                       │
│                   │   DB Manager     │                       │
│                   │  (db_manager.py) │                       │
│                   └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Database Layer                            │
│                   ┌──────────────────┐                       │
│                   │  SQLite Database │                       │
│                   │ (billing_inv.db) │                       │
│                   └──────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Utility Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     PDF      │  │     PDF      │  │    Excel     │     │
│  │  Generator   │  │  Extractor   │  │   Exporter   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│ company_settings│
└─────────────────┘

┌─────────────┐         ┌──────────────┐
│    users    │         │  categories  │
└─────────────┘         └──────────────┘
                               │
                               │ 1:N
                               ↓
┌─────────────┐         ┌──────────────┐
│  customers  │         │   products   │
└─────────────┘         └──────────────┘
      │                        │
      │ 1:N                    │ 1:N
      ↓                        ↓
┌─────────────┐         ┌──────────────────────┐
│  invoices   │←────────│  stock_transactions  │
└─────────────┘  N:1    └──────────────────────┘
      │
      │ 1:N
      ↓
┌──────────────┐
│invoice_items │
└──────────────┘
      │
      │ N:1
      ↓
┌──────────────┐
│   products   │
└──────────────┘

┌─────────────┐
│  payments   │
└─────────────┘
      │
      │ N:1
      ↓
┌─────────────┐
│  invoices   │
└─────────────┘
```

### Table Descriptions

#### company_settings
Stores company information and configuration
- **Primary Key:** id
- **Fields:** company_name, address, phone, email, gstin, logo_path, invoice_prefix, invoice_counter, tax_enabled
- **Purpose:** Single row table for company configuration

#### users
User accounts for authentication
- **Primary Key:** id
- **Unique:** username
- **Fields:** username, password_hash, full_name, role, is_active
- **Purpose:** Multi-user support with role-based access

#### categories
Product categories for organization
- **Primary Key:** id
- **Unique:** name
- **Fields:** name, description
- **Purpose:** Organize products into categories

#### products
Product catalog with stock information
- **Primary Key:** id
- **Unique:** product_code
- **Foreign Keys:** category_id → categories(id)
- **Fields:** product_code, product_name, unit, purchase_price, selling_price, gst_rate, opening_stock, current_stock, min_stock_level, is_active
- **Purpose:** Master product list with pricing and stock

#### customers
Customer database
- **Primary Key:** id
- **Fields:** customer_name, phone, email, address, gstin, opening_balance
- **Purpose:** Store customer information for invoicing and ledger

#### invoices
Invoice headers
- **Primary Key:** id
- **Unique:** invoice_number
- **Foreign Keys:** customer_id → customers(id), created_by → users(id)
- **Fields:** invoice_number, customer details, invoice_date, invoice_time, subtotal, discount, tax_amount, grand_total, rounded_total, payment_status, amount_paid, balance_amount, notes
- **Purpose:** Store invoice master data

#### invoice_items
Invoice line items
- **Primary Key:** id
- **Foreign Keys:** invoice_id → invoices(id), product_id → products(id)
- **Fields:** product details, quantity, unit_price, discount, taxable_amount, gst_rate, gst_amount, total_amount
- **Purpose:** Store individual items in each invoice
- **Cascade:** DELETE on invoice deletion

#### payments
Payment transactions
- **Primary Key:** id
- **Foreign Keys:** invoice_id → invoices(id), created_by → users(id)
- **Fields:** payment_date, payment_time, amount, payment_mode, reference_number, notes
- **Purpose:** Track all payments against invoices

#### stock_transactions
Stock movement history
- **Primary Key:** id
- **Foreign Keys:** product_id → products(id), created_by → users(id)
- **Fields:** transaction_type, quantity, reference_type, reference_id, notes, transaction_date
- **Purpose:** Audit trail for all stock changes

#### price_update_history
Price change audit trail
- **Primary Key:** id
- **Foreign Keys:** product_id → products(id), updated_by → users(id)
- **Fields:** old_purchase_price, new_purchase_price, old_selling_price, new_selling_price, update_source, notes
- **Purpose:** Track price changes over time

## Application Flow

### 1. Application Startup

```
main.py
  ↓
Initialize QApplication
  ↓
Create DatabaseManager
  ↓
Check/Create Database
  ↓
Show Splash Screen
  ↓
Show Login Window
  ↓
Authenticate User
  ↓
Show Main Window
```

### 2. Invoice Creation Flow

```
User clicks "New Invoice"
  ↓
Open Billing Module
  ↓
Select/Add Customer
  ↓
Add Products (search & select)
  ↓
Set Quantity & Discount
  ↓
Calculate Line Totals
  ↓
Calculate Invoice Totals
  ↓
Save Invoice to Database
  ↓
Update Product Stock
  ↓
Record Stock Transaction
  ↓
Generate Invoice Number
  ↓
Show Invoice Preview
  ↓
Print/Save as PDF
```

### 3. PDF Price Import Flow

```
User uploads PDF
  ↓
PDFPriceExtractor.extract_from_pdf()
  ↓
Try pdfplumber (table extraction)
  ↓
Fallback to PyPDF2 (text extraction)
  ↓
Parse product data (code, name, price)
  ↓
Match with existing products
  ↓
Show review screen
  ↓
User confirms matches
  ↓
Update product prices
  ↓
Record price history
  ↓
Show success message
```

### 4. Payment Processing Flow

```
User opens invoice
  ↓
Click "Add Payment"
  ↓
Enter payment details
  ↓
Validate amount
  ↓
Save payment record
  ↓
Update invoice amounts
  ↓
Calculate new balance
  ↓
Update payment status
  ↓
Refresh invoice display
```

## Module Structure

### UI Modules

#### main_window.py
- Main application window
- Menu bar and toolbar
- Module navigation
- Status bar

#### dashboard.py
- Summary statistics
- Quick actions
- Recent activity
- Alerts (low stock, overdue payments)

#### products_module.py
- Product list view
- Add/Edit product forms
- Stock management
- Category management
- Price import interface

#### billing_module.py
- Invoice creation form
- Product selection
- Calculation engine
- Invoice preview
- PDF generation

#### customers_module.py
- Customer list
- Add/Edit customer forms
- Customer ledger view
- Transaction history

#### reports_module.py
- Report selection
- Date range filters
- Report preview
- Export options (PDF/Excel)

#### settings_module.py
- Company settings
- User management
- Backup/Restore
- Application preferences

### Business Logic

#### Invoice Calculator
```python
class InvoiceCalculator:
    def calculate_line_total(item):
        # Calculate single line item
        taxable = (quantity * unit_price) - discount
        gst = taxable * (gst_rate / 100)
        total = taxable + gst
        return total
    
    def calculate_invoice_total(items):
        # Calculate invoice totals
        subtotal = sum(item.taxable_amount)
        tax = sum(item.gst_amount)
        grand_total = subtotal + tax
        rounded_total = round(grand_total)
        return totals
```

#### Stock Manager
```python
class StockManager:
    def update_stock(product_id, quantity, type):
        # Update product stock
        # Record transaction
        # Check minimum level
        # Trigger alerts if needed
```

## Data Flow Patterns

### Read Operations
```
UI Component
  ↓
Call DB Manager method
  ↓
Execute SQL SELECT
  ↓
Return List[Dict]
  ↓
Display in UI
```

### Write Operations
```
UI Component
  ↓
Validate Input
  ↓
Call DB Manager method
  ↓
Execute SQL INSERT/UPDATE
  ↓
Commit transaction
  ↓
Return success/failure
  ↓
Update UI
```

### Transaction Pattern
```python
try:
    # Begin transaction (implicit)
    db.execute_update(query1, params1)
    db.execute_update(query2, params2)
    db.conn.commit()
    return success
except Exception as e:
    db.conn.rollback()
    return failure
```

## Security Considerations

### Authentication
- Password hashing using SHA-256
- Session management
- User role validation

### Data Protection
- Local storage only
- No network transmission
- Encrypted backups (optional)

### Input Validation
- SQL injection prevention (parameterized queries)
- Data type validation
- Range checks
- Required field validation

## Performance Optimization

### Database Indexes
```sql
CREATE INDEX idx_products_code ON products(product_code);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
```

### Query Optimization
- Use prepared statements
- Limit result sets
- Pagination for large lists
- Lazy loading for reports

### UI Optimization
- Async operations for heavy tasks
- Progress indicators
- Caching frequently accessed data
- Virtual scrolling for large lists

## Error Handling

### Database Errors
```python
try:
    result = db.execute_query(query, params)
except sqlite3.IntegrityError:
    # Handle duplicate key, foreign key violations
except sqlite3.OperationalError:
    # Handle database locked, disk full
except Exception as e:
    # Handle unexpected errors
```

### UI Errors
```python
try:
    # UI operation
except Exception as e:
    QMessageBox.critical(self, "Error", str(e))
    logger.error(f"UI Error: {e}")
```

## Logging Strategy

```python
import logging

logging.basicConfig(
    filename='billing_system.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Application started")
logger.error("Database error", exc_info=True)
```

## Testing Strategy

### Unit Tests
- Database operations
- Calculation functions
- PDF generation
- PDF extraction

### Integration Tests
- Invoice creation flow
- Payment processing
- Stock updates
- Report generation

### UI Tests
- Form validation
- Navigation
- Data display
- User interactions

---

**This architecture ensures:**
- ✅ Separation of concerns
- ✅ Maintainability
- ✅ Scalability
- ✅ Testability
- ✅ Security
- ✅ Performance
