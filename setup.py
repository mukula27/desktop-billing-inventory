"""
Setup script for Desktop Billing & Inventory System
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="desktop-billing-inventory",
    version="1.0.0",
    author="Bhindi Team",
    author_email="info@mybusiness.com",
    description="Desktop Billing & Inventory Management System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mukula27/desktop-billing-inventory",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.10",
    install_requires=[
        "PyQt6>=6.6.1",
        "reportlab>=4.0.7",
        "pdfplumber>=0.10.3",
        "PyPDF2>=3.0.1",
        "openpyxl>=3.1.2",
        "Pillow>=10.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "build": [
            "pyinstaller>=6.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "billing-system=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "database": ["*.sql"],
    },
    keywords="billing inventory pos point-of-sale invoice accounting",
    project_urls={
        "Bug Reports": "https://github.com/mukula27/desktop-billing-inventory/issues",
        "Source": "https://github.com/mukula27/desktop-billing-inventory",
        "Documentation": "https://github.com/mukula27/desktop-billing-inventory#readme",
    },
)
