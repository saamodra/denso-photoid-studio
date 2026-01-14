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


class AspectRatioPixmapLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        # Selalu set pixmap asli dulu supaya tidak kosong
        super().setPixmap(pixmap)
        if self._pixmap is not None and not self._pixmap.isNull():
            self._update_scaled_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._pixmap is not None and not self._pixmap.isNull():
            self._update_scaled_pixmap()

    def _update_scaled_pixmap(self):
        if (
            self._pixmap is None
            or self._pixmap.isNull()
        ):
            return
        parent = self.parent()
        available_width = parent.width() if parent is not None else self.width()
        if available_width <= 0:
            return
        original_width = self._pixmap.width()
        original_height = self._pixmap.height()
        if original_width <= 0 or original_height <= 0:
            return
        target_width = available_width
        target_height = int(target_width * original_height / original_width)
        scaled = self._pixmap.scaled(
            target_width,
            target_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        super().setPixmap(scaled)
        self.setMinimumSize(scaled.size())


class ActionSection:
    """Action buttons section"""

    def __init__(self):
        self.instructions_label = None

    def create(self, parent):
        """Create action buttons section"""
        group = QGroupBox()
        group.setFont(QFont("Helvetica", 14, QFont.Weight.Bold))
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        self.instructions_label = AspectRatioPixmapLabel()
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instructions_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # Minimal ukuran agar selalu terlihat (rasio 16:9)
        self.instructions_label.setMinimumSize(640, 360)
        self.instructions_label.setStyleSheet("""
            QLabel {
                background-color: #FFFFFF;
                border-radius: 12px;
                padding: 10px;
            }
        """)

        pixmap = QPixmap(INSTRUCTIONS_IMAGE_PATH)
        if not pixmap.isNull():
            self.instructions_label.setPixmap(pixmap)
        else:
            self.instructions_label.setText(
                "Gambar petunjuk tidak tersedia.\n"
                "Pastikan berkas assets/petunjuk.jpg ada."
            )
            self.instructions_label.setWordWrap(True)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
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
