@echo off
REM Quick run script for Windows

echo ========================================
echo Desktop Billing & Inventory System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from python.org
    pause
    exit /b 1
)

echo Python found!
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/upgrade dependencies
echo Checking dependencies...
pip install -r requirements.txt --quiet
echo.

REM Run the application
echo Starting application...
echo.
python main.py

REM Deactivate virtual environment
deactivate

pause
