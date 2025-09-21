# ID Card Photo Machine - Usage Guide

## Quick Start

### 1. Installation

**🚀 Easiest Way (Recommended):**
```bash
# Unix/macOS/Linux
./start.sh

# Windows
start.bat

# Cross-platform
python run.py
```

**🔧 Manual Virtual Environment Setup:**
```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate    # Unix/macOS
# or
venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create assets
python create_assets.py
```

**⚙️ Alternative Options:**
```bash
# Option 1: Auto setup script
python setup.py

# Option 2: System-wide installation (not recommended)
pip install -r requirements.txt
python create_assets.py
```

### 2. Running the Application

**With Virtual Environment (Recommended):**
```bash
# Use launcher scripts
./start.sh              # Unix/macOS/Linux
start.bat               # Windows
python run.py           # Cross-platform

# Or manually
source venv/bin/activate && python main.py    # Unix/macOS
venv\Scripts\activate && python main.py       # Windows
```

**System-wide Installation:**
```bash
python main.py
```

## Application Workflow

### Step 1: Camera Setup
- **Camera Selection**: Choose from available cameras in the dropdown
- **Camera Settings**: Adjust brightness and contrast as needed
- **Preview**: Live camera feed shows what will be captured
- **Capture Settings**: Set number of photos (1-10) and delay between shots

### Step 2: Photo Capture
1. Click "📸 Take Photos" button
2. Wait for 3-second countdown
3. Photos are taken automatically with specified delay
4. Photos are saved to `temp/captures/` directory

### Step 3: Photo Selection
- **Grid View**: See all captured photos in a grid layout
- **Preview**: Click any photo to see larger preview
- **Selection**: Click to select your preferred photo
- **Options**:
  - "← Back to Camera" - Return to camera for more photos
  - "📸 Retake Photos" - Start over with new photos
  - "Next: Edit Photo →" - Proceed to editing (requires selection)

### Step 4: Background Processing
- **Original View**: See your selected photo on the left
- **Background Options**: Choose from various professional backgrounds:
  - Blue Solid
  - White Solid
  - Light Blue
  - Professional Gray
  - Navy Blue
  - Gradient Blue
  - Professional Gradient
- **Enhancement Controls**:
  - Brightness (50-150%)
  - Contrast (50-150%)
  - Sharpness (50-150%)
- **Processing**: Click "🎨 Process Photo" to apply changes
- **Preview**: See before/after comparison

### Step 5: Print Preview
- **Print Preview**: See final ID card layout
- **Printer Settings**:
  - Select available printer
  - Choose number of copies (1-20)
  - Select print quality (Draft/Normal/High)
- **Layout Options**:
  - Use ID card template
  - Crop to fit
- **Actions**:
  - "💾 Save ID Card" - Save processed image
  - "🖨️ Print ID Card" - Send to printer

## Features

### Camera Management
- **Multiple Camera Support**: Automatically detects all connected cameras
- **Live Preview**: Real-time camera feed with 30 FPS
- **Camera Controls**: Brightness and contrast adjustment
- **Flexible Capture**: 1-10 photos with customizable delay

### Image Processing
- **AI Background Removal**: Uses rembg library with U2Net model
- **Professional Backgrounds**: Multiple background options
- **Image Enhancement**: Brightness, contrast, and sharpness controls
- **Real-time Preview**: See changes instantly

### Printing System
- **System Integration**: Works with all system printers
- **Multiple Copies**: Print 1-20 copies in single layout
- **Quality Control**: Draft, normal, and high quality options
- **Standard Sizes**: Supports CR80 ID card standard (85.6 x 53.98 mm)

## Configuration

### Camera Settings (config.py)
```python
CAMERA_SETTINGS = {
    'default_resolution': (1920, 1080),
    'capture_format': 'jpg',
    'capture_quality': 95,
    'preview_fps': 30,
    'capture_count': 4,
    'capture_delay': 2.0
}
```

### Processing Settings
```python
PROCESSING_SETTINGS = {
    'background_removal_model': 'u2net',
    'output_resolution': (600, 600),
    'supported_formats': ['jpg', 'png'],
    'temp_folder': 'temp/processed/',
    'capture_folder': 'temp/captures/'
}
```

### Print Settings
```python
PRINT_SETTINGS = {
    'default_paper_size': 'CR80',
    'print_quality': 'high',
    'color_mode': 'color',
    'margins': (5, 5, 5, 5),
    'dpi': 300,
    'id_card_size': (85.6, 53.98)
}
```

## Troubleshooting

### Camera Issues
**Problem**: Camera not detected
- **Solution**: Ensure camera is connected and not in use
- **Check**: Try different USB port or camera
- **Verify**: Camera works in other applications

**Problem**: Poor image quality
- **Solution**: Adjust brightness/contrast in camera settings
- **Check**: Ensure good lighting conditions
- **Verify**: Clean camera lens

### Processing Issues
**Problem**: Background removal fails
- **Solution**: Ensure good contrast between subject and background
- **Check**: Subject should be clearly visible
- **Verify**: Try different lighting conditions

**Problem**: Processing is slow
- **Solution**: This is normal for AI processing
- **Check**: Ensure sufficient RAM (4GB+ recommended)
- **Verify**: Close other applications

### Print Issues
**Problem**: No printers found
- **Solution**: Ensure printer is connected and turned on
- **Check**: Printer drivers are installed
- **Verify**: Can print from other applications

**Problem**: Print quality poor
- **Solution**: Select "High Quality" in print settings
- **Check**: Use high-quality photo paper
- **Verify**: Printer has sufficient ink/toner

## File Management

### Temporary Files
- **Captures**: `temp/captures/` - Original photos (auto-cleaned after 24 hours)
- **Processed**: `temp/processed/` - Processed images (auto-cleaned after 24 hours)

### Manual Cleanup
```bash
# Clean all temporary files
rm -rf temp/captures/*
rm -rf temp/processed/*
```

### Backup Important Photos
Processed images are automatically saved with timestamp in `temp/processed/`.
Copy important photos to a permanent location.

## Keyboard Shortcuts

### Main Window
- **Space**: Take photos
- **C**: Change camera
- **Esc**: Exit application

### All Windows
- **F11**: Toggle fullscreen
- **Ctrl+Q**: Quit application
- **Ctrl+R**: Restart workflow

## System Requirements

### Minimum Requirements
- **OS**: Windows 10, macOS 10.14, Ubuntu 18.04
- **Python**: 3.8 or higher
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Camera**: USB webcam or built-in camera

### Recommended Requirements
- **RAM**: 8GB or higher
- **Storage**: 5GB free space
- **Camera**: HD webcam (1080p)
- **Printer**: Photo printer for best results

## Support

### Common Questions

**Q**: Can I use this commercially?
**A**: This is for educational/personal use. Check licensing for commercial use.

**Q**: What image formats are supported?
**A**: Input: JPG, PNG. Output: PNG for processed images.

**Q**: Can I customize backgrounds?
**A**: Yes, add your own images to `assets/backgrounds/` directory.

**Q**: How do I update the application?
**A**: Download new version and run setup again.

### Getting Help
1. Check this guide first
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Try restarting the application

### Reporting Issues
Include the following information:
- Operating system and version
- Python version
- Error messages (full text)
- Steps to reproduce the issue
- Camera model (if camera-related)
