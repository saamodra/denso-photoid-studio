#!/usr/bin/env python3
"""
Force UI to appear on macOS
"""
import sys
import os
import subprocess
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from main import IDCardPhotoApp

def force_ui_visible():
    """Force the UI to be visible on macOS"""
    print("🚀 Starting ID Card Photo Machine with forced UI visibility...")

    # Create application
    app = IDCardPhotoApp()

    # macOS specific: Force app to foreground
    try:
        # Bring Python process to foreground
        subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to set frontmost of first process whose name is "Python" to true'
        ], capture_output=True)
    except:
        pass

    # Start the app
    return app.run()

if __name__ == "__main__":
    sys.exit(force_ui_visible())
