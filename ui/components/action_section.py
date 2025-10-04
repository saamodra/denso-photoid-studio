"""
Action section component for dashboard
"""
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class ActionSection:
    """Action buttons section"""

    def __init__(self):
        self.start_photo_btn = None
        self.instructions_btn = None

    def create(self, parent):
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
        layout.addWidget(self.instructions_btn)

        # Add some spacing
        layout.addStretch()

        return group
