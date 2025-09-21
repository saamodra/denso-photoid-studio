# Virtual Environment Setup Guide

This guide explains how to set up and use the ID Card Photo Machine with Python virtual environments.

## Why Use Virtual Environments?

Virtual environments provide:
- **Isolated dependencies** - No conflicts with other Python projects
- **Clean installation** - Only installs what's needed for this project
- **Version control** - Ensures consistent dependency versions
- **Easy cleanup** - Delete the `venv` folder to remove everything

## Quick Setup

### Option 1: Automatic Setup (Recommended)

**Unix/macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Cross-platform:**
```bash
python run.py
```

These scripts will automatically:
1. Create virtual environment if it doesn't exist
2. Install all dependencies
3. Create application assets
4. Launch the application

### Option 2: Manual Setup

#### Step 1: Create Virtual Environment
```bash
# Navigate to project directory
cd photocard-studio

# Create virtual environment
python3 -m venv venv
```

#### Step 2: Activate Virtual Environment

**Unix/macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

#### Step 3: Upgrade pip and Install Dependencies
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

#### Step 4: Create Application Assets
```bash
python create_assets.py
```

#### Step 5: Run Application
```bash
python main.py
```

## Verifying Installation

### Check Virtual Environment
```bash
# Should show the venv Python path when activated
which python    # Unix/macOS
where python    # Windows
```

### Check Installed Packages
```bash
pip list
```

Should show:
- PyQt6
- opencv-python
- Pillow
- rembg
- numpy
- All their dependencies

### Test Application Structure
```bash
python test_structure.py
```

## Managing the Virtual Environment

### Activating
Always activate before running the application:
```bash
source venv/bin/activate    # Unix/macOS
venv\Scripts\activate       # Windows
```

### Deactivating
When you're done:
```bash
deactivate
```

### Updating Dependencies
```bash
# Activate virtual environment first
source venv/bin/activate

# Update pip
python -m pip install --upgrade pip

# Update all packages
pip install --upgrade -r requirements.txt
```

### Reinstalling Everything
If something goes wrong:
```bash
# Remove virtual environment
rm -rf venv           # Unix/macOS
rmdir /s venv         # Windows

# Recreate from scratch
python3 -m venv venv
source venv/bin/activate    # Unix/macOS
venv\Scripts\activate       # Windows
pip install --upgrade pip
pip install -r requirements.txt
```

## Directory Structure with Virtual Environment

```
photocard-studio/
├── venv/                    # Virtual environment (created by setup)
│   ├── bin/                 # Executables (Unix/macOS)
│   ├── Scripts/             # Executables (Windows)
│   ├── lib/                 # Python packages
│   └── pyvenv.cfg           # Virtual environment config
├── main.py                  # Application entry point
├── run.py                   # Cross-platform launcher
├── start.sh                 # Unix/macOS launcher script
├── start.bat                # Windows launcher script
├── setup.py                 # Setup script
├── requirements.txt         # Dependencies
├── modules/                 # Application modules
├── ui/                      # User interface
├── assets/                  # Generated assets
└── temp/                    # Temporary files
```

## Troubleshooting

### Virtual Environment Won't Create
**Problem:** `python3 -m venv venv` fails
**Solutions:**
- Ensure Python 3.8+ is installed: `python3 --version`
- Try `python -m venv venv` instead
- Install python3-venv: `sudo apt install python3-venv` (Ubuntu/Debian)

### Can't Activate Virtual Environment
**Problem:** Activation script not found
**Solutions:**
- Check if `venv` directory exists
- Verify correct path: `venv/bin/activate` (Unix) or `venv\Scripts\activate.bat` (Windows)
- Recreate virtual environment if corrupted

### Permission Denied (Unix/macOS)
**Problem:** Can't execute shell scripts
**Solution:** Make scripts executable:
```bash
chmod +x start.sh
chmod +x run.py
```

### PowerShell Execution Policy (Windows)
**Problem:** Can't run PowerShell activation script
**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Dependencies Won't Install
**Problem:** pip install fails
**Solutions:**
- Upgrade pip: `python -m pip install --upgrade pip`
- Use alternative index: `pip install -i https://pypi.org/simple/ -r requirements.txt`
- Check internet connection
- Try installing packages individually

### Application Won't Start
**Problem:** Import errors when running
**Solutions:**
- Verify virtual environment is activated
- Check all dependencies installed: `pip list`
- Run structure test: `python test_structure.py`
- Reinstall dependencies

## Environment Variables

The application works without environment variables, but you can set:

```bash
# Optional: Set Qt scale factor for high DPI displays
export QT_SCALE_FACTOR=1.5

# Optional: Set Qt theme
export QT_STYLE_OVERRIDE=Fusion
```

## Best Practices

1. **Always use virtual environment** - Keeps system Python clean
2. **Activate before running** - Ensures correct dependencies
3. **Use launcher scripts** - Handles activation automatically
4. **Don't commit venv/** - Add to .gitignore (already done)
5. **Update requirements.txt** - When adding new dependencies
6. **Test regularly** - Run `python test_structure.py` after changes

## Integration with IDEs

### Visual Studio Code
1. Open project folder
2. Select Python interpreter: Ctrl+Shift+P → "Python: Select Interpreter"
3. Choose `./venv/bin/python` (Unix) or `.\venv\Scripts\python.exe` (Windows)

### PyCharm
1. File → Settings → Project → Python Interpreter
2. Add → Existing Environment
3. Select `venv/bin/python` (Unix) or `venv\Scripts\python.exe` (Windows)

### Cursor
The virtual environment is automatically detected when opening the project.
