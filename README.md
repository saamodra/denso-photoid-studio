# ID Card Photo Machine

A desktop application for automated ID card photo processing using PyQt6.

## Features

- **Camera Management**: Multiple camera support with live preview
- **Photo Capture**: Take multiple photos with countdown timer
- **Photo Selection**: Choose the best photo from captured images
- **Background Processing**: AI-powered background removal and replacement
- **Print System**: Professional ID card printing with preview

## Requirements

- Python 3.8+
- PyQt6
- OpenCV
- PIL (Pillow)
- rembg
- numpy

## Installation

### Quick Start (Recommended)
The easiest way to run the application is using the provided launcher scripts:

**Unix/macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**Cross-platform Python launcher:**
```bash
python run.py
```

### Manual Setup with Virtual Environment

1. Create and activate virtual environment:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it (Unix/macOS)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Create default assets:
```bash
python create_assets.py
```

4. Run the application:
```bash
python main.py
```

### Alternative Setup Options

**Option 1: Auto setup script**
```bash
python setup.py
```

**Option 2: Manual system-wide installation** (not recommended)
```bash
pip install -r requirements.txt
python create_assets.py
python main.py
```

## Usage

1. **Take Photos**: Use the main window to capture 4 photos with your camera
2. **Select Photo**: Choose your best photo from the captured images
3. **Process Image**: Remove background and apply professional ID card background
4. **Print**: Preview and print your ID card

## Configuration

Edit `config.py` to customize:
- Camera settings (resolution, quality)
- Processing settings (background removal model)
- Print settings (paper size, DPI)
- UI settings (window size, theme)

## Supported Cameras

- USB webcams
- Built-in laptop cameras
- External USB cameras

## Supported Printers

- System printers (Windows, macOS, Linux)
- Network printers
- Photo printers

## Troubleshooting

### Camera Issues
- Ensure camera is connected and not in use by another app
- Try switching to a different camera in the dropdown

### Background Removal Issues
- Ensure good lighting for better results
- Position subject clearly against contrasting background

### Print Issues
- Check printer connectivity
- Verify printer drivers are installed
- Try different print quality settings

## File Structure

```
photocard-studio/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── modules/               # Core functionality
│   ├── camera_manager.py  # Camera operations
│   ├── image_processor.py # Image processing
│   └── print_manager.py   # Printing functionality
├── ui/                    # User interface
│   ├── main_window.py     # Main camera window
│   ├── selection_window.py# Photo selection
│   ├── processing_window.py# Background processing
│   └── print_window.py    # Print preview
├── assets/                # Assets and templates
│   ├── backgrounds/       # Background images
│   ├── templates/         # ID card templates
│   └── icons/            # Application icons
└── temp/                  # Temporary files
    ├── captures/          # Captured photos
    └── processed/         # Processed images
```

## License

This project is for educational and personal use.
