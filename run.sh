#!/bin/bash
# Quick run script for Linux/Mac

echo "========================================"
echo "Desktop Billing & Inventory System"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

echo "Python found!"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install/upgrade dependencies
echo "Checking dependencies..."
pip install -r requirements.txt --quiet
echo ""

# Run the application
echo "Starting application..."
echo ""
python main.py

# Deactivate virtual environment
deactivate
