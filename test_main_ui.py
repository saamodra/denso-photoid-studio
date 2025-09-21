#!/usr/bin/env python3
"""
Test the main application UI showing
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMessageBox
from main import IDCardPhotoApp

def main():
    print("Testing main application UI display...")

    try:
        # First test basic PyQt6
        app = QApplication(sys.argv)

        # Show confirmation dialog
        reply = QMessageBox.question(
            None,
            "UI Test",
            "Can you see this dialog box?\n\nClick Yes to continue with the main app, No to exit.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            print("✅ Basic UI is working, starting main application...")
            app.quit()

            # Start main application
            main_app = IDCardPhotoApp()
            return main_app.run()
        else:
            print("❌ UI dialog not visible - there may be a display issue")
            return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
