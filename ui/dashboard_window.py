"""
Dashboard/Welcome Window
Welcome page for logged-in users with options to start photo capture
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QFrame, QGroupBox, QGridLayout, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
import os
from modules.session_manager import session_manager
from config import UI_SETTINGS


class CustomStyledDialog(QDialog):
    """Custom dialog with consistent styling matching the logout confirmation"""

    def __init__(self, parent=None, title="", message="", buttons=None, icon_type="info", rich_text=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(500, 400)  # Larger for instructions

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.message_label.setWordWrap(True)
        if rich_text:
            self.message_label.setTextFormat(Qt.TextFormat.RichText)
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

    def set_cancel_button(self, button_index=0):
        """Set a button as cancel button for different styling"""
        if 0 <= button_index < len(self.buttons):
            self.buttons[button_index].setObjectName("cancelButton")


class DashboardWindow(QMainWindow):
    """Dashboard window for logged-in users"""

    start_photo_capture = pyqtSignal()  # Signal emitted when user wants to start photo capture
    logout_requested = pyqtSignal()  # Signal emitted when logout is requested

    def __init__(self):
        super().__init__()
        self.current_user = None
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
        header_section = self.create_header_section()
        main_layout.addWidget(header_section)

        # Main content section
        content_section = self.create_content_section()
        main_layout.addWidget(content_section)

        # Footer section
        footer_section = self.create_footer_section()
        main_layout.addWidget(footer_section)

        # Set style
        self.apply_modern_style()

    def create_header_section(self):
        """Create header section with welcome message"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        header_frame.setMinimumHeight(120)

        layout = QVBoxLayout(header_frame)
        layout.setContentsMargins(30, 20, 30, 20)

        # Welcome title
        welcome_title = QLabel("Selamat Datang di ID Card Photo Machine")
        welcome_title.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setStyleSheet("""
            QLabel {
                color: #E60012;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(welcome_title)

        # Subtitle
        subtitle = QLabel("Sistem Pembuatan Foto ID Card Otomatis")
        subtitle.setFont(QFont("Helvetica", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #666666;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(subtitle)

        return header_frame

    def create_content_section(self):
        """Create main content section with user info and actions"""
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.StyledPanel)

        layout = QHBoxLayout(content_frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Left side - User info
        user_info_section = self.create_user_info_section()
        layout.addWidget(user_info_section, 40)  # 40% width

        # Right side - Action buttons
        action_section = self.create_action_section()
        layout.addWidget(action_section, 60)  # 60% width

        return content_frame

    def create_user_info_section(self):
        """Create user information section"""
        group = QGroupBox("Informasi Pengguna")
        group.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # User info labels
        self.user_name_label = QLabel("Memuat...")
        self.user_npk_label = QLabel("")
        self.user_role_label = QLabel("")
        self.user_department_label = QLabel("")

        # Style the labels
        user_style = """
            QLabel {
                font-size: 14px;
                color: #2c3e50;
                margin: 5px 0px;
                padding: 5px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
        """

        self.user_name_label.setStyleSheet(user_style + """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #E60012;
                background-color: #fff5f5;
            }
        """)

        self.user_npk_label.setStyleSheet(user_style)
        self.user_role_label.setStyleSheet(user_style)
        self.user_department_label.setStyleSheet(user_style)

        layout.addWidget(self.user_name_label)
        layout.addWidget(self.user_npk_label)
        layout.addWidget(self.user_role_label)
        layout.addWidget(self.user_department_label)

        # Add some spacing
        layout.addStretch()

        return group

    def create_action_section(self):
        """Create action buttons section"""
        group = QGroupBox("Pilih Aksi")
        group.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Main action button - Start Photo Capture
        self.start_photo_btn = QPushButton("📸 Mulai Pengambilan Foto")
        self.start_photo_btn.setMinimumHeight(80)
        self.start_photo_btn.setFont(QFont("Helvetica", 18, QFont.Weight.Bold))
        self.start_photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #E60012;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
                padding: 20px;
            }
            QPushButton:hover {
                background-color: #CC0010;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #99000C;
            }
        """)
        self.start_photo_btn.clicked.connect(self.start_photo_capture_clicked)
        layout.addWidget(self.start_photo_btn)

        # Secondary action button - View Instructions
        self.instructions_btn = QPushButton("📋 Lihat Petunjuk")
        self.instructions_btn.setMinimumHeight(60)
        self.instructions_btn.setFont(QFont("Helvetica", 14))
        self.instructions_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.instructions_btn.clicked.connect(self.show_instructions)
        layout.addWidget(self.instructions_btn)

        # Add some spacing
        layout.addStretch()

        return group

    def create_footer_section(self):
        """Create footer section with logout button"""
        footer_frame = QFrame()
        footer_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        footer_frame.setMaximumHeight(80)

        layout = QHBoxLayout(footer_frame)
        layout.setContentsMargins(30, 15, 30, 15)

        # Left side - Status info
        status_label = QLabel("Sistem siap digunakan")
        status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        layout.addWidget(status_label)

        # Right side - Logout button
        layout.addStretch()
        self.logout_btn = QPushButton("🚪 Logout")
        self.logout_btn.setMinimumHeight(40)
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.logout_btn.clicked.connect(self.logout)
        layout.addWidget(self.logout_btn)

        return footer_frame

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
                self.user_name_label.setText("Tidak ada data pengguna")
                self.user_npk_label.setText("")
                self.user_role_label.setText("")
                self.user_department_label.setText("")

    def start_photo_capture_clicked(self):
        """Handle start photo capture button click"""
        self.start_photo_capture.emit()

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
        <li>Klik "Take Photos" untuk memulai pengambilan</li>
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
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

        # Create custom styled dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Konfirmasi Logout")
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
        logout_btn = QPushButton("Logout")
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
