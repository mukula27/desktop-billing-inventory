# Quick Start Guide

Get up and running with the Billing & Inventory System in 5 minutes!

## 🚀 Quick Installation

### Windows

1. **Download Python** (if not installed)
   - Go to https://python.org/downloads
   - Download Python 3.10 or higher
   - ✅ Check "Add Python to PATH" during installation

2. **Download the Application**
   ```cmd
   git clone https://github.com/mukula27/desktop-billing-inventory.git
   cd desktop-billing-inventory
   ```

3. **Install Dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```cmd
   python main.py
   ```

5. **Login**
   - Username: `admin`
   - Password: `admin123`

### Linux/Mac

```bash
# Install Python 3.10+ (if needed)
# Ubuntu/Debian:
sudo apt install python3.10 python3-pip

# Clone repository
git clone https://github.com/mukula27/desktop-billing-inventory.git
cd desktop-billing-inventory

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 📋 First Steps

### 1. Login
- Use default credentials: `admin` / `admin123`
- Change password in Settings after first login

### 2. Setup Company Information
1. Go to **Settings** → **Company Settings**
2. Enter:
   - Company Name
   - Address
   - Phone & Email
   - GSTIN (if applicable)
3. Click **Save**

### 3. Add Product Categories
1. Go to **Products** → **Categories**
2. Click **Add Category**
3. Enter category name (e.g., "Electronics", "Groceries")
4. Click **Save**

### 4. Add Your First Product
1. Go to **Products** → **Add Product**
2. Fill in:
   - Product Code: `PROD001`
   - Product Name: `Sample Product`
   - Category: Select from dropdown
   - Unit: `PCS`
   - Purchase Price: `100`
   - Selling Price: `150`
   - GST Rate: `18`
   - Opening Stock: `50`
   - Min Stock Level: `10`
3. Click **Save**

### 5. Add a Customer
1. Go to **Customers** → **Add Customer**
2. Fill in:
   - Customer Name: `John Doe`
   - Phone: `9876543210`
   - Address: `123 Main Street`
3. Click **Save**

### 6. Create Your First Invoice
1. Go to **Billing** → **New Invoice**
2. Select customer or enter details
3. Click **Add Product**
4. Search and select product
5. Enter quantity
6. Review totals
7. Click **Save**
8. Click **Print** or **Save as PDF**

### 7. Record Payment
1. Open the invoice from invoice list
2. Click **Add Payment**
3. Enter:
   - Amount
   - Payment Mode (Cash/UPI/Card)
   - Reference Number (optional)
4. Click **Save**

## 🎯 Common Tasks

### Import Price List from PDF
1. Go to **Products** → **Import Prices**
2. Click **Upload PDF**
3. Select supplier price list PDF
4. Review extracted data
5. Match with existing products
6. Click **Apply Updates**

### Generate Reports
1. Go to **Reports**
2. Select report type:
   - Sales Report
   - Stock Report
   - Customer Ledger
   - Payment Report
3. Set date range (if applicable)
4. Click **Generate**
5. Click **Export PDF** or **Export Excel**

### Backup Database
1. Go to **Settings** → **Backup**
2. Click **Create Backup**
3. Choose location and filename
4. Click **Save**

### Check Low Stock
1. Go to **Dashboard**
2. View "Low Stock Alerts" widget
3. Or go to **Reports** → **Low Stock Report**

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Invoice |
| `Ctrl+S` | Save |
| `Ctrl+P` | Print |
| `Ctrl+F` | Search |
| `F5` | Refresh |
| `Esc` | Close Dialog |
| `Ctrl+Q` | Exit Application |

## 🔧 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt --force-reinstall
```

### Database error on startup
```bash
# Delete the database file and restart
rm billing_inventory.db  # Linux/Mac
del billing_inventory.db  # Windows
python main.py
```

### PDF generation not working
```bash
pip install reportlab --upgrade
```

### Application won't start
```bash
# Check Python version (must be 3.10+)
python --version

# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

## 📱 Daily Workflow Example

### Morning Routine
1. **Login** to the system
2. **Check Dashboard** for:
   - Yesterday's sales
   - Pending payments
   - Low stock alerts
3. **Review** unpaid invoices

### During Business Hours
1. **Create invoices** as customers make purchases
2. **Record payments** as they come in
3. **Add new products** as needed
4. **Update stock** for new inventory

### End of Day
1. **Generate sales report** for the day
2. **Check payment status** of all invoices
3. **Review stock levels**
4. **Create backup** of database

## 🎓 Video Tutorials

Coming soon! Check the repository for video guides on:
- Complete setup walkthrough
- Creating your first invoice
- Importing price lists from PDF
- Generating reports
- Advanced features

## 💡 Tips & Best Practices

### Stock Management
- Set realistic minimum stock levels
- Review low stock alerts daily
- Update stock immediately after receiving inventory

### Invoicing
- Use consistent product codes
- Add customer details for better tracking
- Record payments promptly

### Data Safety
- **Backup daily** (or after significant changes)
- Store backups in multiple locations
- Test restore process periodically

### Performance
- Archive old invoices periodically
- Keep product list organized with categories
- Use search instead of scrolling through long lists

## 📞 Need Help?

- **Documentation:** Check README.md and ARCHITECTURE.md
- **Issues:** Open an issue on GitHub
- **Email:** info@mybusiness.com

## 🎉 You're Ready!

You now have a fully functional billing and inventory system. Start by:
1. ✅ Adding your products
2. ✅ Creating your first invoice
3. ✅ Exploring the reports

**Happy Billing! 💰**

---

**Next Steps:**
- Read the full [README.md](README.md) for detailed features
- Check [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) to create standalone .exe
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
