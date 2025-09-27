from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QDialog,
    QLineEdit, QComboBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import sys
from config import APP_NAME

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Admin Settings")
        self.setFixedWidth(768)
        self.setStyleSheet(self.get_settings_stylesheet())

        layout = QVBoxLayout()

        # Save Path Setting
        save_path_frame = QFrame()
        save_path_frame.setObjectName("SettingFrame")
        save_path_layout = QVBoxLayout()

        save_path_label = QLabel("Set Path Save PIC:")
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

        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 1", "Camera 2", "USB Camera", "Built-in Camera"])

        camera_layout.addWidget(camera_label)
        camera_layout.addWidget(self.camera_combo)
        camera_frame.setLayout(camera_layout)

        # Default Printer Setting
        printer_frame = QFrame()
        printer_frame.setObjectName("SettingFrame")
        printer_layout = QVBoxLayout()

        printer_label = QLabel("Set Default Printer:")
        printer_label.setObjectName("SettingLabel")

        self.printer_combo = QComboBox()
        self.printer_combo.addItems(["Printer 1", "Printer 2", "ID Card Printer", "Default Printer"])

        printer_layout.addWidget(printer_label)
        printer_layout.addWidget(self.printer_combo)
        printer_frame.setLayout(printer_layout)

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
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_save_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Path")
        if folder:
            self.save_path_input.setText(folder)

    def save_settings(self):
        # Here you would implement saving the settings
        # For now, just show a confirmation message
        QMessageBox.information(self, "Settings", "Settings saved successfully!")
        self.accept()

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

        QLineEdit, QComboBox {
            padding: 12px;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            background-color: #FFFFFF;
            color: #333333;
            font-size: 14px;
            min-height: 20px;
        }

        QLineEdit:focus, QComboBox:focus {
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
        """

class AdminWindow(QWidget):
    logout_requested = pyqtSignal()

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
        self.show_list_btn.clicked.connect(self.show_employee_list)

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
    def show_employee_list(self):
        QMessageBox.information(self, "Feature", "Show Employee List feature will be implemented here.")

    def print_id_card(self):
        QMessageBox.information(self, "Feature", "Print ID Card feature will be implemented here.")

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
    window.show()
    sys.exit(app.exec())
