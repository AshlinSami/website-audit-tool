#!/bin/bash

echo "=========================================="
echo "Website Audit Tool - Algorithm Agency"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --break-system-packages

echo ""
echo "✅ Installation complete!"
echo ""
echo "=========================================="
echo "Quick Start Guide"
echo "=========================================="
echo ""
echo "Run an audit:"
echo "  python3 website-auditor.py https://yourwebsite.com"
echo ""
echo "Run with custom page limit:"
echo "  python3 website-auditor.py https://yourwebsite.com 100"
echo ""
echo "Examples:"
echo "  python3 website-auditor.py https://subaru.co.za 50"
echo "  python3 website-auditor.py https://environ.co.za 75"
echo ""
echo "=========================================="