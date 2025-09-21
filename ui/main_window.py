"""
Main Window UI
Camera preview and capture functionality
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QComboBox, QGridLayout,
                            QFrame, QProgressBar, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QFont, QPalette
import cv2
import numpy as np
import os
from modules.camera_manager import CameraManager, CaptureTimer
from config import UI_SETTINGS, CAMERA_SETTINGS


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

    def __init__(self):
        super().__init__()
        self.camera_manager = CameraManager()
        self.capture_timer = None
        self.photo_capture_thread = None
        self.countdown_active = False
        self.init_ui()

        # Force window to be visible
        self.show()
        self.raise_()
        self.activateWindow()

        # Setup camera after UI is shown
        self.setup_camera()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("ID Card Photo Machine")
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
        self.camera_label.setText("Camera Preview\nLoading...")

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
        self.capture_button = QPushButton("📸 Take Photos")
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
        title = QLabel("Camera Controls")
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

        # Status section
        status_group = self.create_status_group()
        layout.addWidget(status_group)

        # Spacer
        layout.addStretch()

        return control_frame

    def create_camera_selection_group(self):
        """Create camera selection group"""
        group = QGroupBox("Camera Selection")
        layout = QVBoxLayout(group)

        # Camera dropdown
        self.camera_combo = QComboBox()
        self.camera_combo.currentIndexChanged.connect(self.on_camera_changed)
        layout.addWidget(self.camera_combo)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Cameras")
        refresh_btn.clicked.connect(self.refresh_cameras)
        layout.addWidget(refresh_btn)

        return group


    def create_capture_settings_group(self):
        """Create capture settings group"""
        group = QGroupBox("Capture Settings")
        layout = QGridLayout(group)

        # Number of photos
        photos_label = QLabel("Photos to take:")
        photos_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(photos_label, 0, 0)
        self.photo_count_spin = QSpinBox()
        self.photo_count_spin.setRange(1, 10)
        self.photo_count_spin.setValue(CAMERA_SETTINGS['capture_count'])
        layout.addWidget(self.photo_count_spin, 0, 1)

        # Delay between photos
        delay_label = QLabel("Delay (seconds):")
        delay_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(delay_label, 1, 0)
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(1, 10)
        self.delay_spin.setValue(int(CAMERA_SETTINGS['capture_delay']))
        layout.addWidget(self.delay_spin, 1, 1)

        return group

    def create_status_group(self):
        """Create status group"""
        group = QGroupBox("Status")
        layout = QVBoxLayout(group)

        # Camera status
        self.camera_status = QLabel("Camera: Initializing...")
        self.camera_status.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(self.camera_status)

        # Capture progress
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # Photo counter
        self.photo_counter = QLabel("Photos captured: 0")
        self.photo_counter.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; }")
        layout.addWidget(self.photo_counter)

        return group

    def setup_camera(self):
        """Setup camera and populate camera list"""
        print("Setting up camera...")

        self.refresh_cameras()

        # Don't automatically start camera preview - let user manually start it
        cameras = self.camera_manager.get_available_cameras()
        if cameras:
            print(f"Found {len(cameras)} cameras, waiting for user to start preview")
            self.camera_status.setText(f"Camera: {len(cameras)} found - Select to start")
            self.camera_label.setText("Select a camera from dropdown\nto start preview")
        else:
            print("No cameras found")
            self.camera_status.setText("Camera: No cameras found")
            self.camera_label.setText("No Camera Available\nPlease connect a camera and click Refresh")

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
        """Refresh camera list"""
        self.camera_combo.clear()

        # Force camera re-detection
        self.camera_manager.available_cameras = self.camera_manager.detect_cameras()
        cameras = self.camera_manager.get_available_cameras()

        print(f"UI: Refreshing cameras, found {len(cameras)}")

        for i, camera in enumerate(cameras):
            camera_text = f"{camera['name']} ({camera['resolution'][0]}x{camera['resolution'][1]})"
            self.camera_combo.addItem(camera_text)
            print(f"  Added to combo: {camera_text}")

        if cameras:
            self.camera_status.setText(f"Camera: {len(cameras)} found")
        else:
            self.camera_status.setText("Camera: None found")

    def on_camera_changed(self, index):
        """Handle camera selection change"""
        if index >= 0:
            self.camera_manager.switch_camera(index)
            self.start_camera_preview()

    def start_camera_preview(self):
        """Start camera preview"""
        try:
            print("Attempting to start camera preview...")
            self.camera_manager.start_preview(self.update_camera_frame)
            self.camera_status.setText("Camera: Starting...")
            print("Camera preview start command sent")

            # Set a timer to check if preview actually started
            QTimer.singleShot(3000, self.check_camera_status)

        except Exception as e:
            print(f"Error in start_camera_preview: {e}")
            self.camera_status.setText("Camera: Error")
            self.camera_label.setText("Camera Error\nTry refreshing cameras")

    def check_camera_status(self):
        """Check if camera preview is actually working"""
        if hasattr(self.camera_manager, 'camera_thread') and self.camera_manager.camera_thread:
            if self.camera_manager.camera_thread.isRunning():
                self.camera_status.setText("Camera: Active")
                print("Camera preview confirmed active")
            else:
                self.camera_status.setText("Camera: Failed to start")
                print("Camera preview failed to start")
        else:
            self.camera_status.setText("Camera: Not initialized")
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
        self.capture_overlay.setText(f"📸 CAPTURING\nPhoto {current}/{total}")
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
        self.delay_overlay.setText(f"⏱️ DELAY\nNext photo in {remaining}s\nPhoto {current}/{total}")
        self.delay_overlay.setGeometry(0, 0, self.camera_container.width(), self.camera_container.height())
        self.delay_overlay.show()
        self.delay_overlay.raise_()
        print(f"Delay countdown: {remaining} seconds until photo {current + 1}")

    def on_photo_captured(self, current, total, photo_path):
        """Handle individual photo captured"""
        self.progress_bar.setValue(current)
        self.photo_counter.setText(f"Photos captured: {current}/{total}")
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
        self.photo_counter.setText(f"Photos captured: {len(captured_paths)}")

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
