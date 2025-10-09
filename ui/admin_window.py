from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QDialog,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import sys
from config import APP_NAME
from modules.database import db_manager
from modules.camera_manager import CameraManager
from modules.print_manager import PrintManager


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

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize managers for device detection
        self.camera_manager = CameraManager()
        self.print_manager = PrintManager()
        self.init_ui()
        self.load_settings()
        self.load_devices()

    def init_ui(self):
        self.setWindowTitle("Admin Settings")
        self.setFixedWidth(768)
        self.setStyleSheet(self.get_settings_stylesheet())

        layout = QVBoxLayout()

        # Save Path Setting
        save_path_frame = QFrame()
        save_path_frame.setObjectName("SettingFrame")
        save_path_layout = QVBoxLayout()

        save_path_label = QLabel("Set Path to Save Picture:")
        save_path_label.setObjectName("SettingLabel")

        path_layout = QHBoxLayout()
        self.save_path_input = QLineEdit()
        self.save_path_input.setPlaceholderText("Select folder path...")
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("BrowseButton")
        browse_btn.setMinimumWidth(100)
        browse_btn.clicked.connect(self.browse_save_path)

        path_layout.addWidget(self.save_path_input, 1)  # Give more space to input
        path_layout.addSpacing(10)  # Add spacing between input and button
        path_layout.addWidget(browse_btn, 0)  # Fixed size for button

        save_path_layout.addWidget(save_path_label)
        save_path_layout.addLayout(path_layout)
        save_path_frame.setLayout(save_path_layout)

        # Default Camera Setting
        camera_frame = QFrame()
        camera_frame.setObjectName("SettingFrame")
        camera_layout = QVBoxLayout()

        camera_label = QLabel("Set Default Camera:")
        camera_label.setObjectName("SettingLabel")

        # Camera selection with refresh button
        camera_selection_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(300)

        refresh_camera_btn = QPushButton("🔄 Refresh")
        refresh_camera_btn.setObjectName("RefreshButton")
        refresh_camera_btn.setMaximumWidth(80)
        refresh_camera_btn.clicked.connect(self.refresh_cameras)

        camera_selection_layout.addWidget(self.camera_combo, 1)
        camera_selection_layout.addWidget(refresh_camera_btn, 0)

        camera_layout.addWidget(camera_label)
        camera_layout.addLayout(camera_selection_layout)
        camera_frame.setLayout(camera_layout)

        # Default Printer Setting
        printer_frame = QFrame()
        printer_frame.setObjectName("SettingFrame")
        printer_layout = QVBoxLayout()

        printer_label = QLabel("Set Default Printer:")
        printer_label.setObjectName("SettingLabel")

        # Printer selection with refresh button
        printer_selection_layout = QHBoxLayout()
        self.printer_combo = QComboBox()
        self.printer_combo.setMinimumWidth(300)

        refresh_printer_btn = QPushButton("🔄 Refresh")
        refresh_printer_btn.setObjectName("RefreshButton")
        refresh_printer_btn.setMaximumWidth(80)
        refresh_printer_btn.clicked.connect(self.refresh_printers)

        printer_selection_layout.addWidget(self.printer_combo, 1)
        printer_selection_layout.addWidget(refresh_printer_btn, 0)

        printer_layout.addWidget(printer_label)
        printer_layout.addLayout(printer_selection_layout)
        printer_frame.setLayout(printer_layout)

        # Photos to Take Setting
        photos_frame = QFrame()
        photos_frame.setObjectName("SettingFrame")
        photos_layout = QVBoxLayout()

        photos_label = QLabel("Photos to Take:")
        photos_label.setObjectName("SettingLabel")

        self.photos_spin = QSpinBox()
        self.photos_spin.setRange(1, 10)
        self.photos_spin.setValue(4)

        photos_layout.addWidget(photos_label)
        photos_layout.addWidget(self.photos_spin)
        photos_frame.setLayout(photos_layout)

        # Capture Delay Setting
        delay_frame = QFrame()
        delay_frame.setObjectName("SettingFrame")
        delay_layout = QVBoxLayout()

        delay_label = QLabel("Delay Between Photos (seconds):")
        delay_label.setObjectName("SettingLabel")

        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(2)

        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spin)
        delay_frame.setLayout(delay_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self.save_settings)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        layout.addWidget(save_path_frame)
        layout.addWidget(camera_frame)
        layout.addWidget(printer_frame)
        layout.addWidget(photos_frame)
        layout.addWidget(delay_frame)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_save_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Path")
        if folder:
            self.save_path_input.setText(folder)

    def load_settings(self):
        """Load existing settings from database"""
        try:
            # Load save path setting
            save_path = db_manager.get_app_config('image_save_path')
            if save_path:
                self.save_path_input.setText(save_path)

            # Load camera and printer settings (devices are loaded separately)
            self.load_camera_setting()
            self.load_printer_setting()

            # Load photos to take setting
            photo_count = db_manager.get_app_config('photo_count')
            if photo_count:
                self.photos_spin.setValue(int(photo_count))

            # Load capture delay setting
            capture_delay = db_manager.get_app_config('capture_delay')
            if capture_delay:
                self.delay_spin.setValue(int(capture_delay))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def load_devices(self):
        """Load real camera and printer devices"""
        self.load_cameras()
        self.load_printers()

    def load_cameras(self):
        """Load real camera devices from system"""
        try:
            self.camera_combo.clear()

            # Force camera re-detection
            self.camera_manager.available_cameras = self.camera_manager.detect_cameras()
            cameras = self.camera_manager.get_available_cameras()

            print(f"Loading {len(cameras)} cameras for admin settings")

            for camera in cameras:
                camera_text = f"{camera['name']} ({camera['resolution'][0]}x{camera['resolution'][1]})"
                self.camera_combo.addItem(camera_text)
                print(f"  Added camera: {camera_text}")

            if not cameras:
                self.camera_combo.addItem("No cameras found")
                print("No cameras detected")

        except Exception as e:
            print(f"Error loading cameras: {e}")
            self.camera_combo.clear()
            self.camera_combo.addItem("Error loading cameras")

    def load_printers(self):
        """Load real printer devices from system"""
        try:
            self.printer_combo.clear()

            # Get system printers
            printers = self.print_manager.get_available_printers()

            print(f"Loading {len(printers)} printers for admin settings")

            for printer in printers:
                printer_text = f"{printer['name']} ({printer['status']})"
                self.printer_combo.addItem(printer_text)
                print(f"  Added printer: {printer_text}")

            if not printers:
                self.printer_combo.addItem("No printers found")
                print("No printers detected")

        except Exception as e:
            print(f"Error loading printers: {e}")
            self.printer_combo.clear()
            self.printer_combo.addItem("Error loading printers")

    def refresh_cameras(self):
        """Refresh camera list"""
        self.load_cameras()
        # Try to restore previous selection if it still exists
        self.load_camera_setting()

    def refresh_printers(self):
        """Refresh printer list"""
        self.load_printers()
        # Try to restore previous selection if it still exists
        self.load_printer_setting()

    def load_camera_setting(self):
        """Load camera setting from database and select in combo"""
        try:
            default_camera = db_manager.get_app_config('default_camera')
            if default_camera:
                # Try to find exact match first
                index = self.camera_combo.findText(default_camera, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.camera_combo.setCurrentIndex(index)
                    return

                # Try to find partial match
                for i in range(self.camera_combo.count()):
                    if default_camera.lower() in self.camera_combo.itemText(i).lower():
                        self.camera_combo.setCurrentIndex(i)
                        return
        except Exception as e:
            print(f"Error loading camera setting: {e}")

    def load_printer_setting(self):
        """Load printer setting from database and select in combo"""
        try:
            default_printer = db_manager.get_app_config('default_printer')
            if default_printer:
                # Try to find exact match first
                index = self.printer_combo.findText(default_printer, Qt.MatchFlag.MatchExactly)
                if index >= 0:
                    self.printer_combo.setCurrentIndex(index)
                    return

                # Try to find partial match
                for i in range(self.printer_combo.count()):
                    if default_printer.lower() in self.printer_combo.itemText(i).lower():
                        self.printer_combo.setCurrentIndex(i)
                        return
        except Exception as e:
            print(f"Error loading printer setting: {e}")

    def show_message_box(self, title, message, icon_type):
        """Show a styled message box with proper text visibility"""
        dialog = CustomStyledDialog(self, title, message)
        dialog.exec()

    def save_settings(self):
        """Save settings to database"""
        try:
            # Get values from form
            save_path = self.save_path_input.text().strip()

            # Extract actual device names from display text
            camera_text = self.camera_combo.currentText()
            if "(" in camera_text:
                default_camera = camera_text.split(" (")[0]  # Get name before resolution
            else:
                default_camera = camera_text

            printer_text = self.printer_combo.currentText()
            if "(" in printer_text:
                default_printer = printer_text.split(" (")[0]  # Get name before status
            else:
                default_printer = printer_text

            photo_count = str(self.photos_spin.value())
            capture_delay = str(self.delay_spin.value())

            # Validate required fields
            if not save_path:
                self.show_message_box("Validation Error", "Please select a save path for images.", QMessageBox.Icon.Warning)
                return

            # Save to database
            success = True
            success &= db_manager.set_app_config('image_save_path', save_path)
            success &= db_manager.set_app_config('default_camera', default_camera)
            success &= db_manager.set_app_config('default_printer', default_printer)
            success &= db_manager.set_app_config('photo_count', photo_count)
            success &= db_manager.set_app_config('capture_delay', capture_delay)

            if success:
                self.show_message_box("Settings", "Settings saved successfully!", QMessageBox.Icon.Information)
                self.accept()
            else:
                self.show_message_box("Error", "Failed to save some settings. Please try again.", QMessageBox.Icon.Critical)
        except Exception as e:
            self.show_message_box("Error", f"An error occurred while saving settings: {str(e)}", QMessageBox.Icon.Critical)

    def get_settings_stylesheet(self):
        return """
        QDialog {
            background-color: #F5F5F5;
        }

        #SettingFrame {
            background-color: #FFFFFF;
            border: 1px solid #DDDDDD;
            border-radius: 8px;
            margin: 8px;
            padding: 15px;
        }

        #SettingLabel {
            color: #E60012;
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 8px;
        }

        QLineEdit, QComboBox, QSpinBox {
            padding: 12px;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            background-color: #FFFFFF;
            color: #333333;
            font-size: 14px;
            min-height: 20px;
        }

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 2px solid #E60012;
            background-color: #FFFFFF;
        }

        QPushButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 12px;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #CC0010;
        }

        #CancelButton {
            background-color: #888888;
        }
        #CancelButton:hover {
            background-color: #666666;
        }

        #SaveButton {
            background-color: #28A745;
        }
        #SaveButton:hover {
            background-color: #218838;
        }

        #BrowseButton {
            background-color: #007BFF;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 12px;
            border: none;
            border-radius: 6px;
            padding: 12px 16px;
            min-width: 80px;
        }
        #BrowseButton:hover {
            background-color: #0056B3;
        }

        #RefreshButton {
            background-color: #6C757D;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 11px;
            border: none;
            border-radius: 4px;
            padding: 8px 12px;
            min-width: 60px;
        }
        #RefreshButton:hover {
            background-color: #5A6268;
        }

        #DeviceDisplay {
            background-color: #F8F9FA;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            padding: 12px;
            color: #333333;
            font-size: 14px;
            min-height: 40px;
        }

        #ErrorLabel {
            color: #DC3545;
            font-weight: bold;
            font-size: 12px;
            background-color: #F8D7DA;
            border: 1px solid #F5C6CB;
            border-radius: 4px;
            padding: 8px;
            margin-top: 5px;
        }
        """

class AdminWindow(QWidget):
    logout_requested = pyqtSignal()
    show_employee_list = pyqtSignal()  # Emit user data on successful login


    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Panel - " + APP_NAME)
        self.showFullScreen()  # Make window fullscreen
        self.setStyleSheet(self.get_stylesheet())

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Admin Panel")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setObjectName("TitleLabel")

        # Settings and Logout buttons in header
        header_btn_layout = QHBoxLayout()
        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.setObjectName("HeaderButton")
        settings_btn.clicked.connect(self.show_settings)

        logout_btn = QPushButton("Keluar")
        logout_btn.setObjectName("LogoutButton")
        logout_btn.clicked.connect(self.handle_logout)

        header_btn_layout.addWidget(settings_btn)
        header_btn_layout.addWidget(logout_btn)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addLayout(header_btn_layout)

        # Employee Management Section
        employee_frame = QFrame()
        employee_frame.setObjectName("SectionFrame")
        employee_layout = QVBoxLayout()

        employee_title = QLabel("📋 Employee Management")
        employee_title.setObjectName("SectionTitle")

        # Employee management buttons grid
        employee_grid = QGridLayout()

        # Row 1
        self.show_list_btn = QPushButton("📄 Show List Data Employee")
        self.show_list_btn.setObjectName("FunctionButton")
        self.show_list_btn.clicked.connect(self.handle_show_list)

        employee_grid.addWidget(self.show_list_btn, 0, 0)

        employee_layout.addWidget(employee_title)
        employee_layout.addLayout(employee_grid)
        employee_frame.setLayout(employee_layout)

        # System Information Section
        system_frame = QFrame()
        system_frame.setObjectName("SectionFrame")
        system_layout = QVBoxLayout()

        system_title = QLabel("📊 System Information")
        system_title.setObjectName("SectionTitle")

        # System info display area (placeholder)
        info_layout = QGridLayout()

        info_items = [
            ("Total Employees:", "0"),
            ("Pending Renewals:", "0"),
            ("Today's ID Cards Printed:", "0"),
            ("System Status:", "Online")
        ]

        for i, (label_text, value_text) in enumerate(info_items):
            label = QLabel(label_text)
            label.setObjectName("InfoLabel")
            value = QLabel(value_text)
            value.setObjectName("InfoValue")

            row = i // 2
            col = (i % 2) * 2

            info_layout.addWidget(label, row, col)
            info_layout.addWidget(value, row, col + 1)

        system_layout.addWidget(system_title)
        system_layout.addLayout(info_layout)
        system_frame.setLayout(system_layout)

        # Add everything to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(employee_frame)
        main_layout.addWidget(system_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec()

    def handle_logout(self):
        self.close()
        self.logout_requested.emit()

    # Placeholder methods for button functions
    def handle_show_list(self):
        # dialog = CustomStyledDialog(self, "Feature", "Show Employee List feature will be implemented here.")
        # dialog.exec()
        self.show_employee_list.emit()

    def print_id_card(self):
        dialog = CustomStyledDialog(self, "Feature", "Print ID Card feature will be implemented here.")
        dialog.exec()

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #F5F5F5;
        }

        #TitleLabel {
            color: #E60012;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }

        #SectionFrame {
            background-color: #FFFFFF;
            border: 2px solid #E60012;
            border-radius: 12px;
            margin: 10px 0;
            padding: 20px;
        }

        #SectionTitle {
            color: #E60012;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
        }

        #FunctionButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
            min-height: 50px;
        }
        #FunctionButton:hover {
            background-color: #CC0010;
        }
        #FunctionButton:pressed {
            background-color: #99000C;
        }

        #DeleteButton {
            background-color: #DC3545;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 14px;
            border: none;
            border-radius: 8px;
            padding: 15px;
            margin: 5px;
            min-height: 50px;
        }
        #DeleteButton:hover {
            background-color: #C82333;
        }
        #DeleteButton:pressed {
            background-color: #A71D2A;
        }

        #HeaderButton {
            background-color: #007BFF;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 12px;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            margin-left: 5px;
        }
        #HeaderButton:hover {
            background-color: #0056B3;
        }

        #LogoutButton {
            background-color: #555555;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 12px;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            margin-left: 5px;
        }
        #LogoutButton:hover {
            background-color: #333333;
        }

        #InfoLabel {
            color: #666666;
            font-weight: bold;
            font-size: 12px;
            margin: 5px;
        }

        #InfoValue {
            color: #E60012;
            font-weight: bold;
            font-size: 12px;
            margin: 5px;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.showFullScreen()  # tampilkan dalam mode full screen
    window.show()
    sys.exit(app.exec())
