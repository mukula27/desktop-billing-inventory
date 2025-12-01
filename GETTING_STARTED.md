# Getting Started - Desktop Billing & Inventory System

## 🎉 Welcome!

Thank you for choosing the Desktop Billing & Inventory Management System! This guide will help you get started quickly.

## 📦 What You Have

A **complete, production-ready** desktop application with:

✅ **Full-featured billing system**
✅ **Inventory management with stock tracking**
✅ **PDF invoice generation**
✅ **PDF price list import**
✅ **Customer management**
✅ **Payment tracking**
✅ **Comprehensive reports**
✅ **Local database (no cloud required)**
✅ **Complete documentation**

## 🚀 Quick Start (3 Steps)

### Step 1: Install Python

**Windows:**
1. Download from https://python.org/downloads
2. Run installer
3. ✅ **IMPORTANT:** Check "Add Python to PATH"
4. Click "Install Now"

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.10 python3-pip python3-venv
```

**Mac:**
```bash
brew install python@3.10
```

### Step 2: Get the Code

```bash
# Clone the repository
git clone https://github.com/mukula27/desktop-billing-inventory.git

# Navigate to folder
cd desktop-billing-inventory
```

### Step 3: Run the Application

**Windows:**
```cmd
# Double-click run.bat
# OR run in command prompt:
run.bat
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x run.sh

# Run the script
./run.sh
```

**Manual Method (All Platforms):**
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 🔐 First Login

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change the password after first login!**

## 📋 Initial Setup (5 Minutes)

### 1. Configure Company Settings

Go to **Settings** → **Company Settings**

Fill in:
- Company Name: `Your Business Name`
- Address: `Your Business Address`
- Phone: `Your Phone Number`
- Email: `your@email.com`
- GSTIN: `Your GST Number` (if applicable)

Click **Save**

### 2. Add Product Categories

Go to **Products** → **Categories** → **Add Category**

Add categories like:
- Electronics
- Groceries
- Stationery
- Clothing
- etc.

### 3. Add Your First Product

Go to **Products** → **Add Product**

Example:
```
Product Code: LAPTOP001
Product Name: Dell Laptop
Category: Electronics
Unit: PCS
Purchase Price: 40000
Selling Price: 50000
GST Rate: 18
Opening Stock: 10
Min Stock Level: 2
```

Click **Save**

### 4. Add a Customer

Go to **Customers** → **Add Customer**

Example:
```
Customer Name: John Doe
Phone: 9876543210
Email: john@example.com
Address: 123 Main Street, City
```

Click **Save**

### 5. Create Your First Invoice

Go to **Billing** → **New Invoice**

1. Select customer (or enter new customer details)
2. Click **Add Product**
3. Search and select product
4. Enter quantity: `2`
5. Review totals
6. Click **Save**
7. Click **Print** or **Save as PDF**

### 6. Record Payment

1. Open the invoice from invoice list
2. Click **Add Payment**
3. Enter:
   - Amount: `100000` (full amount)
   - Payment Mode: `Cash`
   - Reference: (optional)
4. Click **Save**

Status will change to **PAID**

## 📊 Understanding the Interface

### Dashboard
- **Today's Sales:** Total sales for today
- **Total Due:** Outstanding payments
- **Low Stock:** Products below minimum level
- **Unpaid Invoices:** Count of unpaid invoices

### Products Module
- **Product List:** View all products
- **Add Product:** Add new product
- **Edit Product:** Modify existing product
- **Import Prices:** Import from PDF price list
- **Categories:** Manage product categories

### Billing Module
- **New Invoice:** Create new invoice
- **Invoice List:** View all invoices
- **Search:** Find invoices by number or customer
- **Reprint:** Reprint old invoices

### Customers Module
- **Customer List:** View all customers
- **Add Customer:** Add new customer
- **Edit Customer:** Modify customer details
- **Ledger:** View customer transaction history

### Reports Module
- **Sales Report:** Sales by date range
- **Stock Report:** Current stock levels
- **Low Stock Report:** Products below minimum
- **Customer Ledger:** Customer-wise transactions
- **Payment Report:** Payment status overview

### Settings Module
- **Company Settings:** Configure company details
- **User Management:** Add/edit users
- **Backup:** Create database backup
- **Restore:** Restore from backup

## 🎯 Common Tasks

### Create an Invoice
1. Billing → New Invoice
2. Select/Add customer
3. Add products
4. Save
5. Print/PDF

### Check Stock Levels
1. Products → Product List
2. View "Current Stock" column
3. Or Reports → Stock Report

### Import Price List
1. Products → Import Prices
2. Upload PDF
3. Review matches
4. Apply updates

### Generate Report
1. Reports → Select report type
2. Set filters (date range, etc.)
3. Click Generate
4. Export as PDF/Excel

### Backup Database
1. Settings → Backup
2. Click "Create Backup"
3. Choose location
4. Save

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+N` | New Invoice |
| `Ctrl+S` | Save |
| `Ctrl+P` | Print |
| `Ctrl+F` | Search |
| `F5` | Refresh |
| `Esc` | Close Dialog |
| `Ctrl+Q` | Exit |

## 🔧 Troubleshooting

### "Python not found"
- Reinstall Python
- Make sure "Add to PATH" is checked

### "Module not found"
```bash
pip install -r requirements.txt --force-reinstall
```

### Database error
```bash
# Delete database and restart
rm billing_inventory.db  # Linux/Mac
del billing_inventory.db  # Windows
python main.py
```

### Application won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall PyQt6
pip uninstall PyQt6
pip install PyQt6
```

## 📚 Documentation

- **README.md** - Complete feature guide
- **QUICKSTART.md** - 5-minute setup
- **BUILD_INSTRUCTIONS.md** - Build executable
- **ARCHITECTURE.md** - Technical details
- **PROJECT_SUMMARY.md** - Project overview
- **CHANGELOG.md** - Version history

## 💡 Tips for Success

### Daily Routine
1. **Morning:** Check dashboard, review pending payments
2. **During Day:** Create invoices, record payments
3. **Evening:** Generate sales report, backup database

### Best Practices
- ✅ Backup database daily
- ✅ Set realistic minimum stock levels
- ✅ Record payments immediately
- ✅ Use consistent product codes
- ✅ Keep customer information updated

### Data Safety
- 📁 Store backups in multiple locations
- 💾 Backup before major changes
- 🔄 Test restore process monthly
- 🔒 Change default password

## 🎓 Learning Path

### Week 1: Basics
- [ ] Setup and configuration
- [ ] Add products and categories
- [ ] Create invoices
- [ ] Record payments

### Week 2: Advanced
- [ ] Import price lists from PDF
- [ ] Generate reports
- [ ] Customer ledger management
- [ ] Backup and restore

### Week 3: Optimization
- [ ] Customize company settings
- [ ] Set up keyboard shortcuts
- [ ] Optimize workflow
- [ ] Train team members

## 🏆 Success Checklist

Before going live:
- [ ] Company settings configured
- [ ] Categories created
- [ ] Products added
- [ ] Test invoice created
- [ ] Payment recorded
- [ ] Report generated
- [ ] Backup created
- [ ] Restore tested
- [ ] Password changed
- [ ] Team trained

## 📞 Need Help?

### Resources
- **Documentation:** Check all .md files
- **GitHub Issues:** Report bugs or request features
- **Email:** info@mybusiness.com

### Common Questions

**Q: Can I use this offline?**
A: Yes! 100% offline, no internet required.

**Q: Where is my data stored?**
A: Locally in `billing_inventory.db` file.

**Q: Can I customize it?**
A: Yes! Full source code provided.

**Q: Is it free?**
A: Yes! MIT License - free for commercial use.

**Q: Can I create a standalone .exe?**
A: Yes! See BUILD_INSTRUCTIONS.md

**Q: Does it support GST?**
A: Yes! GST calculations included.

**Q: Can I import from Excel?**
A: PDF import is supported. Excel import can be added.

**Q: Multi-user support?**
A: Basic user management included. Advanced roles coming soon.

## 🎉 You're Ready!

Congratulations! You're now ready to use the Desktop Billing & Inventory System.

**Next Steps:**
1. ✅ Complete initial setup
2. ✅ Add your products
3. ✅ Create your first invoice
4. ✅ Explore all features

**Happy Billing! 💰**

---

**Repository:** https://github.com/mukula27/desktop-billing-inventory
**License:** MIT
**Version:** 1.0.0

**Built with ❤️ for small businesses**
