"""
ID Card Photo Machine - Main Application
Desktop application for automated ID card photo processing
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from ui.selection_window import SelectionWindow
from ui.processing_window import ProcessingWindow
from ui.print_window import PrintWindow
from config import APP_NAME, APP_VERSION, UI_SETTINGS


class IDCardPhotoApp:
    """Main application class coordinating the workflow"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)

        # Application state
        self.current_window = None
        self.captured_photos = []
        self.selected_photo = None
        self.processed_image = None

        # Windows
        self.main_window = None
        self.selection_window = None
        self.processing_window = None
        self.print_window = None

        self.setup_application()

    def setup_application(self):
        """Setup application-wide settings"""
        # Set application font
        font = QFont()
        font.setPointSize(UI_SETTINGS['font_size'])
        self.app.setFont(font)

        # Set application style
        self.app.setStyle('Fusion')  # Modern look across platforms

        # macOS specific settings for window visibility
        import platform
        if platform.system() == 'Darwin':  # macOS
            self.app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
            # Ensure app appears in dock
            try:
                import objc
                from Foundation import NSBundle
                bundle = NSBundle.mainBundle()
                if bundle:
                    info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
                    if info:
                        info['CFBundleName'] = APP_NAME
            except ImportError:
                pass  # objc not available, continue without

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
            print("🚀 Starting ID Card Photo Machine...")
            print(f"📱 Available screens: {len(self.app.screens())}")

            primary_screen = self.app.primaryScreen()
            if primary_screen:
                geometry = primary_screen.availableGeometry()
                print(f"🖥️  Primary screen: {geometry.width()}x{geometry.height()}")

            self.show_main_window()
            print("✅ Application UI should now be visible")
            print("   If you don't see the window, check:")
            print("   - Dock for the application icon")
            print("   - Mission Control for hidden windows")
            print("   - Alt+Tab to cycle through windows")

            return self.app.exec()
        except Exception as e:
            print(f"❌ Application error: {e}")
            self.show_error_dialog("Application Error", str(e))
            return 1

    def show_main_window(self):
        """Show main camera window"""
        try:
            if self.main_window:
                # If main window exists, just show it and restart camera
                self.main_window.show()
                self.main_window.raise_()  # Bring to front
                self.main_window.activateWindow()  # Activate window
                self.main_window.setup_camera()  # Restart camera
            else:
                # Create new main window
                self.main_window = MainWindow()
                self.main_window.photos_captured.connect(self.on_photos_captured)

                # Ensure window appears on screen
                self.main_window.show()
                self.main_window.raise_()  # Bring to front
                self.main_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.main_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.main_window.move(x, y)

            self.current_window = self.main_window
            print(f"✅ Main window shown at position: {self.main_window.x()}, {self.main_window.y()}")
            print(f"✅ Window size: {self.main_window.width()}x{self.main_window.height()}")
            print(f"✅ Window visible: {self.main_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing main window: {e}")
            self.show_error_dialog("Camera Error",
                                 f"Failed to initialize camera:\n{str(e)}\n\n"
                                 "Please ensure your camera is connected and not in use by another application.")

    def on_photos_captured(self, photo_paths):
        """Handle photos captured from main window"""
        if not photo_paths:
            self.show_info_dialog("No Photos", "No photos were captured. Please try again.")
            return

        self.captured_photos = photo_paths
        self.show_selection_window()

    def show_selection_window(self):
        """Show photo selection window"""
        try:
            if not self.captured_photos:
                self.show_error_dialog("No Photos", "No photos available for selection.")
                return

            if self.selection_window:
                self.selection_window.close()

            self.selection_window = SelectionWindow(self.captured_photos)
            self.selection_window.photo_selected.connect(self.on_photo_selected)
            self.selection_window.back_requested.connect(self.show_main_window)
            self.selection_window.show()
            self.current_window = self.selection_window

            # Stop camera and close main window to save resources
            if self.main_window:
                self.main_window.stop_camera()  # Stop camera before hiding
                self.main_window.hide()

        except Exception as e:
            self.show_error_dialog("Selection Error", f"Failed to show selection window:\n{str(e)}")

    def on_photo_selected(self, photo_path):
        """Handle photo selection"""
        if not photo_path or not os.path.exists(photo_path):
            self.show_error_dialog("Invalid Photo", "Selected photo is not available.")
            return

        self.selected_photo = photo_path
        self.show_processing_window()

    def show_processing_window(self):
        """Show processing window"""
        try:
            if not self.selected_photo:
                self.show_error_dialog("No Photo Selected", "Please select a photo first.")
                return

            if self.processing_window:
                self.processing_window.close()

            self.processing_window = ProcessingWindow(self.selected_photo)
            self.processing_window.processing_complete.connect(self.on_processing_complete)
            self.processing_window.back_requested.connect(self.show_selection_window)
            self.processing_window.show()
            self.current_window = self.processing_window

            # Close selection window
            if self.selection_window:
                self.selection_window.hide()

        except Exception as e:
            self.show_error_dialog("Processing Error", f"Failed to show processing window:\n{str(e)}")

    def on_processing_complete(self, processed_image):
        """Handle processing completion"""
        if processed_image is None:
            self.show_error_dialog("Processing Failed", "Image processing failed. Please try again.")
            return

        self.processed_image = processed_image
        self.show_print_window()

    def show_print_window(self):
        """Show print window"""
        try:
            if not self.processed_image:
                self.show_error_dialog("No Processed Image", "Please process a photo first.")
                return

            if self.print_window:
                self.print_window.close()

            self.print_window = PrintWindow(self.processed_image)
            self.print_window.print_complete.connect(self.on_print_complete)
            self.print_window.back_requested.connect(self.show_processing_window)
            self.print_window.show()
            self.current_window = self.print_window

            # Close processing window
            if self.processing_window:
                self.processing_window.hide()

        except Exception as e:
            self.show_error_dialog("Print Error", f"Failed to show print window:\n{str(e)}")

    def on_print_complete(self, success):
        """Handle print completion"""
        if success:
            reply = QMessageBox.question(
                self.current_window,
                "Print Complete",
                "ID card printed successfully!\n\nWould you like to create another ID card?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.restart_workflow()
            else:
                self.app.quit()
        else:
            reply = QMessageBox.question(
                self.current_window,
                "Print Failed",
                "Printing failed. Would you like to try again or start over?",
                QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.RestartProcess | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Retry
            )

            if reply == QMessageBox.StandardButton.Retry:
                # Stay on print window
                pass
            elif reply == QMessageBox.StandardButton.RestartProcess:
                self.restart_workflow()
            else:
                self.app.quit()

    def restart_workflow(self):
        """Restart the entire workflow"""
        try:
            # Stop camera and close all windows except main
            if self.main_window:
                self.main_window.stop_camera()
            if self.print_window:
                self.print_window.close()
            if self.processing_window:
                self.processing_window.close()
            if self.selection_window:
                self.selection_window.close()

            # Reset state
            self.captured_photos = []
            self.selected_photo = None
            self.processed_image = None

            # Show main window
            QTimer.singleShot(100, self.show_main_window)  # Small delay for cleanup

        except Exception as e:
            self.show_error_dialog("Restart Error", f"Failed to restart workflow:\n{str(e)}")

    def show_error_dialog(self, title, message):
        """Show error dialog"""
        QMessageBox.critical(self.current_window, title, message)

    def show_info_dialog(self, title, message):
        """Show info dialog"""
        QMessageBox.information(self.current_window, title, message)

    def show_warning_dialog(self, title, message):
        """Show warning dialog"""
        QMessageBox.warning(self.current_window, title, message)

    def cleanup(self):
        """Cleanup application resources"""
        try:
            # Close all windows
            if self.main_window:
                self.main_window.close()
            if self.selection_window:
                self.selection_window.close()
            if self.processing_window:
                self.processing_window.close()
            if self.print_window:
                self.print_window.close()

            # Cleanup temp files (optional)
            self.cleanup_temp_files()

        except Exception as e:
            print(f"Cleanup error: {e}")

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        from modules.camera_manager import CameraManager
        from modules.image_processor import ImageProcessor

        try:
            # Cleanup camera temp files
            camera_manager = CameraManager()
            camera_manager.cleanup()

            # Cleanup image processor temp files
            image_processor = ImageProcessor()
            image_processor.cleanup_temp_files()

        except Exception as e:
            print(f"Temp file cleanup error: {e}")


def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'cv2',
        'PIL',
        'mediapipe',
        'numpy',
        'PyQt6'
    ]

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install dependencies using:")
        print("pip install -r requirements.txt")
        return False

    return True


def main():
    """Main entry point"""
    print(f"Starting {APP_NAME} v{APP_VERSION}")

    # Check dependencies
    if not check_dependencies():
        print("Dependency check failed. Exiting.")
        sys.exit(1)

    # Create and run application
    app = IDCardPhotoApp()

    try:
        exit_code = app.run()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        exit_code = 0
    except Exception as e:
        print(f"Application error: {e}")
        exit_code = 1
    finally:
        app.cleanup()

    print(f"{APP_NAME} exited with code {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
