"""
Main Window UI
Camera preview and capture functionality
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QComboBox, QGridLayout,
                            QFrame, QProgressBar, QSpinBox, QGroupBox, QDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QFont, QPalette
import cv2
import numpy as np
import os
from modules.camera_manager import CameraManager, CaptureTimer
from modules.database import db_manager
from modules.session_manager import session_manager
from config import UI_SETTINGS, CAMERA_SETTINGS
from ui.dialogs.custom_dialog import CustomStyledDialog


class PhotoCaptureThread(QThread):
    """Thread for capturing multiple photos without blocking UI"""
    photo_captured = pyqtSignal(int, int, str)  # current, total, photo_path
    capture_starting = pyqtSignal(int, int)  # current, total - when about to capture
    delay_countdown = pyqtSignal(int, int, int)  # current, total, remaining_delay
    capture_complete = pyqtSignal(list)  # captured_paths

    def __init__(self, camera_manager, count, delay):
        super().__init__()
        self.camera_manager = camera_manager
        self.count = count
        self.delay = delay

    def run(self):
        """Capture photos with proper delays"""
        captured_paths = []

        try:
            for i in range(self.count):
                # Check if thread should stop
                if self.isInterruptionRequested():
                    print("Photo capture thread interrupted")
                    break

                # Signal that we're about to capture a photo
                self.capture_starting.emit(i + 1, self.count)

                # Capture photo
                print(f"Capturing photo {i+1}/{self.count}...")
                photo_path = self.camera_manager.capture_photo()

                if photo_path:
                    captured_paths.append(photo_path)

                # Emit progress signal
                self.photo_captured.emit(i + 1, self.count, photo_path)

                # Wait for delay with countdown AFTER photo is captured (except last photo)
                if i < self.count - 1:
                    print(f"Starting {self.delay} second delay after photo {i+1}...")
                    # Wait 1 second for capture overlay to be hidden, then start delay countdown
                    self.sleep(1)
                    for remaining in range(int(self.delay), 0, -1):
                        if self.isInterruptionRequested():
                            break
                        self.delay_countdown.emit(i + 1, self.count, remaining)
                        self.sleep(1)  # Sleep for 1 second

        except Exception as e:
            print(f"Error in photo capture thread: {e}")

        # Emit completion signal
        self.capture_complete.emit(captured_paths)


class MainWindow(QMainWindow):
    """Main application window with camera preview and capture"""

    photos_captured = pyqtSignal(list)  # Signal emitted when photos are captured
    logout_requested = pyqtSignal()  # Signal emitted when logout is requested

    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.capture_timer = None
        self.photo_capture_thread = None
        self.countdown_active = False
        self.current_user = None
        self.init_ui()

        # Force window to be visible
        self.show()
        self.raise_()
        self.activateWindow()

        # Setup camera after UI is shown
        self.setup_camera()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Mesin Foto ID Card Denso")
        # Set to fullscreen by default
        self.showFullScreen()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Camera section (left side)
        camera_section = self.create_camera_section()
        main_layout.addWidget(camera_section, 70)  # 70% width

        # Control section (right side)
        control_section = self.create_control_section()
        main_layout.addWidget(control_section, 30)  # 30% width

        # Set style
        self.apply_modern_style()

    def get_config_value(self, config_name, default_value):
        """Get configuration value from database with fallback to default"""
        try:
            value = db_manager.get_app_config(config_name)
            if value is not None:
                # Try to convert to appropriate type
                if isinstance(default_value, int):
                    return int(value)
                elif isinstance(default_value, float):
                    return float(value)
                else:
                    return value
            return default_value
        except Exception as e:
            print(f"Error loading config {config_name}: {e}")
            return default_value

    def validate_camera_from_database(self):
        """Validate if the camera from database is still available"""
        try:
            default_camera = db_manager.get_app_config('default_camera')
            if not default_camera:
                self.camera_error_label.hide()
                return

            # Check if the saved camera is still available
            cameras = self.camera_manager.get_available_cameras()
            camera_found = False

            for camera in cameras:
                if default_camera.lower() in camera['name'].lower():
                    camera_found = True
                    break

            if not camera_found:
                # Camera not found, show error
                self.camera_error_label.setText(f"⚠️ Kamera yang dikonfigurasi '{default_camera}' tidak tersedia. Silakan hubungi admin untuk memperbarui pengaturan kamera.")
                self.camera_error_label.show()
            else:
                # Camera is available, hide error
                self.camera_error_label.hide()

        except Exception as e:
            print(f"Error validating camera from database: {e}")
            self.camera_error_label.setText(f"Error validating camera: {str(e)}")
            self.camera_error_label.show()

    def auto_select_camera_from_database(self):
        """Auto-select camera from database configuration"""
        try:
            default_camera = db_manager.get_app_config('default_camera')
            if not default_camera:
                self.camera_status.setText("Kamera: Tidak ada kamera yang dikonfigurasi")
                self.camera_label.setText("Tidak Ada Kamera Dikonfigurasi\nSilakan hubungi admin untuk mengkonfigurasi kamera")
                self.camera_error_label.setText("⚠️ Tidak ada kamera yang dikonfigurasi. Silakan hubungi admin untuk mengatur kamera.")
                self.camera_error_label.show()
                return False

            # Check if the saved camera is still available
            cameras = self.camera_manager.get_available_cameras()
            camera_found = False
            camera_index = -1

            for i, camera in enumerate(cameras):
                if default_camera.lower() in camera['name'].lower():
                    camera_found = True
                    camera_index = i
                    break

            if not camera_found:
                # Camera not found, show error
                self.camera_status.setText(f"Kamera: '{default_camera}' tidak tersedia")
                self.camera_label.setText(f"Kesalahan Kamera\n'{default_camera}' tidak tersedia\nSilakan hubungi admin untuk memperbarui pengaturan kamera")
                self.camera_error_label.setText(f"⚠️ Kamera yang dikonfigurasi '{default_camera}' tidak tersedia. Silakan hubungi admin untuk memperbarui pengaturan kamera.")
                self.camera_error_label.show()
                return False
            else:
                # Camera found, select it
                self.camera_manager.switch_camera(camera_index)
                self.camera_status.setText(f"Kamera: {default_camera} (Siap)")
                self.camera_error_label.hide()
                return True

        except Exception as e:
            print(f"Error auto-selecting camera from database: {e}")
            self.camera_status.setText("Kamera: Kesalahan memuat konfigurasi")
            self.camera_label.setText("Kesalahan Kamera\nKesalahan memuat konfigurasi kamera\nSilakan hubungi admin")
            self.camera_error_label.setText(f"Kesalahan memuat konfigurasi kamera: {str(e)}")
            self.camera_error_label.show()
            return False

    def update_camera_info_display(self):
        """Update camera information display"""
        try:
            default_camera = db_manager.get_app_config('default_camera')
            cameras = self.camera_manager.get_available_cameras()

            if not default_camera:
                self.camera_info_label.setText("Tidak ada kamera yang dikonfigurasi\nHubungi admin untuk mengatur kamera")
                return

            # Find the configured camera
            camera_found = False
            for camera in cameras:
                if default_camera.lower() in camera['name'].lower():
                    self.camera_info_label.setText(f"Kamera yang Dikonfigurasi:\n{camera['name']}\nResolusi: {camera['resolution'][0]}x{camera['resolution'][1]}")
                    camera_found = True
                    break

            if not camera_found:
                self.camera_info_label.setText(f"Kamera yang Dikonfigurasi:\n{default_camera}\n(Tidak Tersedia)")

        except Exception as e:
            print(f"Error updating camera info display: {e}")
            self.camera_info_label.setText("Kesalahan memuat informasi kamera")

    def create_camera_section(self):
        """Create camera preview section"""
        camera_frame = QFrame()
        camera_frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(camera_frame)

        # Camera preview container with overlay support
        self.camera_container = QFrame()
        self.camera_container.setMinimumSize(*UI_SETTINGS['camera_preview_size'])
        self.camera_container.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 10px;
            }
        """)

        # Use absolute positioning for overlay
        self.camera_container_layout = QVBoxLayout(self.camera_container)
        self.camera_container_layout.setContentsMargins(0, 0, 0, 0)

        # Camera preview label
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(*UI_SETTINGS['camera_preview_size'])
        self.camera_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: white;
                font-size: 16px;
                text-align: center;
            }
        """)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setText("Pratinjau Kamera\nMemuat...")

        self.camera_container_layout.addWidget(self.camera_label)

        # Countdown overlay (positioned absolutely over camera)
        self.countdown_label = QLabel()
        self.countdown_label.setParent(self.camera_container)
        self.countdown_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                font-size: 72px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
            }
        """)
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.hide()

        # Capture overlay (positioned absolutely over camera)
        self.capture_overlay = QLabel()
        self.capture_overlay.setParent(self.camera_container)
        self.capture_overlay.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 0, 0, 100);
                color: white;
                font-size: 48px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
            }
        """)
        self.capture_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capture_overlay.hide()

        # Delay countdown overlay (positioned absolutely over camera)
        self.delay_overlay = QLabel()
        self.delay_overlay.setParent(self.camera_container)
        self.delay_overlay.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 100, 0, 150);
                color: white;
                font-size: 36px;
                font-weight: bold;
                border-radius: 10px;
                text-align: center;
            }
        """)
        self.delay_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.delay_overlay.hide()

        # Position overlays to cover the entire camera container
        self.countdown_label.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        self.capture_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        self.delay_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())

        layout.addWidget(self.camera_container)

        # Capture button
        self.capture_button = QPushButton("📸 Ambil Foto")
        self.capture_button.setMinimumHeight(60)
        self.capture_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 30px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.capture_button.clicked.connect(self.start_photo_capture)

        layout.addWidget(self.capture_button)

        return camera_frame

    def create_control_section(self):
        """Create control panel section"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(control_frame)

        # Title
        title = QLabel("Kontrol Kamera")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Camera selection
        camera_group = self.create_camera_selection_group()
        layout.addWidget(camera_group)

        # Capture settings
        capture_group = self.create_capture_settings_group()
        layout.addWidget(capture_group)

        # User info section
        user_group = self.create_user_info_group()
        layout.addWidget(user_group)

        # Status section
        status_group = self.create_status_group()
        layout.addWidget(status_group)

        # Spacer
        layout.addStretch()

        return control_frame

    def create_user_info_group(self):
        """Create user information display group"""
        group = QGroupBox("Pengguna Saat Ini")
        layout = QVBoxLayout(group)

        # User info labels
        self.user_name_label = QLabel("Belum login")
        self.user_npk_label = QLabel("")
        self.user_role_label = QLabel("")
        self.user_department_label = QLabel("")

        # Style the labels
        user_style = """
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                margin: 2px 0px;
            }
        """

        self.user_name_label.setStyleSheet(user_style + """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #E60012;
            }
        """)

        self.user_npk_label.setStyleSheet(user_style)
        self.user_role_label.setStyleSheet(user_style)
        self.user_department_label.setStyleSheet(user_style)

        layout.addWidget(self.user_name_label)
        layout.addWidget(self.user_npk_label)
        layout.addWidget(self.user_role_label)
        layout.addWidget(self.user_department_label)

        # Logout button
        logout_btn = QPushButton("Keluar")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        return group

    def set_session_info(self, user_data):
        """Set user session information"""
        self.current_user = user_data
        self.update_user_info()

    def update_user_info(self):
        """Update user information display"""
        if self.current_user:
            self.user_name_label.setText(f"👤 {self.current_user.get('name', 'Unknown')}")
            self.user_npk_label.setText(f"NPK: {self.current_user.get('npk', 'N/A')}")
            self.user_role_label.setText(f"Role: {self.current_user.get('role', 'N/A').title()}")
            self.user_department_label.setText(f"Dept: {self.current_user.get('department_name', 'N/A')}")
        else:
            # Try to get from session manager
            current_user = session_manager.get_current_user()
            if current_user:
                self.current_user = current_user
                self.user_name_label.setText(f"👤 {current_user.get('name', 'Unknown')}")
                self.user_npk_label.setText(f"NPK: {current_user.get('npk', 'N/A')}")
                self.user_role_label.setText(f"Role: {current_user.get('role', 'N/A').title()}")
                self.user_department_label.setText(f"Dept: {current_user.get('department_name', 'N/A')}")
            else:
                self.user_name_label.setText("Belum login")
                self.user_npk_label.setText("")
                self.user_role_label.setText("")
                self.user_department_label.setText("")

    def logout(self):
        """Handle logout request"""
        dialog = CustomStyledDialog(
            self,
            'Konfirmasi Keluar',
            'Apakah Anda yakin ingin keluar?',
            [("Tidak", QDialog.DialogCode.Rejected), ("Ya", QDialog.DialogCode.Accepted)]
        )
        dialog.set_cancel_button(0)  # "No" button as cancel

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Emit signal to main app to handle logout
            self.logout_requested.emit()

    def create_camera_selection_group(self):
        """Create camera selection group - removed, camera is auto-selected from database"""
        group = QGroupBox("Informasi Kamera")
        layout = QVBoxLayout(group)

        # Camera info label (readonly)
        self.camera_info_label = QLabel("Memuat informasi kamera...")
        self.camera_info_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 12px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        layout.addWidget(self.camera_info_label)

        return group


    def create_capture_settings_group(self):
        """Create capture settings group"""
        group = QGroupBox("Pengaturan Pengambilan")
        layout = QGridLayout(group)

        # Number of photos
        photos_label = QLabel("Jumlah foto:")
        photos_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(photos_label, 0, 0)
        self.photo_count_spin = QSpinBox()
        self.photo_count_spin.setRange(1, 10)
        self.photo_count_spin.setReadOnly(True)
        self.photo_count_spin.setStyleSheet("""
            QSpinBox {
                background-color: #f8f9fa;
                color: #6c757d;
                border: 2px solid #dee2e6;
            }
        """)
        # Load value from database
        photo_count = self.get_config_value('photo_count', CAMERA_SETTINGS['capture_count'])
        self.photo_count_spin.setValue(int(photo_count))
        layout.addWidget(self.photo_count_spin, 0, 1)

        # Delay between photos
        delay_label = QLabel("Jeda (detik):")
        delay_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(delay_label, 1, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setReadOnly(True)
        self.delay_spin.setStyleSheet("""
            QSpinBox {
                background-color: #f8f9fa;
                color: #6c757d;
                border: 2px solid #dee2e6;
            }
        """)
        # Load value from database
        delay_value = self.get_config_value('capture_delay', CAMERA_SETTINGS['capture_delay'])
        self.delay_spin.setValue(int(delay_value))
        layout.addWidget(self.delay_spin, 1, 1)

        return group

    def create_status_group(self):
        """Create status group"""
        group = QGroupBox("Status")
        layout = QVBoxLayout(group)

        # Camera status
        self.camera_status = QLabel("Kamera: Memulai...")
        self.camera_status.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(self.camera_status)

        # Camera error label
        self.camera_error_label = QLabel("")
        self.camera_error_label.setStyleSheet("""
            QLabel {
                color: #DC3545;
                font-weight: bold;
                font-size: 11px;
                background-color: #F8D7DA;
                border: 1px solid #F5C6CB;
                border-radius: 4px;
                padding: 5px;
                margin-top: 3px;
            }
        """)
        self.camera_error_label.hide()
        layout.addWidget(self.camera_error_label)

        # Capture progress
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Photo counter
        self.photo_counter = QLabel("Foto diambil: 0")
        self.photo_counter.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(self.photo_counter)

        return group

    def setup_camera(self):
        """Setup camera and auto-select from database"""
        print("Setting up camera...")

        # Load cameras
        self.camera_manager.available_cameras = self.camera_manager.detect_cameras()
        cameras = self.camera_manager.get_available_cameras()

        # Try to auto-select camera from database
        camera_available = self.auto_select_camera_from_database()

        # Update camera info display
        self.update_camera_info_display()

        # If camera is available, start preview automatically
        if camera_available:
            self.start_camera_preview()

    def delayed_camera_start(self):
        """Start camera preview after UI is fully loaded"""
        try:
            print("Starting camera preview...")
            self.start_camera_preview()
            print("Camera preview started successfully")
        except Exception as e:
            print(f"Error starting camera preview: {e}")
            self.camera_status.setText("Camera: Error starting preview")
            self.camera_label.setText("Camera Error\nTry refreshing cameras")

    def refresh_cameras(self):
        """Refresh camera detection and re-validate database camera"""
        # Force camera re-detection
        self.camera_manager.available_cameras = self.camera_manager.detect_cameras()
        cameras = self.camera_manager.get_available_cameras()

        print(f"UI: Refreshing cameras, found {len(cameras)}")

        # Re-validate camera from database
        self.auto_select_camera_from_database()
        self.update_camera_info_display()

    def start_camera_preview(self):
        """Start camera preview if camera is available"""
        try:
            # Check if camera is available before starting
            if not self.auto_select_camera_from_database():
                return  # Camera not available, error already shown

            print("Attempting to start camera preview...")
            self.camera_manager.start_preview(self.update_camera_frame)
            self.camera_status.setText("Kamera: Memulai...")
            print("Camera preview start command sent")

            # Set a timer to check if preview actually started
            QTimer.singleShot(3000, self.check_camera_status)

        except Exception as e:
            print(f"Error in start_camera_preview: {e}")
            self.camera_status.setText("Kamera: Kesalahan")
            self.camera_label.setText("Kesalahan Kamera\nKesalahan memulai pratinjau kamera\nSilakan hubungi admin")

    def check_camera_status(self):
        """Check if camera preview is actually working"""
        if hasattr(self.camera_manager, 'camera_thread') and self.camera_manager.camera_thread:
            if self.camera_manager.camera_thread.isRunning():
                self.camera_status.setText("Kamera: Aktif")
                print("Camera preview confirmed active")
            else:
                self.camera_status.setText("Kamera: Gagal memulai")
                print("Camera preview failed to start")
        else:
            self.camera_status.setText("Kamera: Belum diinisialisasi")
            print("Camera thread not created")

    def update_camera_frame(self, frame):
        """Update camera preview frame"""
        # Always update the camera preview, even during countdown
        # Convert frame to QPixmap and display with proper aspect ratio
        pixmap = self.camera_manager.frame_to_qpixmap(
            frame, UI_SETTINGS['camera_preview_size'], maintain_aspect_ratio=True
        )
        self.camera_label.setPixmap(pixmap)
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def start_photo_capture(self):
        """Start photo capture sequence"""
        if self.countdown_active:
            return

        # Disable capture button
        self.capture_button.setEnabled(False)
        self.countdown_active = True

        # Show progress bar
        self.progress_bar.show()
        self.progress_bar.setMaximum(self.photo_count_spin.value())
        self.progress_bar.setValue(0)

        # Start countdown timer
        self.capture_timer = CaptureTimer(3)  # 3 second countdown
        self.capture_timer.countdown_update.connect(self.update_countdown)
        self.capture_timer.capture_ready.connect(self.capture_photos)
        self.capture_timer.start()

    def update_countdown(self, count):
        """Update countdown display"""
        # Show countdown overlay
        self.countdown_label.setText(str(count))
        # Position countdown to cover the entire camera container
        self.countdown_label.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        self.countdown_label.show()
        self.countdown_label.raise_()

    def capture_photos(self):
        """Start capturing multiple photos asynchronously"""
        # Hide countdown
        self.countdown_label.hide()

        count = self.photo_count_spin.value()
        delay = self.delay_spin.value()

        print(f"Starting capture sequence: {count} photos with {delay}s delay")

        # Start async photo capture
        self.photo_capture_thread = PhotoCaptureThread(
            self.camera_manager, count, delay
        )
        self.photo_capture_thread.capture_starting.connect(self.on_capture_starting)
        self.photo_capture_thread.photo_captured.connect(self.on_photo_captured)
        self.photo_capture_thread.delay_countdown.connect(self.on_delay_countdown)
        self.photo_capture_thread.capture_complete.connect(self.on_capture_complete)
        self.photo_capture_thread.start()

    def on_capture_starting(self, current, total):
        """Handle when a photo is about to be captured"""
        # Hide delay overlay if it's showing
        self.delay_overlay.hide()

        # Show capture overlay
        self.capture_overlay.setText(f"📸 MENGAMBIL FOTO\nFoto {current}/{total}")
        self.capture_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        self.capture_overlay.show()
        self.capture_overlay.raise_()
        print(f"About to capture photo {current}/{total}")

        # Hide capture overlay after 1 second
        QTimer.singleShot(1000, self.hide_capture_overlay)

    def hide_capture_overlay(self):
        """Hide the capture overlay"""
        self.capture_overlay.hide()

    def on_delay_countdown(self, current, total, remaining):
        """Handle delay countdown between photos"""
        # Show delay overlay
        self.delay_overlay.setText(f"⏱️ JEDA\nFoto berikutnya dalam {remaining}s\nFoto {current}/{total}")
        self.delay_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        self.delay_overlay.show()
        self.delay_overlay.raise_()
        print(f"Delay countdown: {remaining} seconds until photo {current + 1}")

    def on_photo_captured(self, current, total, photo_path):
        """Handle individual photo captured"""
        self.progress_bar.setValue(current)
        self.photo_counter.setText(f"Foto diambil: {current}/{total}")
        print(f"Photo {current}/{total} captured: {os.path.basename(photo_path) if photo_path else 'Failed'}")

    def on_capture_complete(self, captured_paths):
        """Handle capture sequence completion"""
        print(f"Capture sequence complete: {len(captured_paths)} photos captured")

        # Hide all overlays
        self.delay_overlay.hide()
        self.capture_overlay.hide()

        # Re-enable capture button
        self.capture_button.setEnabled(True)
        self.countdown_active = False
        self.progress_bar.hide()

        # Update final counter
        self.photo_counter.setText(f"Foto diambil: {len(captured_paths)}")

        # Emit signal with captured photos
        if captured_paths:
            self.photos_captured.emit(captured_paths)

    def apply_modern_style(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 8px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #1b2631;
            }
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            QLabel {
                color: #2c3e50;
                background-color: transparent;
            }
            QComboBox {
                color: #2c3e50;
            }
            QSpinBox {
                color: #2c3e50;
            }
        """)

    def resizeEvent(self, event):
        """Handle window resize event"""
        super().resizeEvent(event)
        # Update overlay positions if they're visible
        if hasattr(self, 'countdown_label') and self.countdown_label.isVisible():
            self.countdown_label.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        if hasattr(self, 'capture_overlay') and self.capture_overlay.isVisible():
            self.capture_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        if hasattr(self, 'delay_overlay') and self.delay_overlay.isVisible():
            self.delay_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())

    def stop_camera(self):
        """Stop camera preview and cleanup resources"""
        print("Stopping camera preview...")

        # Stop photo capture thread if running
        if self.photo_capture_thread and self.photo_capture_thread.isRunning():
            print("Stopping photo capture thread...")
            self.photo_capture_thread.requestInterruption()
            self.photo_capture_thread.quit()
            self.photo_capture_thread.wait(3000)  # Wait up to 3 seconds
            if self.photo_capture_thread.isRunning():
                print("Force terminating photo capture thread...")
                self.photo_capture_thread.terminate()
                self.photo_capture_thread.wait(1000)
            self.photo_capture_thread = None

        # Stop camera preview
        if self.camera_manager:
            self.camera_manager.stop_preview()

    def closeEvent(self, event):
        """Handle window close event"""
        # Use the same cleanup as stop_camera
        self.stop_camera()

        # Additional cleanup
        if self.camera_manager:
            self.camera_manager.cleanup()

        event.accept()
