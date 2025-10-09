"""
Header section component for dashboard
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class HeaderSection:
    """Header section with welcome message"""

    @staticmethod
    def create(parent):
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
