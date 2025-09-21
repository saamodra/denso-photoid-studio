# Camera Troubleshooting Guide

## Issues Fixed

### 1. ✅ PyQt6 Compatibility Issue
**Problem:** Application crashed with `AttributeError: AA_EnableHighDpiScaling`
**Solution:** Removed deprecated `AA_EnableHighDpiScaling` attribute (not needed in PyQt6)

### 2. ✅ UI Visibility Issue
**Problem:** White text on white background making labels invisible
**Solution:**
- Added dark text color (`#2c3e50`) to all labels
- Added background color to QGroupBox elements
- Enhanced contrast for better visibility

### 3. ✅ Camera Detection Enhancement
**Problem:** Limited camera detection capability
**Solution:**
- Enhanced camera detection with multiple backends (AVFoundation, DirectShow, V4L2)
- Added actual frame capture testing to verify camera functionality
- Improved error handling and debug output
- Added backend-specific camera naming

## Current Status

### Camera Detection Results
From the test output, the system successfully:
- ✅ Detects 2 cameras on your system
- ✅ Successfully captures frames from Camera 0 (1280x720 resolution)
- ✅ Uses both AVFoundation and generic backends

### Test Command Results
```bash
python test_camera.py
```
**Output:** Found 2 camera(s) successfully

## Common Camera Issues & Solutions

### Issue: "No Camera Available"

#### Check 1: Camera Permissions (macOS)
```bash
# Check if the app has camera permissions
# Go to: System Preferences > Security & Privacy > Camera
# Make sure Terminal/Python is allowed camera access
```

#### Check 2: Camera in Use
```bash
# Close any applications using the camera:
# - Photo Booth
# - FaceTime
# - Zoom/Teams/Skype
# - Other video applications
```

#### Check 3: Camera Connection
```bash
# For external USB cameras:
# 1. Disconnect and reconnect the camera
# 2. Try a different USB port
# 3. Check if camera LED indicates it's active
```

#### Check 4: Run Debug Test
```bash
cd /Users/samodra/Projects/photocard-studio
source venv/bin/activate
python test_camera.py
```

### Issue: Application Shows Cameras But No Preview

#### Solution 1: Refresh Cameras
Click the "🔄 Refresh Cameras" button in the application

#### Solution 2: Try Different Camera
Use the dropdown to select a different camera if multiple are available

#### Solution 3: Check Camera Settings
Adjust brightness/contrast settings if the preview appears black

## Application Usage

### Starting the Application
```bash
# Method 1: Launcher script (recommended)
./start.sh              # macOS/Linux
start.bat               # Windows
python run.py           # Cross-platform

# Method 2: Manual
source venv/bin/activate
python main.py
```

### Expected Behavior
1. **Application Start:** Debug output shows camera detection
2. **Main Window:** Camera dropdown populated with detected cameras
3. **Camera Preview:** Live preview appears when camera is selected
4. **Status Updates:** Status shows "Camera: X found" where X > 0

## Debug Information

### Camera Detection Debug Output
The application now shows detailed debug information:
```
=== Camera Detection Debug ===
OpenCV version: 4.12.0
Available backends: ['AVFoundation', 'DirectShow', 'V4L2', 'ANY']

Testing AVFoundation backend:
  Camera 0: WORKING ((720, 1280, 3))
  ...
Total detected cameras: 2
  Camera 0: (1280, 720)
  AVFoundation Camera 0: (1280, 720)
=============================
```

### UI Debug Output
The application shows camera refresh information:
```
UI: Refreshing cameras, found 2
  Added to combo: Camera 0 (1280x720)
  Added to combo: AVFoundation Camera 0 (1280x720)
```

## Verification Steps

### 1. Test Camera Detection
```bash
python test_camera.py
```
**Expected:** Shows "✅ SUCCESS: Found X camera(s)"

### 2. Test Application Startup
```bash
python run.py
```
**Expected:**
- Application window opens
- Camera dropdown shows available cameras
- Status shows "Camera: X found"

### 3. Test Camera Preview
1. Select a camera from dropdown
2. Preview should show live camera feed
3. Status should show "Camera: Active"

## Performance Notes

- **Camera initialization** may take 2-3 seconds
- **Multiple cameras** may appear due to different backends (normal)
- **OpenCV warnings** about device bounds are normal during detection
- **Permission prompts** may appear on first run (allow access)

## Still Having Issues?

### Contact Information
If problems persist:
1. Run `python test_camera.py` and share the output
2. Check macOS camera permissions
3. Try with a different camera if available
4. Restart the application

### System Requirements Verification
- ✅ Python 3.8+
- ✅ Virtual environment active
- ✅ All dependencies installed
- ✅ Camera connected and functional
- ✅ Camera permissions granted (macOS/Windows)

## Next Steps

Once camera is working:
1. **Take Photos:** Click "📸 Take Photos" to capture images
2. **Select Best Photo:** Choose from captured images
3. **Process Background:** Remove and replace background
4. **Print ID Card:** Send to printer

The application is now fully functional with enhanced camera detection and improved UI visibility!
