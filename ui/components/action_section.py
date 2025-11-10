"""
Action section component for dashboard
"""
from PyQt6.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
    QScrollArea,
    QWidget,
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import os
from config import ASSETS_DIR


INSTRUCTIONS_IMAGE_PATH = os.path.join(ASSETS_DIR, "petunjuk.jpg")


class ActionSection:
    """Action buttons section"""

    def __init__(self):
        self.instructions_label = None

    def create(self, parent):
        """Create action buttons section"""
        group = QGroupBox("Petunjuk Penggunaan")
        group.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.instructions_label = QLabel()
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.instructions_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        pixmap = QPixmap(INSTRUCTIONS_IMAGE_PATH)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                700,
                1000,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.instructions_label.setPixmap(scaled)
        else:
            self.instructions_label.setText(
                "Gambar petunjuk tidak tersedia.\n"
                "Pastikan berkas assets/petunjuk.jpg ada."
            )
            self.instructions_label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)
        scroll_layout.addWidget(self.instructions_label, 0, Qt.AlignmentFlag.AlignTop)

        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        return group
