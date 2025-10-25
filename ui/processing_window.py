"""
Processing Window UI
Interface for background removal and editing
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QGridLayout, QFrame,
                            QScrollArea, QSlider, QGroupBox, QProgressBar,
                            QButtonGroup, QRadioButton)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QPixmap, QFont
from PIL import Image
import os
import tempfile
from modules.image_processor import ImageProcessor
from modules.session_manager import session_manager
from config import UI_SETTINGS


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


class BackgroundOption(QWidget):
    """Custom background option widget"""

    selected = pyqtSignal(str)  # Emits background type when selected

    def __init__(self, background_type, processor):
        super().__init__()
        self.background_type = background_type
        self.processor = processor
        self.is_selected = False
        self.setup_ui()

    def setup_ui(self):
        """Setup background option UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # Remove spacing

        # Background preview
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(192, 256)  # Larger preview for better visibility
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet(self.get_preview_style())
        layout.addWidget(self.preview_label)

        # Load preview
        self.load_preview()

        # Enable click
        self.mousePressEvent = self.on_clicked

    def get_preview_style(self):
        """Get preview style based on selection"""
        if self.is_selected:
            return """
                QLabel {
                    border: 3px solid #3498db;
                    border-radius: 8px;
                    background-color: #ebf3fd;
                }
            """
        else:
            return """
                QLabel {
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    background-color: white;
                }
                QLabel:hover {
                    border: 2px solid #85c1e9;
                }
            """

    def load_preview(self):
        """Load background preview"""
        try:
            # Get small background sample
            background = self.processor.get_background(self.background_type)
            if background:
                background.thumbnail((192, 256), Image.Resampling.LANCZOS)

                # Save temporary preview
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    background.save(temp_file.name, "JPEG", quality=85)

                    pixmap = QPixmap(temp_file.name)
                    # Scale while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        192, 256, Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.preview_label.setPixmap(scaled_pixmap)
                    self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Clean up
                    try:
                        os.remove(temp_file.name)
                    except:
                        pass
            else:
                self.preview_label.setText("Preview\nN/A")

        except Exception as e:
            print(f"Error loading background preview: {e}")
            self.preview_label.setText("Error")

    def set_selected(self, selected):
        """Set selection state"""
        self.is_selected = selected
        self.preview_label.setStyleSheet(self.get_preview_style())

    def on_clicked(self, event):
        """Handle click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selected.emit(self.background_type)


class ProcessingWindow(QMainWindow):
    """Photo processing window"""

    processing_complete = pyqtSignal(object)  # Emits processed PIL Image
    back_requested = pyqtSignal()

    def __init__(self, photo_path):
        super().__init__()
        self.photo_path = photo_path
        self.processor = ImageProcessor()
        self.processing_thread = None
        self.processed_image = None
        self.current_user = session_manager.get_current_user()
        self.current_background = 'denso_id_card'  # Default to denso template
        self.background_options = []
        self.init_ui()
        self.load_original_image()
        self.create_background_options()

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

        # Title
        title = QLabel("Hapus Background & Terapkan Background ID Card")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin: 15px;
            }
        """)
        main_layout.addWidget(title)

        # Content layout
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Before/After section
        preview_section = self.create_preview_section()
        content_layout.addWidget(preview_section, 70)  # 70% width

        # Controls section
        controls_section = self.create_controls_section()
        content_layout.addWidget(controls_section, 30)  # 30% width

        # Progress section
        progress_section = self.create_progress_section()
        main_layout.addWidget(progress_section)

        # Button section
        button_section = self.create_button_section()
        main_layout.addWidget(button_section)

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
        self.processed_label.setText("Klik 'Proses Foto'\nuntuk melihat hasil")
        after_section_layout.addWidget(self.processed_label)

        content_layout.addWidget(before_section)
        content_layout.addWidget(after_section)
        layout.addLayout(content_layout)

        return frame

    def create_controls_section(self):
        """Create controls section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)

        # Title - aligned with other section titles
        title = QLabel("Pilihan Background")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Add spacing to align with image previews
        layout.addSpacing(20)

        self.backgrounds_container = QWidget()
        self.backgrounds_layout = QGridLayout(self.backgrounds_container)
        self.backgrounds_layout.setSpacing(10)
        self.backgrounds_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        layout.addWidget(self.backgrounds_container)

        # Process button
        self.process_button = QPushButton("🎨 Proses Foto")
        self.process_button.setMinimumHeight(50)
        self.process_button.clicked.connect(self.process_photo)
        layout.addWidget(self.process_button)

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

    def create_button_section(self):
        """Create button section"""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Back button
        self.back_button = QPushButton("← Kembali ke Pilihan")
        self.back_button.setMinimumHeight(50)
        self.back_button.clicked.connect(self.on_back_clicked)

        # Reset button
        self.reset_button = QPushButton("🔄 Ulangi")
        self.reset_button.setMinimumHeight(50)
        self.reset_button.clicked.connect(self.reset_processing)

        # Next button
        self.next_button = QPushButton("Selanjutnya: Pratinjau Cetak →")
        self.next_button.setMinimumHeight(50)
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.on_next_clicked)

        layout.addWidget(self.back_button)
        layout.addWidget(self.reset_button)
        layout.addStretch()
        layout.addWidget(self.next_button)

        return frame

    def load_original_image(self):
        """Load and display original image"""
        try:
            image = Image.open(self.photo_path)
            image.thumbnail((340, 440), Image.Resampling.LANCZOS)

            # Save temporary preview
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                image.save(temp_file.name, "JPEG", quality=90)

                pixmap = QPixmap(temp_file.name)
                # Scale while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    340, 440, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.original_label.setPixmap(scaled_pixmap)
                self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Clean up
                try:
                    os.remove(temp_file.name)
                except:
                    pass

        except Exception as e:
            print(f"Error loading original image: {e}")
            self.original_label.setText("Error loading\noriginal image")

    def create_background_options(self):
        """Create background option widgets - only white and denso template"""
        # Clear existing options
        for option in self.background_options:
            option.setParent(None)
        self.background_options.clear()

        # Only show white and denso template options
        backgrounds = ['denso_id_card', 'white_solid']

        # Create option widgets
        for i, bg_type in enumerate(backgrounds):
            row = i // 2
            col = i % 2

            option = BackgroundOption(bg_type, self.processor)
            option.selected.connect(self.on_background_selected)

            self.backgrounds_layout.addWidget(option, row, col)
            self.background_options.append(option)

        # Select first option by default and update current_background
        if self.background_options:
            self.background_options[0].set_selected(True)
            # Update current_background to match the first selected option
            self.current_background = self.background_options[0].background_type

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

    def on_background_selected(self, background_type):
        """Handle background selection"""
        # Clear previous selection
        for option in self.background_options:
            option.set_selected(False)

        # Set new selection
        for option in self.background_options:
            if option.background_type == background_type:
                option.set_selected(True)
                break

        self.current_background = background_type

        # Re-process if already processed
        if self.processed_image:
            self.process_photo()


    def process_photo(self):
        """Process photo with current settings"""
        if self.processing_thread and self.processing_thread.isRunning():
            return

        # Show progress
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Memproses foto...")
        self.process_button.setEnabled(False)

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
        self.process_button.setEnabled(True)
        self.next_button.setEnabled(True)

        # Store processed image
        self.processed_image = processed_image

    def on_processing_error(self, error_message):
        """Handle processing error"""
        self.progress_bar.hide()
        self.progress_label.setText(f"Error: {error_message}")
        self.process_button.setEnabled(True)
        self.processed_label.setText(f"Kesalahan Pemrosesan:\n{error_message}")

    def display_processed_image(self, image):
        """Display processed image"""
        try:
            # Resize for display
            display_image = image.copy()
            display_image.thumbnail((340, 440), Image.Resampling.LANCZOS)

            # Save temporary preview
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                display_image.save(temp_file.name, "JPEG", quality=90)

                pixmap = QPixmap(temp_file.name)
                # Scale while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    340, 440, Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.processed_label.setPixmap(scaled_pixmap)
                self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Clean up
                try:
                    os.remove(temp_file.name)
                except:
                    pass

        except Exception as e:
            print(f"Error displaying processed image: {e}")
            self.processed_label.setText("Kesalahan menampilkan\nfoto yang diproses")

    def reset_processing(self):
        """Reset to original image"""
        self.processed_image = None
        self.next_button.setEnabled(False)
        self.progress_label.setText("Siap untuk diproses")
        self.processed_label.setText("Klik 'Proses Foto'\nuntuk melihat hasil")

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
