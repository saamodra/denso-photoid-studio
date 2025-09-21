#!/usr/bin/env python3
"""
Quick UI visibility test for macOS
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

def test_basic_ui():
    """Test if basic UI elements can be displayed"""
    print("Testing basic PyQt6 UI visibility...")

    app = QApplication(sys.argv)

    # Test 1: Simple message box
    print("Test 1: Showing message box...")
    reply = QMessageBox.question(
        None,
        "UI Visibility Test",
        "Can you see this message box?\n\nIf YES: UI is working\nIf NO: There's a display issue",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )

    if reply == QMessageBox.StandardButton.No:
        print("❌ Message box not visible - display issue confirmed")
        return False

    print("✅ Message box visible")

    # Test 2: Simple window
    print("Test 2: Showing simple window...")
    window = QMainWindow()
    window.setWindowTitle("UI Test Window")
    window.setGeometry(100, 100, 400, 200)

    widget = QWidget()
    window.setCentralWidget(widget)
    layout = QVBoxLayout(widget)

    label = QLabel("This is a test window")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)

    button = QPushButton("Close")
    button.clicked.connect(app.quit)
    layout.addWidget(button)

    # Force window to appear
    window.show()
    window.raise_()
    window.activateWindow()

    # Center on screen
    screen = app.primaryScreen()
    if screen:
        screen_rect = screen.availableGeometry()
        window_rect = window.geometry()
        x = (screen_rect.width() - window_rect.width()) // 2
        y = (screen_rect.height() - window_rect.height()) // 2
        window.move(x, y)

    print("✅ Test window created and shown")
    print("   Look for 'UI Test Window' on your screen")
    print("   Click 'Close' button to continue")

    app.exec()
    return True

def main():
    """Main test function"""
    print("=" * 50)
    print("ID Card Photo Machine - UI Visibility Test")
    print("=" * 50)

    if test_basic_ui():
        print("\n✅ UI is working! The main application should be able to display.")
        print("\nTroubleshooting tips if main app still doesn't show:")
        print("1. Check if the app appears in the Dock")
        print("2. Try Alt+Tab to cycle through windows")
        print("3. Check Mission Control (F3) for hidden windows")
        print("4. Try running: python main.py &")
        print("5. Check Activity Monitor if the process is running")
    else:
        print("\n❌ UI display issue detected")
        print("\nPossible solutions:")
        print("1. Check Display settings in System Preferences")
        print("2. Try connecting an external monitor")
        print("3. Restart the terminal/IDE")
        print("4. Check if running over SSH (GUI won't work)")

if __name__ == "__main__":
    main()
