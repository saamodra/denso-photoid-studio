"""
Processing Window UI
Interface for background removal and editing
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QFrame,
                            QScrollArea, QSlider, QGroupBox, QProgressBar,
                            QButtonGroup, QRadioButton, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QPixmap, QFont
from PIL import Image
import os
import tempfile
from modules.image_processor import get_shared_processor
from modules.session_manager import session_manager
from config import UI_SETTINGS
from datetime import datetime
from ui.components.navigation_header import NavigationHeader


class ProcessingThread(QThread):
    """Thread for background processing"""
    progress_update = pyqtSignal(int)
    processing_complete = pyqtSignal(object)  # PIL Image
    error_occurred = pyqtSignal(str)

    def __init__(self, image_path, background_type, processor, user_info=None):
        super().__init__()
        self.image_path = image_path
        self.background_type = background_type
        self.processor = processor
        self.user_info = user_info

    def run(self):
        """Run processing in background"""
        try:
            self.progress_update.emit(10)

            # Remove background
            no_bg_image = self.processor.remove_background(self.image_path)
            self.progress_update.emit(50)

            # Apply new background
            final_image = self.processor.apply_id_background(
                no_bg_image,
                self.background_type,
                user_info=self.user_info
            )
            self.progress_update.emit(90)

            # Complete
            self.progress_update.emit(100)
            self.processing_complete.emit(final_image)

        except Exception as e:
            self.error_occurred.emit(str(e))


class ProcessingWindow(QMainWindow):
    """Photo processing window"""

    processing_complete = pyqtSignal(object)  # Emits processed PIL Image
    back_requested = pyqtSignal()

    def __init__(self, photo_path, debug_save=False):
        super().__init__()
        self.photo_path = photo_path
        self.debug_save_enabled = debug_save
        self.processor = get_shared_processor()
        self.processing_thread = None
        self.processed_image = None
        self.current_user = session_manager.get_current_user()
        self.current_background = 'denso_id_card'  # Default to denso template
        self.save_button = None
        self.process_button = None
        self.init_ui()
        self.load_original_image()
        QTimer.singleShot(250, self.process_photo)

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Pemrosesan Background")
        # Set to fullscreen by default
        self.showFullScreen()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        self.navigation_header = NavigationHeader(
            step=3,
            total_steps=4,
            title="Edit & Sesuaikan Foto",
            subtitle="Proses foto secara otomatis",
            prev_text="← Kembali ke Pemilihan Foto",
            next_text="Lanjut ke Pratinjau Cetak →"
        )
        self.navigation_header.prev_clicked.connect(self.on_back_clicked)
        self.navigation_header.next_clicked.connect(self.on_next_clicked)
        self.navigation_header.set_next_enabled(False)
        self.back_button = self.navigation_header.prev_button
        self.next_button = self.navigation_header.next_button
        main_layout.addWidget(self.navigation_header)

        # Content layout - previews only
        preview_section = self.create_preview_section()
        main_layout.addWidget(preview_section)

        # Progress section
        progress_section = self.create_progress_section()
        main_layout.addWidget(progress_section)

        # Apply styling
        self.apply_style()
        self.update_user_info()

    def create_preview_section(self):
        """Create before/after preview section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)

        # Main content layout with titles and previews
        content_layout = QHBoxLayout()
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Before section (Original)
        before_section = QFrame()
        before_section_layout = QVBoxLayout(before_section)
        before_section_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        before_section_layout.setContentsMargins(0, 0, 0, 0)

        # Original title
        before_title = QLabel("Asli")
        before_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        before_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        before_section_layout.addWidget(before_title)

        # Original preview
        self.original_label = QLabel()
        self.original_label.setFixedSize(360, 480)
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        before_section_layout.addWidget(self.original_label)

        # After section (Processed)
        after_section = QFrame()
        after_section_layout = QVBoxLayout(after_section)
        after_section_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        after_section_layout.setContentsMargins(0, 0, 0, 0)

        # Processed title
        after_title = QLabel("Diproses")
        after_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        after_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        after_section_layout.addWidget(after_title)

        # Processed preview
        self.processed_label = QLabel()
        self.processed_label.setFixedSize(360, 480)
        self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.processed_label.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #7f8c8d;
            }
        """)
        self.processed_label.setText("Memproses otomatis...\nSilakan tunggu")
        after_section_layout.addWidget(self.processed_label)

        content_layout.addWidget(before_section)
        content_layout.addWidget(after_section)
        layout.addLayout(content_layout)

        if self.debug_save_enabled:
            self.save_button = QPushButton("💾 Simpan Hasil")
            self.save_button.setMinimumHeight(45)
            self.save_button.setEnabled(False)
            self.save_button.clicked.connect(self.save_processed_image)
            layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return frame

    def create_progress_section(self):
        """Create progress section"""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        self.progress_label = QLabel("Siap untuk diproses")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; font-size: 14px; }")
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        return frame

    def load_original_image(self):
        """Load and display original image"""
        try:
            image = Image.open(self.photo_path)
            image.thumbnail((340, 440), Image.Resampling.LANCZOS)

            # Save temporary preview (Windows-safe)
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = tmp.name
            tmp.close()
            image.save(temp_path, "JPEG", quality=90)

            pixmap = QPixmap(temp_path)
            # Scale while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                340, 440, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.original_label.setPixmap(scaled_pixmap)
            self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Clean up
            try:
                os.remove(temp_path)
            except Exception:
                pass

        except Exception as e:
            print(f"Error loading original image: {e}")
            self.original_label.setText("Error loading\noriginal image")

    def set_session_info(self, user_data):
        """Set session information from outside the window"""
        self.update_user_info(user_data)

    def update_user_info(self, user_data=None):
        """Refresh stored user information"""
        if user_data:
            self.current_user = user_data
            return

        user = session_manager.get_current_user()
        if user:
            self.current_user = user

    def process_photo(self):
        """Process photo with current settings"""
        if self.processing_thread and self.processing_thread.isRunning():
            return

        # Show progress
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Memproses foto...")
        if self.process_button:
            self.process_button.setEnabled(False)
        if self.save_button:
            self.save_button.setEnabled(False)

        # Start processing thread
        self.processing_thread = ProcessingThread(
            self.photo_path,
            self.current_background,
            self.processor,
            user_info=self.current_user
        )
        self.processing_thread.progress_update.connect(self.update_progress)
        self.processing_thread.processing_complete.connect(self.on_processing_complete)
        self.processing_thread.error_occurred.connect(self.on_processing_error)
        self.processing_thread.start()

    def update_progress(self, value):
        """Update progress bar"""
        self.progress_bar.setValue(value)

    def on_processing_complete(self, processed_image):
        """Handle processing completion"""
        self.processed_image = processed_image

        # Display result directly without enhancements
        self.display_processed_image(processed_image)

        # Hide progress and enable buttons
        self.progress_bar.hide()
        self.progress_label.setText("Pemrosesan selesai!")
        if self.process_button:
            self.process_button.setEnabled(True)
        self.next_button.setEnabled(True)
        if self.save_button:
            self.save_button.setEnabled(True)

        # Store processed image
        self.processed_image = processed_image

    def on_processing_error(self, error_message):
        """Handle processing error"""
        self.progress_bar.hide()
        self.progress_label.setText(f"Error: {error_message}")
        if self.process_button:
            self.process_button.setEnabled(True)
        self.processed_label.setText(f"Kesalahan Pemrosesan:\n{error_message}")
        if self.save_button:
            self.save_button.setEnabled(False)

    def display_processed_image(self, image):
        """Display processed image"""
        try:
            # Resize for display
            display_image = image.copy()
            display_image.thumbnail((340, 440), Image.Resampling.LANCZOS)

            # Save temporary preview (Windows-safe)
            tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = tmp.name
            tmp.close()
            display_image.save(temp_path, "JPEG", quality=90)

            pixmap = QPixmap(temp_path)
            # Scale while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                340, 440, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.processed_label.setPixmap(scaled_pixmap)
            self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Clean up
            try:
                os.remove(temp_path)
            except Exception:
                pass

        except Exception as e:
            print(f"Error displaying processed image: {e}")
            self.processed_label.setText("Kesalahan menampilkan\nfoto yang diproses")

    def save_processed_image(self):
        """Save processed image to a user-selected file."""
        if not self.processed_image:
            QMessageBox.information(self, "Belum Ada Hasil", "Silakan proses foto terlebih dahulu sebelum menyimpan.")
            return

        default_name = f"id_card_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        default_path = os.path.join(os.path.expanduser("~"), "Desktop", default_name)
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Simpan Foto ID",
            default_path,
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)"
        )

        if not file_path:
            return

        try:
            # Determine format from selected filter / extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".jpg", ".jpeg"]:
                self.processed_image.convert("RGB").save(file_path, "JPEG", quality=95)
            else:
                if not ext:
                    file_path = file_path + ".png"
                self.processed_image.save(file_path, "PNG")

            QMessageBox.information(self, "Berhasil", f"Foto ID berhasil disimpan di:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Gagal Menyimpan", f"Tidak dapat menyimpan gambar:\n{e}")

    def reset_processing(self):
        """Reset to original image"""
        self.processed_image = None
        self.next_button.setEnabled(False)
        self.progress_label.setText("Siap untuk diproses")
        self.processed_label.setText("Klik 'Proses Foto'\nuntuk melihat hasil")
        if self.save_button:
            self.save_button.setEnabled(False)

    def on_back_clicked(self):
        """Handle back button click"""
        self.back_requested.emit()
        self.close()

    def on_next_clicked(self):
        """Handle next button click"""
        if self.processed_image:
            self.processing_complete.emit(self.processed_image)
            self.close()

    def apply_style(self):
        """Apply modern styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                padding: 15px;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 25px;
                padding: 15px 25px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #1b2631;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #ecf0f1;
            }
            QGroupBox {
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def get_processed_image(self):
        """Get the processed image"""
        return self.processed_image

    def closeEvent(self, event):
        """Handle window close event"""
        if self.processing_thread and self.processing_thread.isRunning():
            self.processing_thread.quit()
            self.processing_thread.wait()
        event.accept()
