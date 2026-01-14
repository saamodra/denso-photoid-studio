from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QGridLayout, QFrame, QDialog,
    QLineEdit, QComboBox, QSpinBox, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
import logging
import sys
from config import APP_NAME
from modules.database import db_manager
from modules.camera_manager import CameraManager
from modules.print_manager import PrintManager
from ui.dialogs.custom_dialog import CustomStyledDialog

logger = logging.getLogger(__name__)


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
                font-size: 16px;
                padding: 10px;
            }
            QPushButton {
                background-color: #E60012;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 16px;
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
        self.setWindowTitle("Pengaturan Admin")
        self.setFixedWidth(768)
        self.setStyleSheet(self.get_settings_stylesheet())

        layout = QVBoxLayout()

        # Save Path Setting components
        save_path_label = QLabel("Atur Path untuk Menyimpan Gambar:")
        save_path_label.setObjectName("FieldLabel")

        path_layout = QHBoxLayout()
        self.save_path_input = QLineEdit()
        self.save_path_input.setPlaceholderText("Pilih path folder...")
        browse_btn = QPushButton("Pilih")
        browse_btn.setObjectName("BrowseButton")
        browse_btn.setMinimumWidth(100)
        browse_btn.clicked.connect(self.browse_save_path)

        path_layout.addWidget(self.save_path_input, 1)
        path_layout.addSpacing(10)
        path_layout.addWidget(browse_btn, 0)

        # Default Camera Setting
        camera_frame = QFrame()
        camera_frame.setObjectName("SettingFrame")
        camera_layout = QVBoxLayout()

        camera_label = QLabel("Atur Kamera Default:")
        camera_label.setObjectName("SettingLabel")

        # Camera selection with refresh button
        camera_selection_layout = QHBoxLayout()
        self.camera_combo = QComboBox()
        self.camera_combo.setMinimumWidth(300)
        self.camera_combo.currentIndexChanged.connect(self.handle_camera_selection_changed)

        refresh_camera_btn = QPushButton("🔄 Refresh")
        refresh_camera_btn.setObjectName("RefreshButton")
        # refresh_camera_btn.setMaximumWidth(80)
        refresh_camera_btn.clicked.connect(self.refresh_cameras)

        camera_selection_layout.addWidget(self.camera_combo, 1)
        camera_selection_layout.addWidget(refresh_camera_btn, 0)

        # Camera preview area
        camera_preview_frame = QFrame()
        camera_preview_frame.setObjectName("CameraPreviewFrame")
        camera_preview_layout = QVBoxLayout()
        camera_preview_layout.setContentsMargins(0, 12, 0, 0)
        camera_preview_layout.setSpacing(8)

        preview_label = QLabel("Pratinjau Kamera:")
        preview_label.setObjectName("PreviewLabel")

        self._camera_preview_placeholder = "Pratinjau kamera akan muncul di sini."
        self.camera_preview_label = QLabel(self._camera_preview_placeholder)
        self.camera_preview_label.setObjectName("CameraPreviewLabel")
        self.camera_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_preview_label.setMinimumSize(320, 200)
        self.camera_preview_label.setWordWrap(True)
        self._preview_active = False

        camera_preview_layout.addWidget(preview_label)
        camera_preview_layout.addWidget(self.camera_preview_label)
        camera_preview_frame.setLayout(camera_preview_layout)

        camera_layout.addWidget(camera_label)
        camera_layout.addLayout(camera_selection_layout)
        camera_layout.addWidget(camera_preview_frame)
        camera_frame.setLayout(camera_layout)

        # Printer selection with refresh button
        printer_label = QLabel("Atur Printer Default:")
        printer_label.setObjectName("FieldLabel")

        printer_selection_layout = QHBoxLayout()
        self.printer_combo = QComboBox()
        self.printer_combo.setMinimumWidth(300)

        refresh_printer_btn = QPushButton("🔄 Refresh")
        refresh_printer_btn.setObjectName("RefreshButton")
        # refresh_printer_btn.setMaximumWidth(80)
        refresh_printer_btn.clicked.connect(self.refresh_printers)

        printer_selection_layout.addWidget(self.printer_combo, 1)
        printer_selection_layout.addWidget(refresh_printer_btn, 0)

        # Photos to Take Setting
        self.photos_spin = QSpinBox()
        self.photos_spin.setRange(1, 10)
        self.photos_spin.setValue(4)
        self.photos_spin.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.photos_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        photos_label = QLabel("Jumlah Foto yang Diambil:")
        photos_label.setObjectName("FieldLabel")

        # Capture Delay Setting
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(2)
        self.delay_spin.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.delay_spin.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        delay_label = QLabel("Jeda Antar Foto (detik):")
        delay_label.setObjectName("FieldLabel")

        # Combined general settings frame
        general_frame = QFrame()
        general_frame.setObjectName("SettingFrame")
        general_layout = QGridLayout()
        general_layout.setContentsMargins(0, 0, 0, 0)
        general_layout.setHorizontalSpacing(18)
        general_layout.setVerticalSpacing(12)

        general_title = QLabel("Pengaturan Umum")
        general_title.setObjectName("SettingLabel")

        general_layout.addWidget(general_title, 0, 0, 1, 2)
        general_layout.addWidget(save_path_label, 1, 0, 1, 2)
        general_layout.addLayout(path_layout, 2, 0, 1, 2)
        general_layout.addWidget(printer_label, 3, 0, 1, 2)
        general_layout.addLayout(printer_selection_layout, 4, 0, 1, 2)

        photos_column = QVBoxLayout()
        photos_column.setSpacing(6)
        photos_column.addWidget(photos_label)
        photos_column.addWidget(self.photos_spin)

        delay_column = QVBoxLayout()
        delay_column.setSpacing(6)
        delay_column.addWidget(delay_label)
        delay_column.addWidget(self.delay_spin)

        general_layout.addLayout(photos_column, 5, 0)
        general_layout.addLayout(delay_column, 5, 1)
        general_layout.setColumnStretch(0, 1)
        general_layout.setColumnStretch(1, 1)

        general_frame.setLayout(general_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Simpan Pengaturan")
        save_btn.setObjectName("SaveButton")
        save_btn.clicked.connect(self.save_settings)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("CancelButton")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        layout.addWidget(general_frame)
        layout.addWidget(camera_frame)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_save_path(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Path Simpan")
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
        cameras = []
        try:
            self.camera_combo.blockSignals(True)
            self.camera_combo.clear()

            # Force camera re-detection
            self.camera_manager.available_cameras = self.camera_manager.detect_cameras()
            cameras = self.camera_manager.get_available_cameras()

            print(f"Loading {len(cameras)} cameras for admin settings")

            for idx, camera in enumerate(cameras):
                camera_text = f"{camera['name']} ({camera['resolution'][0]}x{camera['resolution'][1]})"
                self.camera_combo.addItem(camera_text, idx)
                print(f"  Added camera: {camera_text}")

            if not cameras:
                self.camera_combo.addItem("Tidak ada kamera ditemukan")
                print("No cameras detected")

        except Exception as e:
            print(f"Error loading cameras: {e}")
            self.camera_combo.clear()
            self.camera_combo.addItem("Kesalahan memuat kamera")
            self.handle_camera_selection_changed(-1)
            return
        finally:
            self.camera_combo.blockSignals(False)

        if cameras:
            # Restore previously saved camera if possible
            self.load_camera_setting()
            if self.camera_combo.currentIndex() == -1 and self.camera_combo.count() > 0:
                self.camera_combo.setCurrentIndex(0)
            # Ensure preview reflects current selection
            self.handle_camera_selection_changed(self.camera_combo.currentIndex())
        else:
            self.handle_camera_selection_changed(-1)

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
                self.printer_combo.addItem("Tidak ada printer ditemukan")
                print("No printers detected")

        except Exception as e:
            print(f"Error loading printers: {e}")
            self.printer_combo.clear()
            self.printer_combo.addItem("Kesalahan memuat printer")

    def refresh_cameras(self):
        """Refresh camera list"""
        self.stop_camera_preview(show_placeholder=False)
        self._set_preview_message("Memuat ulang daftar kamera…")
        self.load_cameras()

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

    def handle_camera_selection_changed(self, index):
        """Update camera preview when selection changes"""
        cameras = self.camera_manager.get_available_cameras()
        if index < 0 or not cameras:
            self.stop_camera_preview(show_placeholder=True, message="Kamera tidak tersedia.")
            return

        camera_position = self.camera_combo.itemData(index)
        if camera_position is None:
            camera_position = index

        if camera_position is None or camera_position < 0 or camera_position >= len(cameras):
            self.stop_camera_preview(show_placeholder=True, message="Kamera tidak tersedia.")
            return

        self._preview_active = False

        if not self.camera_manager.switch_camera(camera_position):
            self._preview_active = False
            self._set_preview_message("Gagal mengakses kamera terpilih.")
            return

        self._preview_active = True
        self._set_preview_message("Memuat pratinjau…")
        self.camera_manager.start_preview(self.update_camera_preview)

    def update_camera_preview(self, frame):
        """Render incoming camera frame into preview label"""
        if frame is None or not self._preview_active:
            return

        pixmap = self.camera_manager.frame_to_qpixmap(
            frame,
            size=(self.camera_preview_label.width(), self.camera_preview_label.height()),
            maintain_aspect_ratio=True,
        )
        if pixmap:
            self.camera_preview_label.setPixmap(pixmap)
            self.camera_preview_label.setText("")

    def stop_camera_preview(self, show_placeholder=True, message=None):
        """Stop running camera preview and optionally show placeholder message"""
        self._preview_active = False
        self.camera_manager.stop_preview()
        if show_placeholder:
            self._set_preview_message(message or self._camera_preview_placeholder)

    def _set_preview_message(self, message):
        """Display placeholder text inside camera preview area"""
        self.camera_preview_label.clear()
        self.camera_preview_label.setText(message)

    def closeEvent(self, event):
        """Ensure camera preview thread stops when dialog closes"""
        self.stop_camera_preview(show_placeholder=False)
        super().closeEvent(event)

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
                self.show_message_box("Kesalahan Validasi", "Silakan pilih path simpan untuk gambar.", QMessageBox.Icon.Warning)
                return

            # Save to database
            success = True
            success &= db_manager.set_app_config('image_save_path', save_path)
            success &= db_manager.set_app_config('default_camera', default_camera)
            success &= db_manager.set_app_config('default_printer', default_printer)
            success &= db_manager.set_app_config('photo_count', photo_count)
            success &= db_manager.set_app_config('capture_delay', capture_delay)

            if success:
                self.show_message_box("Pengaturan", "Pengaturan berhasil disimpan!", QMessageBox.Icon.Information)
                self.accept()
            else:
                self.show_message_box("Kesalahan", "Gagal menyimpan beberapa pengaturan. Silakan coba lagi.", QMessageBox.Icon.Critical)
        except Exception as e:
            self.show_message_box("Kesalahan", f"Terjadi kesalahan saat menyimpan pengaturan: {str(e)}", QMessageBox.Icon.Critical)

    def get_settings_stylesheet(self):
        return """
        QDialog {
            background-color: #FFFFFF;
            color: #333333;
        }

        #SettingFrame {
            background-color: #FFFFFF;
            border: 1px solid #DDDDDD;
            border-radius: 8px;
            margin: 8px;
            padding: 12px;
        }

        #SettingLabel {
            color: #E60012;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 8px;
        }

        #FieldLabel {
            color: #333333;
            font-weight: 600;
            font-size: 15px;
        }

        #PreviewLabel {
            color: #E60012;
            font-weight: bold;
            font-size: 15px;
        }

        #CameraPreviewFrame {
            background-color: #FFFFFF;
            border: 1px solid #E1E1E1;
            border-radius: 10px;
            padding: 16px;
        }

        #CameraPreviewLabel {
            background-color: #FAFAFA;
            border: 2px dashed #E60012;
            border-radius: 12px;
            color: #333333;
            font-size: 15px;
            padding: 16px;
        }

        QLineEdit, QComboBox, QSpinBox {
            padding: 12px;
            border: 1px solid #CCCCCC;
            border-radius: 6px;
            background-color: #FFFFFF;
            color: #333333;
            font-size: 16px;
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
            font-size: 14px;
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
            font-size: 14px;
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
            font-size: 13px;
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
            font-size: 16px;
            min-height: 40px;
        }

        #ErrorLabel {
            color: #DC3545;
            font-weight: bold;
            font-size: 14px;
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
        self.load_system_info()

    def init_ui(self):
        self.setWindowTitle("Admin Panel - " + APP_NAME)
        self.setStyleSheet(self.get_stylesheet())

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Panel Admin")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title.setObjectName("TitleLabel")

        # Settings and Logout buttons in header
        header_btn_layout = QHBoxLayout()
        settings_btn = QPushButton("⚙️ Pengaturan")
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

        employee_title = QLabel("📋 Manajemen Karyawan")
        employee_title.setObjectName("SectionTitle")

        # Employee management buttons grid
        employee_grid = QGridLayout()

        # Row 1
        self.show_list_btn = QPushButton("📄 Tampilkan Daftar Data Karyawan")
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

        system_title = QLabel("📊 Informasi Sistem")
        system_title.setObjectName("SectionTitle")

        self.refresh_info_btn = QPushButton("🔄 Muat Ulang Data")
        self.refresh_info_btn.setObjectName("InfoRefreshButton")
        self.refresh_info_btn.clicked.connect(self.load_system_info)

        # System info display area
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)

        self.info_value_labels = {}
        info_items = [
            ("employee_count", "👥 Total Karyawan Saat Ini:"),
            ("pending_requests", "📝 Permintaan Foto Ulang:"),
            ("photos_taken", "📷 Total Foto Diambil:")
        ]

        for key, title_text in info_items:
            card = QFrame()
            card.setObjectName("InfoCard")
            card_layout = QVBoxLayout()
            card_layout.setContentsMargins(20, 20, 20, 20)
            card_layout.setSpacing(12)

            title_label = QLabel(title_text)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setObjectName("InfoCardTitle")

            value_label = QLabel("Memuat…")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setObjectName("InfoCardValue")

            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
            card.setLayout(card_layout)

            info_layout.addWidget(card, 1)
            self.info_value_labels[key] = value_label

        system_layout.addWidget(system_title)
        refresh_layout = QHBoxLayout()
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_info_btn)
        system_layout.addLayout(refresh_layout)
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

    def showEvent(self, event):
        super().showEvent(event)
        self.load_system_info()

    # Placeholder methods for button functions
    def handle_show_list(self):
        # dialog = CustomStyledDialog(self, "Feature", "Show Employee List feature will be implemented here.")
        # dialog.exec()
        self.show_employee_list.emit()

    def print_id_card(self):
        dialog = CustomStyledDialog(self, "Fitur", "Fitur Cetak ID Card akan diimplementasikan di sini.")
        dialog.exec()

    def load_system_info(self):
        summary_queries = {
            "employee_count": ("SELECT COUNT(*) AS total FROM users", ()),
            "pending_requests": ("SELECT COUNT(*) AS total FROM request_histories WHERE status = ?", ("requested",)),
            "photos_taken": ("SELECT COUNT(*) AS total FROM photo_histories", ())
        }

        for key, (query, params) in summary_queries.items():
            value = self._fetch_summary_count(query, params)
            label = self.info_value_labels.get(key)
            if label:
                if isinstance(value, int):
                    label.setText(f"{value:,}".replace(",", "."))
                else:
                    label.setText(str(value))

    def _fetch_summary_count(self, query, params=()):
        try:
            rows = db_manager.execute_query(query, params)
            if rows:
                value = rows[0].get("total")
                if value is None:
                    # Fallback to the first value in the row if alias missing
                    value = next(iter(rows[0].values()), 0)
                return int(value)
        except Exception as exc:
            logger.error("Gagal memuat ringkasan sistem: %s", exc)
        return 0

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #F5F5F5;
        }

        #TitleLabel {
            color: #E60012;
            font-size: 28px;
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
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
        }

        #InfoCard {
            background-color: #FFFFFF;
            border: 2px solid #E60012;
            border-radius: 16px;
        }

        #InfoCardTitle {
            color: #333333;
            font-size: 18px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        #InfoCardValue {
            color: #E60012;
            font-size: 40px;
            font-weight: 800;
        }

        #InfoRefreshButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 16px;
            border-radius: 8px;
            padding: 12px 24px;
        }
        #InfoRefreshButton:hover {
            background-color: #CC0010;
        }
        #InfoRefreshButton:pressed {
            background-color: #99000C;
        }

        #FunctionButton {
            background-color: #E60012;
            color: #FFFFFF;
            font-weight: bold;
            font-size: 20px;
            border: none;
            border-radius: 8px;
            padding: 20px;
            margin: 5px;
            min-height: 60px;
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
            font-size: 16px;
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
            font-size: 14px;
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
            font-size: 14px;
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
            font-size: 14px;
            margin: 5px;
        }

        #InfoValue {
            color: #E60012;
            font-weight: bold;
            font-size: 14px;
            margin: 5px;
        }
        """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminWindow()
    window.showFullScreen()  # tampilkan dalam mode full screen
    window.show()
    sys.exit(app.exec())
