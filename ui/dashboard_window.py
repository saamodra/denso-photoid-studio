"""
Dashboard/Welcome Window
Welcome page for logged-in users with options to start photo capture
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QFrame, QGroupBox, QGridLayout, QDialog, QTextEdit, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
import os
from datetime import datetime, timedelta
from modules.session_manager import session_manager
from modules.database import db_manager
from config import UI_SETTINGS


class CustomStyledDialog(QDialog):
    """Custom dialog with consistent styling that auto-adjusts size based on content"""

    def __init__(self, parent=None, title="", message="", buttons=None, icon_type="info",
                 rich_text=False, custom_size=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

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

        # Set size - either custom or auto-adjust based on content
        if custom_size:
            self.setFixedSize(custom_size[0], custom_size[1])
        else:
            # Auto-adjust size based on content
            self.adjustSize()
            # Set minimum and maximum reasonable sizes
            current_size = self.size()
            min_width = 300
            max_width = 800
            min_height = 120
            max_height = 600

            width = max(min_width, min(max_width, current_size.width()))
            height = max(min_height, min(max_height, current_size.height()))
            self.resize(width, height)

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


class RequestDialog(QDialog):
    """Unified dialog for showing request details and form based on status"""

    def __init__(self, parent=None, user=None, request_data=None):
        super().__init__(parent)
        self.user = user or {}
        self.request_data = request_data or {}
        self.setWindowTitle("Formulir Permintaan")
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Formulir Permintaan")
        title_label.setObjectName("TitleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Add explanation section for why user needs to request
        self._add_explanation_section(layout)

        # Determine what to show based on request status
        status = self.request_data.get('status', '') if self.request_data else ''

        # Show details section if there's a request (requested or rejected)
        if self.request_data and status in ['requested', 'rejected']:
            self._add_details_section(layout)

        # Show form section if no request or if rejected
        if not self.request_data or status == 'rejected':
            self._add_form_section(layout)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if self.request_data and status in ['requested', 'approved']:
            # Show close button for requested/approved
            close_button = QPushButton("Tutup")
            close_button.clicked.connect(self.accept)
            button_layout.addWidget(close_button)
        else:
            # Show cancel and send buttons for form
            cancel_button = QPushButton("Batal")
            cancel_button.setObjectName("cancelButton")
            cancel_button.clicked.connect(self.reject)
            button_layout.addWidget(cancel_button)

            send_button = QPushButton("Kirim Permintaan")
            send_button.clicked.connect(self._handle_send)
            button_layout.addWidget(send_button)

        layout.addLayout(button_layout)

        # Apply styling first
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                color: #333333;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
                margin: 0px;
                padding: 0px;
            }
            QLabel#TitleLabel {
                font-size: 20px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 10px;
            }
            QLabel#SectionTitle {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                margin-bottom: 5px;
            }
            QFrame#DetailsFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame#NotesFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 8px;
                padding: 10px;
            }
            QTextEdit {
                border: 1px solid #CCCCCC;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                background-color: #FFFFFF;
                color: #333333;
            }
            QPushButton {
                background-color: #E60012;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 100px;
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

        # Dynamic sizing based on content
        self._adjust_dialog_size()

    def _add_explanation_section(self, layout):
        """Add explanation section for why user needs to request permission"""
        # Only show explanation if there's no existing request
        if not self.request_data:
            # Check if user's last photo was less than 1 year ago
            last_take_photo = self.user.get('last_take_photo')
            if last_take_photo:
                try:
                    last_take_dt = self._parse_datetime(last_take_photo)
                    if last_take_dt:
                        days_ago = (datetime.now() - last_take_dt).days
                        if days_ago < 365:
                            # Create explanation frame
                            explanation_frame = QFrame()
                            explanation_frame.setObjectName("ExplanationFrame")
                            explanation_frame.setStyleSheet("""
                                QFrame#ExplanationFrame {
                                    background-color: #fff3cd;
                                    border: 1px solid #ffeaa7;
                                    border-radius: 8px;
                                    padding: 15px;
                                }
                            """)

                            explanation_layout = QVBoxLayout(explanation_frame)
                            explanation_layout.setSpacing(8)

                            # Title
                            title_label = QLabel("Perlu Izin untuk Mengambil Foto Baru")
                            title_label.setStyleSheet("""
                                QLabel {
                                    font-size: 16px;
                                    font-weight: bold;
                                    color: #856404;
                                    margin-bottom: 5px;
                                }
                            """)
                            explanation_layout.addWidget(title_label)

                            # Explanation text
                            explanation_text = f"""
                            Your last photo was taken on {last_take_dt.strftime('%Y-%m-%d %H:%M:%S')} ({days_ago} days ago). According to company policy, you can only take a new ID photo once per year. Since your last photo was taken less than a year ago, you need to request permission from the administrator to take a new photo.  Please provide a valid reason for your request below.
                            """

                            explanation_label = QLabel(explanation_text.strip())
                            explanation_label.setWordWrap(True)
                            explanation_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
                            explanation_label.setStyleSheet("""
                                QLabel {
                                    color: #856404;
                                    font-size: 14px;
                                    line-height: 1.4;
                                }
                            """)
                            explanation_layout.addWidget(explanation_label)

                            layout.addWidget(explanation_frame)
                except:
                    pass

    @staticmethod
    def _parse_datetime(value):
        """Parse datetime value from various formats"""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
        return None

    def showEvent(self, event):
        """Override showEvent to ensure proper sizing when dialog is shown"""
        super().showEvent(event)
        # Re-adjust size after the dialog is fully shown
        self._adjust_dialog_size()

    def _add_details_section(self, layout):
        """Add the details section showing last request info"""
        # Section title
        section_title = QLabel("Permintaan Terakhir Anda")
        section_title.setObjectName("SectionTitle")
        section_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(section_title)

        # Details frame
        details_frame = QFrame()
        details_frame.setObjectName("DetailsFrame")
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(8)
        details_layout.setContentsMargins(15, 15, 15, 15)
        details_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        # Request time
        request_time = self.request_data.get('request_time', '')
        if request_time:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(request_time.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                formatted_time = request_time
            time_label = QLabel(f"<b>Time:</b> {formatted_time}")
            details_layout.addWidget(time_label)

        # Status
        status = self.request_data.get('status', 'requested')
        if status == 'approved':
            status_text = "Disetujui"
            status_color = "#28a745"
        elif status == 'rejected':
            status_text = "Ditolak"
            status_color = "#dc3545"
        else:
            status_text = "Menunggu"
            status_color = "#ffc107"

        status_label = QLabel(f"<b>Status:</b> <span style='color: {status_color};'>{status_text}</span>")
        details_layout.addWidget(status_label)

        # Request Description
        request_desc = self.request_data.get('request_desc', '')
        if request_desc:
            desc_label = QLabel(f"<b>Description:</b> {request_desc}")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            details_layout.addWidget(desc_label)

        # Remarks
        remark = self.request_data.get('remark', '')
        if remark:
            remark_label = QLabel(f"<b>Remarks:</b> {remark}")
            remark_label.setWordWrap(True)
            remark_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
            details_layout.addWidget(remark_label)

        layout.addWidget(details_frame)

    def _add_form_section(self, layout):
        """Add the form section for new request"""
        # Reason label
        reason_label = QLabel("Alasan")
        reason_label.setObjectName("SectionTitle")
        reason_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(reason_label)

        # Reason input
        self.reason_input = QTextEdit()
        self.reason_input.setPlaceholderText("Masukkan alasan permintaan Anda...")
        self.reason_input.setMinimumHeight(100)
        self.reason_input.setMaximumHeight(150)
        layout.addWidget(self.reason_input)

    def _adjust_dialog_size(self):
        """Adjust dialog size dynamically based on content"""
        # Force layout update first
        self.layout().update()
        self.updateGeometry()

        # Calculate the required size based on content
        self.adjustSize()

        # Get the size hint from the layout
        size_hint = self.sizeHint()

        # Determine if we have form content (reason input)
        has_form = hasattr(self, 'reason_input')

        # Set reasonable bounds based on content
        min_width = 500
        max_width = 700

        if has_form:
            # When there's a form, allow more height
            min_height = 300
            max_height = 600
        else:
            # When there's no form, be more compact
            min_height = 150
            max_height = 400

        # Calculate optimal size based on content
        width = max(min_width, min(max_width, size_hint.width()))
        height = max(min_height, min(max_height, size_hint.height()))

        # Apply the calculated size
        self.resize(width, height)

        # Set minimum size to prevent it from being too small
        self.setMinimumSize(min_width, min_height)

        # Ensure the dialog doesn't exceed screen bounds
        screen = self.screen().availableGeometry()
        if self.width() > screen.width():
            self.resize(screen.width() - 50, self.height())
        if self.height() > screen.height():
            self.resize(self.width(), screen.height() - 50)


    def _handle_send(self):
        """Handle send request button click"""
        reason = self.reason_input.toPlainText().strip()
        if not reason:
            dialog = CustomStyledDialog(
                self,
                "Alasan Dibutuhkan",
                "Silakan isi alasan permintaan sebelum mengirim."
            )
            dialog.exec()
            return

        npk = self.user.get('npk')
        if not npk:
            dialog = CustomStyledDialog(
                self,
                "Data Pengguna Tidak Lengkap",
                "Tidak dapat mengirim permintaan karena data pengguna tidak lengkap."
            )
            dialog.exec()
            return

        if db_manager.add_request_history(npk, reason):
            self.accept()
        else:
            dialog = CustomStyledDialog(
                self,
                "Gagal Mengirim",
                "Permintaan tidak dapat dikirim saat ini. Silakan coba lagi."
            )
            dialog.exec()




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
        last_take_dt = self._parse_datetime(last_take_photo)

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
        from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton

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

    @staticmethod
    def _parse_datetime(value):
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
        return None
