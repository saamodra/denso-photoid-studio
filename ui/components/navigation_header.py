"""
Reusable navigation header with previous/next buttons and step info.
"""
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal


class NavigationHeader(QFrame):
    """Header menampilkan informasi langkah serta tombol navigasi."""

    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()

    def __init__(
        self,
        step: int,
        total_steps: int,
        title: str,
        subtitle: str = "",
        prev_text: str = "← Sebelumnya",
        next_text: str = "Berikutnya →",
        show_prev: bool = True,
        show_next: bool = True,
    ):
        super().__init__()
        self.prev_button = None
        self.next_button = None
        self.setObjectName("NavigationHeader")
        self._build_ui(prev_text, next_text, show_prev, show_next)
        self.set_step(step, total_steps)
        self.set_title(title)
        self.set_subtitle(subtitle)

    def _build_ui(self, prev_text: str, next_text: str, show_prev: bool, show_next: bool):
        self.setFixedHeight(220 if (show_prev or show_next) else 160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(4)

        text_container = QVBoxLayout()
        text_container.setContentsMargins(0, 0, 0, 0)
        text_container.setSpacing(0)

        self.step_label = QLabel()
        self.step_label.setContentsMargins(0, 0, 0, 0)
        self.step_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                font-weight: bold;
                margin: 0;
                padding: 0;
            }
        """)
        text_container.addWidget(self.step_label)

        self.title_label = QLabel()
        self.title_label.setContentsMargins(0, 0, 0, 0)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 24px;
                font-weight: bold;
                margin: 0;
                padding: 0;
            }
        """)
        text_container.addWidget(self.title_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setContentsMargins(0, 0, 0, 0)
        self.subtitle_label.setStyleSheet("""
            QLabel {
                color: #4a4a4a;
                font-size: 14px;
                margin: 0;
                padding: 0;
            }
        """)
        text_container.addWidget(self.subtitle_label)

        layout.addLayout(text_container)

        if show_prev or show_next:
            button_row = QHBoxLayout()
            button_row.setSpacing(8)
            button_row.setContentsMargins(0, 10, 0, 0)

            if show_prev:
                self.prev_button = QPushButton(prev_text)
                self.prev_button.setMinimumHeight(48)
                self.prev_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.prev_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2c3e50;
                        color: #ffffff;
                        border: none;
                        border-radius: 24px;
                        padding: 0 28px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #1f2a36;
                    }
                    QPushButton:disabled {
                        background-color: #95a5a6;
                    }
                """)
                self.prev_button.clicked.connect(self.prev_clicked.emit)
                button_row.addWidget(self.prev_button, 0, Qt.AlignmentFlag.AlignLeft)
            else:
                button_row.addSpacing(0)

            button_row.addStretch(1)

            if show_next:
                self.next_button = QPushButton(next_text)
                self.next_button.setMinimumHeight(48)
                self.next_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.next_button.setStyleSheet("""
                    QPushButton {
                        background-color: #E60012;
                        color: #ffffff;
                        border: none;
                        border-radius: 24px;
                        padding: 0 32px;
                        font-size: 14px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c2000f;
                    }
                    QPushButton:disabled {
                        background-color: #f5b7b1;
                        color: #ffffff;
                    }
                """)
                self.next_button.clicked.connect(self.next_clicked.emit)
                button_row.addWidget(self.next_button, 0, Qt.AlignmentFlag.AlignRight)

            layout.addLayout(button_row)

        self.setStyleSheet("""
            #NavigationHeader {
                background-color: #ffffff;
                border-bottom: 1px solid #e0e0e0;
            }
        """)

    def set_step(self, step: int, total_steps: int):
        self.step_label.setText(f"Langkah {step} dari {total_steps}")

    def set_title(self, title: str):
        self.title_label.setText(title)

    def set_subtitle(self, subtitle: str):
        self.subtitle_label.setText(subtitle)

    def set_next_enabled(self, enabled: bool):
        if self.next_button:
            self.next_button.setEnabled(enabled)

    def set_prev_enabled(self, enabled: bool):
        if self.prev_button:
            self.prev_button.setEnabled(enabled)

    def set_next_text(self, text: str):
        if self.next_button:
            self.next_button.setText(text)

    def set_prev_text(self, text: str):
        if self.prev_button:
            self.prev_button.setText(text)
