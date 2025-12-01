# Desktop Billing & Inventory Management System

A comprehensive offline desktop application for small businesses to manage billing, inventory, and customer relationships. All data is stored locally on your PC with no cloud dependency.

## Features

### 📦 Product & Stock Management
- Add, edit, and delete products with detailed information
- Automatic stock updates on sales
- Low stock alerts
- Category-based organization
- Search and filter products

### 💰 Billing & Invoices
- Create professional invoices with auto-generated invoice numbers
- Multi-item billing with quantity, discounts, and taxes
- Automatic calculations (subtotal, tax, grand total, rounding)
- Save invoices as PDF
- Print invoices
- Re-open and reprint old invoices

### 📄 PDF Price List Import
- Upload supplier price list PDFs
- Automatic extraction of product codes, names, and prices
- Review and match with existing products
- Bulk price updates with confirmation

### 💳 Payment Tracking
- Track payment status (Paid/Unpaid/Partially Paid)
- Multiple payment modes (Cash, UPI, Bank Transfer, Card)
- Payment history for each invoice
- Customer-wise ledger with total purchases, payments, and dues

### 👥 Customer Management
- Maintain customer database
- Track customer purchase history
- Customer ledger reports
- Export customer statements as PDF

### 📊 Reports & Analytics
- Dashboard with key metrics (today's sales, total due, low stock)
- Sales reports by date range, customer, or product
- Stock reports (current stock, low stock items)
- Payment/due reports
- Export all reports as PDF or Excel

### 🔒 Security & Data
- Password-protected login
- All data stored locally in SQLite database
- Easy backup and restore functionality
- No internet required

## Technology Stack

- **Python 3.10+** - Core language
- **PyQt6** - Modern desktop UI framework
- **SQLite** - Local database
- **ReportLab** - PDF generation
- **pdfplumber** - PDF reading for price updates
- **PyInstaller** - Create standalone .exe

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/mukula27/desktop-billing-inventory.git
cd desktop-billing-inventory
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python main.py
```

## Building Standalone Executable

To create a standalone .exe file for Windows:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Build the executable
pyinstaller --name="BillingSystem" --windowed --onefile --icon=icon.ico main.py

# The .exe will be in the 'dist' folder
```

For a more detailed build with all resources:

```bash
pyinstaller --name="BillingSystem" \
    --windowed \
    --onefile \
    --add-data "database;database" \
    --add-data "utils;utils" \
    --icon=icon.ico \
    main.py
```

## Default Login Credentials

- **Username:** admin
- **Password:** admin123

⚠️ **Important:** Change the default password after first login from Settings.

## Database Schema

The application uses SQLite with the following main tables:

- **company_settings** - Company information and configuration
- **users** - User accounts and authentication
- **categories** - Product categories
- **products** - Product catalog with stock information
- **customers** - Customer database
- **invoices** - Invoice headers
- **invoice_items** - Invoice line items
- **payments** - Payment transactions
- **stock_transactions** - Stock movement history
- **price_update_history** - Price change audit trail

## Usage Guide

### 1. Dashboard
- View today's sales, total dues, and low stock alerts
- Quick access to all modules

### 2. Products Management
- **Add Product:** Click "Add Product" button, fill details, and save
- **Edit Product:** Select product from list and click "Edit"
- **Search:** Use search bar to find products by name or code
- **Stock Update:** Manually adjust stock from product details

### 3. Create Invoice
- Click "New Invoice" from Billing module
- Add customer details (or select existing customer)
- Add products to invoice (search and select)
- Set quantity, discount, and tax for each item
- Review totals and save
- Print or save as PDF

### 4. Import Price List from PDF
- Go to Products → Import Prices
- Upload supplier PDF price list
- Review extracted data
- Match with existing products
- Confirm and apply price updates

### 5. Payment Management
- Open invoice from invoice list
- Click "Add Payment"
- Enter payment amount, mode, and reference
- Payment status updates automatically

### 6. Reports
- **Sales Report:** Filter by date range, view sales summary
- **Stock Report:** View current stock levels
- **Low Stock:** See products below minimum level
- **Customer Ledger:** View customer-wise transactions
- Export any report as PDF or Excel

### 7. Backup & Restore
- Go to Settings → Backup
- Click "Create Backup" to save database file
- Use "Restore Backup" to restore from a backup file
- Store backups in a safe location

## File Structure

```
desktop-billing-inventory/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── database/
│   ├── schema.sql              # Database schema
│   └── db_manager.py           # Database operations
├── ui/
│   ├── login_window.py         # Login screen
│   ├── main_window.py          # Main application window
│   ├── dashboard.py            # Dashboard module
│   ├── products_module.py      # Products management
│   ├── billing_module.py       # Billing/invoicing
│   ├── customers_module.py     # Customer management
│   ├── reports_module.py       # Reports and analytics
│   └── settings_module.py      # Settings and configuration
├── utils/
│   ├── pdf_generator.py        # PDF generation
│   └── pdf_price_extractor.py  # PDF price list extraction
└── billing_inventory.db        # SQLite database (created on first run)
```

## Keyboard Shortcuts

- **Ctrl+N** - New Invoice
- **Ctrl+P** - Print
- **Ctrl+S** - Save
- **Ctrl+F** - Search
- **F5** - Refresh
- **Esc** - Close dialog

## Troubleshooting

### Database Error on First Run
- Ensure `database/schema.sql` exists
- Check file permissions
- Delete `billing_inventory.db` and restart

### PDF Generation Issues
- Ensure ReportLab is installed: `pip install reportlab`
- Check write permissions in output directory

### PDF Import Not Working
- Ensure pdfplumber is installed: `pip install pdfplumber`
- Try different PDF formats
- Use manual entry if automatic extraction fails

### Application Won't Start
- Check Python version: `python --version` (should be 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check for error messages in console

## Support & Contribution

For issues, feature requests, or contributions:
- Open an issue on GitHub
- Submit a pull request
- Contact: info@mybusiness.com

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0 (Initial Release)
- Complete billing and inventory management
- PDF invoice generation
- PDF price list import
- Payment tracking
- Customer management
- Reports and analytics
- Backup and restore functionality

## Future Enhancements

- [ ] Barcode scanning support
- [ ] Multi-user access with roles
- [ ] Email invoice functionality
- [ ] SMS notifications
- [ ] Advanced analytics and charts
- [ ] Purchase order management
- [ ] Expense tracking
- [ ] Multi-currency support
- [ ] Cloud sync (optional)

---

**Made with ❤️ for small businesses**
