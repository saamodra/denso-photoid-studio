#!/usr/bin/env python3
"""
Safe version of main application that doesn't crash on camera issues
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.main_window import MainWindow
    from config import APP_NAME, APP_VERSION, UI_SETTINGS
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

class SafeIDCardPhotoApp:
    """Safe version of ID Card Photo App with better error handling"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)

        self.main_window = None
        self.setup_application()

    def setup_application(self):
        """Setup application-wide settings"""
        # Set application font
        font = QFont()
        font.setPointSize(UI_SETTINGS['font_size'])
        self.app.setFont(font)

        # Set application style
        self.app.setStyle('Fusion')

        # Set application icon (if available)
        try:
            icon_path = os.path.join('assets', 'icons', 'app_icon.png')
            if os.path.exists(icon_path):
                self.app.setWindowIcon(QIcon(icon_path))
        except:
            pass

    def run(self):
        """Start the application"""
        try:
            print("🚀 Starting ID Card Photo Machine (Safe Mode)...")
            print(f"📱 Available screens: {len(self.app.screens())}")

            primary_screen = self.app.primaryScreen()
            if primary_screen:
                geometry = primary_screen.availableGeometry()
                print(f"🖥️  Primary screen: {geometry.width()}x{geometry.height()}")

            self.show_main_window()
            print("✅ Application UI should now be visible")

            return self.app.exec()
        except Exception as e:
            print(f"❌ Application error: {e}")
            self.show_error_dialog("Application Error", str(e))
            return 1

    def show_main_window(self):
        """Show main camera window"""
        try:
            if self.main_window:
                self.main_window.close()

            self.main_window = MainWindow()

            # Ensure window appears on screen
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()

            # Center window on screen
            screen = self.app.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                window_geometry = self.main_window.geometry()
                x = (screen_geometry.width() - window_geometry.width()) // 2
                y = (screen_geometry.height() - window_geometry.height()) // 2
                self.main_window.move(x, y)

            print(f"✅ Main window shown at position: {self.main_window.x()}, {self.main_window.y()}")
            print(f"✅ Window size: {self.main_window.width()}x{self.main_window.height()}")
            print(f"✅ Window visible: {self.main_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing main window: {e}")
            import traceback
            traceback.print_exc()

    def show_error_dialog(self, title, message):
        """Show error dialog"""
        try:
            QMessageBox.critical(None, title, message)
        except:
            print(f"Error dialog: {title} - {message}")

def main():
    """Main entry point"""
    print(f"Starting {APP_NAME} v{APP_VERSION} (Safe Mode)")

    try:
        app = SafeIDCardPhotoApp()
        exit_code = app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        exit_code = 0
    except Exception as e:
        print(f"Application error: {e}")
        exit_code = 1

    print(f"{APP_NAME} exited with code {exit_code}")
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
