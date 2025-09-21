"""
Print Window UI
Interface for print preview and printing
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QGridLayout, QFrame,
                            QComboBox, QSpinBox, QGroupBox, QRadioButton,
                            QButtonGroup, QProgressBar, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap, QFont
from PIL import Image
import os
import tempfile
from modules.print_manager import PrintManager
# from modules.image_processor import ImageProcessor  # Not needed for direct implementation
from config import UI_SETTINGS, PRINT_SETTINGS


class PrintThread(QThread):
    """Thread for printing operations"""
    progress_update = pyqtSignal(int)
    print_complete = pyqtSignal(bool)  # Success/failure
    status_update = pyqtSignal(str)

    def __init__(self, print_manager, image, printer_name, copies, print_method):
        super().__init__()
        self.print_manager = print_manager
        self.image = image
        self.printer_name = printer_name
        self.copies = copies
        self.print_method = print_method

    def run(self):
        """Run printing operation"""
        try:
            self.status_update.emit("Preparing image for printing...")
            self.progress_update.emit(20)

            # Prepare image
            prepared_image = self.print_manager.prepare_image_for_printing(
                self.image, self.copies
            )
            self.progress_update.emit(50)

            self.status_update.emit("Sending to printer...")

            # Print based on method
            if self.print_method == 'qt':
                success = self.print_manager.print_image_qt(prepared_image, self.printer_name)
            else:
                success = self.print_manager.print_image_system(
                    prepared_image, self.printer_name, self.copies
                )

            self.progress_update.emit(100)

            if success:
                self.status_update.emit("Print job sent successfully!")
            else:
                self.status_update.emit("Print job failed")

            self.print_complete.emit(success)

        except Exception as e:
            self.status_update.emit(f"Print error: {str(e)}")
            self.print_complete.emit(False)


class PrintWindow(QMainWindow):
    """Print preview and printing window"""

    print_complete = pyqtSignal(bool)  # Success/failure
    back_requested = pyqtSignal()

    def __init__(self, processed_image):
        super().__init__()
        self.processed_image = processed_image
        self.print_manager = PrintManager()
        self.image_processor = None  # Not needed for direct implementation
        self.print_thread = None
        self.id_card_image = None
        self.init_ui()
        self.create_id_card()
        self.load_print_settings()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Print Preview")
        # Set to fullscreen by default
        self.showFullScreen()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout - use horizontal layout for better space utilization
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Left side - Preview section (portrait orientation)
        left_layout = QVBoxLayout()
        preview_section = self.create_preview_section()
        left_layout.addWidget(preview_section)

        # Right side - Settings and controls
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Title
        title = QLabel("Print Preview - ID Card")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px;
            }
        """)
        right_layout.addWidget(title)

        # Settings section
        settings_section = self.create_settings_section()
        right_layout.addWidget(settings_section)

        # Status section
        status_section = self.create_status_section()
        right_layout.addWidget(status_section)

        # Button section
        button_section = self.create_button_section()
        right_layout.addWidget(button_section)

        # Add layouts to main layout
        main_layout.addLayout(left_layout, 60)  # 60% width for preview
        main_layout.addLayout(right_layout, 40)  # 40% width for controls

        # Apply styling
        self.apply_style()

    def create_preview_section(self):
        """Create print preview section - portrait orientation like ID card"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the entire content

        # Section title
        title = QLabel("Print Preview")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the title
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Preview container to center the preview label
        preview_container = QFrame()
        preview_container_layout = QVBoxLayout(preview_container)
        preview_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_container_layout.setContentsMargins(0, 0, 0, 0)

        # Preview label - portrait orientation for ID card
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(540, 720)
        self.preview_label.setMaximumSize(540, 720)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                padding: 15px;
            }
        """)
        preview_container_layout.addWidget(self.preview_label)

        layout.addWidget(preview_container)

        # Preview info
        self.preview_info = QLabel()
        self.preview_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_info.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                margin-top: 5px;
            }
        """)
        layout.addWidget(self.preview_info)

        return frame

    def create_settings_section(self):
        """Create print settings section - simplified"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Print Settings")
        title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title)

        # Printer selection group
        printer_group = self.create_printer_group()
        layout.addWidget(printer_group)

        # Copy settings group
        copy_group = self.create_copy_group()
        layout.addWidget(copy_group)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Printers")
        refresh_btn.clicked.connect(self.refresh_printers)
        layout.addWidget(refresh_btn)

        layout.addStretch()

        return frame

    def create_printer_group(self):
        """Create printer selection group - compact"""
        group = QGroupBox("Printer")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Printer dropdown
        self.printer_combo = QComboBox()
        self.printer_combo.setMaximumHeight(30)
        layout.addWidget(self.printer_combo)

        # Printer status
        self.printer_status = QLabel("Status: Checking...")
        self.printer_status.setStyleSheet("QLabel { font-size: 9px; color: #2c3e50; font-weight: bold; }")
        layout.addWidget(self.printer_status)

        return group

    def create_copy_group(self):
        """Create copy settings group - compact"""
        group = QGroupBox("Copies")
        layout = QGridLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Number of copies
        copies_label = QLabel("Copies:")
        copies_label.setStyleSheet("QLabel { color: #2c3e50; font-weight: bold; font-size: 11px; }")
        layout.addWidget(copies_label, 0, 0)
        self.copies_spin = QSpinBox()
        self.copies_spin.setRange(1, 20)
        self.copies_spin.setValue(1)
        self.copies_spin.setMaximumHeight(25)
        self.copies_spin.valueChanged.connect(self.update_preview)
        layout.addWidget(self.copies_spin, 0, 1)

        return group


    def create_status_section(self):
        """Create status section - compact"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Status label
        self.status_label = QLabel("Ready to print")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                margin: 5px;
            }
        """)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.progress_bar.setMaximumHeight(20)
        layout.addWidget(self.progress_bar)

        return frame

    def create_button_section(self):
        """Create button section - compact for responsiveness"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        # All buttons in a single row for compactness
        button_row = QHBoxLayout()

        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setMinimumHeight(40)
        self.back_button.clicked.connect(self.on_back_clicked)

        # Save button
        self.save_button = QPushButton("💾 Save")
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.save_id_card)

        # Print button
        self.print_button = QPushButton("🖨️ Print")
        self.print_button.setMinimumHeight(40)
        self.print_button.clicked.connect(self.print_id_card)

        button_row.addWidget(self.back_button)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.print_button)

        layout.addLayout(button_row)

        return frame

    def create_id_card(self):
        """Create ID card from processed image"""
        try:
            # Create ID card layout directly to avoid dependency issues
            self.id_card_image = self.create_id_card_layout_direct(self.processed_image)
            self.update_preview()

        except Exception as e:
            print(f"Error creating ID card: {e}")
            self.preview_label.setText("Error creating\nID card layout")

    def create_id_card_layout_direct(self, processed_image):
        """Create final ID card layout in portrait orientation - direct implementation"""
        # Standard ID card dimensions in portrait (53.98 x 85.6 mm at 300 DPI)
        dpi = 300
        width_mm, height_mm = 53.98, 85.6  # Portrait orientation
        width_px = int(width_mm * dpi / 25.4)
        height_px = int(height_mm * dpi / 25.4)

        print(f"ID card dimensions: {width_px}x{height_px} pixels")
        print(f"Input image size: {processed_image.size}")

        # Create ID card canvas in portrait
        id_card = Image.new('RGB', (width_px, height_px), 'white')

        # Resize processed image to fit card while maintaining aspect ratio
        processed_image.thumbnail((width_px, height_px), Image.Resampling.LANCZOS)
        print(f"After thumbnail resize: {processed_image.size}")

        # Center the image on the card
        paste_x = (width_px - processed_image.size[0]) // 2
        paste_y = (height_px - processed_image.size[1]) // 2
        print(f"Pasting at position: ({paste_x}, {paste_y})")

        id_card.paste(processed_image, (paste_x, paste_y))

        return id_card

    def update_preview(self):
        """Update print preview"""
        if not self.id_card_image:
            return

        try:
            copies = self.copies_spin.value()

            # Create print preview
            preview_image = self.print_manager.create_print_preview(
                self.id_card_image, copies
            )

            # Display preview
            self.display_preview(preview_image)

            # Update info
            width, height = self.id_card_image.size
            self.preview_info.setText(
                f"ID Card Size: {width}x{height} pixels\n"
                f"Print Copies: {copies}\n"
                f"Estimated Size: {PRINT_SETTINGS['id_card_size'][0]:.1f} x {PRINT_SETTINGS['id_card_size'][1]:.1f} mm"
            )

        except Exception as e:
            print(f"Error updating preview: {e}")
            self.preview_label.setText("Error updating\npreview")

    def display_preview(self, image):
        """Display preview image with correct aspect ratio (object-fit: contain behavior) - portrait orientation"""
        try:
            # Calculate the maximum size that fits within the portrait preview area
            # The preview label is set to 540x720, account for padding
            max_width = 540 - 30  # 510px
            max_height = 720 - 30  # 690px

            # Get original image dimensions
            orig_width, orig_height = image.size
            print(f"Display preview - Original image size: {orig_width}x{orig_height}")
            print(f"Display preview - Max display size: {max_width}x{max_height}")

            # Calculate scale factor to fit within bounds while maintaining aspect ratio
            scale_x = max_width / orig_width
            scale_y = max_height / orig_height
            scale = min(scale_x, scale_y)  # Use the smaller scale to ensure it fits

            # Calculate new dimensions
            new_width = int(orig_width * scale)
            new_height = int(orig_height * scale)
            print(f"Display preview - Scaled size: {new_width}x{new_height}")

            # Resize image maintaining aspect ratio
            display_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Save temporary preview
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                display_image.save(temp_file.name, "JPEG", quality=90)

                pixmap = QPixmap(temp_file.name)
                # Set the pixmap directly without additional scaling to maintain aspect ratio
                self.preview_label.setPixmap(pixmap)
                self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # Clean up
                try:
                    os.remove(temp_file.name)
                except:
                    pass

        except Exception as e:
            print(f"Error displaying preview: {e}")
            self.preview_label.setText("Preview error")

    def load_print_settings(self):
        """Load print settings and populate UI"""
        # Load printers
        self.refresh_printers()

        # Set default values from config
        self.copies_spin.setValue(1)

    def refresh_printers(self):
        """Refresh printer list"""
        self.printer_combo.clear()

        printers = self.print_manager.refresh_printers()

        if printers:
            for printer in printers:
                self.printer_combo.addItem(printer['name'])
            self.printer_status.setText(f"Status: {len(printers)} printer(s) found")
        else:
            self.printer_combo.addItem("No printers found")
            self.printer_status.setText("Status: No printers available")

    def save_id_card(self):
        """Save ID card to file"""
        try:
            if not self.id_card_image:
                self.status_label.setText("No ID card to save")
                return

            # Save processed image directly
            from config import PROCESSED_DIR
            save_path = os.path.join(PROCESSED_DIR, "id_card_final.png")
            os.makedirs(PROCESSED_DIR, exist_ok=True)

            # Save PIL Image
            self.id_card_image.save(save_path, format='PNG', quality=95)

            self.status_label.setText(f"ID card saved to: {save_path}")

        except Exception as e:
            self.status_label.setText(f"Save error: {str(e)}")

    def print_id_card(self):
        """Print ID card"""
        if not self.id_card_image:
            self.status_label.setText("No ID card to print")
            return

        if self.print_thread and self.print_thread.isRunning():
            return

        # Get settings
        printer_name = self.printer_combo.currentText()
        if printer_name == "No printers found":
            self.status_label.setText("No printer selected")
            return

        copies = self.copies_spin.value()

        # Disable print button and show progress
        self.print_button.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        # Start print thread
        self.print_thread = PrintThread(
            self.print_manager,
            self.id_card_image,
            printer_name,
            copies,
            'system'  # Use system printing by default
        )

        self.print_thread.progress_update.connect(self.update_print_progress)
        self.print_thread.status_update.connect(self.update_print_status)
        self.print_thread.print_complete.connect(self.on_print_complete)
        self.print_thread.start()

    def update_print_progress(self, value):
        """Update print progress"""
        self.progress_bar.setValue(value)

    def update_print_status(self, message):
        """Update print status"""
        self.status_label.setText(message)

    def on_print_complete(self, success):
        """Handle print completion"""
        self.progress_bar.hide()
        self.print_button.setEnabled(True)

        if success:
            self.status_label.setText("Print job completed successfully!")
        else:
            self.status_label.setText("Print job failed")

        self.print_complete.emit(success)

    def on_back_clicked(self):
        """Handle back button click"""
        self.back_requested.emit()
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
            QComboBox, QSpinBox {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                background-color: white;
                color: #2c3e50;
            }
            QRadioButton {
                margin: 5px;
                color: #2c3e50;
            }
            QCheckBox {
                margin: 5px;
                color: #2c3e50;
            }
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)

    def get_id_card_image(self):
        """Get the final ID card image"""
        return self.id_card_image

    def closeEvent(self, event):
        """Handle window close event"""
        if self.print_thread and self.print_thread.isRunning():
            self.print_thread.quit()
            self.print_thread.wait()
        event.accept()
