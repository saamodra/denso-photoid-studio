"""
Photo Selection Window UI
Interface for selecting from captured photos
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QGridLayout, QFrame,
                            QScrollArea, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from PIL import Image
import os
from config import UI_SETTINGS


class PhotoThumbnail(QLabel):
    """Custom photo thumbnail widget"""

    clicked = pyqtSignal(str)  # Emits photo path when clicked

    def __init__(self, photo_path, size=(200, 200)):
        super().__init__()
        self.photo_path = photo_path
        self.thumbnail_size = size
        self.selected = False
        self.setup_thumbnail()

    def setup_thumbnail(self):
        """Setup thumbnail display"""
        self.setFixedSize(*self.thumbnail_size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.get_style())

        # Load and display image
        self.load_image()

        # Enable mouse tracking
        self.setMousePressEvent = self.mousePressEvent

    def load_image(self):
        """Load and display the image"""
        try:
            # Load image using PIL for better control
            image = Image.open(self.photo_path)

            # Resize to thumbnail while maintaining aspect ratio
            image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)

            # Convert to Qt format
            temp_path = self.photo_path + "_thumb.jpg"
            image.save(temp_path, "JPEG", quality=85)

            pixmap = QPixmap(temp_path)

            # Scale pixmap to fit thumbnail size while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_size[0], self.thumbnail_size[1],
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)

            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass

        except Exception as e:
            print(f"Error loading thumbnail {self.photo_path}: {e}")
            self.setText("Image\nLoad Error")

    def get_style(self):
        """Get thumbnail style based on selection state"""
        if self.selected:
            return """
                QLabel {
                    border: 4px solid #3498db;
                    border-radius: 10px;
                    background-color: #ebf3fd;
                    padding: 5px;
                }
            """
        else:
            return """
                QLabel {
                    border: 2px solid #bdc3c7;
                    border-radius: 10px;
                    background-color: white;
                    padding: 5px;
                }
                QLabel:hover {
                    border: 3px solid #85c1e9;
                    background-color: #f8f9fa;
                }
            """

    def set_selected(self, selected):
        """Set selection state"""
        self.selected = selected
        self.setStyleSheet(self.get_style())

    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.photo_path)


class SelectionWindow(QMainWindow):
    """Photo selection window"""

    photo_selected = pyqtSignal(str)  # Emits selected photo path
    back_requested = pyqtSignal()     # Emits when user wants to go back

    def __init__(self, photo_paths):
        super().__init__()
        self.photo_paths = photo_paths
        self.selected_photo = None
        self.thumbnails = []
        self.init_ui()
        self.load_photos()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Select Your Best Photo")
        self.setGeometry(100, 100, 1000, 700)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Choose Your Best Photo")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px;
            }
        """)
        main_layout.addWidget(title)

        # Content layout
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Photos grid section
        photos_section = self.create_photos_section()
        content_layout.addWidget(photos_section, 60)  # 60% width

        # Preview section
        preview_section = self.create_preview_section()
        content_layout.addWidget(preview_section, 40)  # 40% width

        # Button section
        button_section = self.create_button_section()
        main_layout.addWidget(button_section)

        # Apply styling
        self.apply_style()

    def create_photos_section(self):
        """Create photos grid section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)

        # Section title
        title = QLabel("Captured Photos")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Scroll area for photos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Photos container
        photos_container = QWidget()
        self.photos_layout = QGridLayout(photos_container)
        self.photos_layout.setSpacing(15)

        scroll_area.setWidget(photos_container)
        layout.addWidget(scroll_area)

        return frame

    def create_preview_section(self):
        """Create preview section"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)

        # Section title
        title = QLabel("Preview")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(300, 400)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 14px;
            }
        """)
        self.preview_label.setText("Click on a photo\nto see preview")
        layout.addWidget(self.preview_label)

        # Photo info
        self.photo_info = QLabel()
        self.photo_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.photo_info.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.photo_info)

        return frame

    def create_button_section(self):
        """Create button section"""
        frame = QFrame()
        layout = QHBoxLayout(frame)

        # Back button
        self.back_button = QPushButton("← Back to Camera")
        self.back_button.setMinimumHeight(50)
        self.back_button.clicked.connect(self.on_back_clicked)

        # Retake button
        self.retake_button = QPushButton("📸 Retake Photos")
        self.retake_button.setMinimumHeight(50)
        self.retake_button.clicked.connect(self.on_retake_clicked)

        # Next button
        self.next_button = QPushButton("Next: Edit Photo →")
        self.next_button.setMinimumHeight(50)
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.on_next_clicked)

        layout.addWidget(self.back_button)
        layout.addWidget(self.retake_button)
        layout.addStretch()
        layout.addWidget(self.next_button)

        return frame

    def load_photos(self):
        """Load photos into grid"""
        # Clear existing thumbnails
        for thumbnail in self.thumbnails:
            thumbnail.setParent(None)
        self.thumbnails.clear()

        # Calculate grid layout
        num_photos = len(self.photo_paths)
        if num_photos <= 4:
            cols = 2
        elif num_photos <= 9:
            cols = 3
        else:
            cols = 4

        # Create thumbnails
        for i, photo_path in enumerate(self.photo_paths):
            row = i // cols
            col = i % cols

            thumbnail = PhotoThumbnail(photo_path, size=(180, 180))
            thumbnail.clicked.connect(self.on_photo_selected)

            self.photos_layout.addWidget(thumbnail, row, col)
            self.thumbnails.append(thumbnail)

        # Add instruction label if no photos
        if not self.photo_paths:
            no_photos_label = QLabel("No photos available\nGo back to take photos")
            no_photos_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_photos_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d;
                    font-size: 16px;
                    margin: 50px;
                }
            """)
            self.photos_layout.addWidget(no_photos_label, 0, 0, 1, cols)

    def on_photo_selected(self, photo_path):
        """Handle photo selection"""
        # Clear previous selection
        for thumbnail in self.thumbnails:
            thumbnail.set_selected(False)

        # Set new selection
        for thumbnail in self.thumbnails:
            if thumbnail.photo_path == photo_path:
                thumbnail.set_selected(True)
                break

        self.selected_photo = photo_path
        self.update_preview(photo_path)
        self.next_button.setEnabled(True)

    def update_preview(self, photo_path):
        """Update preview with selected photo"""
        try:
            # Load and resize image for preview
            image = Image.open(photo_path)

            # Resize to fit preview area while maintaining aspect ratio
            preview_size = (280, 380)
            image.thumbnail(preview_size, Image.Resampling.LANCZOS)

            # Save temporary preview
            temp_path = photo_path + "_preview.jpg"
            image.save(temp_path, "JPEG", quality=90)

            # Display in preview label with proper aspect ratio
            pixmap = QPixmap(temp_path)
            scaled_pixmap = pixmap.scaled(
                preview_size[0], preview_size[1],
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
            self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Update photo info
            filename = os.path.basename(photo_path)
            file_size = os.path.getsize(photo_path)
            size_mb = file_size / (1024 * 1024)

            self.photo_info.setText(f"File: {filename}\nSize: {size_mb:.1f} MB\nResolution: {image.size[0]}x{image.size[1]}")
            self.photo_info.setStyleSheet("QLabel { color: #2c3e50; font-size: 12px; }")

            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass

        except Exception as e:
            print(f"Error updating preview: {e}")
            self.preview_label.setText("Preview\nUnavailable")
            self.photo_info.setText("Error loading photo info")
            self.photo_info.setStyleSheet("QLabel { color: #e74c3c; font-size: 12px; }")

    def on_back_clicked(self):
        """Handle back button click"""
        self.back_requested.emit()
        self.close()

    def on_retake_clicked(self):
        """Handle retake button click"""
        self.back_requested.emit()
        self.close()

    def on_next_clicked(self):
        """Handle next button click"""
        if self.selected_photo:
            self.photo_selected.emit(self.selected_photo)
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def get_selected_photo(self):
        """Get currently selected photo path"""
        return self.selected_photo

    def refresh_photos(self, photo_paths):
        """Refresh photos list"""
        self.photo_paths = photo_paths
        self.selected_photo = None
        self.next_button.setEnabled(False)
        self.preview_label.setText("Click on a photo\nto see preview")
        self.photo_info.setText("")
        self.load_photos()
