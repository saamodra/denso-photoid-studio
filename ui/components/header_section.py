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
        header_frame.setFixedHeight(150)

        layout = QVBoxLayout(header_frame)

        # Welcome title
        welcome_title = QLabel("Selamat Datang di ID Card Photo Machine")
        welcome_title.setFont(QFont("Helvetica", 28, QFont.Weight.Bold))
        welcome_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_title.setObjectName("WelcomeTitleLabel")
        welcome_title.setStyleSheet("""
            QLabel {
                color: #E60012;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(welcome_title)

        return header_frame
