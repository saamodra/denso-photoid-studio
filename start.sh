#!/bin/bash
# ID Card Photo Machine - Start Script (Unix/macOS/Linux)

set -e  # Exit on any error

echo "🎉 ID Card Photo Machine - Startup Script"
echo "=========================================="

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo "📋 Checking dependencies..."
if ! python -c "import PyQt6, cv2, PIL, rembg, onnxruntime, numpy" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Launch application
echo "🚀 Launching ID Card Photo Machine..."
echo ""
python main.py

# Deactivate virtual environment
deactivate
