"""
Custom styled dialog with consistent styling
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


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

        # Apply consistent styling FIRST
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

        # Set size - either custom or auto-adjust based on content
        if custom_size:
            self.setFixedSize(custom_size[0], custom_size[1])
        else:
            # Force layout update after stylesheet is applied
            self.layout().update()
            self.updateGeometry()

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

    def showEvent(self, event):
        """Override showEvent to ensure proper sizing when dialog is shown"""
        super().showEvent(event)
        # Force a final size adjustment when the dialog is actually shown
        self.layout().update()
        self.updateGeometry()
        self.adjustSize()

    def set_cancel_button(self, button_index=0):
        """Set a button as cancel button for different styling"""
        if 0 <= button_index < len(self.buttons):
            self.buttons[button_index].setObjectName("cancelButton")
            # Force stylesheet update to apply the cancel button styling
            self.buttons[button_index].setStyleSheet("""
                QPushButton#cancelButton {
                    background-color: #6c757d;
                    color: #FFFFFF;
                    font-weight: bold;
                    font-size: 14px;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    min-width: 80px;
                }
                QPushButton#cancelButton:hover {
                    background-color: #5a6268;
                }
                QPushButton#cancelButton:pressed {
                    background-color: #495057;
                }
            """)
