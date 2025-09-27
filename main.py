"""
ID Card Photo Machine - Main Application
Desktop application for automated ID card photo processing
"""
import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QFont

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_window import LoginPage
from ui.role_selection_window import RoleSelectionWindow
from ui.dashboard_window import DashboardWindow
from ui.camera_window import MainWindow as CameraWindow
from ui.selection_window import SelectionWindow
from ui.processing_window import ProcessingWindow
from ui.print_window import PrintWindow
from config import APP_NAME, APP_VERSION, UI_SETTINGS
from modules.session_manager import session_manager


class CustomStyledDialog(QDialog):
    """Custom dialog with consistent styling matching the logout confirmation"""

    def __init__(self, parent=None, title="", message="", buttons=None, icon_type="info"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 200)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        if buttons is None:
            buttons = [("OK", QDialog.DialogCode.Accepted)]

        self.buttons = []
        for text, role in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, r=role: self.done(r))
            button_layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addLayout(button_layout)

        # Apply consistent styling
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #333333;
            }
            QLabel {
                background-color: #FFFFFF;
                color: #333333;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #E60012;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #CC0010;
            }
            QPushButton:pressed {
                background-color: #99000C;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
            QPushButton#cancelButton:pressed {
                background-color: #495057;
            }
        """)

    def set_cancel_button(self, button_index=0):
        """Set a button as cancel button for different styling"""
        if 0 <= button_index < len(self.buttons):
            self.buttons[button_index].setObjectName("cancelButton")


class IDCardPhotoApp:
    """Main application class coordinating the workflow"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)

        # Application state
        self.current_window = None
        self.current_user = None
        self.captured_photos = []
        self.selected_photo = None
        self.processed_image = None

        # Windows
        self.login_window = None
        self.role_selection_window = None
        self.dashboard_window = None
        self.admin_window = None
        self.camera_window = None
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

            # self.show_main_window()
            self.show_login_window()

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

    def show_login_window(self):
        """Show login window"""
        try:
            if self.login_window:
                self.current_window.hide()

                # If main window exists, just show it
                self.login_window.show()
                self.login_window.raise_()  # Bring to front
                self.login_window.activateWindow()  # Activate window

            else:

                # Create new main window
                self.login_window = LoginPage()
                # Hubungkan sinyal dari halaman login ke fungsi di atas
                self.login_window.login_successful.connect(self.login_success)

                # Ensure window appears on screen
                self.login_window.show()
                self.login_window.raise_()  # Bring to front
                self.login_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.login_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.login_window.move(x, y)

            self.current_window = self.login_window
            print(f"✅ Login window shown at position: {self.login_window.x()}, {self.login_window.y()}")
            print(f"✅ Window size: {self.login_window.width()}x{self.login_window.height()}")
            print(f"✅ Window visible: {self.login_window.isVisible()}")


        except Exception as e:
            print(f"❌ Error showing main window: {e}")
            self.show_error_dialog("Camera Error",
                                 f"Failed to initialize camera:\n{str(e)}\n\n"
                                 "Please ensure your camera is connected and not in use by another application.")

    def login_success(self, user_data):
        """Handle successful login with user data"""
        # Start session using session manager
        if session_manager.login(user_data):
            self.current_user = user_data  # Keep for backward compatibility
            self.current_window.hide()
            self.show_role_selection_window()
        else:
            self.show_error_dialog("Session Error", "Failed to start user session")

    def show_dashboard_window(self):
        """Show dashboard window"""
        try:
            if self.dashboard_window:
                # If dashboard window exists, just show it
                self.dashboard_window.show()
                self.dashboard_window.raise_()  # Bring to front
                self.dashboard_window.activateWindow()  # Activate window
                # Update user info in existing window with current session data
                self.dashboard_window.set_session_info(session_manager.get_current_user())
            else:
                # Create new dashboard window
                self.dashboard_window = DashboardWindow()
                self.dashboard_window.start_photo_capture.connect(self.show_camera_window)
                self.dashboard_window.logout_requested.connect(self.logout)
                # Pass session information to dashboard window
                self.dashboard_window.set_session_info(session_manager.get_current_user())

                # Ensure window appears on screen
                self.dashboard_window.show()
                self.dashboard_window.raise_()  # Bring to front
                self.dashboard_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.dashboard_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.dashboard_window.move(x, y)

            # Close current window
            if self.current_window:
                self.current_window.hide()

            self.current_window = self.dashboard_window
            print(f"✅ Dashboard window shown at position: {self.dashboard_window.x()}, {self.dashboard_window.y()}")
            print(f"✅ Window size: {self.dashboard_window.width()}x{self.dashboard_window.height()}")
            print(f"✅ Window visible: {self.dashboard_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing dashboard window: {e}")
            self.show_error_dialog("Dashboard Error", f"Failed to show dashboard:\n{str(e)}")

    def show_role_selection_window(self):
        """Show role selection window"""
        try:
            # Create new role selection window
            self.role_selection_window = RoleSelectionWindow()
            # Connect signals from role selection to appropriate functions
            self.role_selection_window.user_role_selected.connect(self.show_dashboard_window)
            self.role_selection_window.admin_role_selected.connect(self.show_admin_window)
            self.role_selection_window.logout_successful.connect(self.show_login_window)

            # Ensure window appears on screen
            self.role_selection_window.show()
            self.role_selection_window.raise_()  # Bring to front
            self.role_selection_window.activateWindow()  # Activate window

            # Force window to center and be visible
            screen = self.app.primaryScreen()
            if screen:
                screen_geometry = screen.availableGeometry()
                window_geometry = self.role_selection_window.geometry()
                x = (screen_geometry.width() - window_geometry.width()) // 2
                y = (screen_geometry.height() - window_geometry.height()) // 2
                self.role_selection_window.move(x, y)

            self.current_window = self.role_selection_window
            print(f"✅ Role selection window shown at position: {self.role_selection_window.x()}, {self.role_selection_window.y()}")
            print(f"✅ Window size: {self.role_selection_window.width()}x{self.role_selection_window.height()}")
            print(f"✅ Window visible: {self.role_selection_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing role selection window: {e}")
            self.show_error_dialog("Role Selection Error", f"Failed to show role selection:\n{str(e)}")

    def show_admin_window(self):
        """Show admin window"""
        try:
            from ui.admin_window import AdminWindow

            if self.admin_window:
                # If admin window exists, just show it
                self.admin_window.show()
                self.admin_window.raise_()  # Bring to front
                self.admin_window.activateWindow()  # Activate window
            else:
                # Create new admin window
                self.admin_window = AdminWindow()
                self.admin_window.logout_requested.connect(self.logout)

                # Ensure window appears on screen
                self.admin_window.show()
                self.admin_window.raise_()  # Bring to front
                self.admin_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.admin_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.admin_window.move(x, y)

            # Close current window
            if self.current_window:
                self.current_window.hide()

            self.current_window = self.admin_window
            print(f"✅ Admin window shown at position: {self.admin_window.x()}, {self.admin_window.y()}")
            print(f"✅ Window size: {self.admin_window.width()}x{self.admin_window.height()}")
            print(f"✅ Window visible: {self.admin_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing admin window: {e}")
            self.show_error_dialog("Admin Error", f"Failed to show admin window:\n{str(e)}")

    def show_camera_window(self):
        """Show camera window"""
        try:
            if self.camera_window:
                # If camera window exists, just show it and restart camera
                self.camera_window.show()
                self.camera_window.raise_()  # Bring to front
                self.camera_window.activateWindow()  # Activate window
                self.camera_window.setup_camera()  # Restart camera
                # Update user info in existing window with current session data
                self.camera_window.set_session_info(session_manager.get_current_user())
            else:
                # Create new camera window
                self.camera_window = CameraWindow()
                self.camera_window.photos_captured.connect(self.on_photos_captured)
                self.camera_window.logout_requested.connect(self.logout)
                # Pass session information to camera window
                self.camera_window.set_session_info(session_manager.get_current_user())

                # Ensure window appears on screen
                self.camera_window.show()
                self.camera_window.raise_()  # Bring to front
                self.camera_window.activateWindow()  # Activate window

                # Force window to center and be visible
                screen = self.app.primaryScreen()
                if screen:
                    screen_geometry = screen.availableGeometry()
                    window_geometry = self.camera_window.geometry()
                    x = (screen_geometry.width() - window_geometry.width()) // 2
                    y = (screen_geometry.height() - window_geometry.height()) // 2
                    self.camera_window.move(x, y)

            # close current window open, such as dashboard window
            if self.current_window:
                self.current_window.hide()

            self.current_window = self.camera_window
            print(f"✅ Camera window shown at position: {self.camera_window.x()}, {self.camera_window.y()}")
            print(f"✅ Window size: {self.camera_window.width()}x{self.camera_window.height()}")
            print(f"✅ Window visible: {self.camera_window.isVisible()}")

        except Exception as e:
            print(f"❌ Error showing camera window: {e}")
            self.show_error_dialog("Camera Error",
                                 f"Failed to initialize camera:\n{str(e)}\n\n"
                                 "Please ensure your camera is connected and not in use by another application.")

    def on_photos_captured(self, photo_paths):
        """Handle photos captured from main window"""
        if not photo_paths:
            self.show_info_dialog("No Photos", "No photos were captured. Please try again.")
            return

        # Store user information with captured photos
        current_user = session_manager.get_current_user()
        if current_user:
            # Update user's photo information in database
            if photo_paths:
                # Use the first photo as the main photo filename
                photo_filename = os.path.basename(photo_paths[0])
                session_manager.update_user_photo_info(photo_filename)
                print(f"Updated photo info for user {current_user['npk']}: {photo_filename}")

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
            self.selection_window.back_requested.connect(self.show_camera_window)
            self.selection_window.show()
            self.current_window = self.selection_window

            # Stop camera and close camera window to save resources
            if self.camera_window:
                self.camera_window.stop_camera()  # Stop camera before hiding
                self.camera_window.hide()

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
            dialog = CustomStyledDialog(
                self.current_window,
                "Print Complete",
                "ID card printed successfully!\n\nWould you like to create another ID card?",
                [("No", QDialog.DialogCode.Rejected), ("Yes", QDialog.DialogCode.Accepted)]
            )
            dialog.set_cancel_button(0)  # "No" button as cancel

            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.restart_workflow()
            else:
                self.app.quit()
        else:
            dialog = CustomStyledDialog(
                self.current_window,
                "Print Failed",
                "Printing failed. Would you like to try again or start over?",
                [("Cancel", QDialog.DialogCode.Rejected), ("Try Again", QDialog.DialogCode.Accepted), ("Start Over", 2)]
            )
            dialog.set_cancel_button(0)  # "Cancel" button as cancel

            result = dialog.exec()
            if result == QDialog.DialogCode.Accepted:
                # Stay on print window
                pass
            elif result == 2:  # Start Over
                self.restart_workflow()
            else:
                self.app.quit()

    def restart_workflow(self):
        """Restart the entire workflow"""
        try:
            # Stop camera and close all windows except dashboard
            if self.camera_window:
                self.camera_window.stop_camera()
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

            # Show role selection window
            QTimer.singleShot(100, self.show_role_selection_window)  # Small delay for cleanup

        except Exception as e:
            self.show_error_dialog("Restart Error", f"Failed to restart workflow:\n{str(e)}")

    def logout(self):
        """Logout current user and return to login"""
        try:
            # End current session
            session_manager.logout()
            self.current_user = None

            # Close all windows
            if self.role_selection_window:
                self.role_selection_window.hide()
            if self.dashboard_window:
                self.dashboard_window.hide()
            if self.admin_window:
                self.admin_window.hide()
            if self.camera_window:
                self.camera_window.hide()
            if self.selection_window:
                self.selection_window.hide()
            if self.processing_window:
                self.processing_window.hide()
            if self.print_window:
                self.print_window.hide()

            # Show login window
            self.show_login_window()

        except Exception as e:
            print(f"❌ Error during logout: {e}")
            self.show_error_dialog("Logout Error", f"Failed to logout:\n{str(e)}")

    def show_error_dialog(self, title, message):
        """Show error dialog"""
        dialog = CustomStyledDialog(self.current_window, title, message)
        dialog.exec()

    def show_info_dialog(self, title, message):
        """Show info dialog"""
        dialog = CustomStyledDialog(self.current_window, title, message)
        dialog.exec()

    def show_warning_dialog(self, title, message):
        """Show warning dialog"""
        dialog = CustomStyledDialog(self.current_window, title, message)
        dialog.exec()

    def cleanup(self):
        """Cleanup application resources"""
        try:
            # Close all windows
            if self.role_selection_window:
                self.role_selection_window.close()
            if self.dashboard_window:
                self.dashboard_window.close()
            if self.admin_window:
                self.admin_window.close()
            if self.camera_window:
                self.camera_window.close()
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
