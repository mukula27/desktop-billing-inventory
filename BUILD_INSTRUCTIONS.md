# Build Instructions - Desktop Billing & Inventory System

Complete guide to build, test, and deploy the application.

## Development Setup

### 1. System Requirements

**Minimum:**
- Windows 10/11, Linux (Ubuntu 20.04+), or macOS 10.15+
- Python 3.10 or higher
- 4GB RAM
- 500MB free disk space

**Recommended:**
- Windows 11 or Ubuntu 22.04
- Python 3.11+
- 8GB RAM
- 1GB free disk space

### 2. Install Python

**Windows:**
```bash
# Download from python.org
# During installation, check "Add Python to PATH"
python --version  # Verify installation
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
python3 --version
```

**macOS:**
```bash
brew install python@3.11
python3 --version
```

### 3. Clone Repository

```bash
git clone https://github.com/mukula27/desktop-billing-inventory.git
cd desktop-billing-inventory
```

### 4. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# Verify activation (should show venv path)
which python  # Linux/Mac
where python  # Windows
```

### 5. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Verify installations
pip list
```

### 6. Run Application

```bash
# Run from project root
python main.py
```

## Building Standalone Executable

### Method 1: Simple One-File Build

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Build single executable
pyinstaller --name="BillingSystem" \
    --windowed \
    --onefile \
    main.py

# Output will be in: dist/BillingSystem.exe (Windows) or dist/BillingSystem (Linux/Mac)
```

### Method 2: Advanced Build with Resources

Create a file named `build.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('database/schema.sql', 'database'),
        ('utils/*.py', 'utils'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'reportlab',
        'pdfplumber',
        'PyPDF2',
        'openpyxl',
        'PIL',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BillingSystem',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'  # Add your icon file
)
```

Then build:

```bash
pyinstaller build.spec
```

### Method 3: Directory Build (Faster Startup)

```bash
pyinstaller --name="BillingSystem" \
    --windowed \
    --onedir \
    --add-data "database;database" \
    --add-data "utils;utils" \
    main.py

# Output will be in: dist/BillingSystem/ folder
# Run: dist/BillingSystem/BillingSystem.exe
```

## Build Options Explained

| Option | Description |
|--------|-------------|
| `--name` | Name of the executable |
| `--windowed` | No console window (GUI only) |
| `--onefile` | Single executable file |
| `--onedir` | Directory with executable and dependencies |
| `--add-data` | Include additional files (format: "source;destination") |
| `--icon` | Application icon (.ico for Windows) |
| `--hidden-import` | Manually specify imports PyInstaller might miss |
| `--noconsole` | Same as --windowed |
| `--clean` | Clean PyInstaller cache before building |

## Testing the Build

### 1. Test on Development Machine

```bash
# Navigate to dist folder
cd dist

# Run the executable
# Windows:
BillingSystem.exe

# Linux/Mac:
./BillingSystem
```

### 2. Test on Clean Machine

- Copy the executable to a machine without Python installed
- Run the executable
- Test all features:
  - Login
  - Add products
  - Create invoice
  - Generate PDF
  - Import price list
  - Create backup

### 3. Common Issues and Fixes

**Issue: "Failed to execute script"**
```bash
# Build with console to see errors
pyinstaller --name="BillingSystem" --onefile main.py

# Run and check console output
```

**Issue: Missing modules**
```bash
# Add hidden imports
pyinstaller --name="BillingSystem" \
    --windowed \
    --onefile \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=reportlab \
    main.py
```

**Issue: Database not found**
```bash
# Include database folder
pyinstaller --name="BillingSystem" \
    --windowed \
    --onefile \
    --add-data "database;database" \
    main.py
```

## Creating Installer (Optional)

### Using Inno Setup (Windows)

1. Download Inno Setup: https://jrsoftware.org/isinfo.php

2. Create `installer.iss`:

```ini
[Setup]
AppName=Billing & Inventory System
AppVersion=1.0
DefaultDirName={pf}\BillingSystem
DefaultGroupName=Billing System
OutputDir=installer
OutputBaseFilename=BillingSystemSetup
Compression=lzma2
SolidCompression=yes

[Files]
Source: "dist\BillingSystem.exe"; DestDir: "{app}"
Source: "README.md"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\Billing System"; Filename: "{app}\BillingSystem.exe"
Name: "{commondesktop}\Billing System"; Filename: "{app}\BillingSystem.exe"

[Run]
Filename: "{app}\BillingSystem.exe"; Description: "Launch Billing System"; Flags: postinstall nowait skipifsilent
```

3. Compile with Inno Setup Compiler

### Using NSIS (Windows)

1. Download NSIS: https://nsis.sourceforge.io/

2. Create installer script and compile

## Distribution

### Package Contents

Your distribution should include:

```
BillingSystem/
├── BillingSystem.exe          # Main executable
├── README.md                  # User guide
├── LICENSE.txt                # License file
└── CHANGELOG.txt              # Version history
```

### Recommended Distribution Methods

1. **Direct Download**
   - Upload to GitHub Releases
   - Host on your website
   - Share via cloud storage

2. **Installer Package**
   - Create .msi or .exe installer
   - Include in software repositories

3. **Portable Version**
   - Zip the executable
   - No installation required
   - Run from USB drive

## Optimization Tips

### Reduce Executable Size

```bash
# Use UPX compression
pip install pyinstaller[encryption]

pyinstaller --name="BillingSystem" \
    --windowed \
    --onefile \
    --upx-dir=/path/to/upx \
    main.py
```

### Faster Startup

```bash
# Use --onedir instead of --onefile
# Startup is faster but creates multiple files

pyinstaller --name="BillingSystem" \
    --windowed \
    --onedir \
    main.py
```

### Exclude Unnecessary Modules

```bash
pyinstaller --name="BillingSystem" \
    --windowed \
    --onefile \
    --exclude-module=matplotlib \
    --exclude-module=numpy \
    main.py
```

## Continuous Integration (CI/CD)

### GitHub Actions Example

Create `.github/workflows/build.yml`:

```yaml
name: Build Application

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pyinstaller
      - name: Build executable
        run: |
          pyinstaller --name="BillingSystem" --windowed --onefile main.py
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: BillingSystem-Windows
          path: dist/BillingSystem.exe
```

## Version Management

### Update Version Number

1. Update in `main.py`:
```python
__version__ = "1.0.0"
```

2. Update in `README.md`

3. Create git tag:
```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

## Troubleshooting Build Issues

### PyInstaller Not Found
```bash
pip install pyinstaller --upgrade
```

### Import Errors in Built Executable
```bash
# Test imports
python -c "import PyQt6; import reportlab; import pdfplumber"

# Add to hidden imports if needed
```

### Database Path Issues
```python
# In code, use relative paths
import os
import sys

if getattr(sys, 'frozen', False):
    # Running as compiled executable
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(__file__)

db_path = os.path.join(base_path, 'billing_inventory.db')
```

## Support

For build issues:
1. Check PyInstaller documentation: https://pyinstaller.org/
2. Review error logs in `build/` folder
3. Test with `--debug=all` flag
4. Open issue on GitHub

---

**Happy Building! 🚀**
