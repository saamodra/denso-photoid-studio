"""
Footer section component for dashboard
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


class FooterSection:
    """Footer section with logout button"""

    def __init__(self):
        self.logout_btn = None

    def create(self, parent):
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
        layout.addWidget(self.logout_btn)

        return footer_frame
