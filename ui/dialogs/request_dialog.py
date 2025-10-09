"""
Request dialog for showing request details and form based on status
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QTextEdit, QSizePolicy
from PyQt6.QtCore import Qt
from datetime import datetime
from utils.datetime_utils import parse_datetime, days_since, format_datetime_for_display
from utils.ui_utils import create_dialog_styles, create_standard_button_styles, create_frame_styles, create_text_edit_styles
from modules.database import db_manager


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

        # Apply styling
        self.setStyleSheet(create_dialog_styles() + create_standard_button_styles() +
                          create_frame_styles() + create_text_edit_styles())

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
                    last_take_dt = parse_datetime(last_take_photo)
                    if last_take_dt:
                        days_ago = days_since(last_take_dt)
                        if days_ago < 365:
                            # Create explanation frame
                            explanation_frame = QFrame()
                            explanation_frame.setObjectName("ExplanationFrame")

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
                            Foto terakhir Anda diambil pada {format_datetime_for_display(last_take_dt)} ({days_ago} hari yang lalu). Menurut kebijakan perusahaan, Anda hanya dapat mengambil foto ID baru sekali dalam setahun. Karena foto terakhir Anda diambil kurang dari setahun yang lalu, Anda perlu meminta izin dari administrator untuk mengambil foto baru. Silakan berikan alasan yang valid untuk permintaan Anda di bawah ini.
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
                dt = datetime.fromisoformat(request_time.replace('Z', '+00:00'))
                formatted_time = format_datetime_for_display(dt)
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
        from ui.dialogs.custom_dialog import CustomStyledDialog

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
