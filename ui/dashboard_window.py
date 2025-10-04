"""
Dashboard/Welcome Window
Welcome page for logged-in users with options to start photo capture
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime, timedelta

# Import components
from ui.components.header_section import HeaderSection
from ui.components.user_info_section import UserInfoSection
from ui.components.action_section import ActionSection
from ui.components.footer_section import FooterSection

# Import dialogs
from ui.dialogs.custom_dialog import CustomStyledDialog
from ui.dialogs.request_dialog import RequestDialog

# Import utilities
from utils.datetime_utils import parse_datetime, days_since
from modules.session_manager import session_manager
from modules.database import db_manager


class DashboardWindow(QMainWindow):
    """Dashboard window for logged-in users"""

    start_photo_capture = pyqtSignal()  # Signal emitted when user wants to start photo capture
    logout_requested = pyqtSignal()  # Signal emitted when logout is requested

    def __init__(self):
        super().__init__()
        self.current_user = None

        # Initialize components
        self.user_info_section = UserInfoSection()
        self.action_section = ActionSection()
        self.footer_section = FooterSection()

        self.init_ui()

        # Force window to be visible
        self.show()
        self.raise_()
        self.activateWindow()

    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("ID Card Photo Machine - Dashboard")
        # Set to fullscreen by default
        self.showFullScreen()

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header section
        header_section = HeaderSection.create(self)
        main_layout.addWidget(header_section)

        # Main content section
        content_section = self.create_content_section()
        main_layout.addWidget(content_section)

        # Footer section
        footer_section = self.footer_section.create(self)
        main_layout.addWidget(footer_section)

        # Connect signals
        self.connect_signals()

        # Set style
        self.apply_modern_style()

    def create_content_section(self):
        """Create main content section with user info and actions"""
        content_frame = QWidget()
        content_frame.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
            }
        """)

        layout = QHBoxLayout(content_frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Left side - User info
        user_info_section = self.user_info_section.create(self)
        layout.addWidget(user_info_section, 40)  # 40% width

        # Right side - Action buttons
        action_section = self.action_section.create(self)
        layout.addWidget(action_section, 60)  # 60% width

        return content_frame

    def connect_signals(self):
        """Connect component signals"""
        # Connect action section buttons
        self.action_section.start_photo_btn.clicked.connect(self.start_photo_capture_clicked)
        self.action_section.instructions_btn.clicked.connect(self.show_instructions)

        # Connect footer section logout button
        self.footer_section.logout_btn.clicked.connect(self.logout)

    def set_session_info(self, user_data):
        """Set user session information"""
        self.current_user = user_data
        self.update_user_info()

    def update_user_info(self):
        """Update user information display"""
        if self.current_user:
            self.user_info_section.update_user_info(self.current_user)
        else:
            # Try to get from session manager
            current_user = session_manager.get_current_user()
            if current_user:
                self.current_user = current_user
                self.user_info_section.update_user_info(current_user)
            else:
                self.user_info_section.update_user_info(None)

    def start_photo_capture_clicked(self):
        """Handle start photo capture button click"""
        user = self.current_user or session_manager.get_current_user()

        if not user:
            dialog = CustomStyledDialog(
                self,
                "Pengguna Tidak Ditemukan",
                "Tidak ada pengguna yang sedang login. Silakan login kembali."
            )
            dialog.exec()
            return

        last_take_photo = user.get('last_take_photo')
        last_take_dt = parse_datetime(last_take_photo)

        if not last_take_dt or datetime.now() - last_take_dt >= timedelta(days=365):
            self.start_photo_capture.emit()
            return

        # Get the latest request for the user
        npk = user.get('npk')
        if npk:
            latest_request = db_manager.get_latest_request(npk)
            if latest_request:
                status = latest_request.get('status', '')
                if status == 'requested':
                    # Show details only for requested status
                    request_dialog = RequestDialog(self, user, latest_request)
                    request_dialog.exec()
                    return
                elif status == 'rejected':
                    # Show details + form for rejected status
                    request_dialog = RequestDialog(self, user, latest_request)
                    if request_dialog.exec() == QDialog.DialogCode.Accepted:
                        confirm_dialog = CustomStyledDialog(
                            self,
                            "Permintaan Terkirim",
                            "Permintaan Anda telah dikirim ke admin untuk ditinjau."
                        )
                        confirm_dialog.exec()
                    return

        # No request or approved request, show form only
        request_dialog = RequestDialog(self, user, None)
        if request_dialog.exec() == QDialog.DialogCode.Accepted:
            confirm_dialog = CustomStyledDialog(
                self,
                "Permintaan Terkirim",
                "Permintaan Anda telah dikirim ke admin untuk ditinjau."
            )
            confirm_dialog.exec()

    def show_instructions(self):
        """Show instructions dialog"""
        instructions = """
        <h3>Petunjuk Penggunaan ID Card Photo Machine</h3>
        <p><b>Langkah-langkah:</b></p>
        <ol>
        <li>Klik tombol "Mulai Pengambilan Foto"</li>
        <li>Pilih kamera yang akan digunakan</li>
        <li>Atur jumlah foto dan delay sesuai kebutuhan</li>
        <li>Posisikan diri di depan kamera</li>
        <li>Klik "Ambil Foto" untuk memulai pengambilan</li>
        <li>Ikuti instruksi countdown yang muncul</li>
        <li>Pilih foto terbaik dari hasil pengambilan</li>
        <li>Proses foto menjadi ID card</li>
        <li>Cetak ID card</li>
        </ol>

        <p><b>Tips:</b></p>
        <ul>
        <li>Pastikan pencahayaan cukup</li>
        <li>Posisikan wajah di tengah frame</li>
        <li>Jangan bergerak saat countdown</li>
        <li>Gunakan background putih</li>
        </ul>
        """

        dialog = CustomStyledDialog(
            self,
            "Petunjuk Penggunaan",
            instructions,
            rich_text=True
        )
        dialog.exec()

    def logout(self):
        """Handle logout request"""
        # Create custom styled dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Konfirmasi Keluar")
        dialog.setFixedSize(350, 150)
        dialog.setModal(True)

        # Set white background and dark text
        dialog.setStyleSheet("""
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

        # Layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Message label
        message_label = QLabel("Apakah Anda yakin ingin logout?")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Cancel button
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        # Logout button
        logout_btn = QPushButton("Keluar")
        logout_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(logout_btn)

        layout.addLayout(button_layout)

        # Show dialog and handle result
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Emit signal to main app to handle logout
            self.logout_requested.emit()

    def apply_modern_style(self):
        """Apply modern styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                padding: 10px;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
            QPushButton:pressed {
                background-color: #1b2631;
            }
            QLabel {
                color: #2c3e50;
                background-color: transparent;
            }
        """)

    def closeEvent(self, event):
        """Handle window close event"""
        # Let the main application handle the close event
        # No confirmation dialog here to avoid double confirmation
        event.accept()
