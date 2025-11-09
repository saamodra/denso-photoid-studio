"""
Print Window UI
Interface for print preview and printing
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QFrame,
                            QGroupBox, QMessageBox,
                            QProgressBar, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap
from PIL import Image
import os
import tempfile
from datetime import datetime
from modules.print_manager import PrintManager
from modules.database import db_manager
from modules.session_manager import session_manager
from ui.components.navigation_header import NavigationHeader


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
            self.status_update.emit("Mempersiapkan gambar untuk dicetak...")
            self.progress_update.emit(20)

            # Prepare image
            prepared_image = self.print_manager.prepare_image_for_printing(
                self.image, self.copies
            )
            self.progress_update.emit(50)

            self.status_update.emit("Mengirim ke printer...")

            # Print based on method
            if self.print_method == 'qt':
                success = self.print_manager.print_image_qt(prepared_image, self.printer_name)
            else:
                success = self.print_manager.print_image_system(
                    prepared_image, self.printer_name, self.copies
                )

            self.progress_update.emit(100)

            if success:
                self.status_update.emit("Pekerjaan cetak berhasil dikirim!")
            else:
                self.status_update.emit("Pekerjaan cetak gagal")

            self.print_complete.emit(success)

        except Exception as e:
            self.status_update.emit(f"Kesalahan cetak: {str(e)}")
            self.print_complete.emit(False)


class PrintWindow(QMainWindow):
    """Print preview and printing window"""
    # Slightly smaller preview surface so the card fits on low-resolution displays
    PREVIEW_TARGET_WIDTH = 420
    PREVIEW_TARGET_HEIGHT = 640
    PREVIEW_PADDING = 30  # matches QLabel padding defined in the stylesheet
    PREVIEW_SCALE_FACTOR = 0.85  # additional shrink so nothing gets clipped

    print_complete = pyqtSignal(bool)  # Success/failure
    back_requested = pyqtSignal()
    logout_requested = pyqtSignal()

    def __init__(self, processed_image, original_image_path=None):
        super().__init__()
        self.processed_image = processed_image
        self.original_image_path = original_image_path
        self.print_manager = PrintManager()
        self.image_processor = None  # Not needed for direct implementation
        self.print_thread = None
        self.id_card_image = None
        self.init_ui()
        self.create_id_card()
        self.load_print_settings()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Pratinjau Cetak")
        # Set to fullscreen by default
        self.showFullScreen()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        self.navigation_header = NavigationHeader(
            step=4,
            total_steps=4,
            title="Pratinjau & Cetak",
            subtitle="Periksa hasil akhir dan selesaikan sesi",
            prev_text="← Kembali ke Edit Foto",
            show_next=False
        )
        self.navigation_header.prev_clicked.connect(self.on_back_clicked)
        self.back_button = self.navigation_header.prev_button
        self.finish_button = None
        root_layout.addWidget(self.navigation_header)

        # Main layout - use horizontal layout for better space utilization
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        root_layout.addLayout(main_layout)

        # Left side - Preview section (portrait orientation)
        left_layout = QVBoxLayout()
        preview_section = self.create_preview_section()
        left_layout.addWidget(preview_section)

        # Right side - Settings and controls
        right_layout = QVBoxLayout()
        right_layout.setSpacing(10)

        # Status section
        status_section = self.create_status_section()
        right_layout.addWidget(status_section)

        # Button section
        button_section = self.create_button_section()
        right_layout.addWidget(button_section)

        # Settings section
        settings_section = self.create_settings_section()
        right_layout.addWidget(settings_section)

        # Add layouts to main layout
        main_layout.addLayout(left_layout, 60)  # 60% width for preview
        main_layout.addLayout(right_layout, 40)  # 40% width for controls

        # Apply styling
        self.apply_style()

    def get_copy_count(self):
        """Return fixed copy count since salinan panel has been removed."""
        return 1

    def create_preview_section(self):
        """Create print preview section - portrait orientation like ID card"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the entire content

        # Section title
        title = QLabel("Pratinjau Cetak")
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
        self.preview_label.setFixedSize(
            self.PREVIEW_TARGET_WIDTH,
            self.PREVIEW_TARGET_HEIGHT
        )
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

        return frame

    def create_settings_section(self):
        """Create print settings section - simplified"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title
        title = QLabel("Pengaturan Cetak")
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

        layout.addStretch()

        return frame

    def create_printer_group(self):
        """Create printer information group - readonly"""
        group = QGroupBox("Printer")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Printer info display (readonly)
        self.printer_info_label = QLabel("Memuat informasi printer...")
        self.printer_info_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 11px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                min-height: 20px;
            }
        """)
        layout.addWidget(self.printer_info_label)

        # Printer error label
        self.printer_error_label = QLabel("")
        self.printer_error_label.setStyleSheet("""
            QLabel {
                color: #DC3545;
                font-weight: bold;
                font-size: 10px;
                background-color: #F8D7DA;
                border: 1px solid #F5C6CB;
                border-radius: 4px;
                padding: 4px;
                margin-top: 2px;
            }
        """)
        self.printer_error_label.hide()
        layout.addWidget(self.printer_error_label)

        return group

    def create_status_section(self):
        """Create status section - compact"""
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Status label
        self.status_label = QLabel("Siap untuk mencetak")
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

        # Horizontal button row (flex-like)
        self.save_button = QPushButton("💾 Simpan")
        self.save_button.setMinimumHeight(45)
        self.save_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.save_button.clicked.connect(self.save_id_card)

        self.print_button = QPushButton("🖨️ Cetak")
        self.print_button.setMinimumHeight(45)
        self.print_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.print_button.clicked.connect(self.print_id_card)

        self.finish_button = QPushButton("✅️ Selesaikan Sesi")
        self.finish_button.setMinimumHeight(45)
        self.finish_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.finish_button.clicked.connect(self.on_finish_clicked)

        button_row = QHBoxLayout()
        button_row.setSpacing(12)
        button_row.addWidget(self.save_button)
        button_row.addWidget(self.print_button)
        button_row.addWidget(self.finish_button)

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
            self.preview_label.setText("Kesalahan membuat\nlayout ID card")

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
            copies = self.get_copy_count()

            # Create print preview
            preview_image = self.print_manager.create_print_preview(
                self.id_card_image, copies
            )

            # Display preview
            self.display_preview(preview_image)

        except Exception as e:
            print(f"Error updating preview: {e}")
            self.preview_label.setText("Kesalahan memperbarui\npratinjau")

    def display_preview(self, image):
        """Display preview image with correct aspect ratio (object-fit: contain behavior) - portrait orientation"""
        try:
            # Calculate the maximum size that fits within the portrait preview area
            width_hint = self.preview_label.width() or self.PREVIEW_TARGET_WIDTH
            height_hint = self.preview_label.height() or self.PREVIEW_TARGET_HEIGHT
            usable_width = max(width_hint - self.PREVIEW_PADDING, 100)
            usable_height = max(height_hint - self.PREVIEW_PADDING, 100)
            max_width = int(usable_width * self.PREVIEW_SCALE_FACTOR)
            max_height = int(usable_height * self.PREVIEW_SCALE_FACTOR)

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
            self.preview_label.setText("Kesalahan pratinjau")

    def load_print_settings(self):
        """Load print settings and populate UI"""
        # Load printers
        self.print_manager.available_printers = self.print_manager.get_system_printers()

        # Auto-select printer from database
        self.auto_select_printer_from_database()

        # Update printer info display
        self.update_printer_info_display()

    def auto_select_printer_from_database(self):
        """Auto-select printer from database configuration"""
        try:
            default_printer = db_manager.get_app_config('default_printer')
            if not default_printer:
                self.printer_error_label.setText("⚠️ Tidak ada printer yang dikonfigurasi. Silakan hubungi admin untuk mengatur printer.")
                self.printer_error_label.show()
                return False

            # Check if the saved printer is still available
            printers = self.print_manager.get_available_printers()
            printer_found = False

            for printer in printers:
                if default_printer.lower() in printer['name'].lower():
                    printer_found = True
                    break

            if not printer_found:
                self.printer_error_label.setText(f"⚠️ Printer yang dikonfigurasi '{default_printer}' tidak tersedia. Silakan hubungi admin untuk memperbarui pengaturan printer.")
                self.printer_error_label.show()
                return False
            else:
                self.printer_error_label.hide()
                return True

        except Exception as e:
            print(f"Error auto-selecting printer from database: {e}")
            self.printer_error_label.setText(f"Kesalahan memuat konfigurasi printer: {str(e)}")
            self.printer_error_label.show()
            return False

    def update_printer_info_display(self):
        """Update printer information display"""
        try:
            default_printer = db_manager.get_app_config('default_printer')
            printers = self.print_manager.get_available_printers()

            if not default_printer:
                self.printer_info_label.setText("Tidak ada printer yang dikonfigurasi\nHubungi admin untuk mengatur printer")
                return

            # Find the configured printer
            printer_found = False
            for printer in printers:
                if default_printer.lower() in printer['name'].lower():
                    self.printer_info_label.setText(f"Printer yang Dikonfigurasi:\n{printer['name']}\nStatus: {printer['status']}")
                    printer_found = True
                    break

            if not printer_found:
                self.printer_info_label.setText(f"Printer yang Dikonfigurasi:\n{default_printer}\n(Tidak Tersedia)")

        except Exception as e:
            print(f"Error updating printer info display: {e}")
            self.printer_info_label.setText("Kesalahan memuat informasi printer")

    def validate_printer_from_database(self):
        """Validate if the printer from database is still available"""
        try:
            default_printer = db_manager.get_app_config('default_printer')
            if not default_printer:
                self.printer_error_label.hide()
                return

            # Check if the saved printer is still available
            printers = self.print_manager.get_available_printers()
            printer_found = False

            for printer in printers:
                if default_printer.lower() in printer['name'].lower():
                    printer_found = True
                    break

            if not printer_found:
                # Printer not found, show error
                self.printer_error_label.setText(f"⚠️ Printer yang dikonfigurasi '{default_printer}' tidak tersedia. Silakan hubungi admin untuk memperbarui pengaturan printer.")
                self.printer_error_label.show()
            else:
                # Printer is available, hide error
                self.printer_error_label.hide()

        except Exception as e:
            print(f"Error validating printer from database: {e}")
            self.printer_error_label.setText(f"Kesalahan memvalidasi printer: {str(e)}")
            self.printer_error_label.show()

    def print_id_card(self):
        """Print ID card"""
        if not self.id_card_image:
            self.status_label.setText("Tidak ada ID card untuk dicetak")
            return

        if self.print_thread and self.print_thread.isRunning():
            return

        # Get printer from database
        printer_name = db_manager.get_app_config('default_printer')
        if not printer_name:
            self.status_label.setText("Tidak ada printer yang dikonfigurasi")
            return

        # Validate printer is available
        if not self.auto_select_printer_from_database():
            self.status_label.setText("Printer yang dikonfigurasi tidak tersedia")
            return

        copies = self.get_copy_count()

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
            self.status_label.setText("Pekerjaan cetak berhasil diselesaikan!")
            self.save_id_card()
        else:
            self.status_label.setText("Pekerjaan cetak gagal")

        self.print_complete.emit(success)

    def on_back_clicked(self):
        """Handle back button click"""
        self.back_requested.emit()

    def on_finish_clicked(self):
        """Handle finish button click to end session"""
        self.finish_button.setEnabled(False)
        self.close()
        self.logout_requested.emit()

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

    def generate_unique_filename(self, user_npk, file_type, extension="png"):
        """
        Generate unique filename for user photos and ID cards

        Args:
            user_npk: User's NPK (employee ID)
            file_type: Type of file ('photo' or 'card')
            extension: File extension (default: 'png')

        Returns:
            Unique filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        return f"{user_npk}_{file_type}_{timestamp}.{extension}"

    def save_id_card(self):
        """Save ID card to database and files"""
        try:
            if not self.id_card_image:
                self.status_label.setText("Tidak ada ID card untuk disimpan")
                return

            # Get current user
            current_user = session_manager.get_current_user()
            if not current_user:
                self.status_label.setText("Tidak ada pengguna yang login")
                return

            # Get image save path from database configuration
            image_save_path = db_manager.get_app_config('image_save_path')
            if not image_save_path:
                self.show_save_error("Path simpan gambar tidak dikonfigurasi. Silakan hubungi administrator.")
                return

            # Check if the configured path exists
            if not os.path.exists(image_save_path):
                self.show_save_error(f"Direktori simpan gambar tidak ada:\n{image_save_path}\n\nSilakan hubungi administrator untuk membuat direktori.")
                return

            user_npk = current_user['npk']
            current_time = datetime.now()

            # Create subdirectories within the configured path
            original_dir = os.path.join(image_save_path, "original")
            card_dir = os.path.join(image_save_path, "card")

            # Create directories if they don't exist
            os.makedirs(original_dir, exist_ok=True)
            os.makedirs(card_dir, exist_ok=True)

            # Remove previous files if they exist
            previous_photo = current_user.get('photo_filename')
            previous_card = current_user.get('card_filename')

            if previous_photo:
                old_photo_path = os.path.join(original_dir, previous_photo)
                if os.path.exists(old_photo_path):
                    try:
                        os.remove(old_photo_path)
                    except Exception as remove_err:
                        print(f"Peringatan: gagal menghapus foto sebelumnya {old_photo_path}: {remove_err}")

            if previous_card:
                old_card_path = os.path.join(card_dir, previous_card)
                if os.path.exists(old_card_path):
                    try:
                        os.remove(old_card_path)
                    except Exception as remove_err:
                        print(f"Peringatan: gagal menghapus kartu sebelumnya {old_card_path}: {remove_err}")

            # Generate unique filenames
            photo_filename = self.generate_unique_filename(user_npk, "photo")
            card_filename = self.generate_unique_filename(user_npk, "card")

            # Define file paths
            original_photo_path = os.path.join(original_dir, photo_filename)
            card_photo_path = os.path.join(card_dir, card_filename)

            # Save the ID card image
            self.id_card_image.save(card_photo_path, format='PNG', quality=95)

            # Save the original image if available, otherwise save the processed image
            if self.original_image_path and os.path.exists(self.original_image_path):
                # Load and save the actual original image
                original_image = Image.open(self.original_image_path)
                original_image.save(original_photo_path, format='PNG', quality=95)
            else:
                # Fallback: save the processed image as original (for backward compatibility)
                self.id_card_image.save(original_photo_path, format='PNG', quality=95)

            # Update user record in database
            update_data = {
                'last_take_photo': current_time,
                'photo_filename': photo_filename,
                'card_filename': card_filename
            }

            success = db_manager.update_user(user_npk, update_data)
            if not success:
                self.status_label.setText("Gagal memperbarui database pengguna")
                return

            # Add photo history record
            history_success = db_manager.add_photo_history(user_npk, current_time)
            if not history_success:
                self.status_label.setText("Gagal menambahkan riwayat foto")
                return

            # Update session manager with new photo info
            session_manager.update_user_photo_info(photo_filename, card_filename)

            self.status_label.setText(f"ID card berhasil disimpan!\nFoto: {photo_filename}\nKartu: {card_filename}")

        except Exception as e:
            self.status_label.setText(f"Kesalahan simpan: {str(e)}")
            print(f"Error saving ID card: {e}")

    def show_save_error(self, message):
        """Show error dialog for save failures"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle("Simpan Gagal")
        msg_box.setText("Gagal menyimpan ID card")
        msg_box.setDetailedText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

        # Also update status label
        self.status_label.setText("Simpan gagal - lihat dialog kesalahan")

    def get_id_card_image(self):
        """Get the final ID card image"""
        return self.id_card_image

    def closeEvent(self, event):
        """Handle window close event"""
        if self.print_thread and self.print_thread.isRunning():
            self.print_thread.quit()
            self.print_thread.wait()
        event.accept()
