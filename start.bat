@echo off
REM ID Card Photo Machine - Start Script (Windows)

echo 🎉 ID Card Photo Machine - Startup Script
echo ==========================================

REM Get script directory and change to it
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Virtual environment not found. Creating one...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
echo 📋 Checking dependencies...
python -c "import PyQt6, cv2, PIL, rembg, numpy" 2>nul
if errorlevel 1 (
    echo 📥 Installing dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ✅ Dependencies already installed
)

REM Create assets if they don't exist
if not exist "assets\backgrounds\blue_solid.png" (
    echo 🎨 Creating application assets...
    python create_assets.py
    echo ✅ Assets created
)

REM Launch application
echo 🚀 Launching ID Card Photo Machine...
echo.
python main.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
